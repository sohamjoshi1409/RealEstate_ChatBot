// src/components/MessageList.tsx
import SummaryCard from "./SummaryCard";
import ChartCard from "./ChartCard";
import type { SingleResponse } from "../types";

export default function MessageList({
  messages,
  onToggleChart,
}: {
  messages: { role: "user" | "bot"; text?: string; data?: SingleResponse | null; showChart?: boolean }[];
  onToggleChart: (idx: number) => void;
}) {
  return (
    <div className="w-full space-y-6 chat-contents">
      {messages.map((m, i) => (
        <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
          {m.role === "user" ? (
            <div className="bg-indigo-50 text-indigo-700 p-4 rounded-xl max-w-[70%] whitespace-pre-wrap">{m.text}</div>
          ) : m.data ? (
            <div className="max-w-[80%]">
              <SummaryCard
                summary={m.data.summary}
                area={m.data.area}
                onShowChart={() => onToggleChart(i)}
                showChart={!!m.showChart}
              />
              {m.showChart && m.data.chart && (
                <div className="mt-4">
                  <ChartCard data={m.data.chart} />
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-50 text-slate-800 p-4 rounded-xl max-w-[70%] whitespace-pre-wrap">{m.text}</div>
          )}
        </div>
      ))}
    </div>
  );
}
