export default function Header() {
  return (
    <header className="bg-white border-b">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-4">
        <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-indigo-500 to-sky-500 flex items-center justify-center text-white">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="3" y="6" width="4" height="12" rx="1" fill="currentColor"/><rect x="9" y="3" width="4" height="15" rx="1" fill="currentColor"/><rect x="15" y="9" width="4" height="9" rx="1" fill="currentColor"/></svg>
        </div>
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Real Estate Analytics</h1>
          <p className="text-sm text-slate-500">AI-Powered Property Intelligence</p>
        </div>
        <div className="ml-auto" />
      </div>
    </header>
  );
}
