// src/components/ChatShell.tsx
import { useState, useRef, useEffect } from "react";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import { postQuery } from "../api";
import type { SingleResponse } from "../types";

type Msg = {
  role: "user" | "bot";
  text?: string;
  data?: SingleResponse | null;
  showChart?: boolean;
};

export default function ChatShell() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // scroll to bottom when messages change
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    // small delay to allow DOM to update
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
  }, [messages]);

  async function handleSubmit(text: string) {
    // push user message
    setMessages((m) => [...m, { role: "user", text }]);

    // insert temporary bot placeholder
    setMessages((m) => [...m, { role: "bot", text: "Analyzing...", showChart: false }]);
    setLoading(true);

    try {
      const payload = { query: text, use_preloaded: true };
      const res = await postQuery(payload);

      // replace last placeholder with actual response object
      setMessages((prev) => {
        const copy = prev.slice(0, -1); // remove placeholder
        copy.push({ role: "bot", data: res as SingleResponse, showChart: false });
        return copy;
      });
    } catch (err) {
      setMessages((prev) => {
        const copy = prev.slice(0, -1);
        copy.push({ role: "bot", text: "Sorry — an error occurred. Try again." });
        return copy;
      });
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // toggle chart visibility for message index i
  function toggleChart(idx: number) {
    setMessages((prev) => {
      const copy = [...prev];
      const msg = { ...copy[idx] };
      msg.showChart = !msg.showChart;
      copy[idx] = msg;
      return copy;
    });
  }

  return (
    <div className="bg-white rounded-2xl border shadow-sm">
      <div className="p-6 border-b">
        <h2 className="text-lg font-medium">Query Assistant</h2>
        <p className="text-sm text-slate-500">Ask questions about real estate data in natural language</p>
      </div>

      <div className="h-[560px] flex flex-col overflow-y-scroll">
        <div className="flex-1 p-6">
          <div className="h-full border rounded-lg overflow-hidden flex flex-col">
            {/* message area */}
            <div ref={scrollRef} className="flex-1 chat-scroll p-6">
              <div className="chat-inner">
                {messages.length === 0 ? (
                  <div className="text-center max-w-2xl mx-auto">
                    <div className="mb-6 text-slate-300">
                      {/* simple robot icon */}
                      <svg width="56" height="56" viewBox="0 0 24 24" fill="none">
                        <rect x="3" y="7" width="18" height="10" rx="2" stroke="#CBD5E1" strokeWidth="1.5" />
                        <rect x="7" y="11" width="2" height="2" rx="0.5" fill="#CBD5E1" />
                        <rect x="11" y="11" width="2" height="2" rx="0.5" fill="#CBD5E1" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-slate-800 mb-2">Welcome to Real Estate Analytics</h3>
                    <p className="text-slate-500">Ask me anything about real estate data. Try queries like "Analyze Wakad" or "Compare Ambegaon Budruk and Aundh".</p>
                  </div>
                ) : (
                  <MessageList messages={messages} onToggleChart={toggleChart} />
                )}
              </div>
            </div>

            <div className="p-4 border-t">
              <ChatInput onSubmit={handleSubmit} disabled={loading} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
