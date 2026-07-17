# -*- coding: utf-8 -*-
# =========================================================
# DASHBOARD PERBANDINGAN PARIWISATA
# Desa Wae Rebo vs Taman Nasional Komodo
# =========================================================
import json
import math
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
# LOAD DATA (dengan error handling yang lebih baik)
# ----------------------------------------------------------
DATA = {}
try:
    with open('dashboard_data.json', 'r', encoding='utf-8') as f:
        DATA = json.load(f)
except FileNotFoundError:
    st.error("❌ File `dashboard_data.json` tidak ditemukan. Pastikan file ada di folder yang sama dengan script ini.")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"❌ File `dashboard_data.json` tidak valid (JSON error): {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Error tidak diketahui saat memuat data: {e}")
    st.stop()

# ----------------------------------------------------------
# EXTRACT DATA DENGAN DEFAULT VALUES
# ----------------------------------------------------------
ringkasan = DATA.get('ringkasan', [])
bridge = DATA.get('bridge', {})
lokasi_list = DATA.get('lokasi_list', ['Desa Wae Rebo', 'Taman Nasional Komodo'])
data_rating = DATA.get('rating', {})
data_klasifikasi = DATA.get('klasifikasi', {})
data_klaster = DATA.get('klaster', {})
data_topik = DATA.get('topik', {})
data_trending = DATA.get('trending', {})
data_centrality = DATA.get('centrality', {})
data_ulasan = DATA.get('ulasan_detail', {})
data_temporal = DATA.get('temporal', {})
data_wordcloud = DATA.get('wordcloud', {})

# Initialize default empty structures if missing
for lok in lokasi_list:
    if lok not in data_ulasan:
        data_ulasan[lok] = {}
    if lok not in data_wordcloud:
        data_wordcloud[lok] = {}

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
        "Beranda & Peta": "beranda",
        "Analisis Sentimen": "sentimen",
        "Model Klasifikasi": "klasifikasi",
        "Klasterisasi": "klaster",
        "Radar Perbandingan": "radar",
        "Topic Modeling (LDA)": "topik",
        "Trending Topik": "trending",
        "WordCloud Masalah": "wordcloud",
        "Jaringan Antar Destinasi": "jaringan",
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
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def safe_int(val, default=0):
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
        lat_list = [r.get('lat', -8.5) for r in ringkasan]
        lon_list = [r.get('lon', 120) for r in ringkasan]
        center_lat = sum(lat_list) / max(len(lat_list), 1)
        center_lon = sum(lon_list) / max(len(lon_list), 1)
        
        peta = folium.Map(
            location=[center_lat, center_lon],
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
# HALAMAN 3: KLASIFIKASI
# ══════════════════════════════════════════════════════════
elif halaman == "klasifikasi":
    page_header("Perbandingan Akurasi Model Klasifikasi",
                "SVM · Random Forest · Naive Bayes — per destinasi wisata")
    kpi_row()

    if data_klasifikasi:
        model_names = data_klasifikasi.get('model_names', [])
        akurasi = data_klasifikasi.get('akurasi', {})
        detail_data = data_klasifikasi.get('detail', {})

        # Gunakan session_state agar pilihan model persist
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

        # Tombol pakai session_state
        btn_cols = st.columns(len(model_names))
        for idx, model_name in enumerate(model_names):
            with btn_cols[idx]:
                icon = model_icons.get(model_name, '🤖')
                if st.button(f"{icon} {model_name}", key=f"btn_{model_name}", use_container_width=True):
                    st.session_state.selected_model = model_name
                    st.rerun()

        selected_model = st.session_state.selected_model

        # Cek keberadaan key sebelum akses
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
                st.warning(f"Detail evaluasi untuk model '{selected_model}' tidak ditemukan. Tersedia: {list(detail_data.keys())}")

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
# HALAMAN 5: RADAR PERBANDINGAN
# ══════════════════════════════════════════════════════════
elif halaman == "radar":
    page_header("Radar Chart — Perbandingan Kualitas Clustering",
                "Perbandingan metrik evaluasi klaster antara kedua destinasi (dinormalisasi)")

    try:
        if data_klaster and len(lokasi_list) >= 2:
            metrics_keys = ['silhouette', 'davies_bouldin', 'calinski_harabasz']
            metrics_label = ['Silhouette\n(↑ bagus)', 'Davies-Bouldin\n(↓ bagus)', 'Calinski-Harabasz\n(↑ bagus)']

            # Gunakan .get() dengan default
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
                st.warning("Data klaster tidak lengkap untuk perbandingan radar.")
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
                                margin=dict(l=40, r=15, t=30, b=60)
                            )
                            st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})

            # Distribusi topik (pie chart)
            distribusi = td.get('distribusi', {})
            if distribusi:
                st.markdown("**Distribusi Topik:**")
                col_pie1, col_pie2 = st.columns(2)
                with col_pie1:
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=list(distribusi.keys()),
                        values=list(distribusi.values()),
                        marker=dict(colors=COLORS_TOPIC[:len(distribusi)]),
                        hole=0.4,
                        textposition='inside',
                        textfont=dict(size=11, color='white', family='Inter')
                    )])
                    fig_pie.update_layout(
                        height=300,
                        margin=dict(l=10, r=10, t=30, b=10),
                        showlegend=False
                    )
                    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
                with col_pie2:
                    dist_rows = [{'Topik': k, 'Jumlah Review': v} for k, v in distribusi.items()]
                    st.dataframe(pd.DataFrame(dist_rows), use_container_width=True, hide_index=True, height=200)

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data topic modeling tidak tersedia.")


