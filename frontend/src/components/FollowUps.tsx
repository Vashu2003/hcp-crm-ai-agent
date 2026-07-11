import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchFollowups, markFollowupDone } from '../store/followupsSlice';
import { IconCheck, IconCalendar } from './Icons';

function initials(name?: string | null) {
  if (!name) return '?';
  const parts = name.replace(/^dr\.?\s+/i, '').trim().split(/\s+/);
  return ((parts[0]?.[0] ?? '') + (parts[parts.length - 1]?.[0] ?? '')).toUpperCase();
}

export function FollowUps() {
  const dispatch = useAppDispatch();
  const { items, status } = useAppSelector((s) => s.followups);
  const interactionCount = useAppSelector((s) => s.interactions.items.length);

  useEffect(() => {
    dispatch(fetchFollowups());
  }, [dispatch, interactionCount]);

  const pending = items.filter((f) => (f.status ?? 'pending') === 'pending');
  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="card">
      <div className="card-head">
        <div>
          <h2>Upcoming follow-ups</h2>
          <div className="hint">Auto-created by the AI when a follow-up is implied</div>
        </div>
      </div>
      <div className="list">
        {status === 'loading' && <div className="list-loading">Loading…</div>}
        {status !== 'loading' && pending.length === 0 && (
          <div className="list-empty">No pending follow-ups.</div>
        )}
        {pending.map((f) => {
          const overdue = f.due_date && f.due_date < today;
          return (
            <div className="list-item" key={f.id}>
              <div className="av">{initials(f.hcp?.name)}</div>
              <div className="li-main">
                <div className="li-top">
                  <span className="li-name">{f.hcp?.name ?? `HCP #${f.hcp_id}`}</span>
                  <span className="spacer" />
                  <button className="btn btn-ghost btn-sm" onClick={() => dispatch(markFollowupDone(f.id))}>
                    <IconCheck size={13} /> Done
                  </button>
                </div>
                {f.due_date && (
                  <div className="li-sub">
                    <span className="sent" style={{ color: overdue ? 'var(--neg)' : 'var(--ink-2)' }}>
                      <IconCalendar size={13} />
                      {overdue ? 'Overdue' : 'Due'} {f.due_date}
                    </span>
                  </div>
                )}
                <div className="li-summary">{f.action ?? 'Follow up'}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
