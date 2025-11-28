# analysis/utils.py
import os
import re
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from dateutil import parser

# project base dir (two levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_EXCEL_PATH = os.path.join(BASE_DIR, "datasets", "realestate_data.xlsx")

# --------------------
# Column normalization
# --------------------
def _normalize_colname(c: str) -> str:
    """Normalize a column name into a safe lower-case single-token string."""
    if c is None:
        return ""
    s = str(c).strip().lower()
    s = re.sub(r'[\r\n]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    # replace spaces and hyphens with single underscore; remove trailing dots
    s = s.replace('-', ' ').replace('/', ' ')
    s = re.sub(r'[^0-9a-z_ ]', '', s)
    s = s.replace(' ', '_')
    return s

def load_dataset(path: str = None) -> pd.DataFrame:
    """
    Load the dataset (xlsx or csv), normalize column names and map known columns
    from your provided schema to canonical names used by the rest of the code.
    """
    path = path or SAMPLE_EXCEL_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")

    # load
    if str(path).lower().endswith(".csv"):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path, engine="openpyxl")

    # original columns -> normalized column names
    norm_map = {col: _normalize_colname(col) for col in df.columns}
    df = df.rename(columns=norm_map)

    # Map your known columns to canonical names
    # The user's list included "final location", so handle it explicitly.
    # We look for normalized variants and map to 'area'
    area_candidates = [
        "final_location", "final_location", "final_location",  # explicit redundancy is harmless
        "area", "locality", "location", "area_name", "place",
        "neighbourhood", "neighborhood", "locality_name"
    ]
    found_area = None
    for cand in area_candidates:
        if cand in df.columns:
            found_area = cand
            break
    if found_area and found_area != "area":
        df = df.rename(columns={found_area: "area"})
    if "area" not in df.columns:
        # create empty area col to avoid crashes
        df["area"] = pd.NA

    # Ensure year column exists and normalized name is 'year' (it already is in your list)
    if "year" not in df.columns:
        # try variants
        for cand in ("yr", "year_covered", "reporting_year"):
            if cand in df.columns:
                df = df.rename(columns={cand: "year"})
                break
    # Create helper normalized area column used for substring matching
    df["_area_norm"] = df["area"].astype(str).apply(lambda s: re.sub(r"\s+", " ", s.strip().lower()))

    # Keep numeric conversions for the key numeric columns that may exist
    # price-like columns: any column with 'weighted_average_rate' or 'most_prevailing_rate'
    # demand-like columns: prefer total_sold_igr, total_sales_igr, then total_units
    # (we will detect these later dynamically)

    return df

# --------------------
# Helpers
# --------------------
def normalize_area_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())

def filter_by_area(df: pd.DataFrame, areas: List[str]) -> pd.DataFrame:
    """Return rows where normalized 'area' contains any substring in areas."""
    if df is None or df.empty:
        return df.iloc[0:0]
    if "_area_norm" not in df.columns:
        df["_area_norm"] = df["area"].astype(str).apply(lambda s: re.sub(r"\s+", " ", s.strip().lower()))
    mask = pd.Series(False, index=df.index)
    for area in areas:
        a = normalize_area_text(area)
        # Use regex escape to avoid special char issues
        mask = mask | df["_area_norm"].str.contains(re.escape(a), na=False)
    return df[mask].copy()

def ensure_year_col(df: pd.DataFrame) -> pd.DataFrame:
    if "year" in df.columns:
        try:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        except Exception:
            def try_year(x):
                try:
                    return parser.parse(str(x)).year
                except Exception:
                    return pd.NA
            df["year"] = df["year"].apply(try_year).astype("Int64")
    else:
        df["year"] = pd.NA
    return df

# --------------------
# Column detectors
# --------------------
def detect_price_column(df: pd.DataFrame) -> List[str]:
    """
    Return a list of columns to use for price. Prefer:
      1) flat_weighted_average_rate (i.e. 'flat - weighted average rate')
      2) any '*_weighted_average_rate' columns
      3) any 'most_prevailing_rate' columns
    Returns list (possibly multiple) so we can compute an average if needed.
    """
    candidates = []
    for c in df.columns:
        if "weighted_average_rate" in c:
            candidates.append(c)
    # prefer flat first if present
    flat_candidates = [c for c in candidates if c.startswith("flat")]
    if flat_candidates:
        return flat_candidates  # prefer flat weighted average
    if candidates:
        return candidates
    # fallback: any column containing 'rate'
    rate_cols = [c for c in df.columns if "rate" in c or "price" in c]
    return rate_cols

