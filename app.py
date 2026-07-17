# =========================================================
# DASHBOARD PERBANDINGAN PARIWISATA
# Desa Wae Rebo vs Taman Nasional Komodo
# =========================================================
import json
import math
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
import folium
import plotly.graph_objects as go
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
# CSS
# ----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F0F4F8 !important; }
[data-testid="stSidebar"] { background: #1B3A6B !important; padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebarUserContent"] { padding: 0 10px !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 2px !important; }
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important; border-radius: 8px !important;
    padding: 7px 10px !important; font-size: 0.87rem !important;
    cursor: pointer !important; transition: background .15s !important; width: 100% !important;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,.12) !important; }
[data-testid="stSidebar"] .stRadio label span { color: #E2E8F0 !important; font-size: 0.87rem !important; }
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child { display: none !important; }
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1400px !important; }
.dash-header {
    background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 100%);
    border-radius: 16px; padding: 22px 32px; margin-bottom: 24px; min-height: 84px;
    box-sizing: border-box; display: flex; flex-direction: column; justify-content: center;
}
.dash-header-title { color: white; font-size: 1.5rem; font-weight: 800; margin: 0; line-height: 1.25; }
.dash-header-sub { color: rgba(255,255,255,.75); font-size: 0.85rem; margin: 6px 0 0; line-height: 1.4; }
.kpi-row { display: flex; gap: 16px; margin-bottom: 24px; }
.kpi-card {
    flex: 1; background: white; border-radius: 14px; padding: 20px 22px;
    border-top: 5px solid; box-shadow: 0 2px 12px rgba(0,0,0,.06);
    box-sizing: border-box; min-height: 152px; position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; right: -20px; bottom: -20px;
    width: 80px; height: 80px; border-radius: 50%; background: rgba(0,0,0,.03);
}
.kpi-card.blue { border-color: #2563EB; }
.kpi-card.red  { border-color: #EF4444; }
.kpi-label  { font-size: 0.78rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.kpi-value  { font-size: 2rem; font-weight: 800; color: #0F172A; line-height: 1.1; margin: 4px 0 2px; }
.sec-card {
    background: white; border-radius: 14px; padding: 22px 26px; margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,.05); box-sizing: border-box;
}
.sec-title { font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 0 0 4px; display: flex; align-items: center; gap: 8px; }
.sec-sub { font-size: 0.82rem; color: #64748B; margin: 0 0 18px; }
hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; box-shadow: 0 1px 6px rgba(0,0,0,.06) !important; }
.nav-section { font-size: 0.68rem; font-weight: 700; color: #64748B; letter-spacing: .1em; text-transform: uppercase; padding: 16px 4px 6px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# MATPLOTLIB STYLE
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
def load_data():
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        required_keys = ['ringkasan', 'lokasi_list']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        defaults = {'bridge': {}, 'rating': {}, 'klasifikasi': {}, 'klaster': {}, 'topik': {}, 'trending': {}, 'centrality': {}, 'ulasan_detail': {}, 'temporal': {}, 'wordcloud': {}}
        for key, default_val in defaults.items():
            if key not in data:
                data[key] = default_val
        return data
    except FileNotFoundError:
        st.error("❌ **File `dashboard_data.json` tidak ditemukan!** Pastikan file ini ada di folder yang sama dengan `app.py`.")
        st.stop()
    except json.JSONDecodeError as e:
        st.error(f"❌ **Error parsing JSON:** {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ **Error loading data:** {e}")
        st.stop()

DATA = load_data()
ringkasan        = DATA['ringkasan']
bridge           = DATA.get('bridge', {})
lokasi_list      = DATA['lokasi_list']
data_rating      = DATA.get('rating', {})
data_klasifikasi = DATA.get('klasifikasi', {})
data_klaster     = DATA.get('klaster', {})
data_topik       = DATA.get('topik', {})
data_trending    = DATA.get('trending', {})
data_centrality  = DATA.get('centrality', {})
data_ulasan      = DATA.get('ulasan_detail', {})
data_temporal    = DATA.get('temporal', {})
data_wordcloud   = DATA.get('wordcloud', {})

LOC_COLOR = {'Desa Wae Rebo': '#2563EB', 'Taman Nasional Komodo': '#EF4444'}
for i, lok in enumerate(lokasi_list):
    if lok not in LOC_COLOR:
        LOC_COLOR[lok] = ['#2563EB', '#EF4444', '#10B981', '#F59E0B'][i % 4]
COLORS_TOPIC = ['#4338CA', '#0891B2', '#D97706', '#059669', '#DC2626', '#7C3AED', '#DB2777', '#2563EB']

# ----------------------------------------------------------
# SIDEBAR - DIPERBAIKI (label tidak boleh kosong)
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
    halaman_label = st.radio("Pilih Halaman", list(MENU.keys()), label_visibility="collapsed")
    halaman = MENU[halaman_label]
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem;color:#64748B;text-align:center;line-height:1.6;">
        Universitas Budi Luhur<br>Teknik Informatika · 2025<br>
        <span style="color:#93C5FD;">Text Mining & Sentiment Analysis</span>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# HELPERS - DIPERBAIKI (use_container_width diganti width)
# ----------------------------------------------------------
def page_header(title, subtitle=""):
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-header-title">{title}</div>
        <div class="dash-header-sub">{subtitle if subtitle else "Analisis Ulasan Google Maps · Desa Wae Rebo vs Taman Nasional Komodo"}</div>
    </div>
    """, unsafe_allow_html=True)

def kpi_row():
    cols = st.columns(len(ringkasan))
    for col, r in zip(cols, ringkasan):
        neg_pct = r['persen_negatif']
        color = "red" if neg_pct > 50 else "green"
        col.markdown(f"""
        <div class="kpi-card {color}" style="margin-bottom:4px">
            <div class="kpi-label">{r['lokasi']}</div>
            <div style="display:flex;align-items:baseline;gap:12px;margin:6px 0 4px">
                <div class="kpi-value">{neg_pct}%</div>
                <div style="font-size:0.78rem;color:#64748B">negatif</div>
            </div>
            <div style="font-size:0.8rem;color:#475569;margin-bottom:8px">dari <b>{r['total_ulasan']:,}</b> total ulasan</div>
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

def safe_get(dictionary, key, default=None):
    if dictionary is None: return default
    return dictionary.get(key, default)

# ══════════════════════════════════════════════════════════
# HALAMAN 1: BERANDA & PETA
# ══════════════════════════════════════════════════════════
if halaman == "beranda":
    page_header("RANCANGAN DASHBOARD PERBANDINGAN PARIWISATA", "Analisis Ulasan Google Maps · Desa Wae Rebo vs Taman Nasional Komodo · Nusa Tenggara Timur")
    kpi_row()
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📍 Peta Lokasi Destinasi Wisata</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">🟢 Hijau = positif dominan | 🔴 Merah = negatif >50%</div>', unsafe_allow_html=True)
    try:
        peta = folium.Map(location=[sum(r['lat'] for r in ringkasan)/len(ringkasan), sum(r['lon'] for r in ringkasan)/len(ringkasan)], zoom_start=9, tiles="CartoDB positron")
        for r in ringkasan:
            warna_m = "green" if r['status_warna'] == "Hijau" else "red"
            popup = (f"<b>{r['lokasi']}</b><br>📝 Total: {r['total_ulasan']}<br>✅ Positif: {r['jumlah_positif']}<br>❌ Negatif: {r['jumlah_negatif']}<br>% Negatif: <b>{r['persen_negatif']}%</b>")
            folium.Marker([r['lat'], r['lon']], popup=folium.Popup(popup, max_width=240), tooltip=r['lokasi'], icon=folium.Icon(color=warna_m, icon='info-sign')).add_to(peta)
        st_folium(peta, width="stretch", height=430)
    except Exception as e:
        st.error(f"Error loading map: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📋 Ringkasan Perbandingan</div>', unsafe_allow_html=True)
    df_ring = pd.DataFrame([{'Destinasi': r['lokasi'], 'Total Ulasan': r['total_ulasan'], 'Positif': r['jumlah_positif'], 'Negatif': r['jumlah_negatif'], 'Netral': r['jumlah_netral'], '% Negatif': f"{r['persen_negatif']}%", 'Status': "⚠️ Perlu Perhatian" if r['persen_negatif'] > 50 else "✅ Cukup Baik"} for r in ringkasan])
    st.dataframe(df_ring, width="stretch", hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN 2: SENTIMEN & RATING 
# ══════════════════════════════════════════════════════════
elif halaman == "sentimen":
    page_header("Analisis Sentimen & Distribusi Rating")
    kpi_row()
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📊 Jumlah Sentimen per Destinasi</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Positif = Rating 4-5⭐ · Negatif = Rating 1-2⭐ · Netral = Rating 3⭐</div>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    sentimen_labels = ['Positif', 'Negatif', 'Netral']
    sentimen_colors = ['#10B981', '#EF4444', '#94A3B8']
    for col, r in zip([col_chart1, col_chart2], ringkasan):
        with col:
            lokasi = r['lokasi']
            values = [r['jumlah_positif'], r['jumlah_negatif'], r['jumlah_netral']]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sentimen_labels, y=values, marker_color=sentimen_colors, text=values, textposition='outside', textfont=dict(size=15, color='#0F172A', family='Inter', weight='bold'), marker_line_color='white', marker_line_width=2.5))
            fig.update_layout(title=dict(text=lokasi, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center', y=0.95), height=380, plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter', size=12, color='#334155'), xaxis=dict(tickfont=dict(size=12, color='#475569'), showgrid=False), yaxis=dict(title='Jumlah Ulasan', titlefont=dict(size=11, color='#64748B'), tickfont=dict(size=11, color='#64748B'), gridcolor='#E2E8F0', showline=False, range=[0, max(values) * 1.2] if max(values) > 0 else [0, 10]), margin=dict(l=50, r=20, t=50, b=50), bargap=0.35)
            st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Sentimen</div>', unsafe_allow_html=True)
    tab_positif, tab_negatif, tab_netral = st.tabs(["🟢 Positif", "🔴 Negatif", "🟡 Netral"])
    for tab, sentimen_key, sentimen_label in [(tab_positif, 'contoh_positif', 'Positif'), (tab_negatif, 'contoh_negatif', 'Negatif'), (tab_netral, 'contoh_netral', 'Netral')]:
        with tab:
            col_tabel1, col_tabel2 = st.columns(2)
            for col, r in zip([col_tabel1, col_tabel2], ringkasan):
                with col:
                    lokasi = r['lokasi']
                    contoh_list = safe_get(safe_get(data_ulasan, lokasi, {}), sentimen_key, [])
                    st.markdown(f'**{lokasi}**')
                    if contoh_list:
                        rows = []
                        for ulasan in contoh_list[:5]:
                            rating = safe_get(ulasan, 'rating', 0)
                            stars = '⭐' * int(rating) if rating else ''
                            rows.append({'Penulis': safe_get(ulasan, 'author', 'Anonim'), 'Rating': stars, 'Tanggal': safe_get(ulasan, 'date', ''), 'Ulasan': safe_get(ulasan, 'review', 'Tidak ada teks')})
                        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                    else:
                        st.info(f"Tidak ada contoh ulasan {sentimen_label.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⭐ Distribusi Rating Bintang</div>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    warna_bintang = {1: '#EF4444', 2: '#F97316', 3: '#F59E0B', 4: '#84CC16', 5: '#10B981'}
    for col, lok in zip([col_chart1, col_chart2], lokasi_list):
        with col:
            rc = safe_get(data_rating, lok, {})
            if rc:
                ratings = sorted([int(r) for r in rc.keys()])
                values = [int(rc[str(r)]) for r in ratings]
                colors = [warna_bintang.get(r, '#94A3B8') for r in ratings]
                labels = [f'{r} ⭐' for r in ratings]
                fig = go.Figure()
                fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition='outside', textfont=dict(size=12, color='#0F172A', family='Inter', weight='bold'), marker_line_color='white', marker_line_width=2.5))
                fig.update_layout(title=dict(text=lok, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5), height=380, plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter', size=12, color='#334155'), xaxis=dict(tickfont=dict(size=12, color='#475569'), showgrid=False), yaxis=dict(title='Jumlah Ulasan', gridcolor='#E2E8F0', showline=False, range=[0, max(values) * 1.2] if max(values) > 0 else [0, 10]), margin=dict(l=50, r=20, t=50, b=50), bargap=0.35)
                st.plotly_chart(fig, width="stretch", config={'displayModeBar': False})
            else:
                st.info("Data rating tidak tersedia.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Rating Bintang</div>', unsafe_allow_html=True)
    tab_1, tab_2, tab_3, tab_4, tab_5 = st.tabs(["⭐ 1", "⭐⭐ 2", "⭐⭐⭐ 3", "⭐⭐⭐⭐ 4", "⭐⭐⭐⭐⭐ 5"])
    for tab, rating_key, rating_label in [(tab_1, "rating_1", "1 Bintang"), (tab_2, "rating_2", "2 Bintang"), (tab_3, "rating_3", "3 Bintang"), (tab_4, "rating_4", "4 Bintang"), (tab_5, "rating_5", "5 Bintang")]:
        with tab:
            col_tabel1, col_tabel2 = st.columns(2)
            for col, r in zip([col_tabel1, col_tabel2], ringkasan):
                with col:
                    lokasi = r['lokasi']
                    contoh_list = safe_get(safe_get(data_ulasan, lokasi, {}), rating_key, [])
                    st.markdown(f'**{lokasi}**')
                    if contoh_list:
                        rows = []
                        for ulasan in contoh_list[:5]:
                            rating = safe_get(ulasan, 'rating', 0)
                            stars = '⭐' * int(rating) if rating else ''
                            rows.append({'Penulis': safe_get(ulasan, 'author', 'Anonim'), 'Rating': stars, 'Tanggal': safe_get(ulasan, 'date', ''), 'Ulasan': safe_get(ulasan, 'review', 'Tidak ada teks')})
                        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
                    else:
                        st.info(f"Tidak ada contoh ulasan {rating_label.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN 3: KLASIFIKASI 
# ══════════════════════════════════════════════════════════
elif halaman == "klasifikasi":
    page_header("Perbandingan Akurasi Model Klasifikasi", "SVM · Random Forest · Naive Bayes — per destinasi wisata")
    kpi_row()
    if data_klasifikasi:
        model_names = safe_get(data_klasifikasi, 'model_names', [])
        akurasi = safe_get(data_klasifikasi, 'akurasi', {})
        detail_data = safe_get(data_klasifikasi, 'detail', {})
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Perbandingan Akurasi Antar Model</div>', unsafe_allow_html=True)
        if model_names and akurasi:
            fig_overall = go.Figure()
            for lok in lokasi_list:
                if lok in akurasi:
                    vals = [float(safe_get(akurasi[lok], m, 0)) for m in model_names]
                    fig_overall.add_trace(go.Bar(name=lok, x=model_names, y=vals, marker_color=LOC_COLOR.get(lok, '#2563EB'), text=[f"{v:.2f}%" for v in vals], textposition='outside', textfont=dict(size=14, family='Inter', weight='bold')))
            fig_overall.update_layout(barmode='group', height=420, plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter', size=12, color='#334155'), yaxis=dict(title='Akurasi (%)', range=[0, 115], gridcolor='#E2E8F0'), xaxis=dict(showgrid=False, showline=False), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5), margin=dict(l=50, r=20, t=60, b=50), bargap=0.3)
            st.plotly_chart(fig_overall, width="stretch", config={'displayModeBar': False})
            rows_akurasi = []
            for m in model_names:
                row = {'Model': m}
                for lok in lokasi_list:
                    if lok in akurasi: row[lok] = f"{float(safe_get(akurasi[lok], m, 0)):.2f}%"
                rows_akurasi.append(row)
            st.dataframe(pd.DataFrame(rows_akurasi), width="stretch", hide_index=True, height=120)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Evaluasi Detail per Model</div>', unsafe_allow_html=True)
        model_icons = {'SVM': '🧠', 'Random Forest': '🌲', 'Naive Bayes': '📊'}
        model_colors = {'SVM': '#2563EB', 'Random Forest': '#10B981', 'Naive Bayes': '#F59E0B'}
        model_cmaps = {'SVM': 'Blues', 'Random Forest': 'Greens', 'Naive Bayes': 'YlOrBr'}
        btn_cols = st.columns(len(model_names))
        selected_model = None
        for idx, model_name in enumerate(model_names):
            with btn_cols[idx]:
                icon = model_icons.get(model_name, '🤖')
                clicked = st.button(f"{icon} {model_name}", key=f"btn_{model_name}", use_container_width=True)
                if clicked: selected_model = model_name
        if selected_model is None: selected_model = model_names[0] if model_names else None
        
        if selected_model and selected_model in detail_data:
            model_detail = detail_data[selected_model]
            color = model_colors.get(selected_model, '#2563EB')
            cmap_name = model_cmaps.get(selected_model, 'Blues')
            st.markdown(f'<div style="background: linear-gradient(135deg, {color}15, {color}05); border-left: 5px solid {color}; border-radius: 0 12px 12px 0; padding: 15px 20px; margin-bottom: 25px;"><div style="font-size:1.15rem;font-weight:700;color:{color};margin:0;">{model_icons.get(selected_model, "🤖")} Detail Evaluasi: {selected_model}</div></div>', unsafe_allow_html=True)
            cols_dest = st.columns(len(lokasi_list))
            for col_idx, lok in enumerate(lokasi_list):
                with cols_dest[col_idx]:
                    lok_color = LOC_COLOR.get(lok, '#2563EB')
                    st.markdown(f'<div style="background: {lok_color}10; border-radius: 10px; padding: 12px 16px; margin-bottom: 15px; border: 1px solid {lok_color}30;"><div style="font-size:0.95rem;font-weight:700;color:{lok_color};margin:0;">📍 {lok}</div></div>', unsafe_allow_html=True)
                    loc_detail = safe_get(model_detail, lok, {})
                    labels_asli = safe_get(loc_detail, 'labels', ['Negatif', 'Netral', 'Positif'])
                    report = safe_get(loc_detail, 'report', {})
                    if report:
                        rows = []
                        for cls in labels_asli:
                            if cls in report:
                                r = report[cls]
                                rows.append({'Kelas': cls, 'Precision': f"{float(safe_get(r, 'precision', 0)):.2f}", 'Recall': f"{float(safe_get(r, 'recall', 0)):.2f}", 'F1-Score': f"{float(safe_get(r, 'f1-score', 0)):.2f}", 'Support': int(safe_get(r, 'support', 0))})
                        if rows: st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=220)
                    st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
                    cm = safe_get(loc_detail, 'cm', [])
                    if cm and len(cm) == len(labels_asli):
                        fig_cm = go.Figure(data=go.Heatmap(z=cm, x=labels_asli, y=labels_asli, colorscale=cmap_name, texttemplate="%{text}", textfont={"size": 18, "color": "black", "family": "Inter"}, xgap=4, ygap=4, colorbar=dict(thickness=15, len=0.9)))
                        fig_cm.update_layout(height=420, margin=dict(l=10, r=10, t=45, b=10), xaxis=dict(title='<b>Prediksi</b>', tickfont=dict(size=10)), yaxis=dict(title='<b>Aktual</b>', tickfont=dict(size=10), autorange='reversed'), title=dict(text=f'Confusion Matrix — {lok}', x=0.5, font=dict(size=12, weight='bold')))
                        st.plotly_chart(fig_cm, width="stretch", config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasifikasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 4: KLASTERISASI
# ══════════════════════════════════════════════════════════
elif halaman == "klaster":
    page_header("Hasil K-Means Clustering", "Pengelompokan ulasan berdasarkan kemiripan konten teks (SVD → K-Means)")
    if data_klaster:
        for lok in lokasi_list:
            kd = safe_get(data_klaster, lok)
            if not kd: continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">🧩 {lok}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                sx, sy, sc_clust = safe_get(kd, 'scatter_x', []), safe_get(kd, 'scatter_y', []), safe_get(kd, 'scatter_cluster', [])
                if sx and sy and sc_clust:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    scatter = ax.scatter(np.array(sx), np.array(sy), c=np.array(sc_clust), cmap='tab10', alpha=0.75, edgecolor='white', linewidth=0.5, s=40, zorder=2)
                    plt.colorbar(scatter, ax=ax, label='Klaster')
                    ax.set_title(f"K-Means (K={safe_get(kd, 'k_optimal', '?')})", fontweight='bold', fontsize=11)
                    ax.set_xlabel('SVD Komponen 1'); ax.set_ylabel('SVD Komponen 2'); ax.grid(True, alpha=0.3, zorder=1)
                    fig_style(fig, ax); st.pyplot(fig); plt.close(fig)
            with c2:
                st.metric("Jumlah Klaster (K)", safe_get(kd, 'k_optimal', '-'))
                st.metric("Silhouette Score", safe_get(kd, 'silhouette', '-'))
                st.metric("Davies-Bouldin", safe_get(kd, 'davies_bouldin', '-'))
                st.metric("Calinski-Harabasz", safe_get(kd, 'calinski_harabasz', '-'))
            kata_dom = safe_get(kd, 'kata_dominan', [])
            if kata_dom:
                st.markdown("**Kata Dominan per Klaster:**")
                st.dataframe(pd.DataFrame(kata_dom), width="stretch", hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasterisasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 5: RADAR PERBANDINGAN
# ══════════════════════════════════════════════════════════
elif halaman == "radar":
    page_header("Radar Chart — Perbandingan Kualitas Clustering", "Perbandingan metrik evaluasi klaster antara kedua destinasi (dinormalisasi)")
    if data_klaster and len(lokasi_list) >= 2:
        metrics_keys, metrics_label = ['silhouette', 'davies_bouldin', 'calinski_harabasz'], ['Silhouette\n(↑ bagus)', 'Davies-Bouldin\n(↓ bagus)', 'Calinski-Harabasz\n(↑ bagus)']
        raw = {lok: [data_klaster[lok].get(k, 0) for k in metrics_keys] for lok in lokasi_list if lok in data_klaster}
        def normalize(idx, invert=False):
            all_v = [raw[l][idx] for l in raw]; mn, mx = min(all_v), max(all_v)
            if mx == mn: return {l: 0.5 for l in raw}
            n = {l: (raw[l][idx]-mn)/(mx-mn) for l in raw}
            return {l: 1-v for l,v in n.items()} if invert else n
        norm_sil, norm_db, norm_ch = normalize(0), normalize(1, True), normalize(2)
        normalized = {lok: [norm_sil[lok], norm_db[lok], norm_ch[lok]] for lok in raw}
        N = len(metrics_label); angles = [n/float(N)*2*math.pi for n in range(N)]; angles += angles[:1]
        pemenang = {}
        for i, k in enumerate(metrics_keys): pemenang[k] = min(raw.keys(), key=lambda l: raw[l][i]) if k == 'davies_bouldin' else max(raw.keys(), key=lambda l: raw[l][i])
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Radar Chart Metrik Klasterisasi</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Area lebih luas = kualitas klasterisasi lebih baik</div>', unsafe_allow_html=True)
        col_r, col_t = st.columns([1, 1])
        with col_r:
            fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
            ax.set_facecolor('#F8FAFC')
            for lok in raw:
                vals = normalized[lok] + normalized[lok][:1]; color = LOC_COLOR.get(lok, '#2563EB')
                ax.plot(angles, vals, 'o-', linewidth=2.5, color=color, label=lok, markersize=8); ax.fill(angles, vals, alpha=0.15, color=color)
            ax.set_xticks(angles[:-1]); ax.set_xticklabels(metrics_label, fontsize=9, fontweight='bold')
            ax.set_yticks([0.25, 0.5, 0.75, 1.0]); ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'], fontsize=7, color='#94A3B8')
            ax.set_ylim(0, 1); ax.grid(color='#CBD5E1', linestyle='--', alpha=0.6)
            ax.set_title('Radar Metrik Klasterisasi', fontweight='bold', fontsize=11, pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=9); fig.tight_layout()
            st.pyplot(fig); plt.close(fig)
        with col_t:
            st.markdown("**Pemenang per Metrik:**")
            for k, w in pemenang.items(): st.markdown(f"- 📌 **{k}**: {w}")
            st.markdown("---"); st.markdown("**Tabel Nilai Mentah:**")
            raw_df = pd.DataFrame([{'Metrik': k, **{lok: raw[lok][i] for lok in raw}} for i, k in enumerate(metrics_keys)])
            st.dataframe(raw_df, width="stretch", hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasterisasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 6: TOPIC MODELING
# ══════════════════════════════════════════════════════════
elif halaman == "topik":
    page_header("Distribusi Topik - LDA (Latent Dirichlet Allocation)", "Analisis topik utama dari ulasan wisata")
    kpi_row()
    if data_topik:
        for lok in lokasi_list:
            td = safe_get(data_topik, lok)
            if not td: continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">📋 {lok}</div>', unsafe_allow_html=True)
            labels, values, n_topics, keywords_detail = safe_get(td, 'labels', []), safe_get(td, 'values', []), safe_get(td, 'n_topics', 0), safe_get(td, 'keywords_detail', {})
            if labels and values:
                col_pie, col_table = st.columns([1, 1])
                with col_pie:
                    colors = COLORS_TOPIC[:len(labels)]
                    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.45, marker=dict(colors=colors, line=dict(color='white', width=2)), textinfo='label+percent', textfont=dict(size=11, family='Inter'))])
                    fig_pie.update_layout(height=400, showlegend=True, legend=dict(orientation='h', y=-0.1, font=dict(size=9)), margin=dict(l=20, r=20, t=40, b=80))
                    st.plotly_chart(fig_pie, width="stretch", config={'displayModeBar': False})
                with col_table:
                    st.markdown("**Tabel Distribusi Topik:**")
                    st.dataframe(pd.DataFrame({'Topik': labels, 'Jumlah Review': values, 'Persentase': [f"{v/sum(values)*100:.1f}%" if sum(values) > 0 else "0%" for v in values]}), width="stretch", hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if keywords_detail:
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="sec-title">🔑 Top 10 Kata Kunci per Topik — {lok}</div>', unsafe_allow_html=True)
                n_cols = min(n_topics, 3); n_rows = (n_topics + n_cols - 1) // n_cols
                for row_idx in range(n_rows):
                    cols_bar = st.columns(n_cols)
                    for col_idx in range(n_cols):
                        topic_idx = row_idx * n_cols + col_idx
                        if topic_idx >= n_topics: continue
                        with cols_bar[col_idx]:
                            kw_data = safe_get(keywords_detail, str(topic_idx), [])
                            if kw_data:
                                words, weights = [k[0] for k in kw_data], [k[1] for k in kw_data]
                                fig_bar = go.Figure(data=[go.Bar(y=words[::-1], x=weights[::-1], orientation='h', marker_color=COLORS_TOPIC[topic_idx % len(COLORS_TOPIC)], text=[f"{w:.3f}" for w in weights[::-1]], textposition='outside', textfont=dict(size=9))])
                                fig_bar.update_layout(height=300, margin=dict(l=80, r=30, t=40, b=20), xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(tickfont=dict(size=10)), title=dict(text=f"Topik {topic_idx}: {labels[topic_idx] if topic_idx < len(labels) else ''}", font=dict(size=11, weight='bold', color=COLORS_TOPIC[topic_idx % len(COLORS_TOPIC)])))
                                st.plotly_chart(fig_bar, width="stretch", config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data topik tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 7: TRENDING TOPIK
# ══════════════════════════════════════════════════════════
elif halaman == "trending":
    page_header("Tren Topik dari Waktu ke Waktu", "Analisis bagaimana popularitas topik berubah seiring waktu")
    kpi_row()
    if data_trending:
        for lok in lokasi_list:
            trend = safe_get(data_trending, lok)
            if not trend: continue
            bulan, topik_data = safe_get(trend, 'bulan', []), safe_get(trend, 'topik', {})
            if bulan and topik_data:
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="sec-title">📈 Trending Topik — {lok}</div>', unsafe_allow_html=True)
                fig_trend = go.Figure()
                for i, (topik_name, values) in enumerate(topik_data.items()):
                    fig_trend.add_trace(go.Scatter(x=bulan, y=values, mode='lines+markers', name=topik_name, line=dict(width=2.5, color=COLORS_TOPIC[i % len(COLORS_TOPIC)]), marker=dict(size=8)))
                fig_trend.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter', size=12, color='#334155'), xaxis=dict(title='Bulan', tickfont=dict(size=10), gridcolor='#E2E8F0'), yaxis=dict(title='Jumlah Review', gridcolor='#E2E8F0'), legend=dict(orientation='h', y=-0.2, xanchor='center', x=0.5, font=dict(size=9)), hovermode='x unified', margin=dict(l=50, r=20, t=50, b=80))
                st.plotly_chart(fig_trend, width="stretch", config={'displayModeBar': False})
                st.markdown("**Detail Data per Bulan:**")
                df_trend = pd.DataFrame({'Bulan': bulan})
                for topik_name, values in topik_data.items(): df_trend[topik_name] = values
                st.dataframe(df_trend, width="stretch", hide_index=True)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data trending tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 8: WORDCLOUD
# ══════════════════════════════════════════════════════════
elif halaman == "wordcloud":
    page_header("WordCloud per Topik", "Visualisasi kata yang paling sering muncul dalam setiap topik")
    if data_wordcloud:
        for lok in lokasi_list:
            wc_data = safe_get(data_wordcloud, lok, {})
            if not wc_data: continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">☁️ WordCloud — {lok}</div>', unsafe_allow_html=True)
            n_topik = len(wc_data); n_cols = min(n_topik, 2); n_rows = (n_topik + n_cols - 1) // n_cols
            for row_idx in range(n_rows):
                cols_wc = st.columns(n_cols)
                for col_idx in range(n_cols):
                    topic_idx = row_idx * n_cols + col_idx
                    if topic_idx >= n_topik: continue
                    topic_words = safe_get(wc_data, str(topic_idx), {})
                    if topic_words:
                        with cols_wc[col_idx]:
                            fig, ax = plt.subplots(figsize=(6, 4))
                            wc = WordCloud(width=400, height=300, background_color='white', colormap='viridis', prefer_horizontal=0.9).generate_from_frequencies(topic_words)
                            ax.imshow(wc, interpolation='bilinear'); ax.axis('off')
                            label = f"Topik {topic_idx}"
                            if lok in data_topik:
                                labels = safe_get(data_topik[lok], 'labels', [])
                                if topic_idx < len(labels): label = f"Topik {topic_idx}: {labels[topic_idx]}"
                            ax.set_title(label, fontsize=11, fontweight='bold', pad=10)
                            plt.tight_layout(); st.pyplot(fig); plt.close(fig)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data WordCloud tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 9: JARINGAN
# ══════════════════════════════════════════════════════════
elif halaman == "jaringan":
    page_header("Jaringan Antar Topik", "Analisis keterkaitan antar topik berdasarkan kesamaan kata kunci")
    if data_centrality:
        for lok in lokasi_list:
            cent = safe_get(data_centrality, lok)
            if not cent: continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">🔗 Jaringan Topik — {lok}</div>', unsafe_allow_html=True)
            nodes, edges = safe_get(cent, 'nodes', []), safe_get(cent, 'edges', [])
            degree_cent, betweenness_cent = safe_get(cent, 'degree_centrality', {}), safe_get(cent, 'betweenness_centrality', {})
            if nodes:
                col_net, col_met = st.columns([1, 1])
                with col_net:
                    G = nx.Graph()
                    for node in nodes: G.add_node(node['name'], size=node.get('size', 10))
                    for edge in edges: G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1))
                    fig, ax = plt.subplots(figsize=(8, 6))
                    pos = nx.spring_layout(G, seed=42)
                    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[G.nodes[n].get('size', 10) * 15 for n in G.nodes], node_color=COLORS_TOPIC[:len(nodes)], alpha=0.8)
                    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#94A3B8', width=1.5, alpha=0.6)
                    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight='bold')
                    ax.set_title('Network Topik', fontweight='bold', fontsize=12); ax.axis('off')
                    plt.tight_layout(); st.pyplot(fig); plt.close(fig)
                with col_met:
                    st.markdown("**Metrik Centrality:**")
                    if degree_cent: st.dataframe(pd.DataFrame([{'Node': k, 'Degree Centrality': v} for k, v in sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)]), width="stretch", hide_index=True)
                    st.markdown("**Betweenness Centrality:**")
                    if betweenness_cent: st.dataframe(pd.DataFrame([{'Node': k, 'Betweenness Centrality': v} for k, v in sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)]), width="stretch", hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data jaringan tidak tersedia.")

# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.markdown('<div style="text-align:center;padding:20px;color:#64748B;font-size:0.8rem;border-top:1px solid #E2E8F0;margin-top:30px;"><b>Dashboard Perbandingan Pariwisata</b><br>Desa Wae Rebo vs Taman Nasional Komodo<br>Universitas Budi Luhur · Teknik Informatika · 2025</div>', unsafe_allow_html=True)
