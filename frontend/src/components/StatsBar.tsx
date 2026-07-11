import { useAppSelector } from '../store';

export function StatsBar() {
  const interactions = useAppSelector((s) => s.interactions.items);
  const followups = useAppSelector((s) => s.followups.items);

  const total = interactions.length;
  const positive = interactions.filter((i) => i.sentiment === 'positive').length;
  const negative = interactions.filter((i) => i.sentiment === 'negative').length;
  const hcps = new Set(interactions.map((i) => i.hcp?.name ?? i.hcp_id)).size;
  const pending = followups.filter((f) => (f.status ?? 'pending') === 'pending').length;

  const tiles = [
    { label: 'Interactions', value: total, color: 'var(--ink)' },
    { label: 'HCPs engaged', value: hcps, color: 'var(--ink)' },
    { label: 'Positive', value: positive, color: 'var(--pos)' },
    { label: 'Negative', value: negative, color: 'var(--neg)' },
    { label: 'Follow-ups due', value: pending, color: 'var(--neu)' },
  ];

  return (
    <div className="stats">
      {tiles.map((t) => (
        <div className="stat" key={t.label}>
          <div className="stat-value" style={{ color: t.color }}>{t.value}</div>
          <div className="stat-label">{t.label}</div>
        </div>
      ))}
    </div>
  );
}