def detect_demand_column(df: pd.DataFrame) -> str:
    """
    Pick the best demand/volume column from likely names:
      - total_sold_igr (normalized from 'total sold - igr')
      - total_sales_igr (normalized from 'total_sales - igr')
      - total_units
      - total_carpet_area_supplied_sqft
    """
    prefs = [
        "total_sold_igr",
        "total_sales_igr",
        "total_units",
        "total_carpet_area_supplied_sqft",
        "total_units",  # redundant but harmless
    ]
    for p in prefs:
        if p in df.columns:
            return p
    # fallback: find any column with 'sold' or 'sales' or 'total' in the name
    for c in df.columns:
        if any(k in c for k in ("sold", "sales", "total", "units")):
            return c
    return None

# --------------------
# Chart and summary
# --------------------
def chart_data_for_area(df: pd.DataFrame, area: str, last_n_years: int = None) -> Dict[str, Any]:
    """Return chart JSON with labels, price series and demand series for an area."""
    df = ensure_year_col(df)
    # detect the columns to use
    price_cols = detect_price_column(df)
    demand_col = detect_demand_column(df)

    df_area = filter_by_area(df, [area])
    # use only rows with year
    df_area = df_area[df_area["year"].notna()]
    if df_area.empty:
        return {"labels": [], "price": [], "demand": []}

    # If we have multiple price columns, compute mean across them per group
    def price_agg(group):
        if not price_cols:
            return np.nan
        vals = []
        for pc in price_cols:
            if pc in group.columns:
                v = pd.to_numeric(group[pc], errors="coerce")
                vals.append(v)
        if not vals:
            return np.nan
        stacked = pd.concat(vals, axis=1)
        # mean across available columns (row-wise), then mean of that per year
        return stacked.mean(axis=1).mean()

    # Build grouped dataframe
    agg_map = {}
    if demand_col and demand_col in df_area.columns:
        agg_map[demand_col] = "mean"
    grouped = df_area.groupby("year").agg(agg_map).reset_index()
    grouped = grouped.sort_values("year")

    # compute price series per year using price_agg
    price_series = []
    for _, row in grouped.iterrows():
        year = row["year"]
        rows_for_year = df_area[df_area["year"] == year]
        price_year = price_agg(rows_for_year)
        price_series.append(round(float(price_year), 2) if not pd.isna(price_year) else None)

    # demand series
    demand_series = []
    if demand_col and demand_col in grouped.columns:
        # safe conversion: turn NaN -> None (replace np.nan with None) before listing
        demand_series = (
            grouped[demand_col]
            .astype(float)
            .round(2)
            .where(lambda s: ~s.isna(), other=None)   # keep None for missing values
            .tolist()
        )
    else:
        # if we couldn't aggregate demand via map, try computing from df_area directly per year
        for _, row in grouped.iterrows():
            year = row["year"]
            rows_for_year = df_area[df_area["year"] == year]
            # try total_units
            if "total_units" in rows_for_year.columns:
                val = pd.to_numeric(rows_for_year["total_units"], errors="coerce").mean()
            else:
                # fallback: try sum/mean of any column containing 'sold' or 'sales'
                sold_cols = [c for c in rows_for_year.columns if "sold" in c or "sales" in c]
                if sold_cols:
                    vals = []
                    for sc in sold_cols:
                        tmp = pd.to_numeric(rows_for_year[sc], errors="coerce")
                        if not tmp.dropna().empty:
                            vals.append(tmp.mean(skipna=True))
                    val = np.nan if not vals else (sum(vals) / len(vals))
                else:
                    val = np.nan
            demand_series.append(round(float(val), 2) if not pd.isna(val) else None)

    # trim to last_n_years if requested
    labels = grouped["year"].astype(str).tolist()
    if last_n_years and labels:
        last_year = int(labels[-1])
        cutoff = last_year - (last_n_years - 1)
        filtered_idx = [i for i, y in enumerate(labels) if int(y) >= cutoff]
        labels = [labels[i] for i in filtered_idx]
        price_series = [price_series[i] for i in filtered_idx]
        demand_series = [demand_series[i] for i in filtered_idx]

    return {"labels": labels, "price": price_series, "demand": demand_series}

