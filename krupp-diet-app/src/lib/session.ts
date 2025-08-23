// diet-web/lib/session.ts
export const getUser = () => (typeof window !== 'undefined' ? localStorage.getItem('username') : null);
export const setUser = (u: string) => localStorage.setItem('username', u);
export const clearUser = () => localStorage.removeItem('username');
