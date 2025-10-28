# utils.py
import pandas as pd
import numpy as np
import io
import os

def safe_read_csv(uploaded_file):
    """Try reading uploaded file into DataFrame, return None if fail."""
    try:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file)
    except Exception:
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="latin1")
        except Exception:
            return None

def robust_parse_dates(series: pd.Series) -> pd.Series:
    """Try multiple tactics to parse a date series and return datetime Series."""
    s = series.copy()
    s = s.fillna("").astype(str).str.strip()
    # Replace common placeholders
    s = s.replace({"^none$": "", "^nan$": "", "N/A": "", "NA": ""}, regex=True)

    # Try default parse
    parsed = pd.to_datetime(s, errors="coerce", infer_datetime_format=True, dayfirst=False)
    if parsed.notna().sum() >= len(s) * 0.6:
        return parsed

    # Try dayfirst
    parsed2 = pd.to_datetime(s, errors="coerce", infer_datetime_format=True, dayfirst=True)
    if parsed2.notna().sum() > parsed.notna().sum():
        parsed = parsed2

    # Try replacing slashes
    s2 = s.str.replace("/", "-", regex=False)
    parsed3 = pd.to_datetime(s2, errors="coerce", infer_datetime_format=True)
    if parsed3.notna().sum() > parsed.notna().sum():
        parsed = parsed3

    # Try numeric epoch (ms/s)
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() > 0:
        maxv = numeric.max(skipna=True)
        if pd.notna(maxv):
            if maxv > 1e12:
                parsed_epoch = pd.to_datetime(numeric, unit="ms", errors="coerce")
                parsed = parsed.fillna(parsed_epoch)
            elif maxv > 1e9:
                parsed_epoch = pd.to_datetime(numeric, unit="s", errors="coerce")
                parsed = parsed.fillna(parsed_epoch)

    return parsed

def compute_sma(df: pd.DataFrame, sma_short=50, sma_long=200) -> pd.DataFrame:
    """Compute SMA short and long per stock and add columns."""
    df = df.copy()
    df = df.sort_values(["Stock", "Date"]).reset_index(drop=True)
    df["SMA_50"] = df.groupby("Stock")["Close"].transform(lambda x: x.rolling(sma_short, min_periods=1).mean())
    df["SMA_200"] = df.groupby("Stock")["Close"].transform(lambda x: x.rolling(sma_long, min_periods=1).mean())
    df["Daily_Return"] = df.groupby("Stock")["Close"].pct_change().fillna(0) * 100
    return df

def compute_insights(stock_df: pd.DataFrame) -> dict:
    """Return quick numeric insights for a single stock dataframe (sorted by Date)."""
    d = stock_df.copy().sort_values("Date").reset_index(drop=True)
    last_close = float(d["Close"].iloc[-1])
    last_return = float(d["Daily_Return"].iloc[-1]) if "Daily_Return" in d.columns else 0.0
    high = float(d["Close"].max())
    low = float(d["Close"].min())
    avg_daily_return = float(d["Daily_Return"].mean())
    last_sma50 = float(d["SMA_50"].iloc[-1]) if "SMA_50" in d.columns else np.nan
    last_sma200 = float(d["SMA_200"].iloc[-1]) if "SMA_200" in d.columns else np.nan
    if last_sma50 > last_sma200:
        signal = "Golden Cross (Bullish)"
    elif last_sma50 < last_sma200:
        signal = "Death Cross (Bearish)"
    else:
        signal = "Neutral"

    return {
        "last_close": last_close,
        "return_1d": last_return,
        "high": high,
        "low": low,
        "avg_daily_return": avg_daily_return,
        "sma_signal": signal,
    }

def prepare_sample_df() -> pd.DataFrame:
    """Return a small sample DataFrame (for testing without uploading)."""
    csv = io.StringIO(
        "Date,Stock,Close,Category\n"
        "2025-10-01,RELIANCE,2580.5,NIFTY50\n"
        "2025-10-02,RELIANCE,2605.2,NIFTY50\n"
        "2025-10-03,RELIANCE,2590.0,NIFTY50\n"
        "2025-10-04,RELIANCE,2610.0,NIFTY50\n"
        "2025-10-05,RELIANCE,2625.5,NIFTY50\n"
        "2025-10-01,TCS,3500.0,NIFTY50\n"
        "2025-10-02,TCS,3490.5,NIFTY50\n"
        "2025-10-03,TCS,3510.0,NIFTY50\n"
        "2025-10-04,TCS,3520.0,NIFTY50\n"
        "2025-10-05,TCS,3535.0,NIFTY50\n"
    )
    return pd.read_csv(csv)

# Optional LLM summary (requires openai)
def generate_llm_summary(stock_df: pd.DataFrame) -> str:
    """
    If OPENAI_API_KEY is set in environment, this will call OpenAI to generate a short summary.
    This is optional: if openai isn't installed or key not set, raises an informative error.
    """
    try:
        import openai
        key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = key

        # create a small text brief
        last_rows = stock_df.tail(30)[["Date", "Close", "SMA_50", "SMA_200"]].to_dict(orient="records")
        prompt = (
            "You are a helpful financial analyst. "
            "Summarize the recent behavior of this stock in 3-4 short sentences. "
            "Focus on trend, SMA crossings, and volatility. "
            f"Data (most recent last): {last_rows}"
        )
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=180
        )
        return resp.choices[0].message.content.strip()
    except ModuleNotFoundError:
        raise RuntimeError("openai package not installed. Add openai to requirements to enable LLM summaries.")
