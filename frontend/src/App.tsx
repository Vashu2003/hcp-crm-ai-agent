import { useState } from 'react';
import { InteractionForm } from './components/InteractionForm';
import { ChatPanel } from './components/ChatPanel';
import { InteractionList } from './components/InteractionList';
import { StatsBar } from './components/StatsBar';
import { FollowUps } from './components/FollowUps';

type Mode = 'form' | 'chat';

function App() {
  const [mode, setMode] = useState<Mode>('form');

  return (
    <>
      <header className="app-header">
        <div className="logo">H</div>
        <div>
          <div className="title">HCP CRM · AI Interaction Logging</div>
          <div className="subtitle">Log doctor interactions by form or chat — one AI agent, five tools</div>
        </div>
        <span className="spacer" />
        <span className="rep-chip">👤 Vashu Singh · Field Rep</span>
      </header>

      <main className="container">
        <StatsBar />
        <div className="grid">
          <section className="card">
            <div className="card-head" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h2>Log interaction</h2>
                <div className="hint">Both modes feed the same LangGraph agent</div>
              </div>
              <div className="tabs">
                <button className={`tab ${mode === 'form' ? 'active' : ''}`} onClick={() => setMode('form')}>📋 Form</button>
                <button className={`tab ${mode === 'chat' ? 'active' : ''}`} onClick={() => setMode('chat')}>💬 Chat</button>
              </div>
            </div>
            {mode === 'form' ? (
              <div className="card-body"><InteractionForm /></div>
            ) : (
              <ChatPanel />
            )}
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
