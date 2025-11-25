import Header from "./components/Header.tsx";
import ChatShell from "./components/ChatShell.tsx";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 p-6 md:p-10">
        <div className="max-w-6xl mx-auto">
          <ChatShell />
        </div>
      </main>
      <footer className="text-center py-6 text-sm text-slate-500">
        Real Estate Analytics Platform © 2025
      </footer>
    </div>
  );
}
