import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

# Optimization for Samsung A10s
st.set_page_config(page_title="Biashara App", layout="centered")

# --- NEW: CLOUD CONNECTION ---
# This pulls data from Google Sheets so it doesn't disappear on refresh
conn = st.connection("gsheets", type=GSheetsConnection)
df_cloud = conn.read(ttl="0s") # ttl=0 means always get newest data

st.title("📈 Biashara App (Cloud Sync)")
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
            # 1. Create the new row
            new_entry = pd.DataFrame([{
                'Date': datetime.now().strftime("%Y-%m-%d"),
                'Model': mod if mod else "N/A",
                'Item': itm,
                'Category': cat,
                'Price': prc
            }])
            
            # 2. Merge with existing cloud data
            updated_df = pd.concat([df_cloud, new_entry], ignore_index=True)
            
            # 3. PUSH TO CLOUD (Google Sheets)
            conn.update(data=updated_df)
            
            st.success(f"Imerekodiwa Cloud: {itm}")
            st.rerun() # Refresh to show new ranking
        else:
            st.error("Tafadhali jaza jina na bei.")

st.divider()

# --- REPORTS & RANKING ---
st.subheader("📊 Ripoti na Ranking")

# Use df_cloud for reporting so it's always permanent
if not df_cloud.empty:
    # Ensure Date column is in correct format
    df_cloud['Date'] = pd.to_datetime(df_cloud['Date'])
    
    st.write("Chagua Tarehe za Ripoti:")
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Kuanzia", datetime.now() - timedelta(days=7))
    with c2:
        end = st.date_input("Mpaka", datetime.now())

    # Filter Logic
    mask = (df_cloud['Date'].dt.date >= start) & (df_cloud['Date'].dt.date <= end)
    filtered = df_cloud.loc[mask]

    if not filtered.empty:
        st.write("🏆 **Vitu vinavyoongoza (Ranking)**")
        rank_df = filtered.groupby(['Item', 'Model']).size().reset_index(name='Quantity').sort_values('Quantity', ascending=False)
        st.table(rank_df)

        st.metric("Jumla ya Pesa", f"{filtered['Price'].sum():,.0f} TSh")
    
    st.divider()
    # Backup still available for extra safety
    csv = df_cloud.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Backup", csv, "biashara_backup.csv", "text/csv", use_container_width=True)

else:
    st.info("Bado hujarekodi kitu. Data itatokea hapa ukishaanza kuandika.")
