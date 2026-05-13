import streamlit as st
import numpy  as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Live Coffee Sales Dashboard",layout="wide")
st.title("☕ Sales Trend and Time-Based Performance Analyysis for Afficionado Coffee Roasters")


#----------------------------
#1️⃣ Load Data
# ---------------------------
df=pd.read_csv(r"C:\Users\ns021\OneDrive\Documents\unified mentor project 1\coffee_updated.csv") 

def load_data():
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df['revenue']=df['transaction_qty']*df['unit_price']
    df['hour']=df['transaction_datetime'].dt.hour
    df['day_of_week']=df['transaction_datetime'].dt.day_name()
    df['date']=df['transaction_datetime'].dt.date
    return df;

df=load_data()

#----------------------------
# Sidebar Filters
#----------------------------
st.sidebar.header("Filters")
locations=st.sidebar.multiselect(
    "Select Store Location",options=df['store_location'].unique(),default=df['store_location'].unique())
days=st.sidebar.multiselect(
    "Select Days of Week",options=df['day_of_week'].unique(),default=df['day_of_week'].unique())
hours=st.sidebar.slider("Select Hour Range",0,23,(0,23))

#----------------------------
# Metric Toggle
#----------------------------
metric_option=st.sidebar.radio(
    "Select Metric",
    ["Revenue","Transaction Quantity"]
)

# Slect coluumn based on user choice
if metric_option=="Revenue":
    metric_col="revenue"
else:
    metric_col="transaction_qty"

# Filter data based on selections
df_filtered = df[
    (df['store_location'].isin(locations)) &
    (df['day_of_week'].isin(days)) &
    (df['hour']>=hours[0]) &
    (df['hour']<=hours[1])
]
#----------------------
# KPI Metrics
#----------------------
total_revenue=df_filtered['revenue'].sum()
total_transactions=df_filtered['transaction_qty'].sum()
total_orders=df_filtered['transaction_id'].nunique()
total_value=df_filtered[metric_col].sum()

col1,col2,col3=st.columns(3)

with col1:
    st.metric("💰 Total Revenue", f"${total_revenue:,.0f}")

with col2:
    st.metric("🛒 Transaction Quantity", f"{total_transactions:,}")

with col3:
    st.metric("📦 Total Orders", f"{total_orders:,}")
    col1, col2 = st.columns(2)


#------------------------
# Overall  Sales Trend
#------------------------
st.subheader("📈 Overall Sales Trend")

daily_sales = df_filtered.resample('D', on='transaction_datetime')[metric_col].sum()

fig = px.line(
    x=daily_sales.index,
    y=daily_sales.values,
    markers=True,
    text=daily_sales.values,
    labels={'x': 'Date', 'y': metric_option},
    title=f"Daily {metric_option} Trend"
)
fig.update_traces(textposition="top center")

fig, ax = plt.subplots(figsize=(10,5))

ax.plot(daily_sales.index, daily_sales.values, marker='o')

ax.set_xlabel("Date")
ax.set_ylabel(metric_col.replace("_"," ").title())
ax.set_title("Daily " + metric_option + " Trend")
ax.grid(True)

plt.xticks(rotation=45)

st.plotly_chart(fig, width="stretch")
peak_day = daily_sales.idxmax()
low_day = daily_sales.idxmin()

st.info(f"""
📈 Sales peaked on **{peak_day.date()}**  
📉 Lowest performance was on **{low_day.date()}**  
🔍 Indicates short-term demand fluctuations and possible seasonal spikes.
""")
csv = daily_sales.to_csv(index=False).encode('utf-8')

st.download_button(
    "⬇️ Download Data",
    csv,
    "daily_sales.csv",
    "text/csv",
    key="download_daily"
)

# Weekly Sales Trend
# ---------------------------

weekly_sales = df_filtered.resample('W', on='transaction_datetime')[metric_col].sum()
fig1_weekly = px.line(
    x=weekly_sales.index,
    y=weekly_sales.values,
    markers=True,
    labels={'x': 'Week', 'y': metric_option},
    title=f"📈Weekly {metric_option} Trend"
)
# Hover shows metric name + value
fig1_weekly.update_traces(
    hovertemplate=f"{metric_option}: %{{y}}<extra></extra>",
    text=None
)
fig1_weekly.update_layout(
    plot_bgcolor="white",
    width=900,
    height=500,
    margin=dict(l=50, r=50, t=80, b=50)
)
st.plotly_chart(fig1_weekly, width="stretch")
peak_week = weekly_sales.idxmax()

st.info(f"""
📊 Highest weekly performance observed during **{peak_week.date()}** week  
📅 Weekly trends help identify consistent growth or decline patterns.
""")
csv = weekly_sales.to_csv(index=False).encode('utf-8')

st.download_button(
    "⬇️ Download Data",
    csv,
    "weekly_sales.csv",
    "text/csv",
    key="download_weekly"
)

# ---------------------------
# Monthly Sales Trend
# ---------------------------

