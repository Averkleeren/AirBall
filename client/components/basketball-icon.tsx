export function BasketballIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20" />
      <path d="M12 2v20" />
      <path d="M5.15 5.15c2.85 2.15 4.85 5.35 4.85 6.85s-2 4.7-4.85 6.85" />
      <path d="M18.85 5.15c-2.85 2.15-4.85 5.35-4.85 6.85s2 4.7 4.85 6.85" />
    </svg>
  )
}
