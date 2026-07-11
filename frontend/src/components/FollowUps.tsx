import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchFollowups, markFollowupDone } from '../store/followupsSlice';

export function FollowUps() {
  const dispatch = useAppDispatch();
  const { items, status } = useAppSelector((s) => s.followups);
  // Re-fetch when interactions change (chat/form may add follow-ups).
  const interactionCount = useAppSelector((s) => s.interactions.items.length);

  useEffect(() => {
    dispatch(fetchFollowups());
  }, [dispatch, interactionCount]);

  const pending = items.filter((f) => (f.status ?? 'pending') === 'pending');
  const today = new Date().toISOString().slice(0, 10);

  return (
    <div className="card">
      <div className="card-head">
        <h2>Upcoming follow-ups</h2>
        <div className="hint">Auto-created by the AI when a follow-up is implied</div>
      </div>
      <div className="list">
        {status === 'loading' && <div className="list-loading">Loading…</div>}
        {status !== 'loading' && pending.length === 0 && (
          <div className="list-empty">No pending follow-ups. 🎉</div>
        )}
        {pending.map((f) => {
          const overdue = f.due_date && f.due_date < today;
          return (
            <div className="list-item" key={f.id}>
              <div className="top">
                <span className="name">{f.hcp?.name ?? `HCP #${f.hcp_id}`}</span>
                {f.due_date && (
                  <span className={`badge ${overdue ? 'neg' : 'neu'}`}>
                    {overdue ? 'overdue ' : 'due '}{f.due_date}
                  </span>
                )}
                <span className="spacer" />
                <button className="btn btn-ghost btn-sm" onClick={() => dispatch(markFollowupDone(f.id))}>
                  ✓ Done
                </button>
              </div>
              <div className="summary">{f.action ?? 'Follow up'}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
