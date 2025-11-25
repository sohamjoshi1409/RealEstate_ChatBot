import { useState } from "react";

export default function ChatInput({ onSubmit, disabled }: { onSubmit: (text: string) => void; disabled?: boolean }) {
  const [text, setText] = useState("");

  function handleSend() {
    if (!text.trim()) return;
    onSubmit(text.trim());
    setText("");
  }

  return (
    <div className="flex items-center gap-3">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
        placeholder="Ask about real estate data... (e.g., 'Analyze Wakad')"
        className="flex-1 rounded-full border px-4 py-3 focus:outline-none focus:ring-2 focus:ring-sky-300"
        aria-label="Ask a query"
        disabled={disabled}
      />
      <button onClick={handleSend} disabled={disabled} className="inline-flex items-center gap-2 bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-full shadow">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
        <span className="hidden md:inline">Send</span>
      </button>
    </div>
  );
}
