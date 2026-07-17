# =========================================================
# SEL 42: DASHBOARD PERBANDINGAN PARIWISATA
# Desa Wae Rebo vs Taman Nasional Komodo
# =========================================================
import json, math, os
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

/* Root & App */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F0F4F8 !important; }

/* Sidebar */
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

/* Main content padding */
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1400px !important; }

/* Header strip */
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

/* KPI cards */
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
.kpi-badge  { display:inline-block; padding: 2px 8px; border-radius: 99px; font-size:0.72rem; font-weight:700; }
.badge-neg  { background: #FEE2E2; color: #DC2626; }
.badge-pos  { background: #D1FAE5; color: #059669; }

/* Section card */
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

/* Dividers */
hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }

/* Table */
[data-testid="stDataFrame"] {
    border-radius: 10px !important; overflow: hidden;
    box-shadow: 0 1px 6px rgba(0,0,0,.06) !important;
}

/* Selectbox / filters */
[data-testid="stSelectbox"], [data-testid="stMultiSelect"] {
    border-radius: 10px !important;
}

/* Metrics fallback */
[data-testid="stMetric"] {
    background: white; border-radius: 12px; padding: 14px 18px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.06); border-left: 4px solid #2563EB;
}

/* Nav header in sidebar */
.nav-section {
    font-size: 0.68rem; font-weight: 700; color: #64748B;
    letter-spacing: .1em; text-transform: uppercase;
    padding: 16px 4px 6px; margin-top: 4px;
}

/* Tabs override (used sparingly) */
button[data-baseweb="tab"] {
    font-size: 0.88rem !important; font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #2563EB !important;
    border-bottom: 3px solid #2563EB !important;
}

/* Info / warning / success boxes */
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
# LOAD DATA
# ----------------------------------------------------------
with open('dashboard_data.json', 'r', encoding='utf-8') as f:
    DATA = json.load(f)

ringkasan        = DATA['ringkasan']
bridge           = DATA['bridge']
lokasi_list      = DATA['lokasi_list']
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
# HELPER: header strip
# ----------------------------------------------------------
def page_header(title, subtitle=""):
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-header-title">{title}</div>
        <div class="dash-header-sub">{subtitle if subtitle else "Analisis Ulasan Google Maps &middot; Desa Wae Rebo vs Taman Nasional Komodo"}</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# HELPER: KPI row
