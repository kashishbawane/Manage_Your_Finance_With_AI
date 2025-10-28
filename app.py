# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import (
    safe_read_csv,
    robust_parse_dates,
    compute_sma,
    compute_insights,
    prepare_sample_df,
    generate_llm_summary,
)

st.set_page_config(page_title="Nifty Stock Analysis Dashboard", layout="wide")
st.title("📊 Nifty Stock Analysis Dashboard — SMA50 & SMA200 + Quick Insights")

st.markdown(
    "Upload your CSV or use the sample dataset. Columns expected: `Date`, `Stock`, `Close`, (optional) `Category`."
)

uploaded_file = st.file_uploader("Upload CSV (Date, Stock, Close, Category...)", type=["csv"])
use_sample = st.button("Use sample dataset")

# Load dataframe
if uploaded_file is None and not use_sample:
    st.info("Upload a CSV or click 'Use sample dataset' to get started.")
    st.stop()

if use_sample:
    df = prepare_sample_df()
else:
    df = safe_read_csv(uploaded_file)
    if df is None:
        st.error("Failed to read uploaded CSV. Make sure it's a valid CSV file.")
        st.stop()

st.subheader("Raw data (first 10 rows)")
st.dataframe(df.head(10))

# --- Date parsing ---
date_col = st.selectbox("Select date column", options=[c for c in df.columns if "date" in c.lower()] + ["<other>"])
if date_col == "<other>":
    date_col = st.selectbox("Pick date-like column", df.columns.tolist())

df[date_col + "_parsed"] = robust_parse_dates(df[date_col])
parsed_count = df[date_col + "_parsed"].notna().sum()
st.write(f"Parsed {parsed_count} / {len(df)} rows as dates from column `{date_col}`.")
if parsed_count == 0:
    st.error("No parseable dates. Check your date column formatting.")
    st.stop()

df["Date"] = df[date_col + "_parsed"]
df = df.drop(columns=[date_col + "_parsed"])
df = df.dropna(subset=["Date"]).sort_values(["Stock", "Date"]).reset_index(drop=True)

# --- Basic checks & cleaning ---
if "Stock" not in df.columns:
    st.error("Column 'Stock' not found. Please include 'Stock' column.")
    st.stop()

if "Close" not in df.columns:
    st.error("Column 'Close' not found. Please include 'Close' column.")
    st.stop()

df["Stock"] = df["Stock"].astype(str).str.strip().str.replace(" ", "", regex=False)
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
df = df.dropna(subset=["Close"])

# --- Compute SMA & returns ---
df = compute_sma(df, sma_short=50, sma_long=200)

# --- Filters ---
if "Category" in df.columns:
    categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())
    category = st.selectbox("Category", categories)
    if category != "All":
        dff = df[df["Category"] == category]
    else:
        dff = df.copy()
else:
    dff = df.copy()

stocks = sorted(dff["Stock"].unique().tolist())
stock_choice = st.selectbox("Select Stock", stocks)

stock_df = dff[dff["Stock"] == stock_choice].sort_values("Date").reset_index(drop=True)
if stock_df.empty:
    st.error("No data for the selected stock after filtering.")
    st.stop()

# Quick insights
insights = compute_insights(stock_df)
st.subheader("📌 Quick Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Last Close", f"₹{insights['last_close']:.2f}", delta=f"{insights['return_1d']:.2f}%")
col2.metric("Period High", f"₹{insights['high']:.2f'}")
col3.metric("Period Low", f"₹{insights['low']:.2f'}")
st.markdown(f"**SMA signal:** {insights['sma_signal']}")
st.write(f"Average daily return (period): {insights['avg_daily_return']:.3f}")

# Plot
st.subheader(f"📈 {stock_choice} Chart (Close + SMA50 + SMA200)")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(stock_df["Date"], stock_df["Close"], label="Close", marker="o", markersize=3)
ax.plot(stock_df["Date"], stock_df["SMA_50"], label="SMA 50", linestyle="--")
ax.plot(stock_df["Date"], stock_df["SMA_200"], label="SMA 200", linestyle="--")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.legend()
plt.xticks(rotation=45)
st.pyplot(fig)

# LLM summary (optional)
st.subheader("🧠 AI Summary (optional)")
use_llm = st.checkbox("Generate short natural-language summary using OpenAI (requires OPENAI_API_KEY env var)", value=False)
if use_llm:
    try:
        summary = generate_llm_summary(stock_df)
        st.markdown("**LLM Summary:**")
        st.write(summary)
    except Exception as e:
        st.error(f"LLM summary failed: {e}")

# Show table and download cleaned csv
with st.expander("Show processed rows (tail 200)"):
    st.dataframe(stock_df.tail(200))

download_csv = st.download_button(
    "Download cleaned CSV",
    data=stock_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{stock_choice}_cleaned.csv",
    mime="text/csv",
)
