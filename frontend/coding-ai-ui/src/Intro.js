import { useEffect, useState } from "react";
import "./Intro.css";

const TAGLINE = "Your personal AI coding mentor — fine-tuned, local, private.";

const FEATURES = [
  { title: "Write code", text: "Functions, classes and snippets on demand", color: "red", d: "m16 18 6-6-6-6M8 6l-6 6 6 6" },
  { title: "Debug faster", text: "Explain errors and suggest clean fixes", color: "orange", d: "M12 2a4 4 0 0 1 4 4v2H8V6a4 4 0 0 1 4-4zM6 10h12v6a6 6 0 0 1-12 0zM2 13h4M18 13h4M3 7l3 3M21 7l-3 3" },
  { title: "Learn concepts", text: "Step-by-step explanations with examples", color: "amber", d: "M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5zM20 17v4H6.5A2.5 2.5 0 0 1 4 19.5" },
];

const PARTICLE_COLORS = ["#dc2626", "#f97316", "#ea580c", "#f59e0b"];
const PARTICLES = Array.from({ length: 18 }, (_, i) => ({
  left: (i * 29) % 100,
  size: 2 + (i % 4),
  dur: 10 + ((i * 7) % 14),
  delay: -((i * 3) % 18),
  color: PARTICLE_COLORS[i % PARTICLE_COLORS.length],
}));

function Intro({ onEnter }) {
  const [typed, setTyped] = useState("");
  const [leaving, setLeaving] = useState(false);

  // Typewriter tagline
  useEffect(() => {
    let i = 0;
    const id = setInterval(() => {
      i += 1;
      setTyped(TAGLINE.slice(0, i));
      if (i >= TAGLINE.length) clearInterval(id);
    }, 35);
    return () => clearInterval(id);
  }, []);

  const enter = () => {
    if (leaving) return;
    setLeaving(true);
    setTimeout(onEnter, 700); // matches .intro.leaving animation
  };

  // Enter key also opens the main page
  useEffect(() => {
    const onKey = (e) => e.key === "Enter" && enter();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  return (
    <div className={`intro ${leaving ? "leaving" : ""}`}>
      <div className="intro-bg" aria-hidden="true">
        <div className="intro-blob ib-1" />
        <div className="intro-blob ib-2" />
        <div className="intro-blob ib-3" />
        <div className="intro-grid" />
        {PARTICLES.map((p, i) => (
          <span
            key={i}
            className="intro-particle"
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

      <main className="intro-content">
        <div className="intro-logo">
          <div className="intro-ring" />
          <div className="intro-ring r2" />
          <div className="intro-logo-core">
            <svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="8" width="18" height="12" rx="3" />
              <path d="M12 8V4" />
              <circle cx="12" cy="3" r="1" />
              <circle cx="8.5" cy="14" r="1.2" />
              <circle cx="15.5" cy="14" r="1.2" />
              <path d="M1 13v3M23 13v3" />
            </svg>
          </div>
        </div>

        <span className="intro-badge">
          <span className="intro-dot" /> TinyLlama 1.1B · LoRA fine-tuned
        </span>

        <h1 className="intro-title">
          Koti <span>AI Coding</span>
        </h1>

        <p className="intro-tagline">
          {typed}
          <span className="intro-caret" />
        </p>

        <div className="intro-features">
          {FEATURES.map((f, i) => (
            <div key={f.title} className={`intro-feature ${f.color}`} style={{ animationDelay: `${1.6 + i * 0.15}s` }}>
              <div className="intro-feature-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d={f.d} />
                </svg>
              </div>
              <h3>{f.title}</h3>
              <p>{f.text}</p>
            </div>
          ))}
        </div>

        <button className="intro-cta" onClick={enter}>
          Get Started
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 12h14M13 5l7 7-7 7" />
          </svg>
        </button>
        <p className="intro-hint">or press <kbd>Enter</kbd></p>
      </main>
    </div>
  );
}

export default Intro;
