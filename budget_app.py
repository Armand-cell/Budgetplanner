import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import json
import os

st.set_page_config(page_title="Beate's Budget 💖", page_icon="💖")

DATA_FILE = "budget_data.json"

# -------------------------
# LOAD DATA
# -------------------------

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {"expenses": [], "savings": 0}

if "expenses" not in st.session_state:
    st.session_state.expenses = data["expenses"]

if "savings" not in st.session_state:
    st.session_state.savings = data["savings"]

# -------------------------
# PASTEL STYLE
# -------------------------

st.markdown("""
<style>

.stApp {
background-color:#ffd1e6;
}

h1,h2,h3 {
color:#d63384;
}

.stButton>button{
background-color:#ff85a2;
color:white;
border-radius:10px;
border:none;
}

.stButton>button:hover{
background-color:#d63384;
}

div[data-testid="stMetric"]{
background-color:#ffe6f2;
padding:15px;
border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

st.title("💖 Beate's Budget Planner")

# -------------------------
# PAYDAY
# -------------------------

payday = st.number_input("💰 Payday (day of month)", 1, 31, 25)

today = datetime.now()

days_in_month = calendar.monthrange(today.year, today.month)[1]

if today.day >= payday:
    days_left = days_in_month - today.day + payday
else:
    days_left = payday - today.day

# -------------------------
# SALARY
# -------------------------

salary = st.number_input("Monthly Salary (R)", min_value=0)

# -------------------------
# FIXED COSTS
# -------------------------

st.header("🏠 Fixed Expenses")

rent = st.number_input("Rent 🏠", min_value=0)
phone = st.number_input("Phone 📱", min_value=0)
insurance = st.number_input("Insurance 🛡️", min_value=0)
subscriptions = st.number_input("Subscriptions 📺", min_value=0)

fixed_total = rent + phone + insurance + subscriptions

remaining_after_fixed = salary - fixed_total

st.metric("After Fixed Costs", f"R{remaining_after_fixed}")

# -------------------------
# ADD EXPENSE
# -------------------------

st.header("🛍️ Add Spending")

category = st.selectbox(
"Category",
["⛽ Petrol","🛒 Groceries","☕ Coffee","🍔 Food","🛍️ Shopping","🎬 Entertainment","Other"]
)

amount = st.number_input("Amount",min_value=0)

if st.button("Add Expense 💕"):

    st.session_state.expenses.append(
        {
            "Category":category,
            "Amount":amount,
            "Date":datetime.now().strftime("%Y-%m-%d")
        }
    )

    st.rerun()

# -------------------------
# SPENDING LOG
# -------------------------

st.subheader("📋 Spending Log")

total_spent=0

for i,expense in enumerate(st.session_state.expenses):

    col1,col2,col3=st.columns([3,2,1])

    col1.write(f"{expense['Category']} ({expense['Date']})")
    col2.write(f"R{expense['Amount']}")

    if col3.button("❌",key=i):
        st.session_state.expenses.pop(i)
        st.rerun()

    total_spent+=expense["Amount"]

st.metric("Total Spent",f"R{total_spent}")

# -------------------------
# REMAINING MONEY
# -------------------------

remaining=remaining_after_fixed-total_spent

st.metric("Money Left",f"R{remaining}")

# -------------------------
# DAILY & WEEKLY BUDGET
# -------------------------

daily_budget=remaining/days_left if days_left>0 else remaining
weekly_budget=daily_budget*7

st.metric("💖 Daily Budget",f"R{round(daily_budget,2)}")
st.metric("📅 Weekly Budget",f"R{round(weekly_budget,2)}")

# -------------------------
# TODAY SPENDING
# -------------------------

today_str=today.strftime("%Y-%m-%d")

today_spent=sum(
expense["Amount"]
for expense in st.session_state.expenses
if expense["Date"]==today_str
)

remaining_today=daily_budget-today_spent

st.header("📅 Today's Spending")

st.metric("Spent Today",f"R{today_spent}")
st.metric("Remaining Today",f"R{round(remaining_today,2)}")

if today_spent>daily_budget:
    st.error("⚠️ You spent more than today's budget!")

# -------------------------
# BURN RATE
# -------------------------

if total_spent>0:

    avg_daily_spend=total_spent/max(today.day,1)

    if avg_daily_spend>0:

        days_until_empty=remaining/avg_daily_spend

        st.warning(
        f"🔥 At this spending rate money will last about {round(days_until_empty)} days"
        )

# -------------------------
# SAVINGS GOAL
# -------------------------

st.header("🎯 Savings Goal")

goal=st.number_input("Savings Goal",min_value=0)

add_savings=st.number_input("Add Savings",min_value=0)

if st.button("Add To Savings"):
    st.session_state.savings+=add_savings
    st.rerun()

st.write(f"Saved: R{st.session_state.savings}")

if goal>0:
    progress=st.session_state.savings/goal
    st.progress(min(progress,1.0))

# -------------------------
# CHARTS
# -------------------------

if st.session_state.expenses:

    df=pd.DataFrame(st.session_state.expenses)

    fig=px.pie(df,values="Amount",names="Category",title="Spending Breakdown")

    st.plotly_chart(fig)

    trend=px.line(
        df.groupby("Date")["Amount"].sum().reset_index(),
        x="Date",
        y="Amount",
        title="Daily Spending Trend"
    )

    st.plotly_chart(trend)

# -------------------------
# SAVE DATA
# -------------------------

data={
"expenses":st.session_state.expenses,
"savings":st.session_state.savings
}

with open(DATA_FILE,"w") as f:
    json.dump(data,f)