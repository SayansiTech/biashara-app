import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

# Optimization for Samsung A10s
st.set_page_config(page_title="Biashara App", layout="centered")

# --- CLOUD CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# We tell the app exactly where the URL is
url = st.secrets["public_gsheets_url"]

try:
    # Use the secret URL directly to read
    df_cloud = conn.read(spreadsheet=url, ttl="0s")
except Exception as e:
    # If the sheet is empty or has an issue, start fresh
    df_cloud = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

st.title("📈 Biashara App")

# --- RECORDING SECTION ---
with st.container():
    st.subheader("Ingiza Mauzo (One-by-One)")
    cat = st.radio("Aina", ["Job/Service", "Spare/Good"], horizontal=True)
    mod = st.text_input("Phone Model").strip().upper()
    itm = st.text_input("Item/Service Name").strip().title()
    prc = st.number_input("Price (TSh)", min_value=0, step=500)
    
    if st.button("HIFADHI (SAVE)", use_container_width=True):
        if itm and prc > 0:
            new_entry = pd.DataFrame([{
                'Date': datetime.now().strftime("%Y-%m-%d"),
                'Model': mod if mod else "N/A",
                'Item': itm,
                'Category': cat,
                'Price': prc
            }])
            
            updated_df = pd.concat([df_cloud, new_entry], ignore_index=True)
            # Update using the specific URL
            conn.update(spreadsheet=url, data=updated_df)
            
            st.success(f"Imefanikiwa! {itm} imehifadhiwa.")
            st.rerun()
        else:
            st.error("Tafadhali jaza jina na bei.")

st.divider()

# --- REPORTS ---
if not df_cloud.empty:
    df_cloud['Date'] = pd.to_datetime(df_cloud['Date'])
    st.write("🏆 **Top Repairs & Spares**")
    rank_df = df_cloud.groupby(['Item', 'Model']).size().reset_index(name='Qty').sort_values('Qty', ascending=False)
    st.table(rank_df)
    st.metric("Jumla ya Pesa", f"{df_cloud['Price'].sum():,.0f} TSh")
else:
    st.info("Bado hakuna data. Rekodi mauzo ya kwanza!")
