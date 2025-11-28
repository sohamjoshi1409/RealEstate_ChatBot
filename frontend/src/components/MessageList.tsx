// src/components/MessageList.tsx
import SummaryCard from "./SummaryCard";
import ChartCard from "./ChartCard";
import CompareCard from "./CompareCard.tsx";
import type { SingleResponse, CompareResponse } from "../types";

export type ChatMessage = {
  role: "user" | "bot";
  text?: string;
  single?: SingleResponse;
  compare?: CompareResponse;
  showChart?: boolean;
};

export default function MessageList({
  messages,
  onToggleChart,
}: {
  messages: ChatMessage[];
  onToggleChart: (idx: number) => void;
}) {
  return (
    <div className="space-y-6">
      {messages.map((m, i) => {
        if (m.role === "user") {
          return (
            <div key={i} className="flex justify-end">
              <div className="bg-indigo-50 text-indigo-700 p-4 rounded-xl max-w-[70%] whitespace-pre-wrap">
                {m.text}
              </div>
            </div>
          );
        }

        // BOT messages
        if (m.compare) {
          // compare payload: render CompareCard
          return (
            <div key={i} className="flex justify-start">
              <div className="w-full max-w-[90%]">
                <CompareCard data={m.compare} />
              </div>
            </div>
          );
        }

        if (m.single) {
          // single payload: summary + optional chart toggle
          return (
            <div key={i} className="flex justify-start">
              <div className="max-w-[80%] w-full space-y-4">
                <SummaryCard
                  summary={m.single.summary}
                  area={m.single.area}
                  onShowChart={() => onToggleChart(i)}
                  showChart={!!m.showChart}
                />
                {m.showChart && (
                  <ChartCard data={m.single.chart} />
                )}
              </div>
            </div>
          );
        }

        // generic bot text fallback
        return (
          <div key={i} className="flex justify-start">
            <div className="bg-slate-50 text-slate-800 p-4 rounded-xl max-w-[70%] whitespace-pre-wrap">
              {m.text}
            </div>
          </div>
        );
      })}
    </div>
  );
}
