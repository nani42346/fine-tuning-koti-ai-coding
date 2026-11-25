import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

// Override at build time with REACT_APP_API_URL (e.g. a hosted API); defaults to the local server
const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

/* ---------- Inline icon set (no extra dependency) ---------- */
const paths = {
  bot: (
    <>
      <rect x="3" y="8" width="18" height="12" rx="3" />
      <path d="M12 8V4" />
      <circle cx="12" cy="3" r="1" />
      <circle cx="8.5" cy="14" r="1.2" />
      <circle cx="15.5" cy="14" r="1.2" />
      <path d="M1 13v3M23 13v3" />
    </>
  ),
  user: (
    <>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
    </>
  ),
  send: (
    <>
      <path d="M22 2 11 13" />
      <path d="M22 2 15 22l-4-9-9-4 20-7z" />
    </>
  ),
  plus: <path d="M12 5v14M5 12h14" />,
  chat: <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />,
  zap: <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />,
  clock: (
    <>
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </>
  ),
  cpu: (
    <>
      <rect x="4" y="4" width="16" height="16" rx="2" />
      <rect x="9" y="9" width="6" height="6" />
      <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
    </>
  ),
  code: <path d="m16 18 6-6-6-6M8 6l-6 6 6 6" />,
  copy: (
    <>
      <rect x="9" y="9" width="13" height="13" rx="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </>
  ),
  check: <path d="M20 6 9 17l-5-5" />,
  trash: (
    <>
      <path d="M3 6h18M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6M14 11v6M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
    </>
  ),
  sparkles: (
    <>
      <path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" />
      <path d="M19 3v4M17 5h4M5 17v4M3 19h4" />
    </>
  ),
  database: (
    <>
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5" />
      <path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3" />
    </>
  ),
  bug: (
    <>
      <rect x="8" y="6" width="8" height="14" rx="4" />
      <path d="M19 7l-3 2M5 7l3 2M19 13h-3M5 13h3M19 19l-3-2M5 19l3-2M12 6V3" />
    </>
  ),
  book: (
    <>
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z" />
      <path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5" />
    </>
  ),
  layers: (
    <>
      <path d="m12 2 10 5-10 5L2 7z" />
      <path d="m2 17 10 5 10-5M2 12l10 5 10-5" />
    </>
  ),
  history: (
    <>
      <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
      <path d="M3 3v5h5M12 7v5l4 2" />
    </>
  ),
  menu: <path d="M3 6h18M3 12h18M3 18h18" />,
};

function Icon({ name, size = 18, className = "" }) {
  return (
    <svg
      className={`icon ${className}`}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}

const SUGGESTIONS = [
  { icon: "code", color: "violet", title: "Write a function", prompt: "Write a Python function to reverse a linked list" },
  { icon: "bug", color: "pink", title: "Debug my code", prompt: "Why does my JavaScript forEach not wait for async calls?" },
  { icon: "book", color: "cyan", title: "Explain a concept", prompt: "Explain recursion with a simple example" },
  { icon: "layers", color: "amber", title: "Data structures", prompt: "What is the difference between a stack and a queue?" },
];

const PARTICLE_COLORS = ["#dc2626", "#f97316", "#ea580c", "#f59e0b", "#fca5a5"];
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  left: (i * 37) % 100,
  size: 2 + (i % 4),
  dur: 14 + ((i * 7) % 16),
  delay: -((i * 3) % 20),
  color: PARTICLE_COLORS[i % PARTICLE_COLORS.length],
}));

/* 3D tilt + spotlight that follows the mouse inside a card */
function trackPointer(e) {
  const el = e.currentTarget;
  const r = el.getBoundingClientRect();
  const x = e.clientX - r.left;
  const y = e.clientY - r.top;
  el.style.setProperty("--mx", `${x}px`);
  el.style.setProperty("--my", `${y}px`);
  if (el.dataset.tilt !== undefined) {
    const rx = ((y / r.height) - 0.5) * -12;
    const ry = ((x / r.width) - 0.5) * 12;
    el.style.setProperty("--rx", `${rx}deg`);
    el.style.setProperty("--ry", `${ry}deg`);
  }
}
function resetPointer(e) {
  e.currentTarget.style.setProperty("--rx", "0deg");
  e.currentTarget.style.setProperty("--ry", "0deg");
}

