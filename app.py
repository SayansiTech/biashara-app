import streamlit as st
import pandas as pd
from datetime import datetime

# Setup for Samsung A10s
st.set_page_config(page_title="Biashara App", layout="centered")

# 1. Start the Data Storage
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

st.title("📈 Biashara App")

# 2. Input Section
with st.container():
    st.subheader("Ingiza Mauzo")
    cat = st.radio("Aina", ["Job/Service", "Spare/Good"], horizontal=True)
    mod = st.text_input("Phone Model").upper()
    itm = st.text_input("Item/Service Name").title()
    prc = st.number_input("Price (TSh)", min_value=0, step=500)

    if st.button("HIFADHI (SAVE)", use_container_width=True):
        if itm and prc > 0:
            new_row = pd.DataFrame([{
                'Date': datetime.now().strftime("%Y-%m-%d"),
                'Model': mod if mod else "N/A",
                'Item': itm,
                'Category': cat,
                'Price': prc
            }])
            st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
            st.success(f"Imerekodiwa: {itm}")
        else:
            st.error("Jaza jina na bei!")

st.divider()

# 3. The "Anti-Disappear" Section (Data Safety)
st.subheader("💾 Sehemu ya Usalama (Save/Load)")
col1, col2 = st.columns(2)

with col1:
    # This saves your data to your Samsung's 'Downloads' folder
    csv = st.session_state.db.to_csv(index=False).encode('utf-8')
    st.download_button("DOWNLOAD BACKUP", csv, "mauzo_yangu.csv", "text/csv", use_container_width=True)

with col2:
    # This brings your data back if the phone refreshes
    uploaded_file = st.file_uploader("RESTORE DATA", type="csv")
    if uploaded_file:
        st.session_state.db = pd.read_csv(uploaded_file)
        st.success("Data imerudi!")

st.divider()

# 4. Reports
if not st.session_state.db.empty:
    st.subheader("🏆 Ranking")
    df = st.session_state.db
    # Show Top 5
    rank = df.groupby(['Item', 'Model']).size().reset_index(name='Qty').sort_values('Qty', ascending=False)
    st.table(rank.head(5))
    
    total = pd.to_numeric(df['Price']).sum()
    st.metric("JUMLA KUU", f"{total:,.0f} TSh")
else:
    st.info("Andika mauzo yako ya kwanza hapo juu.")
