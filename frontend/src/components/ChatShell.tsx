// src/components/ChatShell.tsx
import { useEffect, useRef, useState } from "react";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import { postQuery } from "../api";
import type { SingleResponse, CompareResponse } from "../types";

type ChatMessage = {
  role: "user" | "bot";
  text?: string;                         // for user text or simple bot text
  single?: SingleResponse;               // for single-area results
  compare?: CompareResponse;             // for compare results
  showChart?: boolean;                   // for single results (chart toggle)
};

export default function ChatShell() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // auto-scroll to bottom on message change
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight;
    });
  }, [messages]);

  async function handleSubmit(text: string) {
    if (!text.trim()) return;

    // 1. add user message
    setMessages((prev) => [...prev, { role: "user", text }]);

    // 2. temporary bot "Analyzing..."
    setMessages((prev) => [...prev, { role: "bot", text: "Analyzing..." }]);
    setLoading(true);

    try {
      const payload = { query: text, use_preloaded: true };
      const res = await postQuery(payload);

      // remove placeholder & add real response
      setMessages((prev) => {
        const copy = prev.slice(0, -1); // drop last placeholder

        if (res.type === "compare") {
          const compareRes = res as CompareResponse;
          copy.push({ role: "bot", compare: compareRes });
        } else {
          const singleRes = res as SingleResponse;
          copy.push({ role: "bot", single: singleRes, showChart: false });
        }

        return copy;
      });
    } catch (err) {
      console.error(err);
      setMessages((prev) => {
        const copy = prev.slice(0, -1);
        copy.push({
          role: "bot",
          text: "Sorry — something went wrong while analyzing that query.",
        });
        return copy;
      });
    } finally {
      setLoading(false);
    }
  }

  // toggle chart for a single-response bot message
  function toggleChart(idx: number) {
    setMessages((prev) => {
      const copy = [...prev];
      const msg = copy[idx];
      if (msg && msg.single) {
        copy[idx] = { ...msg, showChart: !msg.showChart };
      }
      return copy;
    });
  }

  return (
    <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
      <div className="p-6 border-b">
        <h2 className="text-lg font-medium">Query Assistant</h2>
        <p className="text-sm text-slate-500">
          Ask questions about real estate data in natural language
        </p>
      </div>

      <div className="h-[560px] flex flex-col overflow-y-scroll">
        <div className="flex-1 p-6">
          <div className="h-full border rounded-lg overflow-hidden flex flex-col">
            {/* messages */}
            <div ref={scrollRef} className="flex-1 chat-scroll p-6">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-center max-w-2xl mx-auto">
                  <div>
                    <div className="mb-6 text-slate-300">
                      <svg width="56" height="56" viewBox="0 0 24 24" fill="none">
                        <rect
                          x="3"
                          y="7"
                          width="18"
                          height="10"
                          rx="2"
                          stroke="#CBD5E1"
                          strokeWidth="1.5"
                        />
                        <rect x="7" y="11" width="2" height="2" rx="0.5" fill="#CBD5E1" />
                        <rect x="11" y="11" width="2" height="2" rx="0.5" fill="#CBD5E1" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-slate-800 mb-2">
                      Welcome to Real Estate Analytics
                    </h3>
                    <p className="text-slate-500">
                      Ask me anything about real estate data. Try queries like{" "}
                      <span className="font-medium">"Analyze Wakad"</span> or{" "}
                      <span className="font-medium">
                        "Compare Ambegaon Budruk and Aundh demand trends".
                      </span>
                    </p>
                  </div>
                </div>
              ) : (
                <MessageList messages={messages} onToggleChart={toggleChart} />
              )}
            </div>

            {/* input */}
            <div className="p-4 border-t">
              <ChatInput onSubmit={handleSubmit} disabled={loading} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