def parse_query_text(q: str) -> Dict[str, Any]:
    """
    Lightweight parser for sample queries.

    Supports for example:
    - "Compare Ambegaon Budruk and Aundh demand trends"
    - "Compare Aundh with Wakad"
    - "Compare Aundh vs Wakad"
    - "Show price growth for Akurdi over the last 3 years"
    - "Analyze Wakad"
    """
    qlow = (q or "").lower()
    # normalize whitespace a bit so regexes are easier
    qlow = re.sub(r"\s+", " ", qlow).strip()

    # 1) COMPARE intent
    # allow: and / with / vs / versus
    # allow extra trailing words like "demand trends", "price", "growth", etc.
    cmp_match = re.search(
        r"compare\s+([a-z0-9\s]+?)\s+"
        r"(?:and|with|vs\.?|versus)\s+"
        r"([a-z0-9\s]+?)"
        r"(?:\s+(?:demand|price|growth|trend|trends).*)?$",
        qlow,
    )
    if cmp_match:
        a1 = cmp_match.group(1).strip()
        a2 = cmp_match.group(2).strip()
        return {"intent": "compare", "areas": [a1, a2]}

    # 2) GROWTH intent: "price growth for X over the last N year(s)"
    growth_match = re.search(
        r"price growth for\s+([a-z0-9\s]+)\s+"
        r"(?:over the last|in the last)\s+"
        r"(\d+)\s+years?",
        qlow,
    )
    if growth_match:
        area = growth_match.group(1).strip()
        n = int(growth_match.group(2))
        return {"intent": "growth", "areas": [area], "last_n_years": n}

    # 3) ANALYZE intent: "analyze X", "analysis of X"
    analyze_match = re.search(r"analyz(?:e|is)\s+([a-z0-9\s]+)", qlow) or re.search(
        r"analysis of\s+([a-z0-9\s]+)", qlow
    )
    if analyze_match:
        area = analyze_match.group(1).strip()
        return {"intent": "analyze", "areas": [area]}

    # 4) Fallback: assume analyze + last word as area
    words = re.findall(r"[a-z0-9]+", qlow)
    if words:
        return {"intent": "analyze", "areas": [" ".join(words[-1:])]}

    return {"intent": "analyze", "areas": []}

