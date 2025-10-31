import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import pytesseract
import os
import re

# 🧠 Optional EasyOCR fallback
try:
    import easyocr
    EASY_OCR_AVAILABLE = True
except ImportError:
    EASY_OCR_AVAILABLE = False

# ⚙️ Configure pytesseract for Windows
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------- Streamlit App Configuration --------------------
st.set_page_config(page_title="AI Finance Dashboard", layout="wide")
st.title("💰 Manage Your Finances with AI")
st.write("📸 Upload receipts or CSV files, and get AI-powered financial insights.")

# -------------------- Upload Section --------------------
uploaded_files = st.file_uploader("📤 Upload receipts (images or CSV)", accept_multiple_files=True)

data = []

# -------------------- OCR Function --------------------
def extract_text_from_image(image):
    """Extract text using Tesseract or EasyOCR."""
    text = ""
    try:
        text = pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError:
        if EASY_OCR_AVAILABLE:
            st.warning("⚠️ Tesseract not found, switching to EasyOCR...")
            reader = easyocr.Reader(['en'])
            result = reader.readtext(image)
            text = " ".join([res[1] for res in result])
        else:
            st.error("❌ OCR not available. Please install Tesseract or EasyOCR.")
    return text

# -------------------- Receipt Text Parsing --------------------
def parse_receipt_text(text):
    """Extracts amount, date, and category from receipt text."""
    amount_pattern = r'Rs\.?\s?(\d+(?:\.\d{1,2})?)'
    date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    category_keywords = {
        "Food": ["restaurant", "cafe", "meal", "food"],
        "Travel": ["uber", "ola", "train", "flight", "bus"],
        "Shopping": ["mall", "store", "amazon", "flipkart"],
        "Groceries": ["grocery", "supermarket", "mart"],
        "Entertainment": ["movie", "cinema", "theatre"],
    }

    amount = re.findall(amount_pattern, text)
    date = re.findall(date_pattern, text)
    category = "Other"

    for cat, keywords in category_keywords.items():
        if any(word.lower() in text.lower() for word in keywords):
            category = cat
            break

    return {
        "Amount": float(amount[-1]) if amount else 0.0,
        "Date": date[-1] if date else "Unknown",
        "Category": category
    }

# -------------------- File Processing --------------------
if uploaded_files:
    for file in uploaded_files:
        if file.type.startswith("image/"):
            image = Image.open(file)
            st.image(image, caption=f"🧾 {file.name}", use_container_width=True)
            text = extract_text_from_image(image)
            if text:
                receipt_data = parse_receipt_text(text)
                data.append(receipt_data)
        elif file.name.endswith(".csv"):
            df = pd.read_csv(file)
            data.extend(df.to_dict(orient="records"))

# -------------------- Manual Entry Section --------------------
st.subheader("✍️ Add Transaction Manually")
with st.form("manual_entry"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Groceries", "Entertainment", "Other"])
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    add_btn = st.form_submit_button("Add Entry")
    if add_btn:
        data.append({"Date": str(date), "Category": category, "Amount": amount})
        st.success("✅ Transaction added successfully!")

# -------------------- Data Display & Charts --------------------
if data:
    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    st.subheader("📊 Transaction Summary")
    st.dataframe(df, use_container_width=True)

    # Expense Summary by Category
    category_summary = df.groupby("Category")["Amount"].sum().reset_index()

    # ---- PIE CHART ----
    st.markdown("### 🍕 Expense Distribution (Pie Chart)")
    fig_pie = px.pie(category_summary, values="Amount", names="Category",
                     title="Expense Distribution by Category")
    st.plotly_chart(fig_pie, use_container_width=True)

    # ---- BAR CHART ----
    st.markdown("### 📊 Expense Comparison (Bar Chart)")
    fig_bar = px.bar(category_summary, x="Category", y="Amount",
                     color="Category", text_auto=True,
                     title="Total Expense per Category")
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---- LINE CHART ----
    st.markdown("### 📈 Expense Trend Over Time (Line Chart)")
    date_summary = df.groupby("Date")["Amount"].sum().reset_index()
    fig_line = px.line(date_summary, x="Date", y="Amount",
                       markers=True, title="Daily Spending Trend")
    st.plotly_chart(fig_line, use_container_width=True)

else:
    st.info("📂 Upload receipts or add entries to visualize your financial data.")

