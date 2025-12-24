import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Biashara Pro", layout="centered")

# --- CUSTOM THEME (Fixed) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F0F2F6; }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #004AAD;
        color: white;
        font-weight: bold;
        border: none;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        color: #004AAD;
        font-size: 24px;
    }
    
    /* Input Boxes */
    .stTextInput>div>div>input {
        background-color: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Data
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

# --- SIDEBAR ---
st.sidebar.header("🛠️ Shop Menu")
page = st.sidebar.selectbox("Choose Action:", ["New Sale/Job", "View Reports", "Settings & Backup"])

# --- PAGE 1: ENTRY ---
if page == "New Sale/Job":
    st.title("🛒 Daily Recording")
    
    # Quick Summary for Today
    if not st.session_state.db.empty:
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_total = st.session_state.db[st.session_state.db['Date'] == today_str]['Price'].astype(float).sum()
        st.metric("Today's Total Cash", f"{today_total:,.0f} TSh")
    
    with st.container():
        cat = st.radio("Aina (Type)", ["Job/Service", "Spare/Good"], horizontal=True)
        mod = st.text_input("Phone Model").upper().strip()
        itm = st.text_input("Item/Service Name").title().strip()
        prc = st.number_input("Price (TSh)", min_value=0, step=500)
        
        if st.button("HIFADHI (SAVE TRANSACTION)"):
            if itm and prc > 0:
                new_entry = pd.DataFrame([{
                    'Date': datetime.now().strftime("%Y-%m-%d"),
                    'Model': mod if mod else "N/A",
                    'Item': itm,
                    'Category': cat,
                    'Price': prc
                }])
                st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
                st.success(f"✅ Recorded: {itm}")
                st.rerun()
            else:
                st.error("Please fill Name and Price!")

    st.divider()
    if st.button("🗑️ Delete Last Mistake"):
        if not st.session_state.db.empty:
            st.session_state.db = st.session_state.db[:-1]
            st.warning("Last entry deleted.")
            st.rerun()

# --- PAGE 2: REPORTS ---
elif page == "View Reports":
    st.title("📊 Business Analysis")
    
    if not st.session_state.db.empty:
        df = st.session_state.db.copy()
        df['Date'] = pd.to_datetime(df['Date'])
        
        report_type = st.radio("Show for:", ["Today", "This Month", "All Time"], horizontal=True)
        today = datetime.now().date()
        
        if report_type == "Today":
            filtered = df[df['Date'].dt.date == today]
        elif report_type == "This Month":
            filtered = df[df['Date'].dt.month == today.month]
        else:
            filtered = df

        st.metric(f"Revenue ({report_type})", f"{filtered['Price'].astype(float).sum():,.0f} TSh")
        
        st.subheader("🏆 Ranking")
        # Combine items to see what brings most money/frequency
        rank = filtered.groupby(['Item', 'Model']).size().reset_index(name='Quantity')
        st.table(rank.sort_values('Quantity', ascending=False).head(10))
    else:
        st.info("No data yet. Go to 'New Sale' to start.")

# --- PAGE 3: BACKUP ---
elif page == "Settings & Backup":
    st.title("💾 Data Security")
    
    st.subheader("1. Restore Records")
    uploaded = st.file_uploader("Upload your backup CSV", type="csv")
    if uploaded:
        uploaded_df = pd.read_csv(uploaded)
        # Combine and remove duplicates
        st.session_state.db = pd.concat([st.session_state.db, uploaded_df]).drop_duplicates().reset_index(drop=True)
        st.success("✅ Records Synced Successfully!")

    st.divider()
    st.subheader("2. Download Backup")
    csv_data = st.session_state.db.to_csv(index=False).encode('utf-8')
    st.download_button("📥 DOWNLOAD MASTER FILE", csv_data, "BIASHARA_MASTER.csv", "text/csv")
