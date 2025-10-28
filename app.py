import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import pytesseract
import os
import re
import io

# 🧠 Optional: Use EasyOCR if Tesseract is missing
try:
    import easyocr
    EASY_OCR_AVAILABLE = True
except ImportError:
    EASY_OCR_AVAILABLE = False

# 🪟 WINDOWS CONFIGURATION FOR PYTESSERACT
if os.name == "nt":  # Windows system
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------------- Streamlit App Title ----------------------
st.set_page_config(page_title="AI Smart Finance Manager", layout="wide")
st.title("💰 Manage Your Finance with AI")
st.write("📸 Upload receipts or enter transactions to analyze your spending smartly.")

# ---------------------- Data Upload Section ----------------------
uploaded_files = st.file_uploader("📤 Upload your receipts or CSV files", accept_multiple_files=True)

data = []

def extract_text_from_image(image):
    """Extracts text using Tesseract or EasyOCR fallback."""
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
            st.error("❌ Neither Tesseract nor EasyOCR is available. Please install one.")
    return text


def parse_receipt_text(text):
    """Extract basic fields like amount, date, and category from the receipt."""
    amount_pattern = r'Rs\.?\s?(\d+(?:\.\d{1,2})?)'
    date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    category_keywords = {
        "food": ["restaurant", "cafe", "meal", "food"],
        "travel": ["uber", "ola", "train", "flight", "bus"],
        "shopping": ["mall", "store", "amazon", "flipkart"],
        "groceries": ["grocery", "supermarket", "mart"],
        "entertainment": ["movie", "cinema", "theatre"]
    }

    # Extract amount and date
    amount = re.findall(amount_pattern, text)
    date = re.findall(date_pattern, text)
    category = "Other"

    for cat, keywords in category_keywords.items():
        if any(word.lower() in text.lower() for word in keywords):
            category = cat.capitalize()
            break

    return {
        "Amount": float(amount[-1]) if amount else 0.0,
        "Date": date[-1] if date else "Unknown",
        "Category": category
    }

# ---------------------- File Processing ----------------------
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

# ---------------------- Manual Entry ----------------------
st.subheader("✍️ Add Transaction Manually")
with st.form("manual_entry"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Groceries", "Entertainment", "Other"])
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    add_btn = st.form_submit_button("Add Entry")
    if add_btn:
        data.append({"Date": str(date), "Category": category, "Amount": amount})
        st.success("✅ Transaction added successfully!")

# ---------------------- Display and Charts ----------------------
if data:
    df = pd.DataFrame(data)
    st.subheader("📊 Transaction Summary")
    st.dataframe(df, use_container_width=True)

    # Expense Summary by Category
    cat_summary = df.groupby("Category")["Amount"].sum().reset_index()
    fig = px.pie(cat_summary, values="Amount", names="Category", title="💸 Expense Distribution by Category")
    st.plotly_chart(fig, use_container_width=True)

    # Expense Trend Over Time
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    time_summary = df.groupby("Date")["Amount"].sum().reset_index()
    fig2 = px.line(time_summary, x="Date", y="Amount", title="📆 Spending Over Time")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("📂 Upload receipts or add entries to get started.")