def build_mock_summary(df_area: pd.DataFrame, area: str) -> str:
    """
    Build a more detailed, purely rule-based summary for an area.

    It uses:
    - detected price columns (weighted average rate etc.)
    - detected demand column (total_sold_igr / total_units / similar)
    - per-year aggregates to talk about trends
    """
    if df_area is None or df_area.empty:
        return f"No data found for '{area}'."

    # normalise year column
    df_area = ensure_year_col(df_area)

    # detect columns
    price_cols = detect_price_column(df_area)
    demand_col = detect_demand_column(df_area)

    # use only rows with a year
    df_year = df_area.dropna(subset=["year"]).copy()
    if df_year.empty:
        return f"Data is available for '{area}', but year information is missing, so trends cannot be computed."

    # ---------------------------
    # per-year price aggregation
    # ---------------------------
    year_price: Dict[int, float] = {}
    for year, grp in df_year.groupby("year"):
        vals = []
        for pc in price_cols or []:
            if pc in grp.columns:
                vals.append(pd.to_numeric(grp[pc], errors="coerce"))
        if not vals:
            continue
        stacked = pd.concat(vals, axis=1)
        # mean across columns, then mean for that year
        year_price[int(year)] = float(stacked.mean(axis=1).mean())

    # overall price stats
    price_avg = None
    price_min = None
    price_max = None
    first_price = None
    last_price = None

    if year_price:
        years_sorted = sorted(year_price.keys())
        prices_sorted = [year_price[y] for y in years_sorted]

        price_avg = float(np.nanmean(prices_sorted))
        price_min = float(np.nanmin(prices_sorted))
        price_max = float(np.nanmax(prices_sorted))
        first_price = prices_sorted[0]
        last_price = prices_sorted[-1]

    # ---------------------------
    # per-year demand aggregation
    # ---------------------------
    year_demand: Dict[int, float] = {}
    if demand_col and demand_col in df_year.columns:
        for year, grp in df_year.groupby("year"):
            v = pd.to_numeric(grp[demand_col], errors="coerce")
            if not v.dropna().empty:
                year_demand[int(year)] = float(v.mean())
    elif "total_units" in df_year.columns:
        for year, grp in df_year.groupby("year"):
            v = pd.to_numeric(grp["total_units"], errors="coerce")
            if not v.dropna().empty:
                year_demand[int(year)] = float(v.mean())

    demand_avg = None
    demand_min = None
    demand_max = None
    demand_min_year = None
    demand_max_year = None

    if year_demand:
        years_d = sorted(year_demand.keys())
        vals_d = [year_demand[y] for y in years_d]
        demand_avg = float(np.nanmean(vals_d))
        demand_min = float(np.nanmin(vals_d))
        demand_max = float(np.nanmax(vals_d))
        # year of min / max demand
        demand_min_year = years_d[int(np.nanargmin(vals_d))]
        demand_max_year = years_d[int(np.nanargmax(vals_d))]

    # ---------------------------
    # basic metadata
    # ---------------------------
    try:
        min_year = int(df_year["year"].min())
        max_year = int(df_year["year"].max())
    except Exception:
        min_year = max_year = None

    parts: List[str] = []
    parts.append(f"Summary for {area.title()}:")

    if min_year and max_year:
        n_years = max_year - min_year + 1
        parts.append(f"Data is available from {min_year} to {max_year} (about {n_years} year(s) of history).")

    # price stats sentences
    if price_avg is not None and not np.isnan(price_avg):
        p_avg = round(price_avg, 2)
        if price_min is not None and price_max is not None:
            p_min = round(price_min, 2)
            p_max = round(price_max, 2)
            parts.append(
                f"The typical (average) price across the period is around {p_avg}. "
                f"Observed yearly prices generally range between {p_min} and {p_max}."
            )
        else:
            parts.append(f"The typical (average) price across the period is around {p_avg}.")

    # trend sentence based on first vs last year
    if first_price is not None and last_price is not None and first_price > 0:
        pct_change = (last_price - first_price) / first_price * 100.0
        direction: str
        if pct_change > 8:
            direction = "has grown strongly"
        elif pct_change > 2:
            direction = "has grown moderately"
        elif pct_change > -2:
            direction = "has been broadly stable"
        elif pct_change > -8:
            direction = "has softened slightly"
        else:
            direction = "has declined noticeably"
        parts.append(
            f"From the first year in the dataset to the most recent year, the price {direction}, "
            f"changing by roughly {round(pct_change, 1)}% overall."
        )

    # demand stats sentences
    if demand_avg is not None and not np.isnan(demand_avg):
        d_avg = round(demand_avg, 1)
        base_name = demand_col or "total_units"
        label = base_name.replace("_", " ")
        parts.append(
            f"The average demand (based on '{label}') is about {d_avg} units per year."
        )

        if demand_min is not None and demand_max is not None:
            d_min = round(demand_min, 1)
            d_max = round(demand_max, 1)
            if demand_max_year is not None and demand_min_year is not None:
                parts.append(
                    f"Demand peaked around {demand_max_year} at roughly {d_max} units, "
                    f"while the weakest year was {demand_min_year} with about {d_min} units."
                )
            else:
                parts.append(
                    f"Across the period, yearly demand tends to stay between about {d_min} and {d_max} units."
                )

    # final note
    parts.append(
        "This summary is rule-based and uses simple averages and year-over-year changes. "
    )

    return " ".join(parts)
# --------------------
# Utility: list areas
# --------------------
def list_distinct_areas(path: str = None, n: int = 200) -> List[str]:
    """Load dataset and return a sample of distinct 'area' values (useful for debugging)."""
    df = load_dataset(path)
    vals = df["_area_norm"].dropna().unique().tolist()
    return vals[:n]