# ----------------------------------------------------------
def kpi_row():
    cols = st.columns(len(ringkasan))
    for col, r in zip(cols, ringkasan):
        neg_pct = r['persen_negatif']
        color = "red" if neg_pct > 50 else "green"
        badge = "#FEE2E2;color:#DC2626" if neg_pct > 50 else "#D1FAE5;color:#059669"
        badge_txt = "⚠️ Negatif dominan" if neg_pct > 50 else "✅ Positif dominan"
        col.markdown(f"""
        <div class="kpi-card {color}" style="margin-bottom:4px">
            <div class="kpi-label">{r['lokasi']}</div>
            <div style="display:flex;align-items:baseline;gap:12px;margin:6px 0 4px">
                <div class="kpi-value">{neg_pct}%</div>
                <div style="font-size:0.78rem;color:#64748B">negatif</div>
            </div>
            <div style="font-size:0.8rem;color:#475569;margin-bottom:8px">
                dari <b>{r['total_ulasan']:,}</b> total ulasan
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:0.75rem">
                <span style="background:#D1FAE5;color:#059669;padding:2px 7px;border-radius:99px;font-weight:600">✅ {r['jumlah_positif']} positif</span>
                <span style="background:#FEE2E2;color:#DC2626;padding:2px 7px;border-radius:99px;font-weight:600">❌ {r['jumlah_negatif']} negatif</span>
                <span style="background:#F1F5F9;color:#64748B;padding:2px 7px;border-radius:99px;font-weight:600">➖ {r['jumlah_netral']} netral</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def fig_style(fig, ax=None):
    if ax:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    fig.tight_layout()

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
    peta = folium.Map(
        location=[sum(r['lat'] for r in ringkasan)/len(ringkasan),
                  sum(r['lon'] for r in ringkasan)/len(ringkasan)],
        zoom_start=9, tiles="CartoDB positron"
    )
    for r in ringkasan:
        warna_m = "green" if r['status_warna'] == "Hijau" else "red"
        popup = (f"<b style='font-family:Inter'>{r['lokasi']}</b><br>"
                 f"📝 Total: {r['total_ulasan']}<br>"
                 f"✅ Positif: {r['jumlah_positif']}<br>"
                 f"❌ Negatif: {r['jumlah_negatif']}<br>"
                 f"% Negatif: <b>{r['persen_negatif']}%</b>")
        folium.Marker([r['lat'], r['lon']],
                      popup=folium.Popup(popup, max_width=240),
                      tooltip=r['lokasi'],
                      icon=folium.Icon(color=warna_m, icon='info-sign')).add_to(peta)
    st_folium(peta, width=None, height=430)
    st.markdown('</div>', unsafe_allow_html=True)

    # Ringkasan perbandingan tabel
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📋 Ringkasan Perbandingan</div>', unsafe_allow_html=True)
    df_ring = pd.DataFrame([{
        'Destinasi': r['lokasi'],
        'Total Ulasan': r['total_ulasan'],
        'Positif': r['jumlah_positif'],
        'Negatif': r['jumlah_negatif'],
        'Netral': r['jumlah_netral'],
        '% Negatif': f"{r['persen_negatif']}%",
        'Status': "⚠️ Perlu Perhatian" if r['persen_negatif'] > 50 else "✅ Cukup Baik",
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
    st.markdown('<div class="sec-sub">Positif = Rating 4-5 · Negatif = Rating 1-2 · Netral = Rating 3</div>', unsafe_allow_html=True)

    col_chart1, col_chart2 = st.columns(2)
    sentimen_labels = ['Positif', 'Negatif', 'Netral']
    sentimen_colors = ['#10B981', '#EF4444', '#94A3B8']

    for col, r in zip([col_chart1, col_chart2], ringkasan):
        with col:
            lokasi = r['lokasi']
            values = [r['jumlah_positif'], r['jumlah_negatif'], r['jumlah_netral']]
            try:
                ymax = max(values) * 1.25 if max(values) > 0 else 10
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=sentimen_labels, y=values, marker_color=sentimen_colors,
                    text=values, textposition='outside',
                    textfont=dict(size=15, color='#0F172A'),
                    hovertemplate='<b>' + lokasi + '</b><br>Sentimen: %{x}<br>Jumlah: %{y}<extra></extra>',
                    marker_line_color='white', marker_line_width=2.5
                ))
                fig.update_layout(
                    title=dict(text=lokasi, font=dict(size=14, color='#0F172A', weight='bold'),
                               x=0.5, xanchor='center', y=0.95),
                    height=380,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(size=12, color='#334155'),
                    xaxis=dict(tickfont=dict(size=12, color='#475569'),
                               showgrid=False, showline=False, zeroline=False),
                    yaxis=dict(title=dict(text='Jumlah Ulasan', font=dict(size=11, color='#64748B')),
                               tickfont=dict(size=11, color='#64748B'),
                               gridcolor='#E2E8F0', range=[0, ymax],
                               showline=False, zeroline=False),
                    margin=dict(l=50, r=20, t=50, b=50),
                    bargap=0.35
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except Exception as e:
                st.warning(f"Chart sentimen {lokasi} gagal: {e}")
                st.bar_chart(pd.DataFrame({'Sentimen': sentimen_labels, 'Jumlah': values}).set_index('Sentimen'))
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== CONTOH ULASAN PER SENTIMEN ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Sentimen</div>', unsafe_allow_html=True)
    tab_positif, tab_negatif, tab_netral = st.tabs(["🟢 Positif", "🔴 Negatif", "🟡 Netral"])
    for tab, skey, slab in [(tab_positif,'contoh_positif','Positif'),
                             (tab_negatif,'contoh_negatif','Negatif'),
                             (tab_netral,'contoh_netral','Netral')]:
        with tab:
            c1, c2 = st.columns(2)
            for col, r in zip([c1, c2], ringkasan):
                with col:
                    st.markdown(f'**{r["lokasi"]}**')
                    cl = data_ulasan.get(r['lokasi'], {}).get(skey, [])
                    if cl:
                        rows = []
                        for u in cl[:5]:
                            rating_val = u.get('rating', 0)
                            stars = '⭐' * rating_val
                            rows.append({
                                'Penulis': u.get('author', 'Anonim'),
                                'Rating': stars,
                                'Tanggal': u.get('date', ''),
                                'Ulasan': u.get('review', '')
                            })
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                            column_config={
                                'Penulis': st.column_config.TextColumn('Penulis', width='medium'),
                                'Rating': st.column_config.TextColumn('Rating', width='small'),
                                'Tanggal': st.column_config.TextColumn('Tanggal', width='medium'),
                                'Ulasan': st.column_config.TextColumn('Ulasan', width='large')
                            })
                    else:
                        st.info(f"Tidak ada contoh ulasan {slab.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== DISTRIBUSI RATING BINTANG ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⭐ Distribusi Rating Bintang</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Arahkan kursor ke bar untuk melihat detail jumlah ulasan per bintang</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    warna_bintang = {1: '#EF4444', 2: '#F97316', 3: '#F59E0B', 4: '#84CC16', 5: '#10B981'}

    for col, lok in zip([c1, c2], lokasi_list):
        with col:
            rc = data_rating.get(lok, {})
            if not rc:
                st.info("Data rating tidak tersedia.")
                continue
            try:
                ratings = sorted([int(r) for r in rc.keys()])
                values = [int(rc[str(r)]) for r in ratings]
                colors = [warna_bintang.get(r, '#94A3B8') for r in ratings]
                labels = [f'{r} Bintang' for r in ratings]
                ymax = max(values) * 1.25 if max(values) > 0 else 10

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=labels, y=values, marker_color=colors,
                    text=values, textposition='outside',
                    textfont=dict(size=12, color='#0F172A'),
                    hovertemplate='<b>' + lok + '</b><br>Rating: %{x}<br>Jumlah: %{y}<extra></extra>',
                    marker_line_color='white', marker_line_width=2.5
                ))
                fig.update_layout(
                    title=dict(text=lok, font=dict(size=14, color='#0F172A', weight='bold'),
                               x=0.5, xanchor='center', y=0.95),
                    height=380,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(size=12, color='#334155'),
                    xaxis=dict(tickfont=dict(size=11),
                               showgrid=False, showline=False, zeroline=False),
                    yaxis=dict(title=dict(text='Jumlah Ulasan', font=dict(size=11, color='#64748B')),
                               tickfont=dict(size=11, color='#64748B'),
                               gridcolor='#E2E8F0', range=[0, ymax],
                               showline=False, zeroline=False),
                    margin=dict(l=50, r=20, t=50, b=50),
                    bargap=0.35
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except Exception as e:
                st.warning(f"Chart rating {lok} gagal: {e}")
                df_r = pd.DataFrame({'Rating': [f'{r} Bintang' for r in sorted([int(x) for x in rc.keys()])],
                                     'Jumlah': [int(rc[str(r)]) for r in sorted([int(x) for x in rc.keys()])]})
                st.bar_chart(df_r.set_index('Rating'))
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== CONTOH ULASAN PER BINTANG ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Rating Bintang</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Klik tab untuk melihat contoh ulasan berdasarkan jumlah bintang</div>', unsafe_allow_html=True)
    tabs_r = st.tabs(["⭐ 1", "⭐⭐ 2", "⭐⭐⭐ 3", "⭐⭐⭐⭐ 4", "⭐⭐⭐⭐⭐ 5"])
    for tab, rkey, rlab in zip(tabs_r,
                                [f'rating_{i}' for i in range(1, 6)],
                                [f'{i} Bintang' for i in range(1, 6)]):
        with tab:
            c1, c2 = st.columns(2)
            for col, r in zip([c1, c2], ringkasan):
                with col:
                    st.markdown(f'**{r["lokasi"]}**')
                    cl = data_ulasan.get(r['lokasi'], {}).get(rkey, [])
                    if cl:
                        rows = []
                        for u in cl[:5]:
                            rating_val = u.get('rating', 0)
                            stars = '⭐' * rating_val
                            rows.append({
                                'Penulis': u.get('author', 'Anonim'),
                                'Rating': stars,
                                'Tanggal': u.get('date', ''),
                                'Ulasan': u.get('review', '')
                            })
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                            column_config={
                                'Penulis': st.column_config.TextColumn('Penulis', width='medium'),
                                'Rating': st.column_config.TextColumn('Rating', width='small'),
                                'Tanggal': st.column_config.TextColumn('Tanggal', width='medium'),
                                'Ulasan': st.column_config.TextColumn('Ulasan', width='large')
                            })
                    else:
                        st.info(f"Tidak ada contoh ulasan {rlab.lower()}")
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

        # ========== 1. BAR CHART AKURASI ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Perbandingan Akurasi Antar Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Perbandingan performa ketiga model ML pada kedua lokasi berdasarkan akurasi</div>', unsafe_allow_html=True)
        
        if model_names and akurasi:
            fig_overall = go.Figure()
            for lok in lokasi_list:
                if lok in akurasi:
                    vals = [float(akurasi[lok].get(m, 0)) for m in model_names]
                    fig_overall.add_trace(go.Bar(
                        name=lok, 
                        x=model_names, 
                        y=vals,
                        marker_color=LOC_COLOR.get(lok, '#2563EB'),
                        text=[f"{v:.2f}%" for v in vals], 
                        textposition='outside',
                        textfont=dict(size=14, family='Inter', weight='bold'),
                        hovertemplate=f'<b>{lok}</b><br>Model: %{{x}}<br>Akurasi: %{{y:.2f}}%<extra></extra>'
                    ))
                    
            fig_overall.update_layout(
                barmode='group', 
                height=420, 
                plot_bgcolor='white', 
                paper_bgcolor='white',
                font=dict(family='Inter', size=12, color='#334155'),
                yaxis=dict(title='Akurasi (%)', range=[0, 115], gridcolor='#E2E8F0', gridwidth=1),
                xaxis=dict(title='', showgrid=False, showline=False),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                margin=dict(l=50, r=20, t=60, b=50), 
                bargap=0.3
            )
            st.plotly_chart(fig_overall, use_container_width=True, config={'displayModeBar': False})
            
            rows_akurasi = []
            for m in model_names:
                row = {'Model': m}
                for lok in lokasi_list:
                    if lok in akurasi:
                        row[lok] = f"{float(akurasi[lok].get(m, 0)):.2f}%"
                rows_akurasi.append(row)
            st.dataframe(pd.DataFrame(rows_akurasi), use_container_width=True, hide_index=True, height=120)
        else:
            st.info("Data akurasi tidak tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 2. EVALUASI DETAIL PER MODEL ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Evaluasi Detail per Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Klik tombol algoritma untuk melihat Classification Report dan Confusion Matrix</div>', unsafe_allow_html=True)
        
        model_icons = {'SVM': '🧠', 'Random Forest': '🌲', 'Naive Bayes': '📊'}
        model_colors = {'SVM': '#2563EB', 'Random Forest': '#10B981', 'Naive Bayes': '#F59E0B'}
        model_cmaps = {'SVM': 'Blues', 'Random Forest': 'Greens', 'Naive Bayes': 'YlOrBr'}
        
        btn_cols = st.columns(len(model_names))
        selected_model = model_names[0] if model_names else None
        
        for idx, model_name in enumerate(model_names):
            with btn_cols[idx]:
                icon = model_icons.get(model_name, '🤖')
                if st.button(f"{icon} {model_name}", key=f"btn_{model_name}", use_container_width=True):
                    selected_model = model_name
            
        if selected_model and selected_model in detail_data:
            model_detail = detail_data[selected_model]
            icon = model_icons.get(selected_model, '🤖')
            color = model_colors.get(selected_model, '#2563EB')
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{color}15,{color}05);border-left:5px solid {color};
                        border-radius:0 12px 12px 0;padding:15px 20px;margin-bottom:25px;">
                <div style="font-size:1.15rem;font-weight:700;color:{color};margin:0;">
                    {icon} Detail Evaluasi: {selected_model}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            cols_dest = st.columns(len(lokasi_list))
            report_data_for_f1 = {}
            cmap_name = model_cmaps.get(selected_model, 'Blues')
            
            for col_idx, lok in enumerate(lokasi_list):
                with cols_dest[col_idx]:
                    lok_color = LOC_COLOR.get(lok, '#2563EB')
                    st.markdown(f'<div style="background:{lok_color}10;border-radius:10px;padding:12px 16px;margin-bottom:15px;border:1px solid {lok_color}30;"><div style="font-size:0.95rem;font-weight:700;color:{lok_color};margin:0;">📍 {lok}</div></div>', unsafe_allow_html=True)
                    
                    loc_detail = model_detail.get(lok, {})
                    labels_raw = loc_detail.get('labels', ['Negatif', 'Netral', 'Positif'])
                    if isinstance(labels_raw, list):
                        labels_asli = [str(l).strip() for l in labels_raw if str(l).strip() not in ['', 'None']]
                    else:
                        labels_asli = ['Negatif', 'Netral', 'Positif']
                    report = loc_detail.get('report', {})
                    
                    if report:
                        rows = []
                        for cls in labels_asli:
                            if cls in report:
                                r = report[cls]
                                rows.append({
                                    'Kelas': cls, 
                                    'Precision': f"{float(r.get('precision',0) or 0):.2f}", 
                                    'Recall': f"{float(r.get('recall',0) or 0):.2f}", 
                                    'F1-Score': f"{float(r.get('f1-score',0) or 0):.2f}", 
                                    'Support': int(r.get('support',0) or 0)
                                })
                        if 'macro avg' in report:
                            ma = report['macro avg']
                            rows.append({
                                'Kelas': 'Macro Avg', 
                                'Precision': f"{float(ma.get('precision',0) or 0):.2f}", 
                                'Recall': f"{float(ma.get('recall',0) or 0):.2f}", 
                                'F1-Score': f"{float(ma.get('f1-score',0) or 0):.2f}", 
                                'Support': int(ma.get('support',0) or 0)
                            })
                        if 'weighted avg' in report:
                            wa = report['weighted avg']
                            rows.append({
                                'Kelas': 'Weighted Avg', 
                                'Precision': f"{float(wa.get('precision',0) or 0):.2f}", 
                                'Recall': f"{float(wa.get('recall',0) or 0):.2f}", 
                                'F1-Score': f"{float(wa.get('f1-score',0) or 0):.2f}", 
                                'Support': int(wa.get('support',0) or 0)
                            })
                        if rows:
                            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=220)
                            report_data_for_f1[lok] = report
                    
                    st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
                    
                    cm = loc_detail.get('cm', [])
                    if cm and len(cm) > 0 and len(cm) == len(labels_asli):
                        fig_cm = go.Figure(data=go.Heatmap(
                            z=cm, 
                            x=labels_asli, 
                            y=labels_asli, 
                            colorscale=cmap_name, 
                            texttemplate="%{text}", 
                            textfont={"size":18,"color":"black","family":"Inter"}, 
                            hovertemplate='Aktual: %{y}<br>Prediksi: %{x}<br>Jumlah: %{z}<extra></extra>', 
                            xgap=4, 
                            ygap=4, 
                            colorbar=dict(thickness=15, len=0.9)
                        ))
                        fig_cm.update_layout(
                            height=420, 
                            margin=dict(l=10, r=10, t=45, b=10), 
                            xaxis=dict(
                                title=dict(text='<b>Prediksi</b>', font=dict(size=11, color='#334155')), 
                                tickfont=dict(size=10, color='#334155')
                            ), 
                            yaxis=dict(
                                title=dict(text='<b>Aktual</b>', font=dict(size=11, color='#334155')), 
                                tickfont=dict(size=10, color='#334155'), 
                                autorange='reversed', 
                                scaleanchor="x", 
                                scaleratio=1
                            ), 
                            title=dict(
                                text=f'Confusion Matrix — {lok}', 
                                font=dict(size=12, color='#0F172A', family='Inter', weight='bold'), 
                                x=0.5, xanchor='center'
                            )
                        )
                        st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
            
            if report_data_for_f1:
                st.markdown('<hr style="margin:25px 0 20px;border-color:#E2E8F0">', unsafe_allow_html=True)
                all_classes = sorted(list(set(
                    [c for lok_rep in report_data_for_f1.values() for c in lok_rep.keys() if c not in ['accuracy','macro avg','weighted avg']]
                )))
                if all_classes:
                    fig_f1 = go.Figure()
                    for lok in lokasi_list:
                        if lok in report_data_for_f1:
                            f1_vals = [float(report_data_for_f1[lok].get(c,{}).get('f1-score',0) or 0) for c in all_classes]
                            fig_f1.add_trace(go.Bar(
                                name=lok, 
                                x=all_classes, 
                                y=f1_vals, 
                                marker_color=LOC_COLOR.get(lok, '#2563EB'), 
                                text=[f"{v:.2f}" for v in f1_vals], 
                                textposition='outside', 
                                textfont=dict(size=14, family='Inter', weight='bold')
                            ))
                    
                    fig_f1.update_layout(
                        title=dict(
                            text="Perbandingan F1-Score per Kelas",
                            font=dict(size=15, color='#0F172A', family='Inter', weight='bold'),
                            x=0.5,
                            xanchor='center',
                            y=0.98
                        ),
                        barmode='group',
                        height=380,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family='Inter', size=12, color='#334155'),
                        yaxis=dict(
                            title='F1-Score',
                            range=[0, 1.2],
                            gridcolor='#E2E8F0',
                            gridwidth=1
                        ),
                        xaxis=dict(
                            title='',
                            showgrid=False,
                            showline=False,
                            tickfont=dict(size=12, color='#475569')
                        ),
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=-0.2,
                            xanchor='center',
                            x=0.5
                        ),
                        margin=dict(l=50, r=20, t=80, b=70),
                        bargap=0.3
                    )
                    st.plotly_chart(fig_f1, use_container_width=True, config={'displayModeBar': False'})
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 3. RINGKASAN AKURASI ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Ringkasan Akurasi per Model & Lokasi</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">✅ >= 85% (Sangat Baik) | ⚠️ 70-84% (Cukup) | ❌ < 70% (Perlu Perbaikan)</div>', unsafe_allow_html=True)
        
        summary_rows = []
        for m in model_names:
            row = {'Model': m}
            for lok in lokasi_list:
                if lok in akurasi:
                    acc_val = float(akurasi[lok].get(m, 0))
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
            if not kd: continue
            st.markdown(f'<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">🧩 {lok}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                sx = kd.get('scatter_x', []); sy = kd.get('scatter_y', [])
                sc_clust = kd.get('scatter_cluster', [])
                if sx and sy and sc_clust:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    scatter = ax.scatter(np.array(sx), np.array(sy), c=np.array(sc_clust),
                                         cmap='tab10', alpha=0.75, edgecolor='white',
                                         linewidth=0.5, s=40, zorder=2)
                    plt.colorbar(scatter, ax=ax, label='Klaster')
                    ax.set_title(f"K-Means (K={kd['k_optimal']})", fontweight='bold', fontsize=11)
                    ax.set_xlabel('SVD Komponen 1'); ax.set_ylabel('SVD Komponen 2')
                    ax.grid(True, alpha=0.3, zorder=1)
                    fig_style(fig, ax)
                    st.pyplot(fig); plt.close(fig)
            with c2:
                st.metric("Jumlah Klaster (K)", kd['k_optimal'])
                st.metric("Silhouette Score",    kd['silhouette'])
                st.metric("Davies-Bouldin",      kd['davies_bouldin'])
                st.metric("Calinski-Harabasz",   kd['calinski_harabasz'])
            st.markdown("**Kata Dominan per Klaster:**")
            st.dataframe(pd.DataFrame(kd['kata_dominan']), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasterisasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 5: RADAR PERBANDINGAN
# ══════════════════════════════════════════════════════════
elif halaman == "radar":
    page_header("Radar Chart — Perbandingan Kualitas Clustering",
                "Perbandingan metrik evaluasi klaster antara kedua destinasi (dinormalisasi)")

    if data_klaster and len(lokasi_list) >= 2:
        metrics_keys  = ['silhouette', 'davies_bouldin', 'calinski_harabasz']
        metrics_label = ['Silhouette\n(↑ bagus)', 'Davies-Bouldin\n(↓ bagus)', 'Calinski-Harabasz\n(↑ bagus)']

        raw = {lok: [data_klaster[lok][k] for k in metrics_keys]
               for lok in lokasi_list if lok in data_klaster}

        def normalize(idx, invert=False):
            all_v = [raw[l][idx] for l in raw]
            mn, mx = min(all_v), max(all_v)
            if mx == mn: return {l: 0.5 for l in raw}
            n = {l: (raw[l][idx]-mn)/(mx-mn) for l in raw}
            return {l: 1-v for l,v in n.items()} if invert else n

        norm_sil = normalize(0)
        norm_db = normalize(1, True)
        norm_ch = normalize(2)
        normalized = {lok: [norm_sil[lok], norm_db[lok], norm_ch[lok]] for lok in raw}

        N = len(metrics_label)
        angles = [n/float(N)*2*math.pi for n in range(N)]
        angles += angles[:1]

        # ========== SIAPA MENANG DI TIAP METRIK ==========
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

        # ========== 1. RADAR CHART + TABEL NILAI ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Radar Chart Metrik Klasterisasi</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Area lebih luas = kualitas klasterisasi lebih baik · Nilai sudah dinormalisasi</div>', unsafe_allow_html=True)

        col_r, col_t = st.columns([1, 1])
        with col_r:
            fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
            ax.set_facecolor('#F8FAFC')
            for lok in raw:
                vals  = normalized[lok] + normalized[lok][:1]
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
            st.markdown("**Nilai Metrik Asli:**")
            tbl_r = pd.DataFrame({
                'Destinasi': list(raw.keys()),
                'Silhouette (↑)': [raw[l][0] for l in raw],
                'Davies-Bouldin (↓)': [raw[l][1] for l in raw],
                'Calinski-Harabasz (↑)': [raw[l][2] for l in raw],
            })
            st.dataframe(tbl_r, use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 2. PEMENANG PER METRIK (PAKAI ST.COLUMNS) ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🏆 Pemenang per Metrik</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Destinasi dengan nilai metrik terbaik di setiap aspek</div>', unsafe_allow_html=True)

        col_m1, col_m2, col_m3 = st.columns(3)
        metrik_info = [
            ('silhouette', 'Silhouette', 'Klaster terpisah jelas'),
            ('davies_bouldin', 'Davies-Bouldin', 'Klaster kompak & berjauhan'),
            ('calinski_harabasz', 'Calinski-Harabasz', 'Dispersi antar klaster tinggi'),
        ]
        icon_list = ['🟢', '🔵', '🟡']

        for col, (k, nama, desc), icon in zip([col_m1, col_m2, col_m3], metrik_info, icon_list):
            winner = pemenang[k]
            w_color = LOC_COLOR.get(winner, '#2563EB')
            nilai = raw[winner][metrics_keys.index(k)]
            with col:
                st.metric(label=f"{icon} {nama}", value=winner)
                st.caption(f"Nilai: **{nilai:.4f}**")
                st.caption(desc)

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 3. KESIMPULAN AKHIR ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">💡 Kesimpulan Perbandingan</div>', unsafe_allow_html=True)

        if is_tie:
            kesimpulan_text = (
                f"Kedua destinasi memiliki kualitas klasterisasi yang **SETARA** "
                f"(masing-masing menang di {count_win[overall_winner]} metrik). "
                f"Artinya, ulasan di kedua lokasi sama-sama terstruktur dengan baik."
            )
            badge_text = "🤝 SETARA"
            badge_color = "#F59E0B"
        else:
            loser = [l for l in raw if l != overall_winner][0]
            kesimpulan_text = (
                f"**{overall_winner}** memiliki kualitas klasterisasi yang **lebih baik** secara keseluruhan "
                f"(menang di {count_win[overall_winner]} dari 3 metrik). "
                f"Artinya, ulasan wisatawan di {overall_winner} membentuk kelompok topik "
                f"yang lebih terpisah dan terstruktur dibandingkan {loser}."
            )
            badge_text = f"🏆 {overall_winner}"
            badge_color = LOC_COLOR.get(overall_winner, '#2563EB')

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1B3A6B, #2563EB);
            border-radius: 12px; padding: 20px; color: white;
            font-size: 0.92rem; line-height: 1.7;
        ">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                <span style="background:{badge_color};color:white;padding:5px 14px;
                            border-radius:99px;font-size:0.85rem;font-weight:800;">
                    {badge_text}
                </span>
                <span style="font-size:0.78rem;opacity:0.8;">
                    Skor: {count_win[lokasi_list[0]]} - {count_win[lokasi_list[1]]}
                </span>
            </div>
            {kesimpulan_text}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 4. PANDUAN MEMBACA (PAKAI EXPANDER) ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">ℹ️ Panduan Membaca Radar Chart</div>', unsafe_allow_html=True)

        with st.expander("Klik untuk melihat penjelasan tiap metrik", expanded=False):

            st.markdown("""
            **📈 Silhouette Score**
            - **Rentang:** -1 sampai 1
            - **Arti:** Mengukur seberapa mirip data dengan klaster sendiri vs klaster lain
            - **Makin besar = makin bagus**
            - > 0.5 bagus, 0.25-0.5 cukup, < 0.25 kurang

            ---

            **📉 Davies-Bouldin Index**
            - **Rentang:** 0 sampai ∞
            - **Arti:** Rata-rata kemiripan antar klaster
            - **Makin kecil = makin bagus** (klaster kompak & berjauhan)
            - ⚠️ Di radar, nilai di-*invert* agar konsisten: garis jauh = bagus

            ---

            **📊 Calinski-Harabasz Index**
            - **Rentang:** 0 sampai ∞
            - **Arti:** Rasio jarak antar klaster vs jarak dalam klaster
            - **Makin besar = makin bagus**

            ---

            **🎯 Cara Baca Radar:**
            - **Area lebih luas** = kualitas klasterisasi lebih baik
            - **Garis jauh dari pusat** di satu sisi = unggul di metrik tersebut
            - Ketiga metrik sudah dinormalisasi sehingga bisa dibandingkan adil
            """)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Data klasterisasi belum tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 6: TOPIC MODELING (LDA)
# ══════════════════════════════════════════════════════════
elif halaman == "topik":
    page_header("Topic Modeling (LDA) — Distribusi Topik",
                "Latent Dirichlet Allocation untuk menemukan tema tersembunyi dalam ulasan")
    kpi_row()

    if data_topik:
        # ========== 1. DONUT CHART DISTRIBUSI TOPIK ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Distribusi Topik (Donut Chart Interaktif)</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Proporsi jumlah ulasan per topik yang terdeteksi oleh LDA</div>', unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns(2)
        for col, lok in zip([col_d1, col_d2], lokasi_list):
            with col:
                td = data_topik.get(lok, {})
                labels = td.get('labels', [])
                values = td.get('values', [])
                if labels and values:
                    fig_donut = go.Figure(data=[go.Pie(
                        labels=labels, values=values,
                        hole=0.55,
                        marker=dict(colors=COLORS_TOPIC[:len(labels)],
                                   line=dict(color='white', width=2)),
                        textinfo='percent',
                        texttemplate='%{percent:.1f}%',
                        textfont=dict(size=11, color='white', family='Inter'),
                        hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent:.1f}%<extra></extra>',
                        pull=[0.02]*len(labels)
                    )])
                    fig_donut.update_layout(
                        title=dict(text=lok, font=dict(size=14, color='#0F172A', weight='bold'),
                                   x=0.5, xanchor='center'),
                        height=400,
                        margin=dict(t=50, b=20, l=20, r=20),
                        showlegend=True,
                        legend=dict(font=dict(size=9), orientation='h', yanchor='bottom', y=-0.15)
                    )
                    st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.info(f"Tidak ada data topik untuk {lok}")
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 2. TABEL DISTRIBUSI TOPIK ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Tabel Distribusi Topik</div>', unsafe_allow_html=True)
        
        rows_topik = []
        for lok in lokasi_list:
            td = data_topik.get(lok, {})
            labels = td.get('labels', [])
            values = td.get('values', [])
            keywords = td.get('keywords', [])
            for i, (label, val) in enumerate(zip(labels, values)):
                rows_topik.append({
                    'Destinasi': lok,
                    'Topik': f"Topik {i}",
                    'Label': label,
                    'Jumlah Ulasan': val,
                    'Kata Kunci Utama': keywords[i] if i < len(keywords) else ''
                })
        
        if rows_topik:
            st.dataframe(pd.DataFrame(rows_topik), use_container_width=True, hide_index=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 3. TOP 10 KATA KUNCI PER TOPIK (BAR CHART) ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Top 10 Kata Kunci Per Topik</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Bobot kata tertinggi dalam setiap topik berdasarkan distribusi LDA</div>', unsafe_allow_html=True)
        
        for lok in lokasi_list:
            td = data_topik.get(lok, {})
            keywords_detail = td.get('keywords_detail', {})
            labels_dict = td.get('labels', [])
            
            if not keywords_detail:
                st.info(f"Tidak ada data kata kunci detail untuk {lok}")
                continue
            
            n_topics = len(keywords_detail)
            st.markdown(f"**{lok}**")
            
            n_cols = min(n_topics, 3)
            n_rows = (n_topics + n_cols - 1) // n_cols
            
            for row_idx in range(n_rows):
                cols_chart = st.columns(n_cols)
                for col_idx in range(n_cols):
                    topic_idx = row_idx * n_cols + col_idx
                    if topic_idx >= n_topics:
                        continue
                    
                    with cols_chart[col_idx]:
                        topic_key = str(topic_idx)
                        if topic_key not in keywords_detail:
                            continue
                        
                        topic_data = keywords_detail[topic_key]
                        words = [item[0] for item in topic_data]
                        weights = [item[1] for item in topic_data]
                        
                        # Normalize weights for display
                        max_w = max(weights) if weights else 1
                        norm_weights = [w/max_w for w in weights]
                        
                        label = labels_dict[topic_idx] if topic_idx < len(labels_dict) else f"Topik {topic_idx}"
                        color = COLORS_TOPIC[topic_idx % len(COLORS_TOPIC)]
                        
                        fig_bar = go.Figure()
                        fig_bar.add_trace(go.Bar(
                            y=words[::-1],
                            x=norm_weights[::-1],
                            orientation='h',
                            marker_color=color,
                            text=[f"{w:.4f}" for w in weights[::-1]],
                            textposition='outside',
                            textfont=dict(size=9, color='#334155'),
                            hovertemplate='Kata: %{y}<br>Bobot: %{x:.4f}<extra></extra>'
                        ))
                        fig_bar.update_layout(
                            title=dict(text=f"Topik {topic_idx}: {label}",
                                      font=dict(size=10, color=color, weight='bold'),
                                      x=0.5, xanchor='center'),
                            height=320,
                            margin=dict(t=45, b=20, l=100, r=50),
                            xaxis=dict(showticklabels=False, showgrid=False, showline=False, zeroline=False),
                            yaxis=dict(tickfont=dict(size=10), showgrid=False, showline=False),
                            plot_bgcolor='white',
                            paper_bgcolor='white'
                        )
                        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 4. WORDCLOUD PER TOPIK ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">☁️ WordCloud Per Topik</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Visualisasi kata kunci dalam bentuk awan kata untuk setiap topik</div>', unsafe_allow_html=True)
        
        for lok in lokasi_list:
            td = data_topik.get(lok, {})
            keywords_detail = td.get('keywords_detail', {})
            labels_dict = td.get('labels', [])
            
            if not keywords_detail:
                st.info(f"Tidak ada data wordcloud untuk {lok}")
                continue
            
            n_topics = len(keywords_detail)
            st.markdown(f"**{lok}**")
            
            n_cols = min(n_topics, 3)
            n_rows = (n_topics + n_cols - 1) // n_cols
            
            for row_idx in range(n_rows):
                cols_wc = st.columns(n_cols)
                for col_idx in range(n_cols):
                    topic_idx = row_idx * n_cols + col_idx
                    if topic_idx >= n_topics:
                        continue
                    
                    with cols_wc[col_idx]:
                        topic_key = str(topic_idx)
                        if topic_key not in keywords_detail:
                            continue
                        
                        topic_data = keywords_detail[topic_key]
                        wc_dict = {item[0]: float(item[1]) for item in topic_data}
                        
                        label = labels_dict[topic_idx] if topic_idx < len(labels_dict) else f"Topik {topic_idx}"
                        
                        try:
                            wc = WordCloud(
                                width=400, height=250,
                                background_color='white',
                                colormap='viridis',
                                prefer_horizontal=0.9,
                                min_font_size=8,
                                max_font_size=50
                            ).generate_from_frequencies(wc_dict)
                            
                            fig_wc, ax_wc = plt.subplots(figsize=(5, 3))
                            ax_wc.imshow(wc, interpolation='bilinear')
                            ax_wc.axis('off')
                            ax_wc.set_title(f"Topik {topic_idx}: {label}", 
                                          fontsize=10, fontweight='bold', color='#0F172A')
                            fig_wc.tight_layout()
                            st.pyplot(fig_wc)
                            plt.close(fig_wc)
                        except Exception as e:
                            st.warning(f"WordCloud gagal: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data topic modeling tidak tersedia.")


# ══════════════════════════════════════════════════════════
# HALAMAN 7: TRENDING TOPIK
# ══════════════════════════════════════════════════════════
elif halaman == "trending":
    page_header("Trending Topik dari Waktu ke Waktu",
                "Analisis tren topik berdasarkan bulan publikasi ulasan")
    kpi_row()

    if data_trending:
        # ========== 1. GRAFIK TRENDING TOPIK ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📈 Grafik Trending Topik Per Bulan</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Pergerakan jumlah ulasan per topik dari waktu ke waktu</div>', unsafe_allow_html=True)
        
        col_t1, col_t2 = st.columns(2)
        for col, lok in zip([col_t1, col_t2], lokasi_list):
            with col:
                td = data_trending.get(lok, {})
                bulan = td.get('bulan', [])
                topik_data = td.get('topik', {})
                
                if not bulan or not topik_data:
                    st.info(f"Tidak ada data trending untuk {lok}")
                    continue
                
                fig_trend = go.Figure()
                for i, (topik_name, values) in enumerate(topik_data.items()):
                    fig_trend.add_trace(go.Scatter(
                        x=bulan, y=values,
                        mode='lines+markers',
                        name=topik_name,
                        line=dict(color=COLORS_TOPIC[i % len(COLORS_TOPIC)], width=2.5),
                        marker=dict(size=6),
                        hovertemplate=f'<b>{topik_name}</b><br>Bulan: %{{x}}<br>Jumlah: %{{y}}<extra></extra>'
                    ))
                
                fig_trend.update_layout(
                    title=dict(text=lok, font=dict(size=14, color='#0F172A', weight='bold'),
                              x=0.5, xanchor='center'),
                    height=420,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(size=11, color='#334155'),
                    xaxis=dict(title='Bulan', tickfont=dict(size=9), 
                              tickangle=45, showgrid=False, showline=False),
                    yaxis=dict(title='Jumlah Ulasan', gridcolor='#E2E8F0',
                              showline=False, zeroline=False),
                    legend=dict(font=dict(size=8), orientation='h', 
                               yanchor='bottom', y=-0.25, x=0.5, xanchor='center'),
                    margin=dict(t=50, b=100, l=50, r=20)
                )
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 2. INSIGHT OTOMATIS ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">💡 Insight Otomatis</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Analisis otomatis berdasarkan data trending yang tersedia</div>', unsafe_allow_html=True)
        
        col_ins1, col_ins2, col_ins3 = st.columns(3)
        
        for lok in lokasi_list:
            td = data_trending.get(lok, {})
            topik_data = td.get('topik', {})
            
            if not topik_data:
                continue
            
            # Find peak topic
            all_max = {k: max(v) for k, v in topik_data.items()}
            peak_topic = max(all_max.keys(), key=lambda k: all_max[k])
            peak_value = all_max[peak_topic]
            
            # Find declining topic
            declining_topic = None
            max_decline = 0
            for k, v in topik_data.items():
                if len(v) >= 6:
                    early_avg = sum(v[:3]) / 3
                    late_avg = sum(v[-3:]) / 3
                    if early_avg > 0:
                        decline_pct = ((late_avg - early_avg) / early_avg) * 100
                        if decline_pct < max_decline:
                            max_decline = decline_pct
                            declining_topic = k
            
            with col_ins1:
                st.metric(f"📍 {lok[:15]}... - Puncak", peak_topic[:25])
                st.caption(f"Jumlah: {peak_value} ulasan")
            
            with col_ins2:
                if declining_topic:
                    st.metric(f"📍 {lok[:15]}... - Turun", declining_topic[:25])
                    st.caption(f"Penurunan: {max_decline:.0f}%")
                else:
                    st.metric(f"📍 {lok[:15]}... - Turun", "N/A")
                    st.caption("Data tidak cukup")
            
            with col_ins3:
                n_bulan = len(td.get('bulan', []))
                st.metric(f"📍 {lok[:15]}... - Periode", f"{n_bulan} bulan")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 3. DETAIL DATA PER BULAN (TABEL) ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Detail Data Per Bulan</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Klik tab destinasi untuk melihat label angka lengkap</div>', unsafe_allow_html=True)
        
        tabs_trend = st.tabs(lokasi_list)
        for tab, lok in zip(tabs_trend, lokasi_list):
            with tab:
                td = data_trending.get(lok, {})
                bulan = td.get('bulan', [])
                topik_data = td.get('topik', {})
                
                if not bulan or not topik_data:
                    st.info(f"Tidak ada data untuk {lok}")
                    continue
                
                rows_trend = []
                for i, b in enumerate(bulan):
                    row = {'Bulan': b}
                    for topik_name, values in topik_data.items():
                        row[topik_name] = values[i] if i < len(values) else 0
                    rows_trend.append(row)
                
                if rows_trend:
                    st.dataframe(pd.DataFrame(rows_trend), use_container_width=True, 
                                hide_index=True, height=400)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data trending topik tidak tersedia. Pastikan `trending` ada di dashboard_data.json")


# ══════════════════════════════════════════════════════════
# HALAMAN 8: WORDCLOUD MASALAH
# ══════════════════════════════════════════════════════════
elif halaman == "wordcloud":
    page_header("WordCloud Kata Bermasalah",
                "Analisis kata-kata negatif yang muncul dalam ulasan")
    kpi_row()

    data_wc_masalah = DATA.get('wordcloud_masalah', {})

    if data_wc_masalah:
        # ========== 1. WORDCLOUD VISUALISASI ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">☁️ WordCloud Kata Negatif</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Ukuran kata menunjukkan frekuensi kemunculan dalam ulasan negatif</div>', unsafe_allow_html=True)
        
        col_wc1, col_wc2 = st.columns(2)
        for col, lok in zip([col_wc1, col_wc2], lokasi_list):
            with col:
                wc_data = data_wc_masalah.get(lok, {})
                top_words = wc_data.get('top_words', [])
                
                if not top_words:
                    st.info(f"Tidak ada data wordcloud untuk {lok}")
                    continue
                
                wc_dict = {w: float(c) for w, c in top_words[:50]}
                
                try:
                    wc = WordCloud(
                        width=500, height=350,
                        background_color='white',
                        colormap='Reds',
                        prefer_horizontal=0.8,
                        min_font_size=10,
                        max_font_size=80,
                        collocations=False
                    ).generate_from_frequencies(wc_dict)
                    
                    fig_wc, ax_wc = plt.subplots(figsize=(7, 5))
                    ax_wc.imshow(wc, interpolation='bilinear')
                    ax_wc.axis('off')
                    ax_wc.set_title(lok, fontsize=14, fontweight='bold', color='#0F172A', pad=15)
                    fig_wc.tight_layout()
                    st.pyplot(fig_wc)
                    plt.close(fig_wc)
                    
                    st.caption(f"📊 Total {len(top_words)} kata unik dalam ulasan negatif")
                except Exception as e:
                    st.error(f"Gagal membuat wordcloud: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 2. TOP 10 KATA BERMASALAH (BAR CHART) ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Top 10 Kata Bermasalah</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Sepuluh kata dengan frekuensi tertinggi dalam ulasan negatif</div>', unsafe_allow_html=True)
        
        col_bar1, col_bar2 = st.columns(2)
        for col, lok in zip([col_bar1, col_bar2], lokasi_list):
            with col:
                wc_data = data_wc_masalah.get(lok, {})
                top_words = wc_data.get('top_words', [])
                
                if not top_words:
                    st.info(f"Tidak ada data untuk {lok}")
                    continue
                
                top_10 = top_words[:10]
                words = [w for w, c in top_10][::-1]
                counts = [c for w, c in top_10][::-1]
                
                color = LOC_COLOR.get(lok, '#EF4444')
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    y=words,
                    x=counts,
                    orientation='h',
                    marker_color=color,
                    text=counts,
                    textposition='outside',
                    textfont=dict(size=11, color='#0F172A', weight='bold'),
                    hovertemplate='Kata: %{y}<br>Frekuensi: %{x}<extra></extra>'
                ))
                fig_bar.update_layout(
                    title=dict(text=lok, font=dict(size=13, color='#0F172A', weight='bold'),
                              x=0.5, xanchor='center'),
                    height=400,
                    margin=dict(t=50, b=30, l=120, r=60),
                    xaxis=dict(title='Frekuensi', gridcolor='#E2E8F0',
                              showline=False, zeroline=False),
                    yaxis=dict(tickfont=dict(size=11), showgrid=False, showline=False),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)

        # ========== 3. DETAIL SELURUH KATA NEGATIF (TABEL) ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Detail Seluruh Kata Negatif</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Daftar lengkap kata yang muncul dalam ulasan negatif beserta frekuensinya</div>', unsafe_allow_html=True)
        
        tabs_neg = st.tabs(lokasi_list)
        for tab, lok in zip(tabs_neg, lokasi_list):
            with tab:
                wc_data = data_wc_masalah.get(lok, {})
                all_words = wc_data.get('all_words', [])
                
                if not all_words:
                    st.info(f"Tidak ada data untuk {lok}")
                    continue
                
                rows_neg = []
                for i, (word, count) in enumerate(all_words, 1):
                    rows_neg.append({
                        'Peringkat': i,
                        'Kata': word,
                        'Frekuensi': count
                    })
                
                if rows_neg:
                    st.dataframe(pd.DataFrame(rows_neg), use_container_width=True, 
                                hide_index=True, height=500)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data wordcloud masalah tidak tersedia. Pastikan `wordcloud_masalah` ada di dashboard_data.json")

# ══════════════════════════════════════════════════════════
# HALAMAN 9: JARINGAN ANTAR DESTINASI (BRIDGE WORDS)
# ══════════════════════════════════════════════════════════
elif halaman == "jaringan":
    page_header(
        "Jaringan Bridge Words Antar Destinasi",
        "Kata yang sama-sama dominan di kedua lokasi — pola keluhan & pujian serupa"
    )
    kpi_row()

    # ========== GAMBAR NETWORK ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🕸️ Visualisasi Jaringan Bridge Words</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Node besar = destinasi · Node kuning = bridge word · Node kecil = kata eksklusif</div>', unsafe_allow_html=True)

    img_b64 = DATA.get('bridge_image_base64', '')
    if img_b64:
        st.markdown(
            f'<img src="data:image/png;base64,{img_b64}" '
            f'style="width:100%;max-width:950px;margin:0 auto;display:block;'
            f'border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.08);">',
            unsafe_allow_html=True
        )
    elif os.path.exists('bridge_words_network.png'):
        st.image('bridge_words_network.png', use_container_width=True)
    else:
        st.warning("File gambar bridge words belum tersedia.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ========== PENJELASAN ==========
    expl = DATA.get('bridge_explanation', {})
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📖 Penjelasan Bridge Words</div>', unsafe_allow_html=True)

    if expl:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border-radius:12px;
                    padding:18px 22px;margin-bottom:20px;border-left:5px solid #2563EB;
                    font-size:0.92rem;color:#334155;line-height:1.7;">
            {expl.get('deskripsi', '')}
        </div>
        """, unsafe_allow_html=True)

        total = expl.get('total_bridge', 0)
        daftar = expl.get('daftar_bridge', [])
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;background:white;
                    border:2px solid #E2E8F0;border-radius:12px;padding:14px 20px;margin-bottom:20px;">
            <div style="background:#FEF3C7;color:#D97706;font-size:1.6rem;font-weight:800;
                        width:60px;height:60px;border-radius:12px;display:flex;
                        align-items:center;justify-content:center;">{total}</div>
            <div>
                <div style="font-size:0.78rem;color:#64748B;font-weight:600;
                            text-transform:uppercase;letter-spacing:0.05em;">
                    Total Bridge Words Ditemukan</div>
                <div style="font-size:0.88rem;color:#475569;margin-top:2px;">
                    {', '.join(daftar[:20])}{'...' if len(daftar) > 20 else ''}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if daftar:
            st.dataframe(
                pd.DataFrame({'No': range(1, len(daftar)+1), 'Bridge Word': daftar}),
                use_container_width=True, hide_index=True,
                height=min(300, 40 + len(daftar)*35)
            )

        interp = expl.get('interpretasi', [])
        if interp:
            st.markdown('<hr style="margin:20px 0 16px;border-color:#E2E8F0">', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:14px;">🔍 Interpretasi per Kategori</div>', unsafe_allow_html=True)

            icons = {'Pujian': '✅', 'Keluhan': '❌', 'Aktivitas': '🥾', 'Kuliner': '🍽️', 'Fasilitas': '🏗️', 'Pemandangan': '🌄', 'Lain': '📌'}

            for item in interp:
                kat = item.get('kategori', '')
                kata = item.get('kata', [])
                penjelasan = item.get('penjelasan', '')
                icon = '📌'
                for k, ic in icons.items():
                    if k.lower() in kat.lower():
                        icon = ic
                        break

                badges = ''.join(
                    f'<span style="background:#DBEAFE;color:#1E40AF;padding:3px 10px;'
                    f'border-radius:99px;font-size:0.78rem;font-weight:600;">{w}</span>'
                    for w in kata
                ) if kata else '<span style="color:#94A3B8;font-size:0.85rem;">Tidak ada kata dalam kategori ini</span>'

                st.markdown(f"""
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;
                            padding:14px 18px;margin-bottom:12px;">
                    <div style="font-size:0.92rem;font-weight:700;color:#0F172A;margin-bottom:6px;">
                        {icon} {kat}</div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;">{badges}</div>
                    <div style="font-size:0.85rem;color:#475569;line-height:1.6;">{penjelasan}</div>
                </div>
                """, unsafe_allow_html=True)

        if expl.get('kesimpulan'):
            st.markdown('<hr style="margin:20px 0 16px;border-color:#E2E8F0">', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1B3A6B,#2563EB);border-radius:12px;
                        padding:18px 22px;color:white;font-size:0.92rem;line-height:1.7;">
                <div style="font-size:0.78rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.08em;opacity:0.75;margin-bottom:6px;">💡 KESIMPULAN</div>
                {expl['kesimpulan']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Data penjelasan bridge words belum tersedia. Jalankan sel simpan JSON di Colab.")

    st.markdown('</div>', unsafe_allow_html=True)
