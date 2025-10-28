import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import pytesseract
import os
import io
import re

# 🪟 WINDOWS CONFIGURATION FOR PYTESSERACT
if os.name == "nt":  # 'nt' = Windows
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ------------------------- #
# 📊 Streamlit Page Setup
# ------------------------- #
st.set_page_config(page_title="AI Finance Manager", layout="wide")
st.title("💰 Manage Your Finances Using AI")
st.markdown("### Analyze your spending, visualize your data, and scan receipts smartly using AI 🧠")

# ------------------------- #
# 📁 Upload CSV Section
# ------------------------- #
st.sidebar.header("📂 Upload your financial data")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")

        # Clean up data
        df.columns = df.columns.str.strip()
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        st.write("### Sample Data Preview")
        st.dataframe(df.head())

        if len(numeric_cols) < 1:
            st.warning("⚠️ Not enough numeric data to plot charts.")
        else:
            # Dropdown for numeric column
            col_to_analyze = st.selectbox("Select numeric column for analysis", numeric_cols)

            # ------------------------- #
            # 📈 Bar Chart
            # ------------------------- #
            st.subheader("📊 Expense Bar Chart")
            fig_bar = px.bar(df, x=df.columns[0], y=col_to_analyze, title="Expenses by Category")
            st.plotly_chart(fig_bar, use_container_width=True)

            # ------------------------- #
            # 📉 Line Chart
            # ------------------------- #
            st.subheader("📈 Expense Trend (Line Chart)")
            fig_line = px.line(df, x=df.columns[0], y=col_to_analyze, title="Expense Trend Over Time")
            st.plotly_chart(fig_line, use_container_width=True)

            # ------------------------- #
            # 🥧 Pie Chart
            # ------------------------- #
            st.subheader("🥧 Expense Distribution")
            if len(df.columns) >= 2:
                fig_pie = px.pie(df, names=df.columns[0], values=col_to_analyze, title="Category-wise Expense Share")
                st.plotly_chart(fig_pie, use_container_width=True)

            # ------------------------- #
            # 📈 Quick Insights
            # ------------------------- #
            st.subheader("💡 Quick Insights")
            st.write(f"**Total Spending:** ₹{df[col_to_analyze].sum():,.2f}")
            st.write(f"**Average Spending:** ₹{df[col_to_analyze].mean():,.2f}")
            st.write(f"**Maximum Expense:** ₹{df[col_to_analyze].max():,.2f}")
            st.write(f"**Minimum Expense:** ₹{df[col_to_analyze].min():,.2f}")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

else:
    st.info("⬆️ Upload your financial dataset to begin analysis")

# ------------------------- #
# 🧾 Smart Receipt Scanner
# ------------------------- #
st.markdown("---")
st.header("🧾 Smart Receipt Scanner (OCR)")

uploaded_receipt = st.file_uploader("Upload your receipt image", type=["png", "jpg", "jpeg"])

if uploaded_receipt is not None:
    # Display uploaded image
    st.image(uploaded_receipt, caption="Uploaded Receipt", use_container_width=True)

    try:
        image = Image.open(uploaded_receipt)
        text = pytesseract.image_to_string(image)

        st.subheader("📜 Extracted Text:")
        st.text(text)

        # ------------------------- #
        # 🧠 Simple AI Extraction Logic
        # ------------------------- #
        amount_match = re.search(r'₹\s?([\d,]+\.?\d*)', text)
        date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        category = None

        if "fuel" in text.lower() or "petrol" in text.lower():
            category = "Fuel"
        elif "uber" in text.lower() or "ola" in text.lower():
            category = "Transport"
        elif "pizza" in text.lower() or "restaurant" in text.lower() or "food" in text.lower():
            category = "Food"
        elif "electric" in text.lower() or "power" in text.lower() or "bill" in text.lower():
            category = "Utilities"
        elif "hotel" in text.lower():
            category = "Travel"
        elif "amazon" in text.lower() or "shopping" in text.lower():
            category = "Shopping"
        else:
            category = "Other"

        st.markdown("### 🧾 Extracted Receipt Insights")
        st.write(f"**Detected Date:** {date_match.group(1) if date_match else 'N/A'}")
        st.write(f"**Detected Amount:** ₹{amount_match.group(1) if amount_match else 'N/A'}")
        st.write(f"**Predicted Category:** {category}")

    except Exception as e:
        st.error(f"❌ Error reading receipt: {e}")
