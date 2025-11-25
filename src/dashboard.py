import os
import pandas as pd
import streamlit as st
import psycopg2

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5433"))
PG_USER = os.getenv("PG_USER", "postgres")  # Update user
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")  # Update password
PG_DB = os.getenv("PG_DB", "postgres")

def get_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB
    )

@st.cache_data(ttl=5)
def load_events():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM orders_events;", conn)
    conn.close()
    return df

st.set_page_config(page_title="StreamCart Realtime ETL System Dashboard", layout="wide")
st.title("StreamCart Realtime ETL System Dashboard")

df = load_events()

if df.empty:
    st.warning("No events found in Postgres yet. Run producer + consumer first.")
    st.stop()

# basic cleanup
df["amount"] = df["amount"].astype(float)
df["event_ts"] = pd.to_datetime(df["event_ts"])

# KPIs (Total Events and Revenue)
total_orders = len(df)
total_revenue = df["amount"].sum()

c1, c2 = st.columns(2)
c1.metric("Total Events", f"{total_orders:,}")
c2.metric("Total Revenue", f"{total_revenue:,.2f}")

st.divider()

# Charts (Orders by status and Revenue by currency)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Orders by Status")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    st.bar_chart(status_counts.set_index("status"))

with col2:
    st.subheader("Revenue by Currency")
    currency_rev = df.groupby("currency")["amount"].sum().reset_index()
    currency_rev.columns = ["currency", "revenue"]
    st.bar_chart(currency_rev.set_index("currency"))

st.divider()

# Tables (Top customers by spend and Recent orders)
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 Customers by Spend")
    top_cust = (
        df.groupby("customer_id")["amount"].sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    top_cust.columns = ["customer_id", "total_spend"]
    st.dataframe(top_cust, use_container_width=True)

with col4:
    st.subheader("Recent Orders")
    recent = df.sort_values("event_ts", ascending=False).head(20)
    st.dataframe(
        recent[["event_ts", "order_id", "customer_id", "status", "amount", "currency"]],
        use_container_width=True
    )

st.caption(
    f"Connected to Postgres at {PG_HOST}:{PG_PORT} db={PG_DB}"
)
