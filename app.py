# =========================================================
# DASHBOARD PERBANDINGAN PARIWISATA
# Desa Wae Rebo vs Taman Nasional Komodo
# =========================================================
import json, math, os
import numpy as np
import pandas as pd
import matplotlib
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
    border-radius: 16px; padding: 22px 32px; margin-bottom: 24px;
    min-height: 84px; box-sizing: border-box;
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
.kpi-card::after { content: ''; position: absolute; right: -20px; bottom: -20px; width: 80px; height: 80px; border-radius: 50%; background: rgba(0,0,0,.03); }
.kpi-card.red { border-color: #EF4444; }
.kpi-card.green { border-color: #10B981; }
.kpi-label { font-size: 0.78rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.kpi-value { font-size: 2rem; font-weight: 800; color: #0F172A; line-height: 1.1; margin: 4px 0 2px; }
.sec-card { background: white; border-radius: 14px; padding: 22px 26px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,.05); box-sizing: border-box; }
.sec-title { font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 0 0 4px; display: flex; align-items: center; gap: 8px; }
.sec-sub { font-size: 0.82rem; color: #64748B; margin: 0 0 18px; }
hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; box-shadow: 0 1px 6px rgba(0,0,0,.06) !important; }
[data-testid="stMetric"] { background: white; border-radius: 12px; padding: 14px 18px !important; box-shadow: 0 2px 8px rgba(0,0,0,.06); border-left: 4px solid #2563EB; }
.nav-section { font-size: 0.68rem; font-weight: 700; color: #64748B; letter-spacing: .1em; text-transform: uppercase; padding: 16px 4px 6px; margin-top: 4px; }
button[data-baseweb="tab"] { font-size: 0.88rem !important; font-weight: 600 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #2563EB !important; border-bottom: 3px solid #2563EB !important; }
.stAlert { border-radius: 10px !important; }
.insight-card {
    border-radius: 12px; padding: 18px 20px; border-left: 5px solid;
    box-shadow: 0 2px 8px rgba(0,0,0,.05); background: white; box-sizing: border-box;
}
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
_json_path = os.path.join(os.path.dirname(__file__), 'dashboard_data.json')
try:
    with open(_json_path, 'r', encoding='utf-8') as f:
        DATA = json.load(f)
except FileNotFoundError:
    st.error("""
    ### ❌ File `dashboard_data.json` tidak ditemukan!
    Pastikan file sudah diupload ke repository GitHub di folder yang sama dengan `app.py`.
    """)
    st.stop()

ringkasan        = DATA['ringkasan']
lokasi_list      = DATA['lokasi_list']
data_rating      = DATA.get('rating', {})
data_klasifikasi = DATA.get('klasifikasi', {})
data_klaster     = DATA.get('klaster', {})
data_topik       = DATA.get('topik', {})
data_trending    = DATA.get('trending', {})
data_centrality  = DATA.get('centrality', {})
data_ulasan      = DATA.get('ulasan_detail', {})
data_wordcloud   = DATA.get('wordcloud', {})

LOC_COLOR = {'Desa Wae Rebo': '#2563EB', 'Taman Nasional Komodo': '#EF4444'}
for i, lok in enumerate(lokasi_list):
    if lok not in LOC_COLOR:
        LOC_COLOR[lok] = ['#2563EB', '#EF4444', '#10B981', '#F59E0B'][i % 4]

COLORS_TOPIC = ['#4338CA', '#0891B2', '#D97706', '#059669', '#DC2626', '#7C3AED', '#DB2777', '#2563EB']

# ----------------------------------------------------------
# SIDEBAR
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
        "Beranda & Peta": "beranda", "Analisis Sentimen": "sentimen",
        "Model Klasifikasi": "klasifikasi", "Klasterisasi": "klaster",
        "Radar Perbandingan": "radar", "Topic Modeling (LDA)": "topik",
        "Trending Topik": "trending", "WordCloud Masalah": "wordcloud",
        "Jaringan Antar Destinasi": "jaringan",
    }
    halaman_label = st.radio("", list(MENU.keys()), label_visibility="collapsed")
    halaman = MENU[halaman_label]
    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem;color:#64748B;text-align:center;line-height:1.6;">
        Universitas Budi Luhur<br>Teknik Informatika · 2025<br>
        <span style="color:#93C5FD;">Text Mining & Sentiment Analysis</span>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# HELPERS
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

def safe_max(vals, fallback=10):
    try:
        m = max(vals)
        return m * 1.2 if m > 0 else fallback
    except (ValueError, TypeError):
        return fallback

# ══════════════════════════════════════════════════════════
# HALAMAN 1: BERANDA & PETA
# ══════════════════════════════════════════════════════════
if halaman == "beranda":
    page_header("RANCANGAN DASHBOARD PERBANDINGAN PARIWISATA",
                "Analisis Ulasan Google Maps · Desa Wae Rebo vs Taman Nasional Komodo · Nusa Tenggara Timur")
    kpi_row()

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📍 Peta Lokasi Destinasi Wisata</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">🟢 Hijau = positif dominan | 🔴 Merah = negatif &gt;50%</div>', unsafe_allow_html=True)
    peta = folium.Map(
        location=[sum(r['lat'] for r in ringkasan)/len(ringkasan),
                  sum(r['lon'] for r in ringkasan)/len(ringkasan)],
        zoom_start=9, tiles="CartoDB positron"
    )
    for r in ringkasan:
        warna_m = "green" if r['status_warna'] == "Hijau" else "red"
        popup = (f"<b>{r['lokasi']}</b><br>📝 Total: {r['total_ulasan']}<br>"
                 f"✅ Positif: {r['jumlah_positif']}<br>❌ Negatif: {r['jumlah_negatif']}<br>"
                 f"% Negatif: <b>{r['persen_negatif']}%</b>")
        folium.Marker([r['lat'], r['lon']], popup=folium.Popup(popup, max_width=240),
                      tooltip=r['lokasi'], icon=folium.Icon(color=warna_m, icon='info-sign')).add_to(peta)
    st_folium(peta, width=None, height=430)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📋 Ringkasan Perbandingan</div>', unsafe_allow_html=True)
    df_ring = pd.DataFrame([{
        'Destinasi': r['lokasi'], 'Total Ulasan': r['total_ulasan'],
        'Positif': r['jumlah_positif'], 'Negatif': r['jumlah_negatif'],
        'Netral': r['jumlah_netral'], '% Negatif': f"{r['persen_negatif']}%",
        'Status': "⚠️ Perlu Perhatian" if r['persen_negatif'] > 50 else "✅ Cukup Baik",
    } for r in ringkasan])
    st.dataframe(df_ring, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN 2: SENTIMEN & RATING — FIXED
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
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=sentimen_labels, y=values, marker_color=sentimen_colors,
                    text=values, textposition='outside',
                    textfont=dict(size=15, color='#0F172A', family='Inter', weight='bold'),
                    hovertemplate='<b>' + lokasi + '</b><br>Sentimen: %{x}<br>Jumlah: %{y}<extra></extra>',
                    marker_line_color='white', marker_line_width=2.5
                ))
                fig.update_layout(
                    title=dict(text=lokasi, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center', y=0.95),
                    height=380, plot_bgcolor='white', paper_bgcolor='white',
                    font=dict(family='Inter', size=12, color='#334155'),
                    xaxis=dict(tickfont=dict(size=12, color='#475569'), showgrid=False, showline=False, zeroline=False),
                    yaxis=dict(title='Jumlah Ulasan', titlefont=dict(size=11, color='#64748B'), tickfont=dict(size=11, color='#64748B'), gridcolor='#E2E8F0', range=[0, safe_max(values)]),
                    margin=dict(l=50, r=20, t=50, b=50), bargap=0.35,
                    hoverlabel=dict(bgcolor='#0F172A', font=dict(color='white', size=13, family='Inter'))
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except Exception as e:
                st.error(f"Gagal membuat chart sentimen {lokasi}: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== CONTOH ULASAN PER SENTIMEN ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Sentimen</div>', unsafe_allow_html=True)
    tab_positif, tab_negatif, tab_netral = st.tabs(["🟢 Positif", "🔴 Negatif", "🟡 Netral"])
    for tab, skey, slab in [(tab_positif,'contoh_positif','Positif'),(tab_negatif,'contoh_negatif','Negatif'),(tab_netral,'contoh_netral','Netral')]:
        with tab:
            c1, c2 = st.columns(2)
            for col, r in zip([c1, c2], ringkasan):
                with col:
                    st.markdown(f'**{r["lokasi"]}**')
                    cl = data_ulasan.get(r['lokasi'], {}).get(skey, [])
                    if cl:
                        rows = [{'Penulis': u.get('author','Anonim'), 'Rating': '⭐'*u.get('rating',0), 'Tanggal': u.get('date',''), 'Ulasan': u.get('review','')} for u in cl[:5]]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                            column_config={'Penulis': st.column_config.TextColumn('Penulis', width='medium'), 'Rating': st.column_config.TextColumn('Rating', width='small'), 'Tanggal': st.column_config.TextColumn('Tanggal', width='medium'), 'Ulasan': st.column_config.TextColumn('Ulasan', width='large')})
                    else:
                        st.info(f"Tidak ada contoh ulasan {slab.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== DISTRIBUSI RATING BINTANG — FIXED ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⭐ Distribusi Rating Bintang</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Arahkan kursor ke bar untuk melihat detail jumlah ulasan per bintang</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    warna_bintang = {1:'#EF4444', 2:'#F97316', 3:'#F59E0B', 4:'#84CC16', 5:'#10B981'}

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

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=labels, y=values, marker_color=colors,
                    text=values, textposition='outside',
                    textfont=dict(size=12, color='#0F172A', family='Inter', weight='bold'),
                    hovertemplate='<b>' + lok + '</b><br>Rating: %{x}<br>Jumlah: %{y}<extra></extra>',
                    marker_line_color='white', marker_line_width=2.5
                ))
                fig.update_layout(
                    title=dict(text=lok, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5, xanchor='center', y=0.95),
                    height=380, plot_bgcolor='white', paper_bgcolor='white',
                    font=dict(family='Inter', size=12, color='#334155'),
                    xaxis=dict(tickfont=dict(size=11), showgrid=False, showline=False, zeroline=False),
                    yaxis=dict(title='Jumlah Ulasan', gridcolor='#E2E8F0', range=[0, safe_max(values)]),
                    margin=dict(l=50, r=20, t=50, b=50), bargap=0.35,
                    hoverlabel=dict(bgcolor='#0F172A', font=dict(color='white', size=13, family='Inter'))
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except Exception as e:
                st.error(f"Gagal membuat chart rating {lok}: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ========== CONTOH ULASAN PER BINTANG ==========
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Rating Bintang</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Klik tab untuk melihat contoh ulasan berdasarkan jumlah bintang</div>', unsafe_allow_html=True)
    tabs_r = st.tabs(["⭐ 1", "⭐⭐ 2", "⭐⭐⭐ 3", "⭐⭐⭐⭐ 4", "⭐⭐⭐⭐⭐ 5"])
    for tab, rkey, rlab in zip(tabs_r, [f'rating_{i}' for i in range(1,6)], [f'{i} Bintang' for i in range(1,6)]):
        with tab:
            c1, c2 = st.columns(2)
            for col, r in zip([c1, c2], ringkasan):
                with col:
                    st.markdown(f'**{r["lokasi"]}**')
                    cl = data_ulasan.get(r['lokasi'], {}).get(rkey, [])
                    if cl:
                        rows = [{'Penulis': u.get('author','Anonim'), 'Rating': '⭐'*u.get('rating',0), 'Tanggal': u.get('date',''), 'Ulasan': u.get('review','')} for u in cl[:5]]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                            column_config={'Penulis': st.column_config.TextColumn('Penulis', width='medium'), 'Rating': st.column_config.TextColumn('Rating', width='small'), 'Tanggal': st.column_config.TextColumn('Tanggal', width='medium'), 'Ulasan': st.column_config.TextColumn('Ulasan', width='large')})
                    else:
                        st.info(f"Tidak ada contoh ulasan {rlab.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN 3: KLASIFIKASI
# ══════════════════════════════════════════════════════════
elif halaman == "klasifikasi":
    page_header("Perbandingan Akurasi Model Klasifikasi", "SVM · Random Forest · Naive Bayes")
    kpi_row()

    if data_klasifikasi:
        model_names = data_klasifikasi.get('model_names', [])
        akurasi = data_klasifikasi.get('akurasi', {})
        detail_data = data_klasifikasi.get('detail', {})

        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Perbandingan Akurasi Antar Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Perbandingan performa ketiga model ML pada kedua lokasi</div>', unsafe_allow_html=True)
        if model_names and akurasi:
            fig_ov = go.Figure()
            for lok in lokasi_list:
                if lok in akurasi:
                    vals = [float(akurasi[lok].get(m, 0)) for m in model_names]
                    fig_ov.add_trace(go.Bar(name=lok, x=model_names, y=vals,
                        marker_color=LOC_COLOR.get(lok, '#2563EB'),
                        text=[f"{v:.2f}%" for v in vals], textposition='outside',
                        textfont=dict(size=14, family='Inter', weight='bold'),
                        hovertemplate='<b>' + lok + '</b><br>Model: %{x}<br>Akurasi: %{y:.2f}%<extra></extra>'))
            fig_ov.update_layout(barmode='group', height=420, plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family='Inter', size=12), yaxis=dict(title='Akurasi (%)', range=[0,115], gridcolor='#E2E8F0'),
                xaxis=dict(showgrid=False, showline=False),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
                margin=dict(l=50, r=20, t=60, b=50), bargap=0.3)
            st.plotly_chart(fig_ov, use_container_width=True, config={'displayModeBar': False})
            rows_a = []
            for m in model_names:
                row = {'Model': m}
                for lok in lokasi_list:
                    row[lok] = f"{float(akurasi[lok].get(m, 0)):.2f}%"
                rows_a.append(row)
            st.dataframe(pd.DataFrame(rows_a), use_container_width=True, hide_index=True, height=120)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Evaluasi Detail per Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Klik tombol algoritma untuk melihat Classification Report & Confusion Matrix</div>', unsafe_allow_html=True)
        model_icons = {'SVM': '🧠', 'Random Forest': '🌲', 'Naive Bayes': '📊'}
        model_colors = {'SVM': '#2563EB', 'Random Forest': '#10B981', 'Naive Bayes': '#F59E0B'}
        model_cmaps = {'SVM': 'Blues', 'Random Forest': 'Greens', 'Naive Bayes': 'YlOrBr'}

        btn_cols = st.columns(len(model_names))
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = model_names[0] if model_names else None
        for idx, mn in enumerate(model_names):
            with btn_cols[idx]:
                icon = model_icons.get(mn, '🤖')
                if st.button(f"{icon} {mn}", key=f"btn_{mn}", use_container_width=True,
                             type="primary" if st.session_state.selected_model == mn else "secondary"):
                    st.session_state.selected_model = mn

        selected_model = st.session_state.selected_model
        if selected_model and selected_model in detail_data:
            md = detail_data[selected_model]
            color = model_colors.get(selected_model, '#2563EB')
            icon = model_icons.get(selected_model, '🤖')
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{color}15,{color}05);border-left:5px solid {color};border-radius:0 12px 12px 0;padding:15px 20px;margin-bottom:25px;">
                <div style="font-size:1.15rem;font-weight:700;color:{color};margin:0;">{icon} Detail Evaluasi: {selected_model}</div>
                <div style="font-size:0.82rem;color:#64748B;margin-top:4px;">Classification Report & Confusion Matrix</div>
            </div>
            """, unsafe_allow_html=True)

            cols_dest = st.columns(len(lokasi_list))
            report_data_for_f1 = {}
            cmap_name = model_cmaps.get(selected_model, 'Blues')
            for col_idx, lok in enumerate(lokasi_list):
                with cols_dest[col_idx]:
                    lok_c = LOC_COLOR.get(lok, '#2563EB')
                    st.markdown(f'<div style="background:{lok_c}10;border-radius:10px;padding:12px 16px;margin-bottom:15px;border:1px solid {lok_c}30;"><div style="font-size:0.95rem;font-weight:700;color:{lok_c};margin:0;">📍 {lok}</div></div>', unsafe_allow_html=True)
                    ld = md.get(lok, {})
                    labels_raw = ld.get('labels', ['Negatif','Netral','Positif'])
                    if isinstance(labels_raw, list):
                        labels_asli = [str(l).strip() for l in labels_raw if str(l).strip() not in ['','None']]
                    else:
                        labels_asli = ['Negatif','Netral','Positif']
                    report = ld.get('report', {})
                    try:
                        if report:
                            rows = []
                            for cls in labels_asli:
                                if cls in report:
                                    rv = report[cls]
                                    rows.append({'Kelas': cls, 'Precision': f"{float(rv.get('precision',0) or 0):.2f}",
                                        'Recall': f"{float(rv.get('recall',0) or 0):.2f}",
                                        'F1-Score': f"{float(rv.get('f1-score',0) or 0):.2f}",
                                        'Support': int(rv.get('support',0) or 0)})
                            for avg_key in ['macro avg', 'weighted avg']:
                                if avg_key in report:
                                    a = report[avg_key]
                                    rows.append({'Kelas': avg_key, 'Precision': f"{float(a.get('precision',0) or 0):.2f}",
                                        'Recall': f"{float(a.get('recall',0) or 0):.2f}",
                                        'F1-Score': f"{float(a.get('f1-score',0) or 0):.2f}",
                                        'Support': int(a.get('support',0) or 0)})
                            if rows:
                                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=220)
                                report_data_for_f1[lok] = report
                    except Exception as e:
                        st.error(f"Gagal: {e}")
                    st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
                    try:
                        cm = ld.get('cm', [])
                        if cm and len(cm) == len(labels_asli):
                            fig_cm = go.Figure(data=go.Heatmap(z=cm, x=labels_asli, y=labels_asli,
                                colorscale=cmap_name, texttemplate="%{text}",
                                textfont={"size": 18, "color": "black", "family": "Inter"},
                                hovertemplate='Aktual: %{y}<br>Prediksi: %{x}<br>Jumlah: %{z}<extra></extra>',
                                xgap=4, ygap=4, colorbar=dict(thickness=15, len=0.9)))
                            fig_cm.update_layout(height=420, margin=dict(l=10, r=10, t=45, b=10),
                                xaxis=dict(title=dict(text='<b>Prediksi</b>', font=dict(size=11))),
                                yaxis=dict(title=dict(text='<b>Aktual</b>', font=dict(size=11)), autorange='reversed', scaleanchor="x", scaleratio=1),
                                title=dict(text=f'Confusion Matrix — {lok}', font=dict(size=12, weight='bold'), x=0.5, xanchor='center'))
                            st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
                    except Exception as e:
                        st.error(f"Gagal CM: {e}")

            if report_data_for_f1:
                try:
                    st.markdown('<hr style="margin:25px 0 20px;border-color:#E2E8F0">', unsafe_allow_html=True)
                    all_classes = sorted(list(set([c for lr in report_data_for_f1.values() for c in lr.keys() if c not in ['accuracy','macro avg','weighted avg']])))
                    if all_classes:
                        fig_f1 = go.Figure()
                        for lok in lokasi_list:
                            if lok in report_data_for_f1:
                                f1v = [float(report_data_for_f1[lok].get(c,{}).get('f1-score',0) or 0) for c in all_classes]
                                fig_f1.add_trace(go.Bar(name=lok, x=all_classes, y=f1v,
                                    marker_color=LOC_COLOR.get(lok,'#2563EB'),
                                    text=[f"{v:.2f}" for v in f1v], textposition='outside',
                                    textfont=dict(size=14, family='Inter', weight='bold'),
                                    hovertemplate='<b>' + lok + '</b><br>Kelas: %{x}<br>F1: %{y:.2f}<extra></extra>'))
                        fig_f1.update_layout(
                            title=dict(text="Perbandingan F1-Score per Kelas", font=dict(size=15, weight='bold'), x=0.5, y=0.98),
                            annotations=[dict(text=f"Model: {selected_model}", x=0.5, y=0.92, xref='paper', yref='paper', showarrow=False, font=dict(size=11, color='#64748B'))],
                            barmode='group', height=380, plot_bgcolor='white', paper_bgcolor='white',
                            yaxis=dict(title='F1-Score', range=[0,1.2], gridcolor='#E2E8F0'),
                            xaxis=dict(showgrid=False, showline=False), legend=dict(orientation='h', y=-0.2, x=0.5),
                            margin=dict(l=50, r=20, t=80, b=70), bargap=0.3)
                        st.plotly_chart(fig_f1, use_container_width=True, config={'displayModeBar': False})
                        f1_rows = []
                        for c in all_classes:
                            row = {'Kelas': c}
                            for lok in lokasi_list:
                                if lok in report_data_for_f1:
                                    row[lok] = f"{float(report_data_for_f1[lok].get(c,{}).get('f1-score',0) or 0):.2f}"
                            f1_rows.append(row)
                        if f1_rows:
                            st.markdown('<div style="font-size:0.9rem;font-weight:600;color:#334155;margin-bottom:8px;">📋 Tabel F1-Score</div>', unsafe_allow_html=True)
                            st.dataframe(pd.DataFrame(f1_rows), use_container_width=True, hide_index=True, height=130)
                except Exception as e:
                    st.error(f"Gagal F1: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Ringkasan Akurasi per Model & Lokasi</div>', unsafe_allow_html=True)
        srows = []
        for m in model_names:
            row = {'Model': m}
            for lok in lokasi_list:
                av = float(akurasi.get(lok,{}).get(m, 0))
                if av >= 85: row[lok] = f"✅ {av:.2f}%"
                elif av >= 70: row[lok] = f"⚠️ {av:.2f}%"
                else: row[lok] = f"❌ {av:.2f}%"
            srows.append(row)
        if srows:
            st.dataframe(pd.DataFrame(srows), use_container_width=True, hide_index=True, height=150)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasifikasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 4: KLASTERISASI
# ══════════════════════════════════════════════════════════
elif halaman == "klaster":
    page_header("Hasil K-Means Clustering", "Pengelompokan ulasan berdasarkan kemiripan konten (SVD → K-Means)")
    if data_klaster:
        for lok in lokasi_list:
            kd = data_klaster.get(lok)
            if not kd: continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">🧩 {lok}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                sx, sy, sc = kd.get('scatter_x',[]), kd.get('scatter_y',[]), kd.get('scatter_cluster',[])
                if sx and sy and sc:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    scatter = ax.scatter(np.array(sx), np.array(sy), c=np.array(sc), cmap='tab10', alpha=0.75, edgecolor='white', linewidth=0.5, s=40, zorder=2)
                    plt.colorbar(scatter, ax=ax, label='Klaster')
                    ax.set_title(f"K-Means (K={kd['k_optimal']})", fontweight='bold', fontsize=11)
                    ax.set_xlabel('SVD Komponen 1'); ax.set_ylabel('SVD Komponen 2')
                    ax.grid(True, alpha=0.3, zorder=1)
                    fig_style(fig, ax)
                    st.pyplot(fig); plt.close(fig)
            with c2:
                st.metric("Jumlah Klaster (K)", kd['k_optimal'])
                st.metric("Silhouette Score", kd['silhouette'])
                st.metric("Davies-Bouldin", kd['davies_bouldin'])
                st.metric("Calinski-Harabasz", kd['calinski_harabasz'])
            st.markdown("**Kata Dominan per Klaster:**")
            st.dataframe(pd.DataFrame(kd['kata_dominan']), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasterisasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 5: RADAR PERBANDINGAN
# ══════════════════════════════════════════════════════════
elif halaman == "radar":
    page_header("Radar Chart — Perbandingan Kualitas Clustering", "Metrik evaluasi klaster (dinormalisasi)")
    if data_klaster and len(lokasi_list) >= 2:
        mk = ['silhouette','davies_bouldin','calinski_harabasz']
        ml = ['Silhouette\n(↑ bagus)','Davies-Bouldin\n(↓ bagus)','Calinski-Harabasz\n(↑ bagus)']
        raw = {lok: [data_klaster[lok][k] for k in mk] for lok in lokasi_list if lok in data_klaster}
        def normalize(idx, invert=False):
            all_v = [raw[l][idx] for l in raw]
            mn, mx = min(all_v), max(all_v)
            if mx == mn: return {l: 0.5 for l in raw}
            n = {l: (raw[l][idx]-mn)/(mx-mn) for l in raw}
            return {l: 1-v for l,v in n.items()} if invert else n
        norm = {lok: [normalize(0)[lok], normalize(1,True)[lok], normalize(2)[lok]] for lok in raw}
        N = len(ml)
        angles = [n/float(N)*2*math.pi for n in range(N)]
        angles += angles[:1]

        pemenang = {}
        for i, k in enumerate(mk):
            pemenang[k] = min(raw.keys(), key=lambda l: raw[l][i]) if k == 'davies_bouldin' else max(raw.keys(), key=lambda l: raw[l][i])
        cw = {l: 0 for l in raw}
        for w in pemenang.values(): cw[w] += 1
        ow = max(cw.keys(), key=lambda l: cw[l])
        is_tie = all(v == cw[ow] for v in cw.values())

        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Radar Chart Metrik Klasterisasi</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Area lebih luas = kualitas klasterisasi lebih baik</div>', unsafe_allow_html=True)
        col_r, col_t = st.columns([1, 1])
        with col_r:
            fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
            ax.set_facecolor('#F8FAFC')
            for lok in raw:
                vals = norm[lok] + norm[lok][:1]
                c = LOC_COLOR.get(lok, '#2563EB')
                ax.plot(angles, vals, 'o-', linewidth=2.5, color=c, label=lok, markersize=8)
                ax.fill(angles, vals, alpha=0.15, color=c)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(ml, fontsize=9, fontweight='bold')
            ax.set_yticks([0.25, 0.5, 0.75, 1.0])
            ax.set_yticklabels(['0.25','0.5','0.75','1.0'], fontsize=7, color='#94A3B8')
            ax.set_ylim(0, 1)
            ax.grid(color='#CBD5E1', linestyle='--', alpha=0.6)
            ax.set_title('Radar Metrik Klasterisasi', fontweight='bold', fontsize=11, pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=9)
            fig.tight_layout()
            st.pyplot(fig); plt.close(fig)
        with col_t:
            st.markdown("**Nilai Asli:**")
            raw_rows = []
            for k, label in zip(mk, ['Silhouette','Davies-Bouldin','Calinski-Harabasz']):
                row = {'Metrik': label}
                for lok in raw: row[lok] = raw[lok][mk.index(k)]
                raw_rows.append(row)
            st.dataframe(pd.DataFrame(raw_rows), use_container_width=True, hide_index=True)
            st.markdown("**Nilai Normalisasi:**")
            norm_rows = []
            for k, label in zip(mk, ['Silhouette','Davies-Bouldin (inv)','Calinski-Harabasz']):
                row = {'Metrik': label}
                for lok in raw: row[lok] = round(norm[lok][mk.index(k)], 4)
                norm_rows.append(row)
            st.dataframe(pd.DataFrame(norm_rows), use_container_width=True, hide_index=True)

        st.markdown('<div style="margin-top:20px;"></div>', unsafe_allow_html=True)
        if is_tie:
            st.markdown('<div class="sec-card"><div class="sec-title">🤝 Hasil Imbang</div><div class="sec-sub">Kedua destinasi setara</div>', unsafe_allow_html=True)
            for k, w in pemenang.items():
                lm = {'silhouette':'Silhouette','davies_bouldin':'Davies-Bouldin','calinski_harabasz':'Calinski-Harabasz'}
                st.markdown(f"- **{lm[k]}**: {w}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            wc = LOC_COLOR.get(ow, '#2563EB')
            st.markdown(f'<div class="sec-card"><div style="background:{wc}10;border-left:5px solid {wc};border-radius:0 12px 12px 0;padding:18px 22px;"><div style="font-size:1.15rem;font-weight:700;color:{wc};">🏆 Pemenang: {ow}</div><div style="font-size:0.88rem;color:#334155;margin-top:8px;">Menang di <b>{cw[ow]}</b> dari {len(mk)} metrik:</div>', unsafe_allow_html=True)
            for k, w in pemenang.items():
                lm = {'silhouette':'Silhouette','davies_bouldin':'Davies-Bouldin','calinski_harabasz':'Calinski-Harabasz'}
                icon = "✅" if w == ow else "❌"
                st.markdown(f"&nbsp;&nbsp;{icon} **{lm[k]}**: {w}", unsafe_allow_html=True)
            st.markdown('</div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data klasterisasi tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 6: TOPIC MODELING (LDA) — FIXED: +WordCloud per Topik
# ══════════════════════════════════════════════════════════
elif halaman == "topik":
    page_header("Topic Modeling (LDA)", "Pengidentifikasian topik dominan dari ulasan wisata")
    kpi_row()

    if data_topik:
        for lok in lokasi_list:
            td = data_topik.get(lok, {})
            if not td: continue

            labels = td.get('labels', [])
            values = td.get('values', [])
            keywords = td.get('keywords', [])
            keywords_detail = td.get('keywords_detail', {})
            wc_data = td.get('wordcloud_data', {})
            n_t = len(labels)

            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">📄 {lok}</div>', unsafe_allow_html=True)

            # --- PIE CHART ---
            if labels and values:
                try:
                    fig_p = go.Figure(data=[go.Pie(labels=labels, values=values,
                        marker_colors=COLORS_TOPIC[:len(labels)],
                        textinfo='label+percent', textfont=dict(size=10, family='Inter'), hole=0.45,
                        hovertemplate='%{label}<br>Jumlah: %{value}<br>%{percent}<extra></extra>')])
                    fig_p.update_layout(
                        title=dict(text='Distribusi Topik', font=dict(size=13, weight='bold')),
                        height=420, margin=dict(t=50, b=20, l=20, r=20),
                        showlegend=True, legend=dict(font=dict(size=9), orientation='h', yanchor='bottom', y=-0.15))
                    st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})
                except Exception as e:
                    st.error(f"Gagal pie chart: {e}")

            # --- BAR CHART: Top 10 Kata per Topik ---
            st.markdown('<div style="font-size:1rem;font-weight:700;color:#0F172A;margin:20px 0 12px;">📊 Top 10 Kata Kunci per Topik</div>', unsafe_allow_html=True)
            n_cols_bar = min(n_t, 3)
            n_rows_bar = (n_t + n_cols_bar - 1) // n_cols_bar

            for row_idx in range(n_rows_bar):
                bar_cols = st.columns(n_cols_bar)
                for col_idx in range(n_cols_bar):
                    topic_idx = row_idx * n_cols_bar + col_idx
                    if topic_idx >= n_t:
                        continue
                    with bar_cols[col_idx]:
                        detail = keywords_detail.get(str(topic_idx), [])
                        if detail:
                            words = [d[0] for d in detail]
                            weights = [d[1] for d in detail]
                            try:
                                fig_b = go.Figure(data=[go.Bar(
                                    y=words[::-1], x=weights[::-1], orientation='h',
                                    marker_color=COLORS_TOPIC[topic_idx % len(COLORS_TOPIC)],
                                    text=[f"{w:.3f}" for w in weights[::-1]], textposition='outside',
                                    textfont=dict(size=9, family='Inter'))])
                                fig_b.update_layout(
                                    title=dict(text=f'Topik {topic_idx}: {labels[topic_idx]}',
                                        font=dict(size=11, weight='bold', color=COLORS_TOPIC[topic_idx % len(COLORS_TOPIC)])),
                                    height=max(220, 45*len(words)),
                                    margin=dict(t=40, b=10, l=110, r=50),
                                    xaxis=dict(showgrid=False, showticklabels=False),
                                    yaxis=dict(tickfont=dict(size=9)))
                                st.plotly_chart(fig_b, use_container_width=True, config={'displayModeBar': False})
                            except Exception as e:
                                st.error(f"Gagal bar chart topik {topic_idx}: {e}")

            # --- WORDCLOUD PER TOPIK ---
            st.markdown('<div style="font-size:1rem;font-weight:700;color:#0F172A;margin:25px 0 12px;">☁️ WordCloud per Topik</div>', unsafe_allow_html=True)
            n_cols_wc = min(n_t, 3)
            n_rows_wc = (n_t + n_cols_wc - 1) // n_cols_wc

            for row_idx in range(n_rows_wc):
                wc_cols = st.columns(n_cols_wc)
                for col_idx in range(n_cols_wc):
                    topic_idx = row_idx * n_cols_wc + col_idx
                    if topic_idx >= n_t:
                        continue
                    with wc_cols[col_idx]:
                        # Gunakan wordcloud_data (50 kata) jika ada, fallback ke keywords_detail (10 kata)
                        wc_dict = wc_data.get(str(topic_idx), {})
                        if not wc_dict and keywords_detail.get(str(topic_idx)):
                            wc_dict = dict(keywords_detail[str(topic_idx)])

                        if wc_dict:
                            try:
                                wc = WordCloud(width=500, height=300, background_color='white',
                                    max_words=80, colormap='viridis', prefer_horizontal=0.9,
                                    min_font_size=8).generate_from_frequencies(wc_dict)
                                fig_wc, ax_wc = plt.subplots(figsize=(5, 3))
                                ax_wc.imshow(wc, interpolation='bilinear')
                                ax_wc.axis('off')
                                ax_wc.set_title(f'Topik {topic_idx}: {labels[topic_idx]}',
                                    fontsize=10, fontweight='bold',
                                    color=COLORS_TOPIC[topic_idx % len(COLORS_TOPIC)])
                                fig_wc.tight_layout()
                                st.pyplot(fig_wc); plt.close(fig_wc)
                            except Exception as e:
                                st.error(f"Gagal wordcloud topik {topic_idx}: {e}")
                        else:
                            st.info(f"Tidak ada data wordcloud untuk Topik {topic_idx}")

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data topic modeling tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 7: TRENDING TOPIK — FIXED: +Insight +Detail Tabel
# ══════════════════════════════════════════════════════════
elif halaman == "trending":
    page_header("Trending Topik", "Analisis tren topik dari waktu ke waktu")
    kpi_row()

    has_any = False
    for lok in lokasi_list:
        td = data_trending.get(lok, {})
        if td and td.get('bulan') and len(td['bulan']) > 0:
            has_any = True
            break

    if not has_any:
        st.info("Data trending tidak tersedia. Pastikan data tanggal ulasan memiliki variasi bulan yang cukup.")
    else:
        # ========== LINE CHARTS ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📈 Tren Topik dari Waktu ke Waktu</div>', unsafe_allow_html=True)

        n_loc_with_data = sum(1 for lok in lokasi_list if data_trending.get(lok, {}).get('bulan'))
        chart_cols = st.columns(min(n_loc_with_data, 2))

        col_idx = 0
        for lok in lokasi_list:
            td = data_trending.get(lok, {})
            if not td or not td.get('bulan'):
                continue
            with chart_cols[col_idx]:
                bulan = td['bulan']
                topik = td['topik']
                try:
                    fig_tr = go.Figure()
                    for i, (tn, vals) in enumerate(topik.items()):
                        fig_tr.add_trace(go.Scatter(
                            x=bulan, y=vals, mode='lines+markers', name=tn,
                            line=dict(color=COLORS_TOPIC[i % len(COLORS_TOPIC)], width=2.5),
                            marker=dict(size=7),
                            hovertemplate='<b>' + tn + '</b><br>Bulan: %{x}<br>Jumlah: %{y}<extra></extra>'))
                    fig_tr.update_layout(
                        title=dict(text=lok, font=dict(size=14, weight='bold')),
                        height=400, plot_bgcolor='white', paper_bgcolor='white',
                        font=dict(family='Inter', size=11),
                        xaxis=dict(title='Bulan', tickfont=dict(size=9), showgrid=False, tickangle=45),
                        yaxis=dict(title='Jumlah Review', gridcolor='#E2E8F0'),
                        legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5, font=dict(size=8)),
                        margin=dict(t=45, b=110, l=50, r=20), hovermode='x unified')
                    st.plotly_chart(fig_tr, use_container_width=True, config={'displayModeBar': False})
                except Exception as e:
                    st.error(f"Gagal chart trending {lok}: {e}")
            col_idx += 1

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== INSIGHT OTOMATIS ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">💡 Insight Otomatis</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Analisis otomatis berdasarkan data tren topik</div>', unsafe_allow_html=True)

        insight_cols = st.columns(3)
        insight_data = {
            'puncak': {'icon': '📈', 'title': 'Topik Puncak', 'desc': '', 'color': '#10B981'},
            'naik': {'icon': '📊', 'title': 'Topik Naik Signifikan', 'desc': '', 'color': '#2563EB'},
            'turun': {'icon': '📉', 'title': 'Topik Turun Paling Cepat', 'desc': '', 'color': '#EF4444'},
        }

        for lok in lokasi_list:
            td = data_trending.get(lok, {})
            if not td or not td.get('bulan'):
                continue
            bulan = td['bulan']
            topik = td['topik']

            # Puncak: topik dengan nilai tertinggi di seluruh periode
            max_val = 0
            max_topic = ''
            max_month = ''
            for tn, vals in topik.items():
                for bi, v in enumerate(vals):
                    if v > max_val:
                        max_val = v
                        max_topic = tn
                        max_month = bulan[bi] if bi < len(bulan) else '?'
            if max_topic:
                insight_data['puncak']['desc'] = f'**{max_topic}** mencapai puncak tertinggi dengan **{max_val} ulasan** pada bulan {max_month} ({lok})'

            # Naik: bandingkan 3 bulan terakhir vs 3 bulan pertama
            best_rise_topic = ''
            best_rise_pct = -999
            for tn, vals in topik.items():
                if len(vals) < 4:
                    continue
                first_avg = sum(vals[:3]) / 3
                last_avg = sum(vals[-3:]) / 3
                if first_avg > 0:
                    rise_pct = ((last_avg - first_avg) / first_avg) * 100
                    if rise_pct > best_rise_pct:
                        best_rise_pct = rise_pct
                        best_rise_topic = tn
            if best_rise_topic and best_rise_pct > 0:
                insight_data['naik']['desc'] = f'**{best_rise_topic}** mengalami kenaikan **{best_rise_pct:.0f}%** (rata-rata 3 bulan terakhir vs awal, {lok})'
            else:
                insight_data['naik']['desc'] = f'Tidak ada topik yang menunjukkan kenaikan signifikan ({lok})'

            # Turun: penurunan terbesar
            best_drop_topic = ''
            best_drop_pct = 999
            for tn, vals in topik.items():
                if len(vals) < 4:
                    continue
                first_avg = sum(vals[:3]) / 3
                last_avg = sum(vals[-3:]) / 3
                if first_avg > 0:
                    drop_pct = ((last_avg - first_avg) / first_avg) * 100
                    if drop_pct < best_drop_pct:
                        best_drop_pct = drop_pct
                        best_drop_topic = tn
            if best_drop_topic and best_drop_pct < 0:
                insight_data['turun']['desc'] = f'**{best_drop_topic}** mengalami penurunan **{best_drop_pct:.0f}%** (rata-rata 3 bulan terakhir vs awal, {lok})'
            else:
                insight_data['turun']['desc'] = f'Tidak ada topik yang menunjukkan penurunan signifikan ({lok})'

        for col, (key, idata) in zip(insight_cols, insight_data.items()):
            with col:
                st.markdown(f"""
                <div class="insight-card" style="border-color:{idata['color']};">
                    <div style="font-size:1.8rem;margin-bottom:6px;">{idata['icon']}</div>
                    <div style="font-size:0.95rem;font-weight:700;color:{idata['color']};margin-bottom:8px;">{idata['title']}</div>
                    <div style="font-size:0.82rem;color:#334155;line-height:1.6;">{idata['desc'] if idata['desc'] else 'Data tidak cukup untuk analisis.'}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ========== DETAIL DATA PER BULAN ==========
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📋 Detail Data per Bulan</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Data lengkap jumlah review per topik per bulan</div>', unsafe_allow_html=True)

        tab_lokasi = st.tabs(lokasi_list)
        for tab_idx, lok in enumerate(lokasi_list):
            with tab_lokasi[tab_idx]:
                td = data_trending.get(lok, {})
                if not td or not td.get('bulan'):
                    st.info(f"Data trending tidak tersedia untuk {lok}.")
                    continue
                bulan = td['bulan']
                topik = td['topik']
                rows_tbl = []
                for bi, b in enumerate(bulan):
                    row = {'Bulan': b}
                    for tn, vals in topik.items():
                        row[tn] = vals[bi] if bi < len(vals) else 0
                    rows_tbl.append(row)
                if rows_tbl:
                    st.dataframe(pd.DataFrame(rows_tbl), use_container_width=True, hide_index=True, height=400)
                else:
                    st.info("Tidak ada data.")

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN 8: WORDCLOUD MASALAH
# ══════════════════════════════════════════════════════════
elif halaman == "wordcloud":
    page_header("WordCloud Masalah", "Visualisasi kata yang sering muncul pada ulasan negatif")
    kpi_row()
    if data_wordcloud:
        for lok in lokasi_list:
            wc_d = data_wordcloud.get(lok, {})
            if not wc_d:
                st.info(f"Data wordcloud tidak tersedia untuk {lok}.")
                continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">☁️ {lok} — Kata pada Ulasan Negatif</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-sub">Semakin besar ukuran kata = semakin sering muncul di ulasan negatif</div>', unsafe_allow_html=True)
            try:
                wc = WordCloud(width=900, height=400, background_color='white', max_words=100,
                    colormap='Reds', prefer_horizontal=0.85).generate_from_frequencies(wc_d)
                fig_wc, ax_wc = plt.subplots(figsize=(12, 5))
                ax_wc.imshow(wc, interpolation='bilinear')
                ax_wc.axis('off')
                fig_wc.tight_layout()
                st.pyplot(fig_wc); plt.close(fig_wc)
            except Exception as e:
                st.error(f"Gagal membuat WordCloud: {e}")
            top_w = sorted(wc_d.items(), key=lambda x: x[1], reverse=True)[:20]
            if top_w:
                st.markdown('<div style="font-size:0.9rem;font-weight:600;color:#334155;margin:15px 0 8px;">📋 Top 20 Kata Teratas</div>', unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(top_w, columns=['Kata', 'Frekuensi']), use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data wordcloud tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN 9: JARINGAN ANTAR DESTINASI
# ══════════════════════════════════════════════════════════
elif halaman == "jaringan":
    page_header("Jaringan Antar Destinasi", "Visualisasi hubungan antar topik berdasarkan kata kunci bersama")
    kpi_row()
    if data_centrality and data_centrality.get('nodes') and len(data_centrality['nodes']) > 0:
        nodes = data_centrality['nodes']
        edges = data_centrality['edges']
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔗 Network Graph — Hubungan Topik</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-sub">Node = Topik per destinasi · Garis = Kata kunci bersama (≥2 kata) · Ukuran node = jumlah ulasan</div>', unsafe_allow_html=True)
        try:
            G = nx.Graph()
            for node in nodes:
                G.add_node(node['id'], label=node['label'], lokasi=node['lokasi'], size=node.get('size', 10))
            for edge in edges:
                G.add_edge(edge['source'], edge['target'], weight=edge.get('weight', 1), common_words=edge.get('common_words', []))
            pos_nx = nx.spring_layout(G, k=2.5, seed=42)
            edge_traces = []
            for edge in G.edges(data=True):
                x0, y0 = pos_nx[edge[0]]; x1, y1 = pos_nx[edge[1]]
                w = edge[2].get('weight', 1)
                cw = ', '.join(edge[2].get('common_words', []))
                edge_traces.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None], mode='lines',
                    line=dict(width=max(1, w*1.5), color='#CBD5E1'),
                    hoverinfo='text', text=f"Kata bersama: {cw}", opacity=0.7))
            nx_l, ny_l, nc_l, ns_l, nt_l, nh_l = [], [], [], [], [], []
            for node in G.nodes(data=True):
                x, y = pos_nx[node[0]]
                nx_l.append(x); ny_l.append(y)
                lok = node[1].get('lokasi', '')
                nc_l.append(LOC_COLOR.get(lok, '#2563EB'))
                ns_l.append(max(25, node[1].get('size', 10)*0.5))
                nt_l.append(node[1].get('label', ''))
                nh_l.append(f"<b>{node[1].get('label','')}</b><br>Destinasi: {lok}<br>Jumlah: {node[1].get('size',0)}")
            node_trace = go.Scatter(x=nx_l, y=ny_l, mode='markers+text',
                marker=dict(size=ns_l, color=nc_l, line=dict(width=2, color='white')),
                text=nt_l, textposition='top center',
                textfont=dict(size=9, family='Inter', color='#0F172A'),
                hoverinfo='text', hovertext=nh_l)
            fig_net = go.Figure(data=edge_traces + [node_trace])
            fig_net.update_layout(height=550, plot_bgcolor='white', paper_bgcolor='white',
                showlegend=False, margin=dict(t=20, b=20, l=20, r=20),
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                hoverlabel=dict(bgcolor='#0F172A', font=dict(color='white', size=12, family='Inter')))
            st.plotly_chart(fig_net, use_container_width=True, config={'displayModeBar': False})
            if edges:
                st.markdown('<div style="font-size:0.9rem;font-weight:600;color:#334155;margin:15px 0 8px;">📋 Daftar Koneksi Antar Topik</div>', unsafe_allow_html=True)
                erows = []
                for edge in edges:
                    src = next((n['label'] for n in nodes if n['id'] == edge['source']), '?')
                    tgt = next((n['label'] for n in nodes if n['id'] == edge['target']), '?')
                    erows.append({'Topik 1': src, 'Topik 2': tgt,
                        'Jumlah Kata Bersama': edge.get('weight', 0),
                        'Kata Bersama': ', '.join(edge.get('common_words', []))})
                st.dataframe(pd.DataFrame(erows), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Gagal membuat jaringan: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data jaringan tidak tersedia.")
