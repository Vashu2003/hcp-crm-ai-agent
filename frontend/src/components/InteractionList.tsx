import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchInteractions } from '../store/interactionsSlice';
import { SentimentBadge } from './SentimentBadge';

export function InteractionList() {
  const dispatch = useAppDispatch();
  const { items, status } = useAppSelector((s) => s.interactions);
  const [query, setQuery] = useState('');

  useEffect(() => {
    dispatch(fetchInteractions());
  }, [dispatch]);

  const search = (e: React.FormEvent) => {
    e.preventDefault();
    dispatch(fetchInteractions(query.trim() ? { hcp_name: query.trim() } : undefined));
  };

  return (
    <div className="card">
      <div className="card-head">
        <h2>Recent interactions</h2>
        <div className="hint">Logged via form or chat — updates live</div>
      </div>
      <form className="toolbar" onSubmit={search}>
        <input className="input" placeholder="Filter by HCP name…"
          value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="btn btn-ghost">Search</button>
      </form>
      <div className="list">
        {status === 'loading' && <div className="list-loading">Loading…</div>}
        {status !== 'loading' && items.length === 0 && (
          <div className="list-empty">No interactions yet. Log one to get started.</div>
        )}
        {items.map((i) => (
          <div className="list-item" key={i.id}>
            <div className="top">
              <span className="name">{i.hcp?.name ?? `HCP #${i.hcp_id}`}</span>
              <SentimentBadge sentiment={i.sentiment} />
              <span className="spacer" />
              <span className="meta">{i.date} · {i.channel ?? '—'}</span>
            </div>
            <div className="meta">
              {i.product_discussed ? `💊 ${i.product_discussed}` : 'No product noted'}
            </div>
            <div className="summary">{i.llm_summary ?? i.raw_notes}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