/* Material-style ripple on any button */
function ripple(e) {
  const btn = e.target.closest("button");
  if (!btn) return;
  const r = btn.getBoundingClientRect();
  const size = Math.max(r.width, r.height) * 2;
  const s = document.createElement("span");
  s.className = "ripple";
  s.style.width = s.style.height = `${size}px`;
  s.style.left = `${e.clientX - r.left - size / 2}px`;
  s.style.top = `${e.clientY - r.top - size / 2}px`;
  btn.appendChild(s);
  setTimeout(() => s.remove(), 650);
}

/* Animated number count-up */
function CountUp({ value }) {
  const [shown, setShown] = useState(value);
  const prev = useRef(value);
  useEffect(() => {
    const from = prev.current;
    const to = value;
    prev.current = value;
    if (typeof to !== "number" || typeof from !== "number" || from === to) {
      setShown(to);
      return;
    }
    let raf;
    const start = performance.now();
    const step = (t) => {
      const p = Math.min((t - start) / 500, 1);
      setShown(Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return <>{shown}</>;
}

function formatTime(d) {
  return new Date(d).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };
  return (
    <button className="msg-action" onClick={copy} title="Copy">
      <Icon name={copied ? "check" : "copy"} size={14} />
      <span>{copied ? "Copied" : "Copy"}</span>
    </button>
  );
}

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ online: null, model: "—" });
  const [times, setTimes] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatBoxRef = useRef(null);
  const inputRef = useRef(null);
  const glowRef = useRef(null);
  const abortRef = useRef(null);

  // Glow that follows the cursor across the whole page
  useEffect(() => {
    const move = (e) => {
      if (glowRef.current) {
        glowRef.current.style.transform = `translate(${e.clientX - 300}px, ${e.clientY - 300}px)`;
      }
    };
    window.addEventListener("pointermove", move);
    return () => window.removeEventListener("pointermove", move);
  }, []);

  // Health check
  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API_URL}/`);
        const data = await res.json();
        setStatus({ online: true, model: data.model || "unknown" });
      } catch {
        setStatus((s) => ({ ...s, online: false }));
      }
    };
    check();
    const id = setInterval(check, 15000);
    return () => clearInterval(id);
  }, []);

  // Scroll only the chat box (scrollIntoView would also scroll the page layout)
  useEffect(() => {
    const box = chatBoxRef.current;
    if (box) box.scrollTo({ top: box.scrollHeight, behavior: "smooth" });
  }, [chat, loading]);

  // Make sure the page itself is never left scrolled
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const sendMessage = async (override) => {
    const text = (override ?? message).trim();
    if (!text || loading) return;

    // Previous turns so the model can answer follow-up questions
    const history = chat
      .filter((m) => !m.error && m.text)
      .map((m) => ({ role: m.sender === "ai" ? "assistant" : "user", content: m.text }));

    const newChat = [...chat, { sender: "user", text, time: Date.now() }];
    setChat(newChat);
    setMessage("");
    setLoading(true);
    const start = performance.now();
    const controller = new AbortController();
    abortRef.current = controller;
    let answer = "";

    try {
      const res = await fetch(`${API_URL}/ask/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text, history }),
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      setStatus((s) => ({ ...s, online: true }));

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        answer += decoder.decode(value, { stream: true });
        setChat([...newChat, { sender: "ai", text: answer, time: Date.now(), streaming: true }]);
      }
      const elapsed = (performance.now() - start) / 1000;
      setTimes((t) => [...t, elapsed]);
      setChat([
        ...newChat,
        { sender: "ai", text: answer.trim() || "_(no answer generated)_", time: Date.now(), elapsed },
      ]);
    } catch (err) {
      if (err.name === "AbortError") {
        setChat([
          ...newChat,
          { sender: "ai", text: (answer.trim() || "") + "\n\n_⏹ Stopped._", time: Date.now() },
        ]);
      } else {
        setChat([
          ...newChat,
          {
            sender: "ai",
            error: true,
            text:
              `**Couldn't reach the model** (${err.message}).\n\n` +
              `The model API at \`${API_URL}\` is not running. The model runs locally, so start it from the project folder ` +
              `(or double-click **start.bat** on Windows):\n\n` +
              "```bash\nvenv\\Scripts\\activate   # macOS/Linux: source venv/bin/activate\nuvicorn api:app --reload\n```\n\n" +
              `Wait for **"Application startup complete"**, then ask again. ` +
              `Setup guide: [github.com/nani42346/fine-tuning-koti-ai-coding](https://github.com/nani42346/fine-tuning-koti-ai-coding)`,
            time: Date.now(),
          },
        ]);
        setStatus((s) => ({ ...s, online: false }));
      }
    } finally {
      abortRef.current = null;
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const stopGenerating = () => abortRef.current?.abort();

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const newChat = () => {
    setChat([]);
    setTimes([]);
    setSidebarOpen(false);
    inputRef.current?.focus();
  };

  const questions = chat.filter((m) => m.sender === "user");
  const avg = times.length ? (times.reduce((a, b) => a + b, 0) / times.length).toFixed(1) : "—";
  const modelName = status.model.split("/").pop().replace(/^\.\//, "");

  const stats = [
    { icon: "chat", color: "violet", label: "Messages", value: chat.length, sub: "this session" },
    { icon: "sparkles", color: "pink", label: "Questions", value: questions.length, sub: "asked so far" },
    { icon: "clock", color: "cyan", label: "Avg. response", value: avg === "—" ? avg : `${avg}s`, sub: "generation time" },
    { icon: "cpu", color: "amber", label: "Model", value: modelName || "—", sub: "fine-tuned LoRA", small: true },
  ];

  const statusLabel = status.online === null ? "Connecting…" : status.online ? "API Online" : "API Offline";
  const statusClass = status.online === null ? "pending" : status.online ? "online" : "offline";

  return (
    <div className="layout" onPointerDown={ripple}>
      <div className="bg" aria-hidden="true">
        <div className="bg-blob blob-1" />
        <div className="bg-blob blob-2" />
        <div className="bg-blob blob-3" />
        {PARTICLES.map((p, i) => (
          <span
            key={i}
            className="particle"
            style={{
              left: `${p.left}%`,
              width: p.size,
              height: p.size,
              animationDuration: `${p.dur}s`,
              animationDelay: `${p.delay}s`,
              background: p.color,
              color: p.color,
            }}
          />
        ))}
      </div>
      <div className="cursor-glow" ref={glowRef} aria-hidden="true" />

      {/* ---------- Sidebar ---------- */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-logo">
            <Icon name="bot" size={22} />
          </div>
          <div>
            <div className="brand-name">Koti AI Coding</div>
            <div className="brand-tag">Your AI Mentor</div>
          </div>
        </div>

        <button className="new-chat" onClick={newChat}>
          <Icon name="plus" size={16} /> New conversation
        </button>

        <div className="side-section">
          <div className="side-title">
            <Icon name="history" size={14} /> Recent prompts
          </div>
          {questions.length === 0 ? (
            <div className="side-empty">No questions yet</div>
          ) : (
            <ul className="history">
              {questions
                .slice()
                .reverse()
                .slice(0, 8)
                .map((q, i) => (
                  <li
                    key={i}
                    title={q.text}
                    onClick={() => {
                      setMessage(q.text);
                      setSidebarOpen(false);
                      inputRef.current?.focus();
                    }}
                  >
                    <Icon name="chat" size={14} />
                    <span>{q.text}</span>
                  </li>
                ))}
            </ul>
          )}
        </div>

        <div className="model-card">
          <div className="model-card-head">
            <Icon name="database" size={16} />
            <span>Model info</span>
          </div>
          <div className="model-row">
            <span>Base</span>
            <strong>TinyLlama 1.1B</strong>
          </div>
          <div className="model-row">
            <span>Method</span>
            <strong>LoRA fine-tune</strong>
          </div>
          <div className="model-row">
            <span>Status</span>
            <strong className={`dot-text ${statusClass}`}>{statusLabel}</strong>
          </div>
        </div>
      </aside>
      {sidebarOpen && <div className="scrim" onClick={() => setSidebarOpen(false)} />}

      {/* ---------- Main ---------- */}
      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-btn menu-btn" onClick={() => setSidebarOpen(true)} aria-label="Open menu">
              <Icon name="menu" />
            </button>
            <div>
              <h1>
                Coding <span className="gradient-text">Mentor</span> Dashboard
              </h1>
              <p className="subtitle">Ask anything about code — powered by your fine-tuned model</p>
            </div>
          </div>
          <div className="topbar-right">
            <span className={`status-pill ${statusClass}`}>
              <span className="pulse" />
              {statusLabel}
            </span>
            {chat.length > 0 && (
              <button className="icon-btn" onClick={newChat} title="Clear chat">
                <Icon name="trash" />
              </button>
            )}
          </div>
        </header>

        <section className="stats">
          {stats.map((s, i) => (
            <div
              key={s.label}
              className={`stat-card ${s.color}`}
              data-tilt
              style={{ animationDelay: `${i * 90}ms` }}
              onPointerMove={trackPointer}
              onPointerLeave={resetPointer}
            >
              <div className="stat-icon">
                <Icon name={s.icon} size={20} />
              </div>
              <div className="stat-body">
                <div className="stat-label">{s.label}</div>
                <div className={`stat-value ${s.small ? "small" : ""}`} title={String(s.value)}>
                  <CountUp value={s.value} />
                </div>
                <div className="stat-sub">{s.sub}</div>
              </div>
            </div>
          ))}
        </section>

        <section className={`chat-panel ${loading ? "busy" : ""}`}>
          <div className="chat-box" ref={chatBoxRef}>
            {chat.length === 0 && !loading ? (
              <div className="empty">
                <div className="empty-icon">
                  <Icon name="sparkles" size={34} />
                </div>
                <h2>How can I help you code today?</h2>
                <p>Pick a starter below or type your own question.</p>
                <div className="suggestions">
                  {SUGGESTIONS.map((s, i) => (
                    <button
                      key={s.title}
                      className={`suggestion ${s.color}`}
                      style={{ animationDelay: `${200 + i * 100}ms` }}
                      onPointerMove={trackPointer}
                      onClick={() => sendMessage(s.prompt)}
                    >
                      <span className="suggestion-icon">
                        <Icon name={s.icon} size={18} />
                      </span>
                      <span className="suggestion-text">
                        <strong>{s.title}</strong>
                        <small>{s.prompt}</small>
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              chat.map((msg, index) => (
                <div key={index} className={`msg-row ${msg.sender}`}>
                  <div className="avatar">
                    <Icon name={msg.sender === "ai" ? "bot" : "user"} size={18} />
                  </div>
                  <div className={`bubble ${msg.error ? "error" : ""}`}>
                    <div className="bubble-head">
                      <span className="who">{msg.sender === "ai" ? "Koti AI Coding" : "You"}</span>
                      <span className="time">{formatTime(msg.time)}</span>
                      {msg.elapsed && (
                        <span className="badge">
                          <Icon name="zap" size={11} /> {msg.elapsed.toFixed(1)}s
                        </span>
                      )}
                    </div>
                    <div className={`bubble-content ${msg.streaming ? "streaming" : ""}`}>
                      {msg.sender === "ai" ? <ReactMarkdown>{msg.text}</ReactMarkdown> : msg.text}
                    </div>
                    {msg.sender === "ai" && !msg.error && !msg.streaming && (
                      <div className="msg-actions">
                        <CopyButton text={msg.text} />
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {loading && !chat[chat.length - 1]?.streaming && (
              <div className="msg-row ai">
                <div className="avatar thinking">
                  <Icon name="bot" size={18} />
                </div>
                <div className="bubble typing">
                  <span />
                  <span />
                  <span />
                  <em>Thinking…</em>
                </div>
              </div>
            )}
          </div>

          <div className="input-box">
            <div className="input-wrap">
              <Icon name="code" size={18} className="input-icon" />
              <textarea
                ref={inputRef}
                rows={1}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Ask a coding question…  (Enter to send, Shift+Enter for new line)"
                disabled={loading}
              />
              {loading ? (
                <button className="send-btn stop" onClick={stopGenerating} title="Stop generating">
                  <span className="spinner" />
                  <span>Stop</span>
                </button>
              ) : (
                <button className="send-btn" onClick={() => sendMessage()} disabled={!message.trim()}>
                  <Icon name="send" size={18} />
                  <span>Send</span>
                </button>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
