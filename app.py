"""Streamlit web interface for FreeWork Data Scraper."""

from __future__ import annotations

import logging
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from freework_scraper import __version__
from freework_scraper.export.exporter import export_jobs
from freework_scraper.models import FreeWorkJob
from freework_scraper.scraper.browser import BrowserManager
from freework_scraper.scraper.search import collect_all_job_links
from freework_scraper.scraper.job_extractor import extract_all_jobs

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FreeWork Data Scraper | SoClose",
    page_icon=":briefcase:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# SoClose Brand Colors
# ---------------------------------------------------------------------------
BRAND_PRIMARY = "#575ECF"
BRAND_LIGHT = "#7B80E0"
BRAND_DARK = "#1b1b1b"
BRAND_TEXT = "#c5c1b9"
BRAND_BG_SOFT = "#F2F4F8"

# ---------------------------------------------------------------------------
# Custom CSS — SoClose Branding
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
    .stApp {{ font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; }}
    div[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BRAND_DARK} 0%, #242424 100%);
    }}
    div[data-testid="stSidebar"] .stMarkdown h1,
    div[data-testid="stSidebar"] .stMarkdown h2,
    div[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {BRAND_LIGHT} !important;
    }}
    div[data-testid="stSidebar"] label {{
        color: {BRAND_TEXT} !important;
    }}
    .stButton > button[kind="primary"] {{
        background-color: {BRAND_PRIMARY} !important;
        border-color: {BRAND_PRIMARY} !important;
        color: white !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.32, 1);
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: {BRAND_LIGHT} !important;
        border-color: {BRAND_LIGHT} !important;
    }}
    div[data-testid="stMetric"] {{
        background: {BRAND_BG_SOFT};
        border-radius: 8px;
        padding: 12px;
        border-left: 3px solid {BRAND_PRIMARY};
    }}
    div[data-testid="stMetric"] label {{ font-size: 0.85rem !important; color: #666 !important; }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{ color: {BRAND_PRIMARY} !important; }}
    .stDownloadButton > button {{
        border-color: {BRAND_PRIMARY} !important;
        color: {BRAND_PRIMARY} !important;
        border-radius: 6px !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {BRAND_PRIMARY} !important;
        color: white !important;
    }}
    .stProgress > div > div > div {{
        background-color: {BRAND_PRIMARY} !important;
    }}
    a {{ color: {BRAND_PRIMARY} !important; }}
    .soclose-footer {{
        text-align: center;
        padding: 20px 0;
        margin-top: 40px;
        border-top: 1px solid rgba(87, 94, 207, 0.15);
        color: #999;
        font-size: 0.85rem;
    }}
    .soclose-footer a {{ color: {BRAND_PRIMARY} !important; text-decoration: none; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
for key, default in {
    "jobs": [],
    "running": False,
    "logs": [],
    "search_url": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state["logs"].append(f"[{ts}] {msg}")


# ---------------------------------------------------------------------------
# Sidebar — Search form
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title(":briefcase: FreeWork Scraper")
    st.caption(f"v{__version__} by SoClose | Selenium + BeautifulSoup")
    st.divider()

    st.subheader(":mag: Recherche")
    search_url = st.text_input(
        "URL de recherche FreeWork *",
        placeholder="https://www.free-work.com/fr/tech-it/jobs?query=python",
        help="Collez ici l'URL de recherche FreeWork avec vos filtres appliques.",
    )

    st.divider()
    st.subheader(":gear: Options")

    max_pages = st.number_input(
        "Pages max (0 = toutes)",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        help="Nombre max de pages a scraper (0 = toutes les pages).",
    )

    headless = st.checkbox(
        "Mode invisible (headless)",
        value=True,
        help="Executer Chrome en arriere-plan sans fenetre visible.",
    )

    export_format = st.selectbox(
        "Format d'export",
        ["both", "excel", "csv"],
        format_func=lambda x: {"both": "Excel + CSV", "excel": "Excel uniquement", "csv": "CSV uniquement"}[x],
        help="Choisissez le format d'export des donnees.",
    )

    st.divider()
    start_btn = st.button(
        ":rocket: Lancer le Scraping",
        use_container_width=True,
        disabled=st.session_state["running"] or not search_url.strip(),
        type="primary",
    )

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.header(":bar_chart: Resultats")

if st.session_state["jobs"]:
    jobs: list[FreeWorkJob] = st.session_state["jobs"]

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Missions", len(jobs))
    with col2:
        with_salary = sum(1 for j in jobs if j.has_salary())
        pct_salary = f"{with_salary * 100 // max(len(jobs), 1)}%"
        st.metric("Avec Salaire", f"{with_salary}", delta=pct_salary)
    with col3:
        with_remote = sum(1 for j in jobs if j.has_remote())
        st.metric("Teletravail", with_remote)
    with col4:
        ok_count = sum(1 for j in jobs if j.status == "ok")
        st.metric("Extractions OK", ok_count)

    # Data table
    rows = []
    for j in jobs:
        rows.append({
            "Titre": j.title,
            "Entreprise": j.company_name or "",
            "Localisation": j.location or j.company_location or "",
            "Teletravail": j.remote or "",
            "Salaire / TJM": j.salary or "",
            "Experience": j.experience or "",
            "Duree": j.duration or "",
            "Date debut": j.start_date or "",
            "Publication": j.publish_date or "",
            "Competences": j.skills or "",
            "Lien": j.job_url,
            "Statut": j.status,
        })
    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        height=min(600, 50 + len(df) * 35),
        column_config={
            "Lien": st.column_config.LinkColumn("Lien", display_text="Ouvrir"),
        },
    )

    # Download buttons
    st.divider()
    col_dl1, col_dl2, col_info = st.columns([1, 1, 2])

    with tempfile.TemporaryDirectory() as tmpdir:
        files = export_jobs(
            jobs,
            output_dir=tmpdir,
            fmt="both",
            search_url=st.session_state.get("search_url", search_url),
        )
        for f in files:
            data = Path(f).read_bytes()
            if f.suffix == ".csv":
                with col_dl1:
                    st.download_button(
                        ":page_facing_up: Telecharger CSV",
                        data=data,
                        file_name=f.name,
                        mime="text/csv",
                        use_container_width=True,
                    )
            elif f.suffix == ".xlsx":
                with col_dl2:
                    st.download_button(
                        ":bar_chart: Telecharger Excel",
                        data=data,
                        file_name=f.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )

    with col_info:
        st.caption(
            "L'Excel inclut des en-tetes codes par couleur, mise en evidence du salaire, "
            "liens cliquables, filtres automatiques, et une feuille resume."
        )

else:
    st.info(
        "Configurez votre recherche dans la barre laterale et cliquez **Lancer le Scraping**.\n\n"
        "Le scraper va :\n"
        "1. Ouvrir la page de recherche FreeWork\n"
        "2. Detecter toutes les pages de resultats\n"
        "3. Collecter les liens de chaque mission\n"
        "4. Extraire les details de chaque mission\n"
        "5. Exporter les resultats en Excel et/ou CSV"
    )

# ---------------------------------------------------------------------------
# Live log
# ---------------------------------------------------------------------------
if st.session_state["logs"]:
    with st.expander(f"Logs ({len(st.session_state['logs'])} entrees)", expanded=False):
        st.code("\n".join(st.session_state["logs"][-100:]))

# ---------------------------------------------------------------------------
# Scraping workflow
# ---------------------------------------------------------------------------
if start_btn:
    st.session_state["running"] = True
    st.session_state["logs"] = []
    st.session_state["jobs"] = []
    st.session_state["search_url"] = search_url

    progress_bar = st.progress(0, text="Initialisation...")
    status_text = st.empty()

    browser = None
    try:
        # Phase 1: Start browser
        _log("Demarrage du navigateur...")
        status_text.text("Demarrage du navigateur Chrome...")
        progress_bar.progress(5, text="Lancement du navigateur...")

        browser = BrowserManager(headless=headless)
        browser.start()
        _log("Navigateur demarre.")

        # Phase 2: Collect job links
        _log(f"Collecte des liens: {search_url}")
        status_text.text("Collecte des liens de missions...")
        progress_bar.progress(10, text="Navigation dans les pages de resultats...")

        def on_page_done(page_num, total_pages, links_count):
            pct = 10 + int(30 * page_num / max(total_pages, 1))
            _log(f"Page {page_num}/{total_pages}: {links_count} liens trouves")
            progress_bar.progress(min(pct, 40), text=f"Page {page_num}/{total_pages}...")

        job_links = collect_all_job_links(
            browser,
            search_url,
            max_pages=max_pages,
            on_page_done=on_page_done,
        )

        if not job_links:
            _log("Aucun lien de mission trouve.")
            status_text.warning("Aucun resultat trouve. Verifiez l'URL de recherche.")
            st.session_state["running"] = False
            st.stop()

        _log(f"{len(job_links)} liens de missions collectes.")
        progress_bar.progress(40, text=f"{len(job_links)} missions trouvees. Extraction...")

        # Phase 3: Extract job details
        _log("Extraction des details de chaque mission...")
        status_text.text("Extraction des details...")

        def on_job_done(idx, total, job):
            pct = 40 + int(50 * idx / max(total, 1))
            status_icon = "OK" if job.status == "ok" else "ERREUR"
            _log(f"[{idx}/{total}] [{status_icon}] {job.summary()}")
            progress_bar.progress(min(pct, 90), text=f"Extraction {idx}/{total}...")

        all_jobs = extract_all_jobs(
            browser,
            job_links,
            search_url=search_url,
            on_job_done=on_job_done,
        )

        _log(f"Extraction terminee: {len(all_jobs)} missions.")
        progress_bar.progress(90, text="Export des donnees...")

        # Phase 4: Export to disk
        export_jobs(
            all_jobs,
            output_dir="output",
            fmt=export_format,
            search_url=search_url,
        )

        # Save to session
        st.session_state["jobs"] = all_jobs

        progress_bar.progress(100, text="Termine !")
        ok = sum(1 for j in all_jobs if j.status == "ok")
        with_sal = sum(1 for j in all_jobs if j.has_salary())
        status_text.success(
            f"Scraping termine ! {ok} missions extraites "
            f"({with_sal} avec salaire/TJM)."
        )
        _log("Termine !")

    except Exception as exc:
        _log(f"Erreur: {exc}")
        _log(traceback.format_exc())
        status_text.error(f"Erreur: {exc}")
    finally:
        if browser:
            browser.quit()
        st.session_state["running"] = False
        st.rerun()

# ---------------------------------------------------------------------------
# Brand footer
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="soclose-footer">'
    'Built by <a href="https://soclose.co" target="_blank">SoClose</a>'
    ' &mdash; Digital Innovation Through Automation & AI'
    '</div>',
    unsafe_allow_html=True,
)
