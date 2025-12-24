import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration & Theme
st.set_page_config(page_title="Biashara App Pro", layout="centered")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #28a745; color: white; }
    </style>
    """, unsafe_index=True)

# Initialize Data
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("⚙️ Management")
page = st.sidebar.radio("Go to:", ["Daily Entry", "Reports & Analytics", "Data Safety"])

# --- PAGE 1: DAILY ENTRY ---
if page == "Daily Entry":
    st.title("📱 New Transaction")
    
    with st.container():
        cat = st.radio("Category", ["Job/Service", "Spare/Good"], horizontal=True)
        mod = st.text_input("Phone Model").upper().strip()
        itm = st.text_input("Item/Service Name").title().strip()
        prc = st.number_input("Price (TSh)", min_value=0, step=500)
        
        if st.button("HIFADHI (SAVE)"):
            if itm and prc > 0:
                new_entry = pd.DataFrame([{
                    'Date': datetime.now().strftime("%Y-%m-%d"),
                    'Model': mod if mod else "N/A",
                    'Item': itm,
                    'Category': cat,
                    'Price': prc
                }])
                st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
                st.success(f"✅ Saved: {itm}")
            else:
                st.error("Please fill Name and Price!")

    st.divider()
    if st.button("🗑️ Delete Last Entry"):
        if not st.session_state.db.empty:
            st.session_state.db = st.session_state.db[:-1]
            st.warning("Last entry removed.")
            st.rerun()

# --- PAGE 2: REPORTS & ANALYTICS ---
elif page == "Reports & Analytics":
    st.title("📊 Business Reports")
    
    if not st.session_state.db.empty:
        df = st.session_state.db.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Report Filters
        period = st.selectbox("Select Period", ["Today", "This Month", "This Year", "Custom Range"])
        today = datetime.now().date()
        
        if period == "Today":
            start, end = today, today
        elif period == "This Month":
            start, end = today.replace(day=1), today
        else:
            start, end = today.replace(month=1, day=1), today

        mask = (df['Date'].dt.date >= start) & (df['Date'].dt.date <= end)
        filtered = df.loc[mask]

        st.metric("Total Revenue", f"{filtered['Price'].sum():,.0f} TSh")
        
        # Ranking Table
        st.subheader("🏆 Top Performers")
        rank = filtered.groupby(['Category', 'Item', 'Model']).size().reset_index(name='Qty')
        st.dataframe(rank.sort_values('Qty', ascending=False), use_container_width=True)
    else:
        st.info("No data available. Please upload a backup or enter new sales.")

# --- PAGE 3: DATA SAFETY ---
elif page == "Data Safety":
    st.title("💾 Backup & Restore")
    
    st.subheader("1. Restore Data")
    uploaded = st.file_uploader("Upload your MASTER_BIASHARA.csv", type="csv")
    if uploaded:
        uploaded_df = pd.read_csv(uploaded)
        st.session_state.db = pd.concat([st.session_state.db, uploaded_df]).drop_duplicates().reset_index(drop=True)
        st.success("✅ Data Restored and Merged!")

    st.divider()
    st.subheader("2. Save Data")
    master_csv = st.session_state.db.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DOWNLOAD MASTER BACKUP", master_csv, "MASTER_BIASHARA.csv", "text/csv")
