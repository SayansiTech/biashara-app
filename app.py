import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
import gspread

# Optimization for Samsung A10s
st.set_page_config(page_title="Biashara App", layout="centered")

# --- CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["public_gsheets_url"]

# 1. READ DATA (To show the Ranking)
try:
    df_cloud = conn.read(spreadsheet=url, ttl="0s")
except:
    df_cloud = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

st.title("📈 Biashara App")

# --- RECORDING SECTION ---
with st.container():
    st.subheader("Ingiza Mauzo")
    cat = st.radio("Aina", ["Job/Service", "Spare/Good"], horizontal=True)
    mod = st.text_input("Phone Model").strip().upper()
    itm = st.text_input("Item/Service Name").strip().title()
    prc = st.number_input("Price (TSh)", min_value=0, step=500)
    
    if st.button("HIFADHI (SAVE)", use_container_width=True):
        if itm and prc > 0:
            # Prepare the row
            new_row = [
                datetime.now().strftime("%Y-%m-%d"),
                mod if mod else "N/A",
                itm,
                cat,
                prc
            ]
            
            try:
                # Direct Write to Google Sheets via CSV export/import logic
                # This bypasses the 'UnsupportedOperationError'
                updated_df = pd.concat([df_cloud, pd.DataFrame([new_row], columns=df_cloud.columns)], ignore_index=True)
                conn.update(spreadsheet=url, data=updated_df)
                st.success(f"Imerekodiwa! {itm}")
                st.rerun()
            except Exception as e:
                st.error("Sheet Permission Error: Make sure the Sheet is set to 'Anyone with link can EDITOR'")
        else:
            st.error("Jaza jina na bei!")

st.divider()

# --- REPORTS ---
if not df_cloud.empty:
    st.write("🏆 **Top Repairs & Spares**")
    # Clean price column to numbers
    df_cloud['Price'] = pd.to_numeric(df_cloud['Price'], errors='coerce').fillna(0)
    rank_df = df_cloud.groupby(['Item', 'Model']).size().reset_index(name='Qty').sort_values('Qty', ascending=False)
    st.table(rank_df.head(10))
    st.metric("Jumla ya Pesa", f"{df_cloud['Price'].sum():,.0f} TSh")
