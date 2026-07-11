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
    { label: 'Interactions', value: total, accent: 'var(--primary)' },
    { label: 'HCPs engaged', value: hcps, accent: 'var(--primary)' },
    { label: 'Positive', value: positive, accent: 'var(--pos)' },
    { label: 'Negative', value: negative, accent: 'var(--neg)' },
    { label: 'Follow-ups due', value: pending, accent: 'var(--neu)' },
  ];

  return (
    <div className="stats">
      {tiles.map((t) => (
        <div className="stat" key={t.label}>
          <div className="stat-value" style={{ color: t.accent }}>{t.value}</div>
          <div className="stat-label">{t.label}</div>
        </div>
      ))}
    </div>
  );
}
