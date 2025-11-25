// src/components/SummaryCard.tsx
export default function SummaryCard({
  summary,
  area,
  onShowChart,
  showChart,
}: {
  summary: string;
  area?: string;
  onShowChart?: () => void;
  showChart?: boolean;
}) {
  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      <div className="flex items-start gap-4">
        <div className="flex-1">
          <div className="text-sm text-slate-500">Summary • {area ?? "Area"}</div>
          <div className="mt-2 text-slate-800" style={{ whiteSpace: "pre-wrap" }}>{summary}</div>
        </div>
        <div className="flex-shrink-0">
          {onShowChart && (
            <button
              onClick={onShowChart}
              className="text-sm text-indigo-600 hover:underline"
              aria-pressed={!!showChart}
            >
              {showChart ? "Hide chart" : "Show chart"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
