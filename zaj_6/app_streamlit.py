"""Panel sprzedaży w Streamlit.  Uruchomienie:  streamlit run app_streamlit.py

Streamlit przy KAŻDEJ zmianie widżetu wykonuje cały skrypt od góry do dołu.
"""
from pathlib import Path

import streamlit as st

import sales_logic as L
from generate_sales_db import create_sales_db

if not Path(L.DB_PATH).exists():
    create_sales_db(L.DB_PATH)

st.set_page_config(page_title="Panel sprzedaży", page_icon="📊", layout="wide")
st.title("📊 Panel sprzedaży")

conn = L.get_connection()
products = L.get_products(conn)
stores = L.get_stores(conn)

# --- filtry w panelu bocznym ---
with st.sidebar:
    st.header("Filtry")
    chosen = st.multiselect("Produkty", products, default=products)
    date_range = st.date_input("Zakres dat", value=(L.pd.Timestamp("2026-09-01"), L.pd.Timestamp("2026-11-30")))
    show_table = st.checkbox("Pokaż tabelę z danymi")

date_from, date_to = (list(date_range) + [None])[:2]   # w trakcie wyboru może być tylko data "od"
df = L.get_sales(conn, chosen, date_from, date_to)

if df.empty:
    st.warning("Brak danych dla wybranych filtrów.")
    st.stop()

# --- wskaźniki ---
c1, c2, c3 = st.columns(3)
c1.metric("Transakcje", f"{len(df):,}".replace(",", " "))
c2.metric("Przychód", f"{df['revenue'].sum():,.0f} zł".replace(",", " "))
c3.metric("Średnia transakcja", f"{df['revenue'].mean():,.0f} zł".replace(",", " "))

# --- wykresy ---
st.plotly_chart(L.fig_daily(df), width="stretch")
left, right = st.columns(2)
left.plotly_chart(L.fig_products(df), width="stretch")
right.plotly_chart(L.fig_map(df), width="stretch")

if show_table:
    st.dataframe(df, width="stretch", hide_index=True)

# --- formularz dodawania rekordu ---
with st.expander("➕ Dodaj sprzedaż"):
    with st.form("add_sale", clear_on_submit=True):
        product = st.selectbox("Produkt", products)
        quantity = st.number_input("Ilość", min_value=1, value=1)
        price = st.number_input("Cena [zł]", min_value=0.01, value=100.0)
        day = st.date_input("Data", value=L.pd.Timestamp("2026-11-30"))
        city = st.selectbox("Sklep", stores["city"])
        if st.form_submit_button("Dodaj"):
            store_id = int(stores.loc[stores["city"] == city, "store_id"].iloc[0])
            L.add_sale(conn, product, quantity, price, day, store_id)
            st.success(f"Dodano: {quantity} × {product} ({city})")
            st.balloons()
