# Eksploracja danych: narzędzia do interaktywnej eksploracji (3 h)

| Plik | Do czego |
|---|---|
| `zaj_narzedzia_eksploracji.typ` / `.pdf` | slajdy (Typst + Polylux 0.4) |
| `ED_narzedzia_eksploracji.ipynb` | notebook dla studentów (Colab), z `# TODO` i testami `assert` |
| `ED_narzedzia_eksploracji_rozwiazanie.ipynb` | to samo z rozwiązaniami |
| `generate_sales_db.py` | generator `sales.db` (tabele `stores` + `sales`, ok. 2450 transakcji, 3 ukryte błędy) |
| `sales_logic.py` | wspólna warstwa logiki (zapytania + wykresy Plotly) dla aplikacji demo |
| `app_streamlit.py` | demo: `streamlit run app_streamlit.py` |
| `app_panel.py` | demo: `panel serve app_panel.py --show` |
| `demo_mercury.ipynb` | demo: `mercury` w tym katalogu (podgląd 🎉 w JupyterLab) |

Notebook jest samowystarczalny: generator bazy jest w pierwszej komórce, więc w Colabie nic nie trzeba wgrywać.
Aplikacje demo same tworzą `sales.db`, jeśli go nie ma.

Instalacja do demo (lokalnie):

```
pip install pandas plotly duckdb ipywidgets streamlit panel mercury
```

Ukryte błędy w danych (zadanie A.5):
- Laptop za 32 000 zł (literówka w cenie),
- Mysz z ilością −5,
- 400 monitorów w jednej transakcji (9.11), która tworzy wyraźny pik na wykresie dziennym i zawyża poniedziałki w zadaniu B.1.
