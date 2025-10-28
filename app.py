import streamlit as st
import pandas as pd
import plotly.express as px
import pytesseract
from PIL import Image
import re
import os

# 🪟 WINDOWS CONFIGURATION FOR PYTESSERACT
if os.name == "nt":  # Windows system
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(page_title="AI Finance Manager Dashboard", layout="wide")

# Create receipts directory
os.makedirs("receipts", exist_ok=True)

# --------------------------------
# HERO SECTION
# --------------------------------
st.markdown(
    """
    <style>
    .hero {background-color:#f3f6fc;padding:40px;border-radius:15px;text-align:center;margin-bottom:40px;}
    .hero h1 {font-size:40px;color:#2a3b6b;margin-bottom:10px;}
    .hero p {color:#5a5a5a;font-size:18px;}
    .stats {display:flex;justify-content:center;gap:80px;margin-top:30px;}
    .stat-box{text-align:center;}
    .stat-box h2{color:#3b7ddd;font-size:30px;margin-bottom:5px;}
    .stat-box p{color:#555;margin:0;}
    </style>
    <div class="hero">
        <h1>💸 Manage Your Finances with AI</h1>
        <p>Track, analyze, and optimize your financial life effortlessly</p>
        <div class="stats">
            <div class="stat-box"><h2>50K+</h2><p>Active Users</p></div>
            <div class="stat-box"><h2>$2B+</h2><p>Transactions Tracked</p></div>
            <div class="stat-box"><h2>99.9%</h2><p>Uptime</p></div>
            <div class="stat-box"><h2>4.9/5</h2><p>User Rating</p></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------
# FEATURE SECTION
# --------------------------------
st.markdown(
    """
    <h3 style='text-align:center; color:#2a3b6b;'>Everything You Need to Manage Your Finances</h3>
    """,
    unsafe_allow_html=True
)

cols = st.columns(3)
features = [
    ("📊 Advanced Analytics", "Get detailed insights into your spending patterns with AI-powered analytics."),
    ("🧾 Smart Receipt Scanner", "Extract data automatically from receipts using OCR AI technology."),
    ("🪙 Budget Planning", "Create and manage budgets with intelligent recommendations."),
    ("💳 Multi-Account Support", "Manage multiple accounts and credit cards in one place."),
    ("🌍 Multi-Currency", "Support for multiple currencies with real-time conversion."),
    ("🤖 Automated Insights", "Get automated financial insights and recommendations."),
]

for i, (title, desc) in enumerate(features):
    with cols[i % 3]:
        st.markdown(f"#### {title}")
        st.write(desc)

# --------------------------------
# UPLOAD CSV SECTION
# --------------------------------
st.subheader("📂 Upload Your Financial Data")
uploaded_file = st.file_uploader("Upload your finance CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("No file uploaded — sample dataset will be created.")
    df = pd.DataFrame(columns=['Date', 'Account', 'Category', 'Description', 'Amount', 'Currency', 'Type'])

# --------------------------------
# 🧾 SMART RECEIPT SCANNER FEATURE
# --------------------------------
st.subheader("🧾 Smart Receipt Scanner")

receipt_img = st.file_uploader("Upload a receipt image", type=["jpg", "png", "jpeg"])

if receipt_img:
    image = Image.open(receipt_img)
    st.image(image, caption="Uploaded Receipt", use_column_width=True)

    with st.spinner("🔍 Extracting data using AI..."):
        try:
            text = pytesseract.image_to_string(image)

            # Simple regex-based extraction
            amount_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text)
            date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)

            category = "Miscellaneous"
            if re.search(r'grocery|mart|supermarket', text, re.IGNORECASE):
                category = "Groceries"
            elif re.search(r'uber|travel|taxi|train', text, re.IGNORECASE):
                category = "Travel"
            elif re.search(r'food|restaurant|pizza|hotel', text, re.IGNORECASE):
                category = "Food"
            elif re.search(r'bill|electricity|gas|recharge', text, re.IGNORECASE):
                category = "Utilities"

            amount = float(amount_match.group(1).replace(',', '')) if amount_match else 0.0
            date = date_match.group(1) if date_match else pd.Timestamp.now().strftime('%d-%m-%Y')

            new_entry = {
                'Date': date,
                'Account': 'Cash',
                'Category': category,
                'Description': 'Auto-entry from receipt',
                'Amount': amount,
                'Currency': 'INR',
                'Type': 'Expense'
            }

            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            st.success(f"✅ Extracted Transaction: {category} — ₹{amount:,.2f} on {date}")

        except pytesseract.TesseractNotFoundError:
            st.error("⚠️ Tesseract OCR not found. Please install it from https://github.com/UB-Mannheim/tesseract/wiki")

# --------------------------------
# ANALYTICS SECTION
# --------------------------------
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    st.subheader("📈 Financial Summary")
    total_income = df[df['Type'].str.lower() == 'income']['Amount'].sum()
    total_expense = df[df['Type'].str.lower() == 'expense']['Amount'].sum()
    savings = total_income - total_expense

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Total Income", f"₹{total_income:,.0f}")
    c2.metric("💸 Total Expenses", f"₹{total_expense:,.0f}")
    c3.metric("💰 Net Savings", f"₹{savings:,.0f}")

    # Charts
    st.subheader("📊 Category-wise Expenses")
    bar_df = df[df['Type'].str.lower() == 'expense'].groupby('Category')['Amount'].sum().reset_index()
    if not bar_df.empty:
        st.plotly_chart(px.bar(bar_df, x='Category', y='Amount', color='Amount', text_auto=True,
                               title="Expense by Category"), use_container_width=True)

    st.subheader("🥧 Expense Distribution")
    if not bar_df.empty:
        st.plotly_chart(px.pie(bar_df, values='Amount', names='Category', hole=0.4,
                               title="Expense Share by Category"), use_container_width=True)

    # Budget Goal Tracker
    st.subheader("🎯 Budget Goal Tracker")
    goal = st.number_input("Set your monthly savings goal (₹)", min_value=1000, value=10000, step=1000)
    progress = (savings / goal) * 100 if goal > 0 else 0
    st.progress(min(progress / 100, 1.0))

    if savings >= goal:
        st.success(f"🎉 Goal achieved! Saved ₹{savings:,.0f}.")
    else:
        st.info(f"💡 Saved ₹{savings:,.0f} out of ₹{goal:,.0f} ({progress:.1f}%)")

    st.subheader("📋 Transactions")
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)
else:
    st.info("👆 Upload a CSV or scan a receipt to start.")
