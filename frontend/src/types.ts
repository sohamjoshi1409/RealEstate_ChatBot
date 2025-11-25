export type ChartSeries = {
  labels: string[];
  price: (number | null)[];
  demand: (number | null)[];
};

export type TableRow = { [k: string]: any };

export type SingleResponse = {
  type: "single";
  area: string;
  summary: string;
  chart: ChartSeries;
  table: TableRow[];
};

export type CompareResponse = {
  type: "compare";
  results: Record<string, SingleResponse>;
};
