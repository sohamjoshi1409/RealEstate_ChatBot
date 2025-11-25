// src/components/ChartCard.tsx
import { Line } from "react-chartjs-2";
import type { ChartSeries } from "../types";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function ChartCard({ data }: { data: ChartSeries }) {
  const chartData = {
    labels: data?.labels ?? [],
    datasets: [
      {
        label: "Price",
        data: data?.price ?? [],
        borderColor: "#6366F1",
        backgroundColor: "rgba(99,102,241,0.08)",
        tension: 0.2,
        yAxisID: "y",
      },
      {
        label: "Demand",
        data: data?.demand ?? [],
        borderColor: "#06B6D4",
        backgroundColor: "rgba(6,182,212,0.06)",
        tension: 0.2,
        yAxisID: "y1",
      },
    ],
  };

  const options = {
    maintainAspectRatio: false,
    responsive: true,
    interaction: { mode: "index" as const, intersect: false },
    scales: {
      y: { type: "linear" as const, position: "left" as const, ticks: { beginAtZero: true } },
      y1: { type: "linear" as const, position: "right" as const, grid: { drawOnChartArea: false }, ticks: { beginAtZero: true } },
    },
  };

  return (
    <div className="bg-white border rounded-lg p-3" style={{ height: 280 }}>
      <Line data={chartData as any} options={options as any} />
    </div>
  );
}
