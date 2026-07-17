# =========================================================
# SEL 42: DASHBOARD PERBANDINGAN PARIWISATA
# Desa Wae Rebo vs Taman Nasional Komodo
# =========================================================
import json, math
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import streamlit as st
import folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_folium import st_folium
from wordcloud import WordCloud

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Perbandingan Pariwisata",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------
# CSS PROFESIONAL
# ----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F0F4F8 !important; }

[data-testid="stSidebar"] {
    background: #1B3A6B !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebarUserContent"] { padding: 0 10px !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    border-radius: 8px !important;
    padding: 7px 10px !important;
    font-size: 0.87rem !important;
    cursor: pointer !important;
    transition: background .15s !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,.12) !important;
}
[data-testid="stSidebar"] .stRadio label span { color: #E2E8F0 !important; font-size: 0.87rem !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }

.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1400px !important; }

.dash-header {
    background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 100%);
    border-radius: 16px;
    padding: 22px 32px;
    margin-bottom: 24px;
    min-height: 84px;
    box-sizing: border-box;
    display: flex; flex-direction: column; justify-content: center;
}
.dash-header-title { color: white; font-size: 1.5rem; font-weight: 800; margin: 0; line-height: 1.25; }
.dash-header-sub { color: rgba(255,255,255,.75); font-size: 0.85rem; margin: 6px 0 0; line-height: 1.4; }

