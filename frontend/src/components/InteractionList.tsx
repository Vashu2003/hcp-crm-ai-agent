import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchInteractions } from '../store/interactionsSlice';
import { SentimentBadge } from './SentimentBadge';
import { IconSearch } from './Icons';

function initials(name?: string | null) {
  if (!name) return '?';
  const parts = name.replace(/^dr\.?\s+/i, '').trim().split(/\s+/);
  return ((parts[0]?.[0] ?? '') + (parts[parts.length - 1]?.[0] ?? '')).toUpperCase();
}

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
        <div>
          <h2>Recent interactions</h2>
          <div className="hint">Logged via form or chat — updates live</div>
        </div>
      </div>
      <form className="toolbar" onSubmit={search}>
        <div className="search-wrap">
          <IconSearch size={15} />
          <input className="input" placeholder="Filter by HCP name…"
            value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <button className="btn btn-ghost">Search</button>
      </form>
      <div className="list">
        {status === 'loading' && <div className="list-loading">Loading…</div>}
        {status !== 'loading' && items.length === 0 && (
          <div className="list-empty">No interactions yet. Log one to get started.</div>
        )}
        {items.map((i) => (
          <div className="list-item" key={i.id}>
            <div className="av">{initials(i.hcp?.name)}</div>
            <div className="li-main">
              <div className="li-top">
                <span className="li-name">{i.hcp?.name ?? `HCP #${i.hcp_id}`}</span>
                <span className="spacer" />
                <span className="li-meta">{i.date} · {i.channel ?? '—'}</span>
              </div>
              <div className="li-sub">
                <SentimentBadge sentiment={i.sentiment} />
                {i.product_discussed && <span className="tag">{i.product_discussed}</span>}
              </div>
              <div className="li-summary">{i.llm_summary ?? i.raw_notes}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
