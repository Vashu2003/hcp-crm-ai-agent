// Minimal 16px line icons (stroke = currentColor) — replaces emoji for a cleaner look.
type P = { size?: number; className?: string };
const base = (size = 16) => ({
  width: size, height: size, viewBox: '0 0 24 24', fill: 'none',
  stroke: 'currentColor', strokeWidth: 1.75, strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
});

export const IconForm = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <rect x="4" y="3" width="16" height="18" rx="2" /><path d="M8 8h8M8 12h8M8 16h5" />
  </svg>
);
export const IconChat = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M4 5h16v11H9l-4 3v-3H4z" />
  </svg>
);
export const IconSearch = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />
  </svg>
);
export const IconCheck = ({ size, className }: P) => (
  <svg {...base(size)} className={className}><path d="M20 6L9 17l-5-5" /></svg>
);
export const IconCalendar = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 9h18M8 3v4M16 3v4" />
  </svg>
);
export const IconPulse = ({ size, className }: P) => (
  <svg {...base(size)} className={className}><path d="M3 12h4l2-6 4 12 2-6h6" /></svg>
);
export const IconSpark = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M12 3v6M12 15v6M3 12h6M15 12h6" /><path d="M6.5 6.5l3 3M14.5 14.5l3 3M17.5 6.5l-3 3M9.5 14.5l-3 3" />
  </svg>
);
export const IconTool = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M14 7a3.5 3.5 0 0 0-4.9 4.2l-5 5a1.5 1.5 0 0 0 2.1 2.1l5-5A3.5 3.5 0 0 0 17 10l-2 2-2-2z" />
  </svg>
);
export const IconSun = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
  </svg>
);
export const IconMoon = ({ size, className }: P) => (
  <svg {...base(size)} className={className}>
    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
  </svg>
);