.kpi-row { display: flex; gap: 16px; margin-bottom: 24px; }
.kpi-card {
    flex: 1; background: white; border-radius: 14px;
    padding: 20px 22px; border-top: 5px solid;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
    box-sizing: border-box; min-height: 152px;
    position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute;
    right: -20px; bottom: -20px;
    width: 80px; height: 80px;
    border-radius: 50%; background: rgba(0,0,0,.03);
}
.kpi-card.blue { border-color: #2563EB; }
.kpi-card.red  { border-color: #EF4444; }
.kpi-card.green{ border-color: #10B981; }
.kpi-card.amber{ border-color: #F59E0B; }
.kpi-label  { font-size: 0.78rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.kpi-value  { font-size: 2rem; font-weight: 800; color: #0F172A; line-height: 1.1; margin: 4px 0 2px; }
.kpi-sub    { font-size: 0.8rem; color: #64748B; }

.sec-card {
    background: white; border-radius: 14px;
    padding: 22px 26px; margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,.05);
    box-sizing: border-box;
}
.sec-title {
    font-size: 1.05rem; font-weight: 700; color: #0F172A;
    margin: 0 0 4px; display: flex; align-items: center; gap: 8px;
}
.sec-sub { font-size: 0.82rem; color: #64748B; margin: 0 0 18px; }

hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }

[data-testid="stDataFrame"] {
    border-radius: 10px !important; overflow: hidden;
    box-shadow: 0 1px 6px rgba(0,0,0,.06) !important;
}

[data-testid="stMetric"] {
    background: white; border-radius: 12px; padding: 14px 18px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.06); border-left: 4px solid #2563EB;
}

.nav-section {
    font-size: 0.68rem; font-weight: 700; color: #64748B;
    letter-spacing: .1em; text-transform: uppercase;
    padding: 16px 4px 6px; margin-top: 4px;
}

button[data-baseweb="tab"] {
    font-size: 0.88rem !important; font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #2563EB !important;
    border-bottom: 3px solid #2563EB !important;
}

.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# MATPLOTLIB GLOBAL STYLE
# ----------------------------------------------------------
matplotlib.rcParams.update({
    'figure.facecolor': 'white', 'axes.facecolor': '#F8FAFC',
    'axes.edgecolor': '#E2E8F0', 'axes.labelcolor': '#334155',
    'xtick.color': '#64748B', 'ytick.color': '#64748B',
    'text.color': '#0F172A', 'grid.color': '#E2E8F0',
    'grid.linewidth': 0.8, 'font.family': 'DejaVu Sans',
})

# ----------------------------------------------------------
# LOAD DATA (dengan error handling)
# ----------------------------------------------------------
try:
    with open('dashboard_data.json', 'r', encoding='utf-8') as f:
        DATA = json.load(f)
except FileNotFoundError:
    st.error("❌ File `dashboard_data.json` tidak ditemukan. Pastikan file ada di folder yang sama dengan script ini.")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"❌ File `dashboard_data.json` tidak valid (JSON error): {e}")
    st.stop()

ringkasan        = DATA.get('ringkasan', [])
bridge           = DATA.get('bridge', [])
lokasi_list      = DATA.get('lokasi_list', [])
data_rating      = DATA.get('rating', {})
data_klasifikasi = DATA.get('klasifikasi', {})
data_klaster     = DATA.get('klaster', {})
data_topik       = DATA.get('topik', {})
data_trending    = DATA.get('trending', {})
data_centrality  = DATA.get('centrality', {})
data_ulasan      = DATA.get('ulasan_detail', {})
data_temporal    = DATA.get('temporal', {})

LOC_COLOR = {'Desa Wae Rebo': '#2563EB', 'Taman Nasional Komodo': '#EF4444'}
for i, lok in enumerate(lokasi_list):
    if lok not in LOC_COLOR:
        LOC_COLOR[lok] = ['#2563EB', '#EF4444', '#10B981', '#F59E0B'][i % 4]

COLORS_TOPIC = ['#4338CA', '#0891B2', '#D97706', '#059669', '#DC2626', '#7C3AED', '#DB2777', '#2563EB']

# ----------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="background:rgba(255,255,255,.07);border-radius:12px;padding:16px;margin-bottom:8px;">
        <div style="font-size:1.05rem;font-weight:800;color:white;line-height:1.3;">DASHBOARD PERBANDINGAN PARIWISATA</div>
        <div style="font-size:0.72rem;color:#93C5FD;margin-top:4px;">Analisis Perbandingan Destinasi</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">NAVIGASI UTAMA</div>', unsafe_allow_html=True)

    MENU = {
        "Beranda & Peta"               : "beranda",
        "Analisis Sentimen"            : "sentimen",
        "Model Klasifikasi"            : "klasifikasi",
        "Klasterisasi"                 : "klaster",
        "Radar Perbandingan"           : "radar",
        "Topic Modeling (LDA)"         : "topik",
        "Trending Topik"               : "trending",
        "WordCloud Masalah"            : "wordcloud",
        "Jaringan Antar Destinasi"     : "jaringan",
    }

    halaman_label = st.radio("", list(MENU.keys()), label_visibility="collapsed")
    halaman = MENU[halaman_label]

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem;color:#64748B;text-align:center;line-height:1.6;">
        Universitas Budi Luhur<br>
        Teknik Informatika · 2025<br>
        <span style="color:#93C5FD;">Text Mining & Sentiment Analysis</span>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------
def page_header(title, subtitle=""):
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-header-title">{title}</div>
        <div class="dash-header-sub">{subtitle if subtitle else "Analisis Ulasan Google Maps &middot; Desa Wae Rebo vs Taman Nasional Komodo"}</div>
    </div>
    """, unsafe_allow_html=True)

def kpi_row():
    cols = st.columns(len(ringkasan))
    for col, r in zip(cols, ringkasan):
        neg_pct = r.get('persen_negatif', 0)
        color = "red" if neg_pct > 50 else "green"
        col.markdown(f"""
        <div class="kpi-card {color}" style="margin-bottom:4px">
            <div class="kpi-label">{r.get('lokasi', '-')}</div>
            <div style="display:flex;align-items:baseline;gap:12px;margin:6px 0 4px">
                <div class="kpi-value">{neg_pct}%</div>
                <div style="font-size:0.78rem;color:#64748B">negatif</div>
            </div>
            <div style="font-size:0.8rem;color:#475569;margin-bottom:8px">
                dari <b>{r.get('total_ulasan', 0):,}</b> total ulasan
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:0.75rem">
                <span style="background:#D1FAE5;color:#059669;padding:2px 7px;border-radius:99px;font-weight:600">✅ {r.get('jumlah_positif', 0)} positif</span>
                <span style="background:#FEE2E2;color:#DC2626;padding:2px 7px;border-radius:99px;font-weight:600">❌ {r.get('jumlah_negatif', 0)} negatif</span>
                <span style="background:#F1F5F9;color:#64748B;padding:2px 7px;border-radius:99px;font-weight:600">➖ {r.get('jumlah_netral', 0)} netral</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def fig_style(fig, ax=None):
    if ax:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()

def safe_float(val, default=0.0):
    """Aman konversi ke float."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def safe_int(val, default=0):
    """Aman konversi ke int."""
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


# ══════════════════════════════════════════════════════════
# HALAMAN 1: BERANDA & PETA
# ══════════════════════════════════════════════════════════
if halaman == "beranda":
    page_header("RANCANGAN DASHBOARD PERBANDINGAN PARIWISATA",
                "Analisis Ulasan Google Maps · Desa Wae Rebo vs Taman Nasional Komodo · Nusa Tenggara Timur")
    kpi_row()

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📍 Peta Lokasi Destinasi Wisata</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">🟢 Hijau = positif dominan &nbsp;|&nbsp; 🔴 Merah = negatif &gt;50%</div>', unsafe_allow_html=True)

    try:
        peta = folium.Map(
            location=[sum(r.get('lat', -8.5) for r in ringkasan)/max(len(ringkasan), 1),
                      sum(r.get('lon', 120) for r in ringkasan)/max(len(ringkasan), 1)],
            zoom_start=9, tiles="CartoDB positron"
        )
        for r in ringkasan:
            warna_m = "green" if r.get('status_warna') == "Hijau" else "red"
            popup = (f"<b style='font-family:Inter'>{r.get('lokasi', '')}</b><br>"
                     f"📝 Total: {r.get('total_ulasan', 0)}<br>"
                     f"✅ Positif: {r.get('jumlah_positif', 0)}<br>"
                     f"❌ Negatif: {r.get('jumlah_negatif', 0)}<br>"
                     f"% Negatif: <b>{r.get('persen_negatif', 0)}%</b>")
            folium.Marker(
                [r.get('lat', -8.5), r.get('lon', 120)],
                popup=folium.Popup(popup, max_width=240),
                tooltip=r.get('lokasi', ''),
                icon=folium.Icon(color=warna_m, icon='info-sign')
            ).add_to(peta)
        st_folium(peta, width=None, height=430)
    except Exception as e:
        st.error(f"Gagal memuat peta: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Ringkasan perbandingan tabel
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📋 Ringkasan Perbandingan</div>', unsafe_allow_html=True)
    df_ring = pd.DataFrame([{
        'Destinasi': r.get('lokasi', '-'),
        'Total Ulasan': r.get('total_ulasan', 0),
        'Positif': r.get('jumlah_positif', 0),
        'Negatif': r.get('jumlah_negatif', 0),
        'Netral': r.get('jumlah_netral', 0),
        '% Negatif': f"{r.get('persen_negatif', 0)}%",
        'Status': "⚠️ Perlu Perhatian" if r.get('persen_negatif', 0) > 50 else "✅ Cukup Baik",
    } for r in ringkasan])
    st.dataframe(df_ring, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HALAMAN 2: SENTIMEN & RATING
# ══════════════════════════════════════════════════════════
elif halaman == "sentimen":
    page_header("Analisis Sentimen & Distribusi Rating")
    kpi_row()

    # ========== DISTRIBUSI SENTIMEN ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📊 Jumlah Sentimen per Destinasi</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Positif = Rating 4-5⭐ · Negatif = Rating 1-2⭐ · Netral = Rating 3⭐</div>', unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)
    sentimen_labels = ['Positif', 'Negatif', 'Netral']
    sentimen_colors = ['#10B981', '#EF4444', '#94A3B8']

    for col, r in zip([col_chart1, col_chart2], ringkasan):
        with col:
            lokasi = r.get('lokasi', '')
            values = [r.get('jumlah_positif', 0), r.get('jumlah_negatif', 0), r.get('jumlah_netral', 0)]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sentimen_labels, y=values,
                marker_color=sentimen_colors,
                text=values, textposition='outside',
                textfont=dict(size=15, color='#0F172A', family='Inter', weight='bold'),
                hovertemplate=[
                    f'<b>{lokasi}</b><br>Sentimen: {s}<br>Jumlah: {v} ulasan<extra></extra>'
                    for s, v in zip(sentimen_labels, values)
                ],
                marker_line_color='white', marker_line_width=2.5
            ))

            max_val = max(values) if max(values) > 0 else 10
            fig.update_layout(
                title=dict(text=lokasi, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center', y=0.95),
                height=380, plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family='Inter', size=12, color='#334155'),
                xaxis=dict(tickfont=dict(size=12, color='#475569', family='Inter'), showgrid=False, showline=False, zeroline=False),
                yaxis=dict(title='Jumlah Ulasan', titlefont=dict(size=11, color='#64748B', family='Inter'), tickfont=dict(size=11, color='#64748B'), gridcolor='#E2E8F0', gridwidth=1, showline=False, zeroline=False, range=[0, max_val * 1.2]),
                margin=dict(l=50, r=20, t=50, b=50),
                hoverlabel=dict(bgcolor='#0F172A', font=dict(color='white', size=13, family='Inter'), bordercolor='#0F172A'),
                bargap=0.35
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown('</div>', unsafe_allow_html=True)

    # ========== CONTOH ULASAN PER SENTIMEN ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Sentimen</div>', unsafe_allow_html=True)

    tab_positif, tab_negatif, tab_netral = st.tabs(["🟢 Positif", "🔴 Negatif", "🟡 Netral"])

    for tab, sentimen_key, sentimen_label in [
        (tab_positif, 'contoh_positif', 'Positif'),
        (tab_negatif, 'contoh_negatif', 'Negatif'),
        (tab_netral,  'contoh_netral',  'Netral')
    ]:
        with tab:
            col_tabel1, col_tabel2 = st.columns(2)
            for col, r in zip([col_tabel1, col_tabel2], ringkasan):
                with col:
                    lokasi = r.get('lokasi', '')
                    contoh_list = data_ulasan.get(lokasi, {}).get(sentimen_key, [])
                    st.markdown(f'**{lokasi}**')
                    if contoh_list:
                        rows = []
                        for ulasan in contoh_list[:5]:
                            rating = safe_int(ulasan.get('rating', 0))
                            stars = '⭐' * rating
                            rows.append({
                                'Penulis': ulasan.get('author', 'Anonim'),
                                'Rating': stars,
                                'Tanggal': ulasan.get('date', ''),
                                'Ulasan': ulasan.get('review', 'Tidak ada teks')
                            })
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    else:
                        st.info(f"Tidak ada contoh ulasan {sentimen_label.lower()}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ========== DISTRIBUSI RATING BINTANG ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⭐ Distribusi Rating Bintang</div>', unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)
    warna_bintang = {1: '#EF4444', 2: '#F97316', 3: '#F59E0B', 4: '#84CC16', 5: '#10B981'}

    for col, lok in zip([col_chart1, col_chart2], lokasi_list):
        with col:
            try:
                rc = data_rating.get(lok, {})
                if rc:
                    ratings = sorted([safe_int(r) for r in rc.keys()])
                    values = [safe_int(rc.get(str(r), 0)) for r in ratings]
                    colors = [warna_bintang.get(r, '#94A3B8') for r in ratings]
                    labels = [f'{r} ⭐' for r in ratings]

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=labels, y=values, marker_color=colors,
                        text=values, textposition='outside',
                        textfont=dict(size=12, color='#0F172A', family='Inter', weight='bold'),
                        hovertemplate=[f'<b>{lok}</b><br>Rating: {r} ⭐<br>Jumlah: {v} ulasan<extra></extra>' for r, v in zip(ratings, values)],
                        marker_line_color='white', marker_line_width=2.5
                    ))
                    max_val = max(values) if max(values) > 0 else 10
                    fig.update_layout(
                        title=dict(text=lok, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center', y=0.95),
                        height=380, plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Inter', size=12, color='#334155'),
                        xaxis=dict(tickfont=dict(size=12, color='#475569', family='Inter'), showgrid=False, showline=False, zeroline=False),
                        yaxis=dict(title='Jumlah Ulasan', titlefont=dict(size=11, color='#64748B'), gridcolor='#E2E8F0', gridwidth=1, showline=False, zeroline=False, range=[0, max_val * 1.2]),
                        margin=dict(l=50, r=20, t=50, b=50), bargap=0.35
                    )
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info("Data rating tidak tersedia.")
            except Exception as e:
                st.error(f"Gagal memuat rating {lok}: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ========== CONTOH ULASAN PER RATING BINTANG ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Rating Bintang</div>', unsafe_allow_html=True)

    tab_1, tab_2, tab_3, tab_4, tab_5 = st.tabs(["⭐ 1", "⭐⭐ 2", "⭐⭐⭐ 3", "⭐⭐⭐⭐ 4", "⭐⭐⭐⭐⭐ 5"])

    rating_tabs = [
        (tab_1, "rating_1", "1 Bintang"), (tab_2, "rating_2", "2 Bintang"),
        (tab_3, "rating_3", "3 Bintang"), (tab_4, "rating_4", "4 Bintang"),
        (tab_5, "rating_5", "5 Bintang"),
    ]

    for tab, rating_key, rating_label in rating_tabs:
        with tab:
            col_tabel1, col_tabel2 = st.columns(2)
            for col, r in zip([col_tabel1, col_tabel2], ringkasan):
                with col:
                    lokasi = r.get('lokasi', '')
                    contoh_list = data_ulasan.get(lokasi, {}).get(rating_key, [])
                    st.markdown(f'**{lokasi}**')
                    if contoh_list:
                        rows = []
                        for ulasan in contoh_list[:5]:
                            rating = safe_int(ulasan.get('rating', 0))
                            stars = '⭐' * rating
                            rows.append({
                                'Penulis': ulasan.get('author', 'Anonim'),
                                'Rating': stars,
                                'Tanggal': ulasan.get('date', ''),
                                'Ulasan': ulasan.get('review', 'Tidak ada teks')
                            })
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    else:
                        st.info(f"Tidak ada contoh ulasan {rating_label.lower()}")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HALAMAN 3: KLASIFIKASI  (FIX: session_state untuk button)
# ══════════════════════════════════════════════════════════
elif halaman == "klasifikasi":
    page_header("Perbandingan Akurasi Model Klasifikasi",
                "SVM · Random Forest · Naive Bayes — per destinasi wisata")
    kpi_row()

    if data_klasifikasi:
        model_names = data_klasifikasi.get('model_names', [])
        akurasi = data_klasifikasi.get('akurasi', {})
        detail_data = data_klasifikasi.get('detail', {})

        # ===== FIX BUG #2: Gunakan session_state agar pilihan model persist =====
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = model_names[0] if model_names else None

        # ========== 1. PERBANDINGAN AKURASI KESELURUHAN ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Perbandingan Akurasi Antar Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Perbandingan performa ketiga model ML pada kedua lokasi</div>', unsafe_allow_html=True)

        if model_names and akurasi:
            fig_overall = go.Figure()
            for lok in lokasi_list:
                if lok in akurasi:
                    vals = [safe_float(akurasi[lok].get(m, 0)) for m in model_names]
                    fig_overall.add_trace(go.Bar(
                        name=lok, x=model_names, y=vals,
                        marker_color=LOC_COLOR.get(lok, '#2563EB'),
                        text=[f"{v:.2f}%" for v in vals], textposition='outside',
                        textfont=dict(size=14, family='Inter', weight='bold'),
                        hovertemplate=f'<b>{lok}</b><br>Model: %{{x}}<br>Akurasi: %{{y:.2f}}%<extra></extra>'
                    ))

            fig_overall.update_layout(
                barmode='group', height=420, plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family='Inter', size=12, color='#334155'),
                yaxis=dict(title='Akurasi (%)', range=[0, 115], gridcolor='#E2E8F0', gridwidth=1),
                xaxis=dict(title='', showgrid=False, showline=False),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                margin=dict(l=50, r=20, t=60, b=50), bargap=0.3
            )
            st.plotly_chart(fig_overall, use_container_width=True, config={'displayModeBar': False})

            rows_akurasi = []
            for m in model_names:
                row = {'Model': m}
                for lok in lokasi_list:
                    if lok in akurasi:
                        row[lok] = f"{safe_float(akurasi[lok].get(m, 0)):.2f}%"
                rows_akurasi.append(row)
            st.dataframe(pd.DataFrame(rows_akurasi), use_container_width=True, hide_index=True, height=120)
        else:
            st.info("Data akurasi keseluruhan tidak tersedia.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 2. EVALUASI DETAIL PER MODEL ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Evaluasi Detail per Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Klik tombol algoritma di bawah untuk melihat Classification Report & Confusion Matrix</div>', unsafe_allow_html=True)

        model_icons = {'SVM': '🧠', 'Random Forest': '🌲', 'Naive Bayes': '📊'}
        model_colors = {'SVM': '#2563EB', 'Random Forest': '#10B981', 'Naive Bayes': '#F59E0B'}
        model_cmaps = {'SVM': 'Blues', 'Random Forest': 'Greens', 'Naive Bayes': 'YlOrBr'}

        # ===== FIX: Tombol pakai session_state =====
        btn_cols = st.columns(len(model_names))
        for idx, model_name in enumerate(model_names):
            with btn_cols[idx]:
                icon = model_icons.get(model_name, '🤖')
                is_selected = (st.session_state.selected_model == model_name)
                # FIX BUG #5: Hindari parameter type yang bisa error di Streamlit lama
                if st.button(f"{icon} {model_name}", key=f"btn_{model_name}", use_container_width=True):
                    st.session_state.selected_model = model_name
                    st.rerun()

        selected_model = st.session_state.selected_model

        # ===== FIX BUG #3: Cek keberadaan key sebelum akses =====
        if selected_model and selected_model in detail_data:
            model_detail = detail_data[selected_model]
            icon = model_icons.get(selected_model, '🤖')
            color = model_colors.get(selected_model, '#2563EB')
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}15, {color}05);border-left: 5px solid {color};border-radius: 0 12px 12px 0;padding: 15px 20px;margin-bottom: 25px;">
                <div style="font-size:1.15rem;font-weight:700;color:{color};margin:0;">{icon} Detail Evaluasi: {selected_model}</div>
                <div style="font-size:0.82rem;color:#64748B;margin-top:4px;">Classification Report & Confusion Matrix</div>
            </div>
            """, unsafe_allow_html=True)

            cmap_name = model_cmaps.get(selected_model, 'Blues')
            cols_dest = st.columns(len(lokasi_list))
            report_data_for_f1 = {}

            for col_idx, lok in enumerate(lokasi_list):
                with cols_dest[col_idx]:
                    lok_color = LOC_COLOR.get(lok, '#2563EB')
                    st.markdown(f"""
                    <div style="background:{lok_color}10;border-radius:10px;padding:12px 16px;margin-bottom:15px;border:1px solid {lok_color}30;">
                        <div style="font-size:0.95rem;font-weight:700;color:{lok_color};margin:0;">📍 {lok}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    loc_detail = model_detail.get(lok, {})

                    labels_raw = loc_detail.get('labels', ['Negatif', 'Netral', 'Positif'])
                    if isinstance(labels_raw, list):
                        labels_asli = [str(l).strip() for l in labels_raw if str(l).strip() not in ['', 'None']]
                    else:
                        labels_asli = ['Negatif', 'Netral', 'Positif']

                    report = loc_detail.get('report', {})

                    # --- TABEL CLASSIFICATION REPORT ---
                    try:
                        if report:
                            rows = []
                            for cls in labels_asli:
                                if cls in report:
                                    r_data = report[cls]
                                    rows.append({
                                        'Kelas': cls,
                                        'Precision': f"{safe_float(r_data.get('precision', 0)):.2f}",
                                        'Recall': f"{safe_float(r_data.get('recall', 0)):.2f}",
                                        'F1-Score': f"{safe_float(r_data.get('f1-score', 0)):.2f}",
                                        'Support': safe_int(r_data.get('support', 0))
                                    })
                            for avg_key in ['macro avg', 'weighted avg']:
                                if avg_key in report:
                                    ma = report[avg_key]
                                    rows.append({
                                        'Kelas': avg_key,
                                        'Precision': f"{safe_float(ma.get('precision', 0)):.2f}",
                                        'Recall': f"{safe_float(ma.get('recall', 0)):.2f}",
                                        'F1-Score': f"{safe_float(ma.get('f1-score', 0)):.2f}",
                                        'Support': safe_int(ma.get('support', 0))
                                    })
                            if rows:
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=220)
                                report_data_for_f1[lok] = report
                            else:
                                st.caption("Tidak ada data kelas yang valid.")
                        else:
                            st.info("Detail report tidak tersedia.")
                    except Exception as e:
                        st.error(f"Gagal memuat tabel: {e}")

                    st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)

                    # --- CONFUSION MATRIX ---
                    try:
                        cm = loc_detail.get('cm', [])
                        if cm and len(cm) == len(labels_asli):
                            fig_cm = go.Figure(data=go.Heatmap(
                                z=cm, x=labels_asli, y=labels_asli,
                                colorscale=cmap_name,
                                texttemplate="%{text}",
                                textfont={"size": 18, "color": "black", "family": "Inter"},
                                hovertemplate='Aktual: %{y}<br>Prediksi: %{x}<br>Jumlah: %{z}<extra></extra>',
                                xgap=4, ygap=4,
                                colorbar=dict(thickness=15, len=0.9)
                            ))
                            fig_cm.update_layout(
                                height=420, margin=dict(l=10, r=10, t=45, b=10),
                                xaxis=dict(title=dict(text='<b>Prediksi</b>', font=dict(size=11, color='#334155')), tickfont=dict(size=10, color='#334155')),
                                yaxis=dict(title=dict(text='<b>Aktual</b>', font=dict(size=11, color='#334155')), tickfont=dict(size=10, color='#334155'), autorange='reversed', scaleanchor="x", scaleratio=1),
                                title=dict(text=f'Confusion Matrix — {lok}', font=dict(size=12, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center')
                            )
                            st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
                        elif cm:
                            st.warning("Ukuran Confusion Matrix tidak sesuai dengan jumlah label.")
                    except Exception as e:
                        st.error(f"Gagal memuat Confusion Matrix: {e}")

            # --- GRAFIK F1-SCORE ---
            if report_data_for_f1:
                try:
                    st.markdown('<hr style="margin:25px 0 20px;border-color:#E2E8F0">', unsafe_allow_html=True)
                    all_classes = sorted(list(set(
                        [c for lok_rep in report_data_for_f1.values()
                         for c in lok_rep.keys()
                         if c not in ['accuracy', 'macro avg', 'weighted avg']]
                    )))
                    if all_classes:
                        fig_f1 = go.Figure()
                        for lok in lokasi_list:
                            if lok in report_data_for_f1:
                                f1_vals = [safe_float(report_data_for_f1[lok].get(c, {}).get('f1-score', 0)) for c in all_classes]
                                fig_f1.add_trace(go.Bar(
                                    name=lok, x=all_classes, y=f1_vals,
                                    marker_color=LOC_COLOR.get(lok, '#2563EB'),
                                    text=[f"{v:.2f}" for v in f1_vals], textposition='outside',
                                    textfont=dict(size=14, family='Inter', weight='bold'),
                                    hovertemplate=f'<b>{lok}</b><br>Kelas: %{{x}}<br>F1-Score: %{{y:.2f}}<extra></extra>'
                                ))
                        fig_f1.update_layout(
                            title=dict(text="Perbandingan F1-Score per Kelas", font=dict(size=15, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center', y=0.98),
                            annotations=[dict(text=f"Model: {selected_model}", x=0.5, y=0.92, xref='paper', yref='paper', showarrow=False, font=dict(size=11, color='#64748B'))],
                            barmode='group', height=380, plot_bgcolor='white', paper_bgcolor='white',
                            font=dict(family='Inter', size=12, color='#334155'),
                            yaxis=dict(title='F1-Score', range=[0, 1.2], gridcolor='#E2E8F0', gridwidth=1),
                            xaxis=dict(title='', showgrid=False, showline=False, tickfont=dict(size=12, color='#475569')),
                            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
                            margin=dict(l=50, r=20, t=80, b=70), bargap=0.3
                        )
                        st.plotly_chart(fig_f1, use_container_width=True, config={'displayModeBar': False})

                        f1_rows = []
                        for c in all_classes:
                            row = {'Kelas': c}
                            for lok in lokasi_list:
                                if lok in report_data_for_f1:
                                    row[lok] = f"{safe_float(report_data_for_f1[lok].get(c, {}).get('f1-score', 0)):.2f}"
                            f1_rows.append(row)
                        if f1_rows:
                            st.markdown('<div style="font-size:0.9rem;font-weight:600;color:#334155;margin:15px 0 8px;">📋 Tabel F1-Score per Kelas</div>', unsafe_allow_html=True)
                            st.dataframe(pd.DataFrame(f1_rows), use_container_width=True, hide_index=True, height=130)
                except Exception as e:
                    st.error(f"Gagal memuat grafik F1-Score: {e}")
        else:
            if selected_model:
                st.warning(f"Detail evaluasi untuk model '{selected_model}' tidak ditemukan di data. Tersedia: {list(detail_data.keys())}")

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 3. RINGKASAN AKURASI ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Ringkasan Akurasi per Model & Lokasi</div>', unsafe_allow_html=True)
        summary_rows = []
        for m in model_names:
            row = {'Model': m}
            for lok in lokasi_list:
                if lok in akurasi:
                    acc_val = safe_float(akurasi[lok].get(m, 0))
                    if acc_val >= 85:
                        row[lok] = f"✅ {acc_val:.2f}%"
                    elif acc_val >= 70:
                        row[lok] = f"⚠️ {acc_val:.2f}%"
                    else:
                        row[lok] = f"❌ {acc_val:.2f}%"
            summary_rows.append(row)
        if summary_rows:
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True, height=150)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasifikasi tidak tersedia.")


# ══════════════════════════════════════════════════════════
# HALAMAN 4: KLASTERISASI
# ══════════════════════════════════════════════════════════
elif halaman == "klaster":
    page_header("Hasil K-Means Clustering",
                "Pengelompokan ulasan berdasarkan kemiripan konten teks (SVD → K-Means)")

    if data_klaster:
        for lok in lokasi_list:
            kd = data_klaster.get(lok)
            if not kd:
                continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">🧩 {lok}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                sx = kd.get('scatter_x', [])
                sy = kd.get('scatter_y', [])
                sc_clust = kd.get('scatter_cluster', [])
                if sx and sy and sc_clust:
                    try:
                        fig, ax = plt.subplots(figsize=(8, 5))
                        scatter = ax.scatter(np.array(sx), np.array(sy), c=np.array(sc_clust),
                                             cmap='tab10', alpha=0.75, edgecolor='white',
                                             linewidth=0.5, s=40, zorder=2)
                        plt.colorbar(scatter, ax=ax, label='Klaster')
                        ax.set_title(f"K-Means (K={kd.get('k_optimal', '?')})", fontweight='bold', fontsize=11)
                        ax.set_xlabel('SVD Komponen 1')
                        ax.set_ylabel('SVD Komponen 2')
                        ax.grid(True, alpha=0.3, zorder=1)
                        fig_style(fig, ax)
                        st.pyplot(fig)
                        plt.close(fig)
                    except Exception as e:
                        st.error(f"Gagal membuat scatter plot: {e}")
                else:
                    st.info("Data scatter tidak tersedia.")
            with c2:
                st.metric("Jumlah Klaster (K)", kd.get('k_optimal', '-'))
                st.metric("Silhouette Score", kd.get('silhouette', '-'))
                st.metric("Davies-Bouldin", kd.get('davies_bouldin', '-'))
                st.metric("Calinski-Harabasz", kd.get('calinski_harabasz', '-'))

            kata_dom = kd.get('kata_dominan', [])
            if kata_dom:
                st.markdown("**Kata Dominan per Klaster:**")
                st.dataframe(pd.DataFrame(kata_dom), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasterisasi tidak tersedia.")


# ══════════════════════════════════════════════════════════
# HALAMAN 5: RADAR PERBANDINGAN  (FIX BUG #4: safe access)
# ══════════════════════════════════════════════════════════
elif halaman == "radar":
    page_header("Radar Chart — Perbandingan Kualitas Clustering",
                "Perbandingan metrik evaluasi klaster antara kedua destinasi (dinormalisasi)")

    try:
        if data_klaster and len(lokasi_list) >= 2:
            metrics_keys = ['silhouette', 'davies_bouldin', 'calinski_harabasz']
            metrics_label = ['Silhouette\n(↑ bagus)', 'Davies-Bouldin\n(↓ bagus)', 'Calinski-Harabasz\n(↑ bagus)']

            # FIX BUG #4: Gunakan .get() dengan default, bukan akses langsung []
            raw = {}
            for lok in lokasi_list:
                if lok in data_klaster:
                    vals = []
                    valid = True
                    for k in metrics_keys:
                        v = data_klaster[lok].get(k)
                        if v is None:
                            valid = False
                            break
                        vals.append(safe_float(v))
                    if valid:
                        raw[lok] = vals

            if len(raw) < 2:
                st.warning("Data klaster tidak lengkap untuk perbandingan radar. Dibutuhkan minimal 2 destinasi dengan data metrik lengkap.")
            else:
                def normalize(idx, invert=False):
                    all_v = [raw[l][idx] for l in raw]
                    mn, mx = min(all_v), max(all_v)
                    if mx == mn:
                        return {l: 0.5 for l in raw}
                    n = {l: (raw[l][idx] - mn) / (mx - mn) for l in raw}
                    return {l: 1 - v for l, v in n.items()} if invert else n

                norm_sil = normalize(0)
                norm_db = normalize(1, True)
                norm_ch = normalize(2)
                normalized = {lok: [norm_sil[lok], norm_db[lok], norm_ch[lok]] for lok in raw}

                N = len(metrics_label)
                angles = [n / float(N) * 2 * math.pi for n in range(N)]
                angles += angles[:1]

                # Siapa menang di tiap metrik
                pemenang = {}
                for i, k in enumerate(metrics_keys):
                    if k == 'davies_bouldin':
                        winner = min(raw.keys(), key=lambda l: raw[l][i])
                    else:
                        winner = max(raw.keys(), key=lambda l: raw[l][i])
                    pemenang[k] = winner

                count_win = {l: 0 for l in raw}
                for k, w in pemenang.items():
                    count_win[w] += 1
                overall_winner = max(count_win.keys(), key=lambda l: count_win[l])
                is_tie = all(v == count_win[overall_winner] for v in count_win.values())

                # ========== RADAR CHART + TABEL ==========
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">📊 Radar Chart Metrik Klasterisasi</div>', unsafe_allow_html=True)
                st.markdown('<div class="sec-sub">Area lebih luas = kualitas klasterisasi lebih baik · Nilai dinormalisasi 0-1</div>', unsafe_allow_html=True)

                col_r, col_t = st.columns([1, 1])
                with col_r:
                    fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
                    ax.set_facecolor('#F8FAFC')
                    for lok in raw:
                        vals = normalized[lok] + normalized[lok][:1]
                        color = LOC_COLOR.get(lok, '#2563EB')
                        ax.plot(angles, vals, 'o-', linewidth=2.5, color=color, label=lok, markersize=8)
                        ax.fill(angles, vals, alpha=0.15, color=color)
                    ax.set_xticks(angles[:-1])
                    ax.set_xticklabels(metrics_label, fontsize=9, fontweight='bold')
                    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
                    ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'], fontsize=7, color='#94A3B8')
                    ax.set_ylim(0, 1)
                    ax.grid(color='#CBD5E1', linestyle='--', alpha=0.6)
                    ax.set_title('Radar Metrik Klasterisasi', fontweight='bold', fontsize=11, pad=20)
                    ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=9)
                    fig.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

                with col_t:
                    st.markdown("**Nilai Asli:**")
                    raw_rows = []
                    for k, label in zip(metrics_keys, ['Silhouette', 'Davies-Bouldin', 'Calinski-Harabasz']):
                        row = {'Metrik': label}
                        for lok in raw:
                            idx = metrics_keys.index(k)
                            row[lok] = f"{raw[lok][idx]:.4f}"
                        winner = pemenang.get(k, '-')
                        row['Pemenang'] = winner
                        raw_rows.append(row)
                    st.dataframe(pd.DataFrame(raw_rows), use_container_width=True, hide_index=True, height=180)

                    st.markdown("**Nilai Normalisasi (0-1):**")
                    norm_rows = []
                    for k, label in zip(metrics_keys, ['Silhouette', 'Davies-Bouldin', 'Calinski-Harabasz']):
                        row = {'Metrik': label}
                        for lok in raw:
                            idx = metrics_keys.index(k)
                            row[lok] = f"{normalized[lok][idx]:.2f}"
                        norm_rows.append(row)
                    st.dataframe(pd.DataFrame(norm_rows), use_container_width=True, hide_index=True, height=180)

                st.markdown('</div>', unsafe_allow_html=True)

                # ========== KESIMPULAN ==========
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">🏆 Kesimpulan Perbandingan</div>', unsafe_allow_html=True)

                if is_tie:
                    st.info("⚖️ Kedua destinasi memiliki kualitas klasterisasi yang seimbang (seri).")
                else:
                    winner_color = LOC_COLOR.get(overall_winner, '#2563EB')
                    win_count = count_win[overall_winner]
                    st.markdown(f"""
                    <div style="background:{winner_color}10;border-left:5px solid {winner_color};border-radius:0 12px 12px 0;padding:16px 20px;">
                        <div style="font-size:1.1rem;font-weight:700;color:{winner_color};">
                            🏆 {overall_winner}
                        </div>
                        <div style="font-size:0.85rem;color:#475569;margin-top:4px;">
                            Menang di <b>{win_count} dari {len(metrics_keys)}</b> metrik evaluasi klasterisasi.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    detail_lines = []
                    for k, label in zip(metrics_keys, ['Silhouette', 'Davies-Bouldin', 'Calinski-Harabasz']):
                        w = pemenang.get(k, '-')
                        icon = "✅" if w == overall_winner else "➖"
                        detail_lines.append(f"{icon} **{label}**: {w}")
                    st.markdown("\n".join(detail_lines))

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Data klasterisasi tidak tersedia atau kurang dari 2 destinasi.")
    except Exception as e:
        st.error(f"Gagal memuat halaman radar: {e}")


# ══════════════════════════════════════════════════════════
# HALAMAN 6: TOPIC MODELING (LDA)
# ══════════════════════════════════════════════════════════
elif halaman == "topik":
    page_header("Topic Modeling (LDA)",
                "Pengidentifikasian topik utama dari ulasan menggunakan Latent Dirichlet Allocation")

    if data_topik:
        for lok in lokasi_list:
            td = data_topik.get(lok)
            if not td:
                continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">📚 {lok}</div>', unsafe_allow_html=True)

            n_topics = td.get('n_topics', 0)
            coherence = td.get('coherence_score', '-')
            st.markdown(f"<div class='sec-sub'>Jumlah Topik: <b>{n_topics}</b> · Coherence Score: <b>{coherence}</b></div>", unsafe_allow_html=True)

            topics = td.get('topics', [])
            if topics:
                # Tampilkan per topik
                for i, topic in enumerate(topics):
                    words = topic.get('words', [])
                    weights = topic.get('weights', [])
                    topic_label = topic.get('label', f'Topik {i+1}')

                    if words and weights:
                        col_w, col_b = st.columns([1, 2])
                        with col_w:
                            st.markdown(f"**{topic_label}**")
                            for w, wt in zip(words[:8], weights[:8]):
                                bar_len = int(wt * 20)
                                st.markdown(f"<span style='font-size:0.82rem;color:#334155'>{w}</span> <span style='color:#94A3B8;font-size:0.75rem'>{'█' * bar_len} {wt:.3f}</span>", unsafe_allow_html=True)

                        with col_b:
                            fig_t = go.Figure()
                            fig_t.add_trace(go.Bar(
                                x=[w[:15] for w in words[:10]],
                                y=weights[:10],
                                marker_color=COLORS_TOPIC[i % len(COLORS_TOPIC)],
                                text=[f"{w:.3f}" for w in weights[:10]],
                                textposition='outside',
                                textfont=dict(size=10, family='Inter'),
                                marker_line_color='white', marker_line_width=1.5
                            ))
                            fig_t.update_layout(
                                height=250, plot_bgcolor='white', paper_bgcolor='white',
                                font=dict(family='Inter', size=11, color='#334155'),
                                xaxis=dict(tickfont=dict(size=9, color='#475569'), showgrid=False),
                                yaxis=dict(title='Bobot', titlefont=dict(size=10, color='#64748B'), gridcolor='#E2E8F0', showline=False),
                                margin=dict(l=40, r=15, t=10, b=50), bargap=0.3
                            )
                            st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})

                    if i < len(topics) - 1:
                        st.markdown('<hr style="margin:12px 0;border-color:#F1F5F9">', unsafe_allow_html=True)
            else:
                st.info("Detail topik tidak tersedia.")

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data topic modeling tidak tersedia.")


# ══════════════════════════════════════════════════════════
# HALAMAN 7: TRENDING TOPIK
# ══════════════════════════════════════════════════════════
elif halaman == "trending":
    page_header("Trending Topik",
                "Topik yang sedang tren berdasarkan frekuensi kemunculan dalam ulasan")

    if data_trending:
        for lok in lokasi_list:
            tr = data_trending.get(lok)
            if not tr:
                continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">📈 {lok}</div>', unsafe_allow_html=True)

            words = tr.get('words', [])
            counts = tr.get('counts', [])
            categories = tr.get('categories', [])

            if words and counts:
                col_tb, col_cb = st.columns([2, 1])
                with col_tb:
                    fig_tr = go.Figure()
                    colors_bar = []
                    for cat in (categories if categories else [''] * len(words)):
                        cat_lower = str(cat).lower()
                        if 'negatif' in cat_lower or 'masalah' in cat_lower or 'buruk' in cat_lower:
                            colors_bar.append('#EF4444')
                        elif 'positif' in cat_lower or 'baik' in cat_lower:
                            colors_bar.append('#10B981')
                        else:
                            colors_bar.append('#2563EB')

                    fig_tr.add_trace(go.Bar(
                        y=[w[:20] for w in words[:15]][::-1],
                        x=counts[:15][::-1],
                        orientation='h',
                        marker_color=colors_bar[:15][::-1],
                        text=counts[:15][::-1],
                        textposition='outside',
                        textfont=dict(size=11, family='Inter', weight='bold'),
                        marker_line_color='white', marker_line_width=1.5
                    ))
                    fig_tr.update_layout(
                        height=450, plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Inter', size=11, color='#334155'),
                        xaxis=dict(title='Frekuensi', titlefont=dict(size=10, color='#64748B'), gridcolor='#E2E8F0', showline=False),
                        yaxis=dict(showgrid=False, tickfont=dict(size=10, color='#334155')),
                        margin=dict(l=80, r=30, t=10, b=40), bargap=0.25
                    )
                    st.plotly_chart(fig_tr, use_container_width=True, config={'displayModeBar': False})

                with col_cb:
                    st.markdown("**Legenda Warna:**")
                    st.markdown('<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:15px;">'
                                '<span style="background:#D1FAE5;color:#059669;padding:3px 10px;border-radius:99px;font-size:0.78rem;font-weight:600">🟢 Positif</span>'
                                '<span style="background:#FEE2E2;color:#DC2626;padding:3px 10px;border-radius:99px;font-size:0.78rem;font-weight:600">🔴 Negatif/Masalah</span>'
                                '<span style="background:#DBEAFE;color:#2563EB;padding:3px 10px;border-radius:99px;font-size:0.78rem;font-weight:600">🔵 Lainnya</span>'
                                '</div>', unsafe_allow_html=True)

                    st.markdown("**Top 10 Kata Trending:**")
                    trending_rows = []
                    for i, (w, c) in enumerate(zip(words[:10], counts[:10])):
                        cat = categories[i] if i < len(categories) else '-'
                        trending_rows.append({'#': i+1, 'Kata': w, 'Frekuensi': c, 'Kategori': cat})
                    st.dataframe(pd.DataFrame(trending_rows), use_container_width=True, hide_index=True, height=380)

            else:
                st.info("Data trending tidak tersedia.")

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data trending topik tidak tersedia.")


# ══════════════════════════════════════════════════════════
# HALAMAN 8: WORDCLOUD MASALAH
# ══════════════════════════════════════════════════════════
elif halaman == "wordcloud":
    page_header("WordCloud Kata Masalah",
                "Visualisasi kata-kata yang paling sering muncul dalam ulasan negatif")

    if data_ulasan:
        col_wc1, col_wc2 = st.columns(2)
        for col, r in zip([col_wc1, col_wc2], ringkasan):
            lokasi = r.get('lokasi', '')
            neg_reviews = data_ulasan.get(lokasi, {}).get('contoh_negatif', [])
            with col:
                st.markdown(f'<div class="sec-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="sec-title">🔴 {lokasi}</div>', unsafe_allow_html=True)

                if neg_reviews:
                    text = ' '.join([u.get('review', '') for u in neg_reviews if u.get('review', '')])
                    if text.strip():
                        try:
                            wc = WordCloud(
                                width=600, height=350,
                                background_color='white',
                                colormap='Reds',
                                max_words=80,
                                min_font_size=8,
                                max_font_size=80,
                                contour_width=1,
                                contour_color='#FEE2E2',
                                prefer_horizontal=0.7
                            ).generate(text)
                            fig_wc, ax_wc = plt.subplots(figsize=(7, 4))
                            ax_wc.imshow(wc, interpolation='bilinear')
                            ax_wc.axis('off')
                            ax_wc.set_title(f'WordCloud Negatif — {lokasi}', fontsize=11, fontweight='bold', color='#0F172A', pad=10)
                            fig_wc.tight_layout()
                            st.pyplot(fig_wc)
                            plt.close(fig_wc)
                        except Exception as e:
                            st.error(f"Gagal membuat wordcloud: {e}")
                    else:
                        st.info("Tidak ada teks ulasan negatif.")
                else:
                    st.info("Tidak ada ulasan negatif untuk dibuat wordcloud.")

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data ulasan tidak tersedia untuk wordcloud.")


# ══════════════════════════════════════════════════════════
# HALAMAN 9: JARINGAN ANTAR DESTINASI
# ══════════════════════════════════════════════════════════
elif halaman == "jaringan":
    page_header("Jaringan Antar Destinasi",
                "Visualisasi hubungan antar destinasi berdasarkan kata kunci bersama & centrality")

    try:
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🕸️ Network Graph</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Node = destinasi · Edge = kemiripan kata kunci · Ukuran node = berdasarkan centrality</div>', unsafe_allow_html=True)

        G = nx.Graph()

        # Tambah node dari ringkasan
        node_sizes = {}
        for r in ringkasan:
            lok = r.get('lokasi', '')
            total = safe_int(r.get('total_ulasan', 0))
            G.add_node(lok)
            node_sizes[lok] = max(total / 5, 300)  # minimum size

        # Tambah edges dari bridge
        if bridge:
            for b in bridge:
                src = b.get('source', '')
                tgt = b.get('target', '')
                weight = safe_float(b.get('weight', 1))
                if src and tgt:
                    G.add_edge(src, tgt, weight=weight)

        # Gunakan centrality data jika ada, untuk ukuran node
        if data_centrality:
            for lok, cdata in data_centrality.items():
                if lok in G:
                    degree = safe_float(cdata.get('degree', 0))
                    betweenness = safe_float(cdata.get('betweenness', 0))
                    node_sizes[lok] = max(degree * 500 + 300, 300)

        if G.number_of_nodes() > 0 and G.number_of_edges() > 0:
            fig_net, ax_net = plt.subplots(figsize=(9, 6))
            pos = nx.spring_layout(G, k=2, seed=42)

            sizes = [node_sizes.get(n, 500) for n in G.nodes()]
            colors = [LOC_COLOR.get(n, '#2563EB') for n in G.nodes()]

            nx.draw_networkx_nodes(G, pos, ax=ax_net, node_size=sizes,
                                   node_color=colors, alpha=0.85, edgecolors='white', linewidths=2)
            nx.draw_networkx_labels(G, pos, ax=ax_net, font_size=9, font_weight='bold', font_color='white')

            if G.number_of_edges() > 0:
                edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
                max_w = max(edge_weights) if edge_weights else 1
                nx.draw_networkx_edges(G, pos, ax=ax_net,
                                       width=[max(1, w / max_w * 5) for w in edge_weights],
                                       edge_color='#94A3B8', alpha=0.6,
                                       style='solid', connectionstyle='arc3,rad=0.1')

                # Label edge weight
                edge_labels = {(u, v): f"{G[u][v].get('weight', 0):.2f}" for u, v in G.edges()}
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                             ax=ax_net, font_size=8, font_color='#64748B',
                                             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#E2E8F0', alpha=0.9))

            ax_net.set_facecolor('#F8FAFC')
            ax_net.axis('off')
            ax_net.set_title('Jaringan Kemiripan Antar Destinasi', fontsize=12, fontweight='bold', color='#0F172A', pad=15)
            fig_net.tight_layout()
            st.pyplot(fig_net)
            plt.close(fig_net)
        else:
            st.info("Tidak cukup data untuk membuat jaringan (butuh minimal 2 node dan 1 edge).")

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== TABEL CENTRALITY ==========
        if data_centrality:
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">📊 Metrik Centrality per Destinasi</div>', unsafe_allow_html=True)

            cent_rows = []
            for lok, cdata in data_centrality.items():
                cent_rows.append({
                    'Destinasi': lok,
                    'Degree Centrality': f"{safe_float(cdata.get('degree', 0)):.4f}",
                    'Betweenness Centrality': f"{safe_float(cdata.get('betweenness', 0)):.4f}",
                    'Closeness Centrality': f"{safe_float(cdata.get('closeness', 0)):.4f}",
                    'Eigenvector Centrality': f"{safe_float(cdata.get('eigenvector', 0)):.4f}",
                })
            if cent_rows:
                st.dataframe(pd.DataFrame(cent_rows), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ========== TABEL BRIDGE/EDGE ==========
        if bridge:
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">🔗 Detail Koneksi Antar Destinasi</div>', unsafe_allow_html=True)
            bridge_rows = []
            for b in bridge:
                bridge_rows.append({
                    'Sumber': b.get('source', '-'),
                    'Target': b.get('target', '-'),
                    'Bobot Kemiripan': f"{safe_float(b.get('weight', 0)):.4f}",
                    'Kata Bersama': ', '.join(b.get('common_words', [])) if b.get('common_words') else '-',
                })
            if bridge_rows:
                st.dataframe(pd.DataFrame(bridge_rows), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal memuat halaman jaringan: {e}")
