"""
Koti AI Coding - Mentor API

Run (from this folder, with the venv active):
    uvicorn api:app --reload

Environment options:
    USE_ADAPTER=0        -> skip the LoRA fine-tune and use the plain base chat model
    ADAPTER_PATH=...     -> which adapter folder to load (default: ./tinyllama-coding-model-v2 if it has an adapter, else ./tinyllama-coding-model)
    MAX_NEW_TOKENS=768   -> longer / shorter answers (default 384)
    QUANTIZE=0           -> disable int8 speed-up (full fp32, slower but exact)
"""
import os
import threading
import time
from typing import List, Optional

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# Uses a v2 adapter if one is ever trained into this folder; otherwise the original adapter
_V2 = "./tinyllama-coding-model-v2"
ADAPTER_PATH = os.getenv(
    "ADAPTER_PATH",
    _V2 if os.path.exists(os.path.join(_V2, "adapter_config.json")) else "./tinyllama-coding-model",
)
USE_ADAPTER = os.getenv("USE_ADAPTER", "1") != "0"
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "384"))
QUANTIZE = os.getenv("QUANTIZE", "1") != "0"
MAX_HISTORY = 4  # previous messages kept for follow-up questions (shorter prompt = faster)

from prompts import SYSTEM_PROMPT  # shared system prompt

# ---------------------------------------------------------------- small talk
# A 1.1B model fine-tuned on a handful of coding examples tends to turn
# "hi how are you" into a coding tutorial, so casual messages get instant,
# fixed replies and never reach the model.
import random
import re

_GREETING = r"(hi+|hey+|hello+|hii+|helo|yo|hola|namaste|good (morning|afternoon|evening|night))"
_HOW_ARE_YOU = r"(how are (you|u)|how r u|how('?s| is) it going|how do you do|what'?s up|wassup|sup)"
SMALL_TALK = [
    (rf"^{_GREETING}?\W*(there|bro|buddy|koti)?\W*{_HOW_ARE_YOU}(\W*(doing|today|bro|buddy|koti))*\W*$",
     ["I'm doing great, thanks for asking! 😊 How can I help you with your code today?",
      "All good here, thank you! What would you like to build or learn today?"]),
    (rf"^{_GREETING}\W*(there|bro|buddy|koti|ai)?\W*$",
     ["Hello! 👋 I'm Koti AI Coding, your coding mentor. What can I help you with today?",
      "Hi there! Ask me to write, explain or debug some code."]),
    (r"^(thanks|thank you|thx|ty|thank u)( so much| a lot| very much)?\W*(bro|buddy|koti)?\W*$",
     ["You're welcome! Let me know if you have any other questions.",
      "Happy to help! Anything else you'd like to work on?"]),
    (r"^(bye|goodbye|see you|see ya|good night|gn|cya)\W*$",
     ["Goodbye! Happy coding! 👋", "See you later. Keep coding! 🚀"]),
    (r"^(who are you|what are you|what is your name|what'?s your name|your name\??|introduce yourself)\W*$",
     ["I'm **Koti AI Coding**, a coding mentor built on TinyLlama 1.1B and fine-tuned with LoRA. "
      "I can write code, explain concepts and help you debug."]),
    (r"^(ok|okay|k|cool|nice|great|awesome|good|fine|i'?m (good|fine|great))\W*$",
     ["Great! What would you like to do next?", "Nice! Ask me anything about code whenever you're ready."]),
]


def small_talk_reply(prompt: str) -> Optional[str]:
    text = re.sub(r"\s+", " ", prompt.strip().lower())
    if len(text) > 60:
        return None
    for pattern, replies in SMALL_TALK:
        if re.match(pattern, text):
            return random.choice(replies)
    return None


def max_tokens_for(prompt: str) -> int:
    """Short, casual prompts get short answers; real questions get the full budget."""
    words = len(prompt.split())
    looks_technical = bool(re.search(
        r"code|function|program|python|java|script|error|bug|class|explain|write|how|why|what|sql|api|algorithm|```",
        prompt.lower()))
    if words <= 6 and not looks_technical:
        return min(80, MAX_NEW_TOKENS)
    return MAX_NEW_TOKENS

