import { useState } from 'react';
import { InteractionForm } from './components/InteractionForm';
import { ChatPanel } from './components/ChatPanel';
import { InteractionList } from './components/InteractionList';
import { StatsBar } from './components/StatsBar';
import { FollowUps } from './components/FollowUps';
import { IconPulse, IconForm, IconChat } from './components/Icons';

type Mode = 'form' | 'chat';

function App() {
  const [mode, setMode] = useState<Mode>('form');

  return (
    <>
      <header className="app-header">
        <div className="brandmark"><IconPulse size={18} /></div>
        <span className="wordmark">HCP&nbsp;CRM</span>
        <span className="divider-v" />
        <span className="subtitle">Interaction logging · one agent, five tools</span>
        <span className="spacer" />
        <span className="rep">
          <span className="avatar">VS</span>
          Vashu Singh · Field Rep
        </span>
      </header>

      <main className="container">
        <StatsBar />
        <div className="grid">
          <section className="card">
            <div className="card-head">
              <div>
                <h2>Log interaction</h2>
                <div className="hint">Both modes feed the same LangGraph agent</div>
              </div>
              <div className="tabs">
                <button className={`tab ${mode === 'form' ? 'active' : ''}`} onClick={() => setMode('form')}>
                  <IconForm size={14} /> Form
                </button>
                <button className={`tab ${mode === 'chat' ? 'active' : ''}`} onClick={() => setMode('chat')}>
                  <IconChat size={14} /> Chat
                </button>
              </div>
            </div>
            {mode === 'form' ? <div className="card-body"><InteractionForm /></div> : <ChatPanel />}
          </section>

          <div className="col">
            <InteractionList />
            <FollowUps />
          </div>
        </div>
        <p className="footer-note">
          FastAPI · LangGraph · Groq ({import.meta.env.VITE_MODEL ?? 'gpt-oss-20b'}) · PostgreSQL · React + Redux
        </p>
      </main>
    </>
  );
}

export default App;