# ══════════════════════════════════════════════════════════
# HALAMAN 7: TRENDING TOPIK
# ══════════════════════════════════════════════════════════
elif halaman == "trending":
    page_header("Trending Topik",
                "Analisis tren topik dari waktu ke waktu berdasarkan ulasan")

    if data_trending:
        cols_trend = st.columns(len(data_trending))
        for idx, (lok, trend_data) in enumerate(data_trending.items()):
            with cols_trend[idx]:
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="sec-title">📈 {lok}</div>', unsafe_allow_html=True)

                bulan = trend_data.get('bulan', [])
                topik_data = trend_data.get('topik', {})

                if bulan and topik_data:
                    fig_trend = go.Figure()
                    for i, (topik, values) in enumerate(topik_data.items()):
                        fig_trend.add_trace(go.Scatter(
                            x=bulan,
                            y=values,
                            mode='lines+markers',
                            name=topik,
                            line=dict(color=COLORS_TOPIC[i % len(COLORS_TOPIC)], width=2.5),
                            marker=dict(size=8),
                            hovertemplate=f'<b>{topik}</b><br>Bulan: %{{x}}<br>Jumlah: %{{y}}<extra></extra>'
                        ))

                    fig_trend.update_layout(
                        height=350,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family='Inter', size=11, color='#334155'),
                        xaxis=dict(title='Bulan', tickfont=dict(size=10), gridcolor='#E2E8F0'),
                        yaxis=dict(title='Jumlah Review', gridcolor='#E2E8F0'),
                        legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5, font=dict(size=9)),
                        margin=dict(l=40, r=15, t=40, b=80),
                        hoverlabel=dict(bgcolor='#0F172A', font=dict(color='white'))
                    )
                    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

                    # Tabel data
                    trend_rows = []
                    for b_idx, bulan_val in enumerate(bulan):
                        row = {'Bulan': bulan_val}
                        for topik, values in topik_data.items():
                            if b_idx < len(values):
                                row[topik] = values[b_idx]
                        trend_rows.append(row)
                    if trend_rows:
                        st.dataframe(pd.DataFrame(trend_rows), use_container_width=True, hide_index=True, height=200)
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
                "Visualisasi kata-kata yang sering muncul pada ulasan negatif dan netral")

    for lok in lokasi_list:
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">☁️ {lok}</div>', unsafe_allow_html=True)

        wc_data = data_wordcloud.get(lok, {})
        if not wc_data:
            st.info("Data wordcloud tidak tersedia untuk lokasi ini.")
            st.markdown('</div>', unsafe_allow_html=True)
            continue

        col_neg, col_net = st.columns(2)

        with col_neg:
            st.markdown("**🔴 Ulasan Negatif**")
            neg_words = wc_data.get('negatif', {})
            if neg_words:
                try:
                    wc = WordCloud(
                        width=500, height=300,
                        background_color='white',
                        colormap='Reds',
                        max_words=50,
                        prefer_horizontal=0.8
                    ).generate_from_frequencies(neg_words)
                    fig_wc, ax_wc = plt.subplots(figsize=(6, 4))
                    ax_wc.imshow(wc, interpolation='bilinear')
                    ax_wc.axis('off')
                    ax_wc.set_title('Kata Negatif', fontsize=12, fontweight='bold', color='#EF4444')
                    plt.tight_layout()
                    st.pyplot(fig_wc)
                    plt.close(fig_wc)
                except Exception as e:
                    st.error(f"Gagal membuat wordcloud negatif: {e}")
            else:
                st.info("Tidak ada data kata negatif.")

        with col_net:
            st.markdown("**🟡 Ulasan Netral**")
            net_words = wc_data.get('netral', {})
            if net_words:
                try:
                    wc = WordCloud(
                        width=500, height=300,
                        background_color='white',
                        colormap='YlOrBr',
                        max_words=50,
                        prefer_horizontal=0.8
                    ).generate_from_frequencies(net_words)
                    fig_wc, ax_wc = plt.subplots(figsize=(6, 4))
                    ax_wc.imshow(wc, interpolation='bilinear')
                    ax_wc.axis('off')
                    ax_wc.set_title('Kata Netral', fontsize=12, fontweight='bold', color='#F59E0B')
                    plt.tight_layout()
                    st.pyplot(fig_wc)
                    plt.close(fig_wc)
                except Exception as e:
                    st.error(f"Gagal membuat wordcloud netral: {e}")
            else:
                st.info("Tidak ada data kata netral.")

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# HALAMAN 9: JARINGAN ANTAR DESTINASI
# ══════════════════════════════════════════════════════════
elif halaman == "jaringan":
    page_header("Jaringan Antar Destinasi",
                "Visualisasi hubungan antar aspek wisata berdasarkan co-occurrence kata")

    if data_centrality:
        try:
            nodes = data_centrality.get('nodes', [])
            edges = data_centrality.get('edges', [])

            if nodes and edges:
                # Buat graph
                G = nx.Graph()

                # Tambah nodes
                for node in nodes:
                    G.add_node(
                        node['id'],
                        degree=node.get('degree', 0),
                        betweenness=node.get('betweenness', 0),
                        closeness=node.get('closeness', 0),
                        group=node.get('group', 0)
                    )

                # Tambah edges
                for edge in edges:
                    G.add_edge(edge['source'], edge['target'], weight=edge.get('value', 1))

                # Visualisasi
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">🔗 Network Graph</div>', unsafe_allow_html=True)
                st.markdown('<div class="sec-sub">Ukuran node = degree centrality · Ketebalan garis = bobot hubungan</div>', unsafe_allow_html=True)

                fig_net, ax_net = plt.subplots(figsize=(12, 8))
                ax_net.set_facecolor('#F8FAFC')

                # Layout
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

                # Warna berdasarkan group
                group_colors = {0: '#2563EB', 1: '#EF4444', 2: '#10B981'}
                node_colors = [group_colors.get(G.nodes[n].get('group', 0), '#94A3B8') for n in G.nodes()]

                # Ukuran node berdasarkan degree
                node_sizes = [G.nodes[n].get('degree', 1) * 300 + 200 for n in G.nodes()]

                # Gambar edges
                edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
                nx.draw_networkx_edges(
                    G, pos, ax=ax_net,
                    width=[w * 0.5 for w in edge_weights],
                    alpha=0.4,
                    edge_color='#94A3B8'
                )

                # Gambar nodes
                nx.draw_networkx_nodes(
                    G, pos, ax=ax_net,
                    node_color=node_colors,
                    node_size=node_sizes,
                    alpha=0.85,
                    edgecolors='white',
                    linewidths=2
                )

                # Labels
                nx.draw_networkx_labels(
                    G, pos, ax=ax_net,
                    font_size=10,
                    font_weight='bold',
                    font_color='white'
                )

                ax_net.set_title('Jaringan Hubungan Antar Aspek Wisata', fontweight='bold', fontsize=13, pad=15)
                ax_net.axis('off')
                plt.tight_layout()
                st.pyplot(fig_net)
                plt.close(fig_net)

                st.markdown('</div>', unsafe_allow_html=True)

                # Tabel centrality
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">📊 Tabel Centrality Metrics</div>', unsafe_allow_html=True)

                centrality_rows = []
                for node in nodes:
                    centrality_rows.append({
                        'Node': node['id'],
                        'Degree': node.get('degree', 0),
                        'Betweenness': f"{node.get('betweenness', 0):.4f}",
                        'Closeness': f"{node.get('closeness', 0):.4f}",
                        'Grup': ['Destinasi 1', 'Destinasi 2', 'Aspek Bersama'][node.get('group', 0)]
                    })
                st.dataframe(pd.DataFrame(centrality_rows), use_container_width=True, hide_index=True, height=300)

                st.markdown('</div>', unsafe_allow_html=True)

                # Tabel edges
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">🔗 Tabel Hubungan (Edges)</div>', unsafe_allow_html=True)

                edge_rows = []
                for edge in edges:
                    edge_rows.append({
                        'Dari': edge['source'],
                        'Ke': edge['target'],
                        'Bobot': edge.get('value', 1)
                    })
                st.dataframe(pd.DataFrame(edge_rows), use_container_width=True, hide_index=True, height=350)

                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.info("Data nodes atau edges tidak tersedia.")
        except Exception as e:
            st.error(f"Gagal memuat jaringan: {e}")
    else:
        st.info("Data jaringan tidak tersedia.")
