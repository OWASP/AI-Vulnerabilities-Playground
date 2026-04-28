/**
 * URL pathname <-> app view sync. Enables back/forward and shareable links.
 * Paths: / (home), /about, /explore, /knowme, /contact, /labs/:labId (e.g. /labs/MM_01)
 */
export function pathToView(pathname: string): string {
  const path = (pathname || '/').replace(/\/+$/, '') || '/';
  if (path === '/') return 'home';
  if (path === '/about') return 'about';
  if (path === '/explore') return 'explore';
  if (path === '/knowme') return 'knowme';
  if (path === '/contact') return 'contact';
  const m = path.match(/^\/labs\/([A-Za-z0-9_]+)$/);
  if (m) return 'lab_' + m[1];
  return 'home';
}

export function viewToPath(view: string): string {
  if (view === 'home') return '/';
  if (view === 'about') return '/about';
  if (view === 'explore') return '/explore';
  if (view === 'knowme') return '/knowme';
  if (view === 'contact') return '/contact';
  if (view.startsWith('lab_')) return '/labs/' + view.slice(4);
  return '/';
}