# Physical cores are faster than all logical threads for matrix math (12 threads -> 6 cores)
torch.set_num_threads(max(1, (os.cpu_count() or 4) // 2))

app = FastAPI(title="Koti AI Coding Mentor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------- model loading
print(f"Loading base model: {BASE_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, dtype=torch.float32)

adapter_loaded = False
if USE_ADAPTER and os.path.exists(os.path.join(ADAPTER_PATH, "adapter_config.json")):
    try:
        from peft import PeftModel

        print(f"Applying LoRA adapter from: {ADAPTER_PATH}")
        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
        model = model.merge_and_unload()  # merge for faster inference
        adapter_loaded = True
    except Exception as e:  # keep the API usable even if the adapter is broken
        print(f"WARNING: could not load adapter ({e}). Using base model only.")
else:
    print("LoRA adapter disabled or not found - using base model only.")

model.eval()
model.generation_config.max_length = None
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

MODEL_LABEL = f"{os.path.basename(ADAPTER_PATH.rstrip('/'))} (LoRA)" if adapter_loaded else BASE_MODEL
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model.to(DEVICE)

# ---- CPU speed-up: int8 dynamic quantization of the Linear layers (~2x faster, ~1/4 the memory)
if DEVICE == "cpu" and QUANTIZE:
    try:
        from torch.ao.quantization import quantize_dynamic

        model = quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
        MODEL_LABEL += " int8"
        print("Applied int8 dynamic quantization for faster CPU inference.")
    except Exception as e:
        print(f"WARNING: int8 quantization unavailable ({e}); using fp32.")
generate_lock = threading.Lock()  # one generation at a time (CPU friendly)
print(f"Model ready on {DEVICE}: {MODEL_LABEL}")


# ---------------------------------------------------------------- schemas
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class Question(BaseModel):
    prompt: str
    history: Optional[List[ChatMessage]] = None


class StopOnEvent(StoppingCriteria):
    """Stops generation when the client disconnects."""

    def __init__(self, event: threading.Event):
        self.event = event

    def __call__(self, input_ids, scores, **kwargs):
        return self.event.is_set()


# ---------------------------------------------------------------- helpers
def build_inputs(data: Question):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in (data.history or [])[-MAX_HISTORY:]:
        if m.role in ("user", "assistant") and m.content.strip():
            messages.append({"role": m.role, "content": m.content})
    messages.append({"role": "user", "content": data.prompt})

    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    )
    return {k: v.to(DEVICE) for k, v in input_ids.items()}


def gen_kwargs(inputs, max_new_tokens=MAX_NEW_TOKENS, **extra):
    return dict(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.4,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id,
        **extra,
    )


# ---------------------------------------------------------------- routes
@app.get("/")
def health():
    return {
        "status": "ok",
        "model": MODEL_LABEL,
        "adapter": adapter_loaded,
        "device": DEVICE,
    }


@app.post("/ask")
def ask(data: Question):
    """Returns the whole answer at once (kept for compatibility)."""
    quick = small_talk_reply(data.prompt)
    if quick:
        return {"response": quick}
    inputs = build_inputs(data)
    with generate_lock, torch.inference_mode():
        outputs = model.generate(**gen_kwargs(inputs, max_tokens_for(data.prompt)))
    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return {"response": answer}


@app.post("/ask/stream")
def ask_stream(data: Question):
    """Streams the answer token-by-token as plain text."""
    quick = small_talk_reply(data.prompt)
    if quick:
        def quick_stream():
            for word in re.findall(r"\S+\s*", quick):  # word-by-word typing effect
                yield word
                time.sleep(0.03)

        return StreamingResponse(
            quick_stream(),
            media_type="text/plain; charset=utf-8",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    inputs = build_inputs(data)
    budget = max_tokens_for(data.prompt)
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    stop_event = threading.Event()

    def run():
        with generate_lock, torch.inference_mode():
            try:
                model.generate(
                    **gen_kwargs(
                        inputs,
                        budget,
                        streamer=streamer,
                        stopping_criteria=StoppingCriteriaList([StopOnEvent(stop_event)]),
                    )
                )
            except Exception as e:
                print(f"Generation error: {e}")
                streamer.end()

    threading.Thread(target=run, daemon=True).start()

    def token_stream():
        try:
            for text in streamer:
                yield text
        finally:
            stop_event.set()  # client went away -> stop generating

    return StreamingResponse(
        token_stream(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
