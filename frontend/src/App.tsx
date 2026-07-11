import { useEffect, useState } from 'react';
import { InteractionForm } from './components/InteractionForm';
import { ChatPanel } from './components/ChatPanel';
import { InteractionList } from './components/InteractionList';
import { StatsBar } from './components/StatsBar';
import { FollowUps } from './components/FollowUps';
import { IconPulse, IconSun, IconMoon } from './components/Icons';

type Theme = 'light' | 'dark';

function App() {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <>
      <header className="app-header">
        <div className="brandmark"><IconPulse size={18} /></div>
        <span className="wordmark">HCP&nbsp;CRM</span>
        <span className="divider-v" />
        <span className="subtitle">Interaction logging · one agent, five tools</span>
        <span className="spacer" />
        <button className="icon-btn" onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} title="Toggle theme">
          {theme === 'dark' ? <IconSun size={17} /> : <IconMoon size={17} />}
        </button>
        <span className="rep">
          <span className="avatar">VS</span>
          Vashu Singh · Field Rep
        </span>
      </header>

      <main className="container">
        <StatsBar />

        <section className="card log-card">
          <div className="card-head">
            <div>
              <h2>Log interaction</h2>
              <div className="hint">Describe the visit in chat — the AI fills the form on the left. You can edit any field, then Save.</div>
            </div>
          </div>
          <div className="split">
            <div className="split-form">
              <div className="pane-label">Interaction details</div>
              <InteractionForm />
            </div>
            <div className="split-chat">
              <div className="pane-label">Assistant</div>
              <ChatPanel />
            </div>
          </div>
        </section>

        <div className="grid">
          <InteractionList />
          <FollowUps />
        </div>

        <p className="footer-note">
          FastAPI · LangGraph · Groq ({import.meta.env.VITE_MODEL ?? 'gpt-oss-20b'}) · PostgreSQL · React + Redux
        </p>
      </main>
    </>
  );
}

export default App;
