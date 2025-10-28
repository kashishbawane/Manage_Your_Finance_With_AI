import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="AI Finance Dashboard", page_icon="💰", layout="wide")

# Header Section
st.title("💹 AI Finance Management Dashboard")

# Top KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Active Users", "50K+", "+5%")
col2.metric("💵 Transactions Tracked", "$2B+", "+12%")
col3.metric("⚙️ Uptime", "99.9%", "Stable")
col4.metric("⭐ User Rating", "4.9 / 5", "Excellent")

st.markdown("---")
st.subheader("Everything you need to manage your finances")

# Feature cards
c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

with c1:
    st.info("**📊 Advanced Analytics**\nGet detailed insights into your spending patterns with AI-powered analytics.")
with c2:
    st.info("**🧾 Smart Receipt Scanner**\nExtract data automatically from receipts using advanced AI technology.")
with c3:
    st.info("**📅 Budget Planning**\nCreate and manage budgets with intelligent recommendations.")
with c4:
    st.info("**🏦 Multi-Account Support**\nManage multiple accounts and credit cards in one place.")
with c5:
    st.info("**💱 Multi-Currency**\nSupport for multiple currencies with real-time conversion.")
with c6:
    st.info("**🤖 Automated Insights**\nGet automated financial insights and recommendations.")

st.markdown("---")
st.subheader("📈 Financial Insights Dashboard")

# Upload CSV file
uploaded_file = st.file_uploader("Upload your financial data (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Try to handle different date column names
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    if date_cols:
        df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')

    st.write("### Sample Data", df.head())

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if len(numeric_cols) < 2:
        st.warning("⚠️ Not enough numeric data to plot charts.")
    else:
        col_a, col_b = st.columns(2)

        # Line Chart
        with col_a:
            st.markdown("#### 📉 Trend Over Time")
            x_axis = st.selectbox("Select Date/Time Column", options=df.columns)
            y_axis = st.selectbox("Select Value Column", options=numeric_cols)
            line_fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
            st.plotly_chart(line_fig, use_container_width=True)

        # Bar Chart
        with col_b:
            st.markdown("#### 📊 Category Comparison")
            category_col = st.selectbox("Select Category Column", options=df.columns)
            value_col = st.selectbox("Select Value Column for Bar Chart", options=numeric_cols)
            bar_fig = px.bar(df, x=category_col, y=value_col, title=f"{value_col} by {category_col}")
            st.plotly_chart(bar_fig, use_container_width=True)

        st.markdown("#### 🥧 Expense Distribution")
        pie_col = st.selectbox("Select Category for Pie Chart", options=df.columns)
        pie_val = st.selectbox("Select Value for Pie Chart", options=numeric_cols)
        pie_fig = px.pie(df, names=pie_col, values=pie_val, title=f"{pie_val} Distribution by {pie_col}")
        st.plotly_chart(pie_fig, use_container_width=True)

else:
    st.info("⬆️ Upload a CSV file to view interactive insights.")

st.markdown("---")
st.caption("💡 Built with Streamlit & Plotly | AI Finance Platform")