monthly_sales = df_filtered.resample('ME', on='transaction_datetime')[metric_col].sum()
fig2_monthly = px.line(
    x=monthly_sales.index,
    y=monthly_sales.values,
    markers=True,
    labels={'x': 'Month', 'y': metric_option},
    title=f"📈Monthly {metric_option} Trend"
)
fig2_monthly.update_traces(
    hovertemplate=f"{metric_option}: %{{y}}<extra></extra>",
    text=None
)
fig2, ax2 = plt.subplots(figsize=(12,5))
ax2.plot(monthly_sales.index, monthly_sales.values, marker='o', color='green')
ax2.set_xlabel("Month")
ax2.set_ylabel(metric_option)
ax2.set_title("Monthly " + metric_option + " Trend")
ax2.grid(True)
st.plotly_chart(fig2_monthly, width='stretch')
best_month = monthly_sales.idxmax()

st.info(f"""
📆 Best performing month: **{best_month.strftime('%B %Y')}**  
📈 Shows long-term growth trend and seasonal demand behavior.
""")
csv = monthly_sales.to_csv(index=False).encode('utf-8')

st.download_button(
    "⬇️ Download Data",
    csv,
    "monthly_sales.csv",
    "text/csv",
    key="download_monthly"
)
# ---------------------------
# Day-of-Week Performance
# ---------------------------
st.subheader("📊 Day-of-Week Performance")
dow_sales = df_filtered.groupby('day_of_week')[metric_col].sum().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)
yticks = np.arange(1000, dow_sales.max()+ 2000,2000)
fig3, ax3 = plt.subplots(figsize=(14,6))
fig3 = px.bar(
    dow_sales,
    x=dow_sales.index,
    y=dow_sales.values,
    text=dow_sales.values,
    color=dow_sales.values,
    color_continuous_scale='Viridis',
    labels={'x':'Day of Week','y':metric_option},
    title="Day-of-Week " + metric_option + " Performance"
)

fig3.update_traces(texttemplate='%{text:.2s}', textposition='outside')
colors = ["#4E79A7","#59A14F","#F28E2B","#E15759","#76B7B2","#EDC948","#B07AA1"]
sns.barplot(x=dow_sales.index, y=dow_sales.values, hue=dow_sales.index, palette=colors, ax=ax3, legend=False)
ax3.set_xlabel("Day of Week")
ax3.set_ylabel(metric_option)
ax3.set_title(metric_option + " by Day of Week")
# rotate labels for better UI
ax3.tick_params(axis='x', rotation=30)
plt.tight_layout()

# grid for dashboard look
ax3.grid(axis="y", linestyle="--", alpha=0.6)
st.plotly_chart(fig3, width='stretch')
peak_day = dow_sales.idxmax()
low_day = dow_sales.idxmin()

st.info(f"""
📌 Highest sales occur on **{peak_day}**  
📉 Lowest sales occur on **{low_day}**  
🧠 Suggests strong weekday/weekend demand differences.
""")
csv = dow_sales.to_csv(index=False).encode('utf-8')

st.download_button(
    "⬇️ Download Data",
    csv,
    "dow_sales.csv",
    "text/csv",
    key="download_dow"
)

# ---------------------------
# Hourly Demand Heatmap
# ---------------------------
st.subheader("⏰ Hourly Demand Heatmap")
hourly_sales = df_filtered.pivot_table(index='day_of_week', columns='hour', values=metric_col, aggfunc='sum').reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)
fig4, ax4 = plt.subplots(figsize=(14,5))
sns.heatmap(hourly_sales, cmap="YlGnBu", linewidths=0.5, annot=True, fmt=".0f", ax=ax4)
ax4.set_xlabel("Hour of Day")
ax4.set_ylabel(metric_option)
ax4.set_title(metric_option + " Heatmap by Hour & Day")
st.pyplot(fig4)
peak_hour = hourly_sales.sum().idxmax()
peak_day_hour = hourly_sales.stack().idxmax()

st.info(f"""
⏰ Peak demand hour: **{peak_hour}:00 hrs**  
🔥 Highest intensity observed on **{peak_day_hour[0]} at {peak_day_hour[1]}:00 hrs**  
📊 Helps optimize staffing and inventory during peak hours.
""")
csv = hourly_sales.to_csv(index=False).encode('utf-8')

st.download_button(
    "⬇️ Download Data",
    csv,
    "hourly_sales.csv",
    "text/csv",
    key="download_hourly"
)

# ---------------------------
# Location Comparison Panel
# ---------------------------
st.subheader("🏪 " + metric_option + " by Store Location")
location_sales = df.groupby('store_location')[metric_col].sum()  # notice 'location_sales' is renamed for consistency
fig5 = px.bar(
    location_sales, 
    x=location_sales.index, 
    y=location_sales.values, 
    text=location_sales.values, 
    color=location_sales.values,
    color_continuous_scale='Viridis',
    labels={'x':'Store Location','y':metric_option},
    title=metric_option + " by Store Location"
)
st.plotly_chart(fig5, width='stretch')
best_location = location_sales.idxmax()
Lowperf_location = location_sales.idxmin()

st.info(f"""
🏪 Top performing store: **{best_location}**  
📉 Lowest performing store: **{Lowperf_location}**  
📍 Useful for regional strategy and resource allocation.
""")
csv = location_sales.to_csv(index=False).encode('utf-8')

st.download_button(
    "⬇️ Download Data",
    csv,
    "location_sales.csv",
    "text/csv",
    key="download_location"
)


