import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# APP CONFIGURATION
# -------------------------------
st.set_page_config(page_title="AI Finance Manager Dashboard", layout="wide")
st.title("💰 Manage Your Finances with AI")
st.markdown("Get powerful insights into your income, expenses, and spending behavior.")

# -------------------------------
# FILE UPLOAD
# -------------------------------
uploaded_file = st.file_uploader("📂 Upload your Finance CSV file", type=["csv"])

if uploaded_file is not None:
    # Load and preprocess
    df = pd.read_csv(uploaded_file)

    # Check column consistency
    expected_cols = ['Date', 'Account', 'Category', 'Description', 'Amount', 'Currency', 'Type']
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        st.stop()

    # Clean and process
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df = df.dropna(subset=['Amount'])

    # -------------------------------
    # SUMMARY INSIGHTS
    # -------------------------------
    st.subheader("📊 Quick Financial Insights")

    total_income = df[df['Type'].str.lower() == 'income']['Amount'].sum()
    total_expense = df[df['Type'].str.lower() == 'expense']['Amount'].sum()
    savings = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Total Income", f"₹{total_income:,.0f}")
    col2.metric("💸 Total Expenses", f"₹{total_expense:,.0f}")
    col3.metric("💰 Net Savings", f"₹{savings:,.0f}")

    # -------------------------------
    # AI-LIKE FINANCIAL INSIGHT
    # -------------------------------
    top_category = (
        df[df['Type'].str.lower() == 'expense']
        .groupby('Category')['Amount'].sum()
        .sort_values(ascending=False)
        .head(1)
    )

    if not top_category.empty:
        cat_name = top_category.index[0]
        cat_value = top_category.iloc[0]
        st.success(f"🤖 *AI Insight:* You spent the most on **{cat_name}** (₹{cat_value:,.0f}). "
                   f"Consider reducing expenses here for better savings.")

    # -------------------------------
    # FILTERS
    # -------------------------------
    st.subheader("🔍 Filter Data")
    category_filter = st.multiselect("Select Categories", df['Category'].unique())
    account_filter = st.multiselect("Select Accounts", df['Account'].unique())

    filtered_df = df.copy()
    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]
    if account_filter:
        filtered_df = filtered_df[filtered_df['Account'].isin(account_filter)]

    # -------------------------------
    # CHARTS
    # -------------------------------
    st.subheader("📈 Visual Analysis")

    # Line Chart: Income vs Expenses Over Time
    line_df = (
        filtered_df.groupby(['Date', 'Type'])['Amount']
        .sum()
        .reset_index()
        .sort_values('Date')
    )

    if not line_df.empty:
        fig_line = px.line(
            line_df,
            x='Date',
            y='Amount',
            color='Type',
            title="Income vs Expense Over Time",
            markers=True
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("⚠️ Not enough numeric data to plot the line chart.")

    # Bar Chart: Category-wise Expenses
    bar_df = (
        filtered_df[filtered_df['Type'].str.lower() == 'expense']
        .groupby('Category')['Amount']
        .sum()
        .reset_index()
        .sort_values('Amount', ascending=False)
    )
    if not bar_df.empty:
        fig_bar = px.bar(
            bar_df,
            x='Category',
            y='Amount',
            title="Category-wise Expenses",
            color='Amount',
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("⚠️ Not enough data for the bar chart.")

    # Pie Chart: Expense Distribution
    if not bar_df.empty:
        fig_pie = px.pie(
            bar_df,
            values='Amount',
            names='Category',
            title="Expense Distribution by Category",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # -------------------------------
    # DATA TABLE
    # -------------------------------
    st.subheader("📋 Transaction Details")
    st.dataframe(filtered_df.sort_values('Date', ascending=False), use_container_width=True)

else:
    st.info("👆 Upload a CSV file to begin financial analysis.")
    st.caption("Use the sample file named `finance_data.csv` provided earlier.")
