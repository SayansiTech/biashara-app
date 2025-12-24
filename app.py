import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Biashara Pro", layout="centered")

# --- CUSTOM THEME (Fixed) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #004AAD;
        color: white;
        font-weight: bold;
    }
    [data-testid="stMetricValue"] { color: #004AAD; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Data
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("⚙️ Shop Menu")
page = st.sidebar.radio("Go to:", ["Daily Entry", "Reports & Analytics", "Data Safety"])

# --- PAGE 1: DAILY ENTRY ---
if page == "Daily Entry":
    st.title("📱 New Transaction")
    
    # Today's Quick Summary
    if not st.session_state.db.empty:
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_df = st.session_state.db[st.session_state.db['Date'] == today_str]
        st.metric("Today's Total Cash", f"{today_df['Price'].astype(float).sum():,.0f} TSh")
    
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
                st.rerun()
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
        
        # --- REPORT TYPE SELECTOR ---
        report_type = st.selectbox("Select Report Period", ["Daily", "Monthly", "Yearly", "Custom Range"])
        today = datetime.now().date()
        
        if report_type == "Daily":
            start_date = end_date = today
        elif report_type == "Monthly":
            start_date = today.replace(day=1)
            end_date = today
        elif report_type == "Yearly":
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:
            c1, c2 = st.columns(2)
            start_date = c1.date_input("From", today - timedelta(days=7))
            end_date = c2.date_input("To", today)

        # Filter Data
        mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
        filtered_df = df.loc[mask]

        if not filtered_df.empty:
            st.metric(f"Total Revenue ({report_type})", f"{filtered_df['Price'].astype(float).sum():,.0f} TSh")
            
            # Ranking Tabs
            tab1, tab2 = st.tabs(["🏆 Services Rank", "📦 Spares Rank"])
            
            with tab1:
                services = filtered_df[filtered_df['Category'] == "Job/Service"]
                if not services.empty:
                    st.table(services.groupby(['Item', 'Model']).size().reset_index(name='Qty').sort_values('Qty', ascending=False))
                else: st.info("No services found.")

            with tab2:
                spares = filtered_df[filtered_df['Category'] == "Spare/Good"]
                if not spares.empty:
                    st.table(spares.groupby(['Item', 'Model']).size().reset_index(name='Qty').sort_values('Qty', ascending=False))
                else: st.info("No spares found.")

            # Download this specific report
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download {report_type} Report", csv, f"report_{report_type}.csv", "text/csv")
    else:
        st.info("No data recorded yet.")

# --- PAGE 3: DATA SAFETY ---
elif page == "Data Safety":
    st.title("💾 Backup & Restore")
    
    st.subheader("1. Restore Records")
    uploaded = st.file_uploader("Upload your backup CSV", type="csv")
    if uploaded:
        uploaded_df = pd.read_csv(uploaded)
        # Smart Merge
        st.session_state.db = pd.concat([st.session_state.db, uploaded_df]).drop_duplicates().reset_index(drop=True)
        st.success("✅ Data Synced and Merged!")

    st.divider()
    st.subheader("2. Master Backup")
    master_csv = st.session_state.db.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DOWNLOAD MASTER FILE", master_csv, "MASTER_BIASHARA.csv", "text/csv")
