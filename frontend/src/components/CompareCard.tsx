// src/components/CompareCard.tsx
import { useState } from "react";
import type { CompareResponse, SingleResponse } from "../types";
import SummaryCard from "./SummaryCard";
import ChartCard from "./ChartCard";

interface CompareCardProps {
  data: CompareResponse;
}

type AreaToggleState = Record<string, boolean>;

export default function CompareCard({ data }: CompareCardProps) {
  const areas: SingleResponse[] = Object.values(data.results || {});
  const [showForArea, setShowForArea] = useState<AreaToggleState>({});

  function toggle(areaKey: string) {
    setShowForArea((prev) => ({ ...prev, [areaKey]: !prev[areaKey] }));
  }

  if (!areas.length) {
    return (
      <div className="bg-slate-50 border rounded-lg p-4 text-sm text-slate-500">
        No comparable areas found for this query.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-slate-600">
        Comparison result ({areas.length} area{areas.length > 1 ? "s" : ""})
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {areas.map((s, idx) => {
          const key = s.area || `area-${idx}`;
          const showChart = !!showForArea[key];

          return (
            <div key={key} className="space-y-3">
              <SummaryCard
                summary={s.summary}
                area={s.area}
                onShowChart={() => toggle(key)}
                showChart={showChart}
              />
              {showChart && <ChartCard data={s.chart} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
