export function SentimentBadge({ sentiment }: { sentiment?: string | null }) {
  if (!sentiment) return null;
  const s = sentiment.toLowerCase();
  const cls = s === 'positive' ? 'pos' : s === 'negative' ? 'neg' : 'neu';
  return <span className={`badge ${cls}`}>{sentiment}</span>;
}
