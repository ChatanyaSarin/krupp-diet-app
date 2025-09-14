export function pretty(s?: string | null) {
  return (s ?? '').replace(/_/g, ' ');
}
