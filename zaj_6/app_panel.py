"""Panel sprzedaży w Panel (HoloViz).  Uruchomienie:  panel serve app_panel.py --show

Panel działa reaktywnie: pn.bind wiąże funkcję z widżetami i wywołuje ją
ponownie tylko wtedy, gdy zmieni się któryś z jej argumentów.
Ten sam kod działa też w komórce notebooka (Jupyter, Colab).
"""
from pathlib import Path

import pandas as pd
import panel as pn

import sales_logic as L
from generate_sales_db import create_sales_db

pn.extension("plotly", sizing_mode="stretch_width")

if not Path(L.DB_PATH).exists():
    create_sales_db(L.DB_PATH)

conn = L.get_connection()
products = L.get_products(conn)

# --- widżety ---
w_products = pn.widgets.MultiChoice(name="Produkty", options=products, value=products)
w_dates = pn.widgets.DateRangePicker(
    name="Zakres dat",
    value=(pd.Timestamp("2026-09-01").date(), pd.Timestamp("2026-11-30").date()),
)


# --- funkcje reagujące na widżety ---
def dashboard(chosen, dates):
    df = L.get_sales(conn, chosen, *dates)
    if df.empty:
        return pn.pane.Alert("Brak danych dla wybranych filtrów.", alert_type="warning")
    kpi = pn.Row(
        pn.indicators.Number(name="Transakcje", value=len(df), format="{value:,.0f}"),
        pn.indicators.Number(name="Przychód [zł]", value=df["revenue"].sum(), format="{value:,.0f}"),
    )
    return pn.Column(
        kpi,
        pn.pane.Plotly(L.fig_daily(df)),
        pn.Row(pn.pane.Plotly(L.fig_products(df)), pn.pane.Plotly(L.fig_map(df))),
    )


pn.template.FastListTemplate(
    title="Panel sprzedaży",
    sidebar=[w_products, w_dates],
    main=[pn.bind(dashboard, w_products, w_dates)],
).servable()
