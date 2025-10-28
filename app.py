import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(page_title="AI Finance Manager Dashboard", layout="wide")

# --------------------------------
# HERO SECTION
# --------------------------------
st.markdown(
    """
    <style>
    .hero {
        background-color: #f3f6fc;
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 40px;
    }
    .hero h1 {
        font-size: 40px;
        color: #2a3b6b;
        margin-bottom: 10px;
    }
    .hero p {
        color: #5a5a5a;
        font-size: 18px;
        margin-bottom: 0;
    }
    .stats {
        display: flex;
        justify-content: center;
        gap: 80px;
        margin-top: 30px;
    }
    .stat-box {
        text-align: center;
    }
    .stat-box h2 {
        color: #3b7ddd;
        font-size: 30px;
        margin-bottom: 5px;
    }
    .stat-box p {
        color: #555;
        margin: 0;
    }
    </style>
    <div class="hero">
        <h1>💸 Manage Your Finances with AI</h1>
        <p>Track, analyze, and optimize your financial life effortlessly</p>
        <div class="stats">
            <div class="stat-box">
                <h2>50K+</h2>
                <p>Active Users</p>
            </div>
            <div class="stat-box">
                <h2>$2B+</h2>
                <p>Transactions Tracked</p>
            </div>
            <div class="stat-box">
                <h2>99.9%</h2>
                <p>Uptime</p>
            </div>
            <div class="stat-box">
                <h2>4.9/5</h2>
                <p>User Rating</p>
            </div>
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
    <style>
    .features {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 25px;
        margin-bottom: 40px;
    }
    .feature-card {
        border: 1px solid #e5e7eb;
        border-radius: 15px;
        padding: 20px;
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: left;
    }
    .feature-card h4 {
        color: #2a3b6b;
        margin-bottom: 8px;
    }
    .feature-card p {
        color: #555;
        font-size: 15px;
    }
    </style>
    <h3 style='text-align:center; color:#2a3b6b;'>Everything You Need to Manage Your Finances</h3>
    <div class="features">
        <div class="feature-card">
            <h4>📊 Advanced Analytics</h4>
            <p>Get detailed insights into your spending patterns with AI-powered analytics.</p>
        </div>
        <div class="feature-card">
            <h4>🧾 Smart Receipt Scanner</h4>
            <p>Extract data automatically from receipts using advanced AI technology.</p>
        </div>
        <div class="feature-card">
            <h4>🪙 Budget Planning</h4>
            <p>Create and manage budgets with intelligent recommendations.</p>
        </div>
        <div class="feature-card">
            <h4>💳 Multi-Account Support</h4>
            <p>Manage multiple accounts and credit cards in one place.</p>
        </div>
        <div class="feature-card">
            <h4>🌍 Multi-Currency</h4>
            <p>Support for multiple currencies with real-time conversion.</p>
        </div>
        <div class="feature-card">
            <h4>🤖 Automated Insights</h4>
            <p>Get automated financial insights and recommendations.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------
# FILE UPLOAD
# --------------------------------
st.subheader("📂 Upload Your Financial Data")
uploaded_file = st.file_uploader("Upload your finance CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    required_cols = ['Date', 'Account', 'Category', 'Description', 'Amount', 'Currency', 'Type']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        st.stop()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df = df.dropna(subset=['Amount'])

    # Summary Stats
    st.subheader("📈 Financial Summary")
    total_income = df[df['Type'].str.lower() == 'income']['Amount'].sum()
    total_expense = df[df['Type'].str.lower() == 'expense']['Amount'].sum()
    savings = total_income - total_expense

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Total Income", f"₹{total_income:,.0f}")
    c2.metric("💸 Total Expenses", f"₹{total_expense:,.0f}")
    c3.metric("💰 Net Savings", f"₹{savings:,.0f}")

    # Quick AI Insight
    top_cat = df[df['Type'].str.lower() == 'expense'].groupby('Category')['Amount'].sum().sort_values(ascending=False).head(1)
    if not top_cat.empty:
        st.success(f"🤖 AI Insight: You spent the most on **{top_cat.index[0]}** (₹{top_cat.iloc[0]:,.0f}).")

    # Filters
    st.subheader("🔍 Filters")
    category_filter = st.multiselect("Select Categories", df['Category'].unique())
    acc_filter = st.multiselect("Select Accounts", df['Account'].unique())

    filtered = df.copy()
    if category_filter:
        filtered = filtered[filtered['Category'].isin(category_filter)]
    if acc_filter:
        filtered = filtered[filtered['Account'].isin(acc_filter)]

    # Line Chart
    st.subheader("📉 Income vs Expense Over Time")
    line_df = filtered.groupby(['Date', 'Type'])['Amount'].sum().reset_index()
    if not line_df.empty:
        st.plotly_chart(px.line(line_df, x='Date', y='Amount', color='Type', markers=True,
                                title="Income vs Expense Over Time"), use_container_width=True)

    # Bar Chart
    st.subheader("📊 Category-wise Expenses")
    bar_df = filtered[filtered['Type'].str.lower() == 'expense'].groupby('Category')['Amount'].sum().reset_index()
    if not bar_df.empty:
        st.plotly_chart(px.bar(bar_df, x='Category', y='Amount', text_auto=True,
                               color='Amount', title="Category-wise Expense Analysis"),
                        use_container_width=True)

    # Pie Chart
    st.subheader("🥧 Expense Distribution")
    if not bar_df.empty:
        st.plotly_chart(px.pie(bar_df, values='Amount', names='Category', hole=0.4,
                               title="Expense Share by Category"),
                        use_container_width=True)

    # Transaction Table
    st.subheader("📋 All Transactions")
    st.dataframe(filtered.sort_values('Date', ascending=False), use_container_width=True)

    # --------------------------------
    # 💰 BUDGET GOAL TRACKER
    # --------------------------------
    st.subheader("🎯 Budget Goal Tracker")
    st.markdown("Set your monthly savings goal and track your progress in real time.")

    goal = st.number_input("Enter your monthly savings goal (₹)", min_value=1000, value=10000, step=1000)
    progress = (savings / goal) * 100 if goal > 0 else 0

    st.progress(min(progress / 100, 1.0))
    if savings >= goal:
        st.success(f"🎉 Congratulations! You’ve achieved your goal with ₹{savings:,.0f} saved.")
    else:
        st.info(f"💡 You’ve saved ₹{savings:,.0f} towards your ₹{goal:,.0f} goal ({progress:.1f}%). Keep going!")
else:
    st.info("👆 Upload your CSV file (use `finance_data.csv` sample) to start analyzing.")
