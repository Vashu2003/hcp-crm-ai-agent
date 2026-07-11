import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAppDispatch, useAppSelector } from '../store';
import { sendMessage, pushUserMessage } from '../store/chatSlice';
import { fetchInteractions } from '../store/interactionsSlice';
import { IconTool } from './Icons';

const SUGGESTIONS = [
  'Met Dr. Menon on a call about Januvia, he had insurance concerns.',
  'Show me all positive interactions about Xarelto',
  'Summarize my last month with Dr. Sharma',
  'Schedule a follow-up with Dr. Patel next Tuesday',
];

export function ChatPanel() {
  const dispatch = useAppDispatch();
  const { messages, sending } = useAppSelector((s) => s.chat);
  const [text, setText] = useState('');
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, sending]);

  const send = (value: string) => {
    const msg = value.trim();
    if (!msg || sending) return;
    dispatch(pushUserMessage(msg));
    setText('');
    dispatch(sendMessage(msg)).then(() => dispatch(fetchInteractions()));
  };

  return (
    <div className="chat">
      <div className="chat-log" ref={logRef}>
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.role === 'assistant' ? (
              <div className="md">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
              </div>
            ) : (
              m.content
            )}
            {m.tool_calls && m.tool_calls.length > 0 && (
              <div className="tools">
                {m.tool_calls.map((t, j) => (
                  <span key={j} className="tool-chip"><IconTool size={11} /> {t}</span>
                ))}
              </div>
            )}
          </div>
        ))}
        {sending && <div className="typing">Assistant is thinking…</div>}
        {messages.length <= 1 && (
          <div className="suggest">
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" className="suggest-chip" onClick={() => send(s)}>{s}</button>
            ))}
          </div>
        )}
      </div>
      <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send(text); }}>
        <input className="input" placeholder="Log a visit or ask the agent…"
          value={text} onChange={(e) => setText(e.target.value)} />
        <button className="btn btn-primary" disabled={sending || !text.trim()}>Send</button>
      </form>
    </div>
  );
}
