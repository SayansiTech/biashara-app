import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Optimization for Samsung A10s
st.set_page_config(page_title="Biashara App", layout="centered")

# Initialize Data
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

st.title("📈 Biashara App")
st.write("Technician & Spares Tracker")

# --- RECORDING SECTION ---
with st.container():
    st.subheader("Ingiza Mauzo (One-by-One)")
    cat = st.radio("Aina", ["Job/Service", "Spare/Good"], horizontal=True)
    mod = st.text_input("Phone Model (e.g., Samsung A10s)").strip().upper()
    itm = st.text_input("Item/Service Name (e.g., Charging Port)").strip().title()
    prc = st.number_input("Price (TSh)", min_value=0, step=500)
    
    if st.button("HIFADHI (SAVE)", use_container_width=True):
        if itm and prc > 0:
            new_entry = pd.DataFrame([{
                'Date': pd.to_datetime(datetime.now().date()),
                'Model': mod if mod else "N/A",
                'Item': itm,
                'Category': cat,
                'Price': prc
            }])
            st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
            st.success(f"Imerekodiwa: {itm}")
        else:
            st.error("Tafadhali jaza jina na bei.")

st.divider()

# --- REPORTS & RANKING ---
st.subheader("📊 Ripoti na Ranking")

if not st.session_state.db.empty:
    # DATE RANGE SELECTOR
    st.write("Chagua Tarehe za Ripoti:")
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Kuanzia", datetime.now() - timedelta(days=7))
    with c2:
        end = st.date_input("Mpaka", datetime.now())

    # Filter Logic
    mask = (st.session_state.db['Date'].dt.date >= start) & (st.session_state.db['Date'].dt.date <= end)
    filtered = st.session_state.db.loc[mask]

    if not filtered.empty:
        # RANKING BY VOLUME
        st.write("🏆 **Vitu vinavyoongoza (Ranking)**")
        # Combine Item and Model for specific rank
        rank_df = filtered.groupby(['Item', 'Model']).size().reset_index(name='Quantity').sort_values('Quantity', ascending=False)
        st.table(rank_df)

        # TOTAL REVENUE
        st.metric("Jumla ya Pesa", f"{filtered['Price'].sum():,.0f} TSh")
    
    # DATA SAFETY
    st.divider()
    csv = st.session_state.db.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Backup (Save to Phone)", csv, "biashara_backup.csv", "text/csv", use_container_width=True)

    # UPLOAD OLD DATA
    uploaded = st.file_uploader("📤 Rudisha Data (Upload Backup)")
    if uploaded:
        st.session_state.db = pd.read_csv(uploaded)
        st.session_state.db['Date'] = pd.to_datetime(st.session_state.db['Date'])
        st.rerun()
else:
    st.info("Bado hujarekodi kitu kwa leo.")
