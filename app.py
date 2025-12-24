import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Optimization for Samsung A10s
st.set_page_config(page_title="Biashara App Pro", layout="centered")

# --- DATA INITIALIZATION ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Date', 'Model', 'Item', 'Category', 'Price'])

st.title("📈 Biashara App Pro")

# --- 1. RECORDING SECTION ---
with st.expander("➕ Ingiza Mauzo Mapya", expanded=True):
    cat = st.radio("Aina", ["Job/Service", "Spare/Good"], horizontal=True)
    mod = st.text_input("Phone Model").upper().strip()
    itm = st.text_input("Item/Service Name").title().strip()
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
            # Add to current session
            st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
            st.success(f"Imerekodiwa: {itm}")
        else:
            st.error("Jaza jina na bei!")

st.divider()

# --- 2. DATA SAFETY (BACKUP & RESTORE) ---
# Move this up so you can Restore BEFORE checking reports
st.subheader("💾 Data Safety & Restore")
uploaded = st.file_uploader("UPLOAD LATEST BACKUP", type="csv")
if uploaded:
    uploaded_df = pd.read_csv(uploaded)
    # SMART MERGE: Combine uploaded data with current session, removing duplicates
    combined = pd.concat([st.session_state.db, uploaded_df]).drop_duplicates().reset_index(drop=True)
    st.session_state.db = combined
    st.success("✅ Data imerudishwa na kuunganishwa!")

# --- 3. REPORTS & FILTERING ---
st.subheader("📊 Ripoti na Ranking")

if not st.session_state.db.empty:
    df = st.session_state.db.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- DATE SELECTION ---
    report_type = st.selectbox("Aina ya Ripoti", ["Custom Range", "Today", "This Month", "This Year"])
    
    today = datetime.now().date()
    if report_type == "Today":
        start_date, end_date = today, today
    elif report_type == "This Month":
        start_date = today.replace(day=1)
        end_date = today
    elif report_type == "This Year":
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        c1, c2 = st.columns(2)
        start_date = c1.date_input("Kuanzia", today - timedelta(days=7))
        end_date = c2.date_input("Mpaka", today)

    # Filter Logic
    mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
    filtered_df = df.loc[mask]

    if not filtered_df.empty:
        st.metric(f"Mapato ({report_type})", f"{filtered_df['Price'].sum():,.0f} TSh")

        # --- RANKING (Both Spares & Services) ---
        st.write("🏆 **Top Performers**")
        # Combine everything for a full ranking
        full_rank = filtered_df.groupby(['Category', 'Item', 'Model']).size().reset_index(name='Qty')
        full_rank = full_rank.sort_values(['Category', 'Qty'], ascending=[True, False])
        st.dataframe(full_rank, use_container_width=True)

        # --- DOWNLOAD SPECIFIC REPORT ---
        report_csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {report_type} CSV",
            data=report_csv,
            file_name=f"biashara_{report_type}_{today}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("Hakuna data kwenye tarehe hizi.")

st.divider()
# Final Master Backup
master_csv = st.session_state.db.to_csv(index=False).encode('utf-8')
st.download_button("📥 DOWNLOAD MASTER BACKUP (Save Everything)", master_csv, "MASTER_BIASHARA.csv", "text/csv", use_container_width=True)
