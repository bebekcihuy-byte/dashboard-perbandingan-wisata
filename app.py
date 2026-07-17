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
# CSS PROFESIONAL
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
.kpi-card::after {
    content: ''; position: absolute; right: -20px; bottom: -20px;
    width: 80px; height: 80px; border-radius: 50%; background: rgba(0,0,0,.03);
}
.kpi-card.red { border-color: #EF4444; }
.kpi-card.green { border-color: #10B981; }
.kpi-label { font-size: 0.78rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.kpi-value { font-size: 2rem; font-weight: 800; color: #0F172A; line-height: 1.1; margin: 4px 0 2px; }
.sec-card {
    background: white; border-radius: 14px;
    padding: 22px 26px; margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,.05); box-sizing: border-box;
}
.sec-title { font-size: 1.05rem; font-weight: 700; color: #0F172A; margin: 0 0 4px; display: flex; align-items: center; gap: 8px; }
.sec-sub { font-size: 0.82rem; color: #64748B; margin: 0 0 18px; }
hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; box-shadow: 0 1px 6px rgba(0,0,0,.06) !important; }
.nav-section { font-size: 0.68rem; font-weight: 700; color: #64748B; letter-spacing: .1em; text-transform: uppercase; padding: 16px 4px 6px; margin-top: 4px; }
.stAlert { border-radius: 10px !important; }
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
try:
    with open('dashboard_data.json', 'r', encoding='utf-8') as f:
        DATA = json.load(f)
except FileNotFoundError:
    st.error("❌ File `dashboard_data.json` tidak ditemukan.")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"❌ JSON error: {e}")
    st.stop()

ringkasan = DATA.get('ringkasan', [])
bridge = DATA.get('bridge', {})
lokasi_list = DATA.get('lokasi_list', [])
data_rating = DATA.get('rating', {})
data_klasifikasi = DATA.get('klasifikasi', {})
data_klaster = DATA.get('klaster', {})
data_topik = DATA.get('topik', {})
data_trending = DATA.get('trending', {})
data_centrality = DATA.get('centrality', {})
data_ulasan = DATA.get('ulasan_detail', {})

LOC_COLOR = {'Desa Wae Rebo': '#2563EB', 'Taman Nasional Komodo': '#EF4444'}
COLORS_TOPIC = ['#4338CA', '#0891B2', '#D97706', '#059669', '#DC2626', '#7C3AED', '#DB2777', '#2563EB']

# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def safe_float(val, default=0.0):
    try: return float(val)
    except: return default

def safe_int(val, default=0):
    try: return int(val)
    except: return default

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
        neg_pct = r.get('persen_negatif', 0)
        color = "red" if neg_pct > 50 else "green"
        col.markdown(f"""
        <div class="kpi-card {color}">
            <div class="kpi-label">{r.get('lokasi', '-')}</div>
            <div style="display:flex;align-items:baseline;gap:12px;margin:6px 0 4px">
                <div class="kpi-value">{neg_pct}%</div>
                <div style="font-size:0.78rem;color:#64748B">negatif</div>
            </div>
            <div style="font-size:0.8rem;color:#475569;margin-bottom:8px">dari <b>{r.get('total_ulasan', 0):,}</b> total ulasan</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:0.75rem">
                <span style="background:#D1FAE5;color:#059669;padding:2px 7px;border-radius:99px;font-weight:600">✅ {r.get('jumlah_positif', 0)} positif</span>
                <span style="background:#FEE2E2;color:#DC2626;padding:2px 7px;border-radius:99px;font-weight:600">❌ {r.get('jumlah_negatif', 0)} negatif</span>
                <span style="background:#F1F5F9;color:#64748B;padding:2px 7px;border-radius:99px;font-weight:600">➖ {r.get('jumlah_netral', 0)} netral</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="background:rgba(255,255,255,.07);border-radius:12px;padding:16px;margin-bottom:8px;">
        <div style="font-size:1.05rem;font-weight:800;color:white;">DASHBOARD PERBANDINGAN PARIWISATA</div>
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

# ══════════════════════════════════════════════════════════
# HALAMAN: BERANDA & PETA
# ══════════════════════════════════════════════════════════
if halaman == "beranda":
    page_header("RANCANGAN DASHBOARD PERBANDINGAN PARIWISATA", "Analisis Ulasan Google Maps · Desa Wae Rebo vs Taman Nasional Komodo · Nusa Tenggara Timur")
    kpi_row()
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📍 Peta Lokasi Destinasi Wisata</div>', unsafe_allow_html=True)
    try:
        peta = folium.Map(
            location=[sum(r.get('lat', -8.5) for r in ringkasan)/max(len(ringkasan), 1),
                      sum(r.get('lon', 120) for r in ringkasan)/max(len(ringkasan), 1)],
            zoom_start=9, tiles="CartoDB positron"
        )
        for r in ringkasan:
            warna_m = "green" if r.get('status_warna') == "Hijau" else "red"
            popup = f"<b>{r.get('lokasi', '')}</b><br>📝 Total: {r.get('total_ulasan', 0)}<br>✅ Positif: {r.get('jumlah_positif', 0)}<br>❌ Negatif: {r.get('jumlah_negatif', 0)}<br>% Negatif: <b>{r.get('persen_negatif', 0)}%</b>"
            folium.Marker([r.get('lat', -8.5), r.get('lon', 120)], popup=folium.Popup(popup, max_width=240), tooltip=r.get('lokasi', ''), icon=folium.Icon(color=warna_m, icon='info-sign')).add_to(peta)
        st_folium(peta, width=None, height=430)
    except Exception as e:
        st.error(f"Gagal memuat peta: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📋 Ringkasan Perbandingan</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{'Destinasi': r.get('lokasi', '-'), 'Total Ulasan': r.get('total_ulasan', 0), 'Positif': r.get('jumlah_positif', 0), 'Negatif': r.get('jumlah_negatif', 0), 'Netral': r.get('jumlah_netral', 0), '% Negatif': f"{r.get('persen_negatif', 0)}%", 'Status': "⚠️ Perlu Perhatian" if r.get('persen_negatif', 0) > 50 else "✅ Cukup Baik"} for r in ringkasan]), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: SENTIMEN
# ══════════════════════════════════════════════════════════
elif halaman == "sentimen":
    page_header("Analisis Sentimen & Distribusi Rating")
    kpi_row()
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📊 Jumlah Sentimen per Destinasi</div>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    sentimen_labels = ['Positif', 'Negatif', 'Netral']
    sentimen_colors = ['#10B981', '#EF4444', '#94A3B8']
    for col, r in zip([col_chart1, col_chart2], ringkasan):
        with col:
            lokasi = r.get('lokasi', '')
            values = [r.get('jumlah_positif', 0), r.get('jumlah_negatif', 0), r.get('jumlah_netral', 0)]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=sentimen_labels, y=values, marker_color=sentimen_colors, text=values, textposition='outside', textfont=dict(size=15, color='#0F172A', family='Inter', weight='bold'), marker_line_color='white', marker_line_width=2.5))
            max_val = max(values) if max(values) > 0 else 10
            fig.update_layout(title=dict(text=lokasi, font=dict(size=14, color='#0F172A', family='Inter', weight='bold'), x=0.5), height=380, plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Inter', size=12, color='#334155'), yaxis=dict(title='Jumlah Ulasan', range=[0, max_val * 1.2], gridcolor='#E2E8F0'), xaxis=dict(showgrid=False), margin=dict(l=50, r=20, t=50, b=50), bargap=0.35)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Contoh Ulasan
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">📝 Contoh Ulasan per Sentimen</div>', unsafe_allow_html=True)
    tab_positif, tab_negatif, tab_netral = st.tabs(["🟢 Positif", "🔴 Negatif", "🟡 Netral"])
    for tab, sentimen_key, sentimen_label in [(tab_positif, 'contoh_positif', 'Positif'), (tab_negatif, 'contoh_negatif', 'Negatif'), (tab_netral, 'contoh_netral', 'Netral')]:
        with tab:
            col_tabel1, col_tabel2 = st.columns(2)
            for col, r in zip([col_tabel1, col_tabel2], ringkasan):
                with col:
                    lokasi = r.get('lokasi', '')
                    contoh_list = data_ulasan.get(lokasi, {}).get(sentimen_key, [])
                    st.markdown(f'**{lokasi}**')
                    if contoh_list:
                        rows = [{'Penulis': u.get('author', 'Anonim'), 'Rating': '⭐' * safe_int(u.get('rating', 0)), 'Tanggal': u.get('date', ''), 'Ulasan': u.get('review', 'Tidak ada teks')} for u in contoh_list[:5]]
                        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                    else:
                        st.info(f"Tidak ada contoh ulasan {sentimen_label.lower()}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rating Bintang
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">⭐ Distribusi Rating Bintang</div>', unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)
    warna_bintang = {1: '#EF4444', 2: '#F97316', 3: '#F59E0B', 4: '#84CC16', 5: '#10B981'}
    for col, lok in zip([col_chart1, col_chart2], lokasi_list):
        with col:
            rc = data_rating.get(lok, {})
            if rc:
                ratings = sorted([safe_int(r) for r in rc.keys()])
                values = [safe_int(rc.get(str(r), 0)) for r in ratings]
                colors = [warna_bintang.get(r, '#94A3B8') for r in ratings]
                labels = [f'{r} ⭐' for r in ratings]
                fig = go.Figure()
                fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition='outside', textfont=dict(size=12, color='#0F172A'), marker_line_color='white', marker_line_width=2.5))
                max_val = max(values) if max(values) > 0 else 10
                fig.update_layout(title=dict(text=lok, font=dict(size=14, color='#0F172A', weight='bold'), x=0.5), height=380, plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(title='Jumlah Ulasan', range=[0, max_val * 1.2], gridcolor='#E2E8F0'), xaxis=dict(showgrid=False), margin=dict(l=50, r=20, t=50, b=50), bargap=0.35)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Data rating tidak tersedia.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: KLASIFIKASI
# ══════════════════════════════════════════════════════════
elif halaman == "klasifikasi":
    page_header("Perbandingan Akurasi Model Klasifikasi", "SVM · Random Forest · Naive Bayes")
    kpi_row()
    if data_klasifikasi:
        model_names = data_klasifikasi.get('model_names', [])
        akurasi = data_klasifikasi.get('akurasi', {})
        detail_data = data_klasifikasi.get('detail', {})
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = model_names[0] if model_names else None
        
        # Chart Akurasi
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">📊 Perbandingan Akurasi Antar Model</div>', unsafe_allow_html=True)
        if model_names and akurasi:
            fig_overall = go.Figure()
            for lok in lokasi_list:
                if lok in akurasi:
                    vals = [safe_float(akurasi[lok].get(m, 0)) for m in model_names]
                    fig_overall.add_trace(go.Bar(name=lok, x=model_names, y=vals, marker_color=LOC_COLOR.get(lok, '#2563EB'), text=[f"{v:.2f}%" for v in vals], textposition='outside', textfont=dict(size=14, family='Inter', weight='bold')))
            fig_overall.update_layout(barmode='group', height=420, plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(title='Akurasi (%)', range=[0, 115], gridcolor='#E2E8F0'), xaxis=dict(showgrid=False), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5), margin=dict(l=50, r=20, t=60, b=50), bargap=0.3)
            st.plotly_chart(fig_overall, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Detail Model
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-title">🔍 Evaluasi Detail per Model</div>', unsafe_allow_html=True)
        model_icons = {'SVM': '🧠', 'Random Forest': '🌲', 'Naive Bayes': '📊'}
        model_colors = {'SVM': '#2563EB', 'Random Forest': '#10B981', 'Naive Bayes': '#F59E0B'}
        model_cmaps = {'SVM': 'Blues', 'Random Forest': 'Greens', 'Naive Bayes': 'YlOrBr'}
        btn_cols = st.columns(len(model_names))
        for idx, model_name in enumerate(model_names):
            with btn_cols[idx]:
                icon = model_icons.get(model_name, '🤖')
                if st.button(f"{icon} {model_name}", key=f"btn_{model_name}", use_container_width=True):
                    st.session_state.selected_model = model_name
                    st.rerun()
        
        selected_model = st.session_state.selected_model
        if selected_model and selected_model in detail_data:
            model_detail = detail_data[selected_model]
            color = model_colors.get(selected_model, '#2563EB')
            st.markdown(f'<div style="background:{color}10;border-left:5px solid {color};border-radius:0 12px 12px 0;padding:15px 20px;margin-bottom:25px;"><div style="font-size:1.15rem;font-weight:700;color:{color};">Detail Evaluasi: {selected_model}</div></div>', unsafe_allow_html=True)
            cmap_name = model_cmaps.get(selected_model, 'Blues')
            cols_dest = st.columns(len(lokasi_list))
            for col_idx, lok in enumerate(lokasi_list):
                with cols_dest[col_idx]:
                    st.markdown(f'**📍 {lok}**')
                    loc_detail = model_detail.get(lok, {})
                    labels_asli = loc_detail.get('labels', ['Negatif', 'Netral', 'Positif'])
                    report = loc_detail.get('report', {})
                    if report:
                        rows = []
                        for cls in labels_asli:
                            if cls in report:
                                r_data = report[cls]
                                rows.append({'Kelas': cls, 'Precision': f"{safe_float(r_data.get('precision', 0)):.2f}", 'Recall': f"{safe_float(r_data.get('recall', 0)):.2f}", 'F1-Score': f"{safe_float(r_data.get('f1-score', 0)):.2f}", 'Support': safe_int(r_data.get('support', 0))})
                        if rows:
                            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=200)
                    cm = loc_detail.get('cm', [])
                    if cm and len(cm) == len(labels_asli):
                        fig_cm = go.Figure(data=go.Heatmap(z=cm, x=labels_asli, y=labels_asli, colorscale=cmap_name, texttemplate="%{text}", textfont={"size": 16}, xgap=4, ygap=4))
                        fig_cm.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10), xaxis=dict(title='Prediksi'), yaxis=dict(title='Aktual', autorange='reversed'), title=dict(text=f'Confusion Matrix', font=dict(size=11)))
                        st.plotly_chart(fig_cm, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: KLASTERISASI
# ══════════════════════════════════════════════════════════
elif halaman == "klaster":
    page_header("Hasil K-Means Clustering", "Pengelompokan ulasan berdasarkan kemiripan konten teks")
    if data_klaster:
        for lok in lokasi_list:
            kd = data_klaster.get(lok)
            if not kd: continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">🧩 {lok}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns([3, 1])
            with c1:
                sx, sy, sc_clust = kd.get('scatter_x', []), kd.get('scatter_y', []), kd.get('scatter_cluster', [])
                if sx and sy and sc_clust and len(sx) > 0:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    scatter = ax.scatter(np.array(sx), np.array(sy), c=np.array(sc_clust), cmap='tab10', alpha=0.75, edgecolor='white', linewidth=0.5, s=40)
                    plt.colorbar(scatter, ax=ax, label='Klaster')
                    ax.set_title(f"K-Means (K={kd.get('k_optimal', '?')})", fontweight='bold')
                    ax.set_xlabel('SVD Komponen 1'); ax.set_ylabel('SVD Komponen 2'); ax.grid(True, alpha=0.3)
                    plt.tight_layout(); st.pyplot(fig); plt.close(fig)
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
# HALAMAN: RADAR
# ══════════════════════════════════════════════════════════
elif halaman == "radar":
    page_header("Radar Chart — Perbandingan Kualitas Clustering", "Perbandingan metrik evaluasi klaster (dinormalisasi)")
    try:
        if data_klaster and len(lokasi_list) >= 2:
            metrics_keys = ['silhouette', 'davies_bouldin', 'calinski_harabasz']
            metrics_label = ['Silhouette\n(↑ bagus)', 'Davies-Bouldin\n(↓ bagus)', 'Calinski-Harabasz\n(↑ bagus)']
            raw = {}
            for lok in lokasi_list:
                if lok in data_klaster:
                    vals, valid = [], True
                    for k in metrics_keys:
                        v = data_klaster[lok].get(k)
                        if v is None: valid = False; break
                        vals.append(safe_float(v))
                    if valid: raw[lok] = vals
            if len(raw) < 2:
                st.warning("Data klaster tidak lengkap.")
            else:
                def normalize(idx, invert=False):
                    all_v = [raw[l][idx] for l in raw]
                    mn, mx = min(all_v), max(all_v)
                    if mx == mn: return {l: 0.5 for l in raw}
                    n = {l: (raw[l][idx] - mn) / (mx - mn) for l in raw}
                    return {l: 1 - v for l, v in n.items()} if invert else n
                norm_sil, norm_db, norm_ch = normalize(0), normalize(1, True), normalize(2)
                normalized = {lok: [norm_sil[lok], norm_db[lok], norm_ch[lok]] for lok in raw}
                N = len(metrics_label)
                angles = [n / float(N) * 2 * math.pi for n in range(N)] + [0]
                st.markdown('<div class="sec-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">📊 Radar Chart Metrik Klasterisasi</div>', unsafe_allow_html=True)
                col_r, col_t = st.columns([1, 1])
                with col_r:
                    fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
                    ax.set_facecolor('#F8FAFC')
                    for lok in raw:
                        vals = normalized[lok] + normalized[lok][:1]
                        color = LOC_COLOR.get(lok, '#2563EB')
                        ax.plot(angles, vals, 'o-', linewidth=2.5, color=color, label=lok, markersize=8)
                        ax.fill(angles, vals, alpha=0.15, color=color)
                    ax.set_xticks(angles[:-1]); ax.set_xticklabels(metrics_label, fontsize=9, fontweight='bold')
                    ax.set_ylim(0, 1); ax.grid(color='#CBD5E1', linestyle='--', alpha=0.6)
                    ax.set_title('Radar Metrik Klasterisasi', fontweight='bold', fontsize=11, pad=20)
                    ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=9)
                    plt.tight_layout(); st.pyplot(fig); plt.close(fig)
                with col_t:
                    st.markdown("**Nilai Asli:**")
                    raw_rows = []
                    for k, label in zip(metrics_keys, ['Silhouette', 'Davies-Bouldin', 'Calinski-Harabasz']):
                        row = {'Metrik': label}
                        for lok in raw: row[lok] = f"{raw[lok][metrics_keys.index(k)]:.4f}"
                        raw_rows.append(row)
                    st.dataframe(pd.DataFrame(raw_rows), use_container_width=True, hide_index=True, height=180)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Data klasterisasi tidak tersedia.")
    except Exception as e:
        st.error(f"Gagal memuat halaman radar: {e}")

# ══════════════════════════════════════════════════════════
# HALAMAN: TOPIC MODELING
# ══════════════════════════════════════════════════════════
elif halaman == "topik":
    page_header("Topic Modeling (LDA)", "Pengidentifikasian topik utama dari ulasan")
    if data_topik:
        for lok in lokasi_list:
            td = data_topik.get(lok)
            if not td: st.info(f"Data topic modeling untuk {lok} tidak tersedia."); continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">📚 {lok}</div>', unsafe_allow_html=True)
            st.markdown(f"<div class='sec-sub'>Jumlah Topik: <b>{td.get('n_topics', 0)}</b></div>", unsafe_allow_html=True)
            topics = td.get('topics', [])
            if topics:
                for i, topic in enumerate(topics):
                    words, weights = topic.get('words', []), topic.get('weights', [])
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
                            fig_t.add_trace(go.Bar(x=words[:10], y=weights[:10], marker_color=COLORS_TOPIC[i % len(COLORS_TOPIC)], text=[f"{wt:.3f}" for wt in weights[:10]], textposition='outside', textfont=dict(size=10)))
                            fig_t.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white', yaxis=dict(title='Bobot', gridcolor='#E2E8F0'), xaxis=dict(tickfont=dict(size=9)), margin=dict(l=40, r=20, t=40, b=60))
                            st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Data topik tidak tersedia.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data topic modeling tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN: TRENDING
# ══════════════════════════════════════════════════════════
elif halaman == "trending":
    page_header("Trending Topik dari Waktu ke Waktu", "Analisis perubahan popularitas topik")
    if data_trending:
        for lok in lokasi_list:
            trend_data = data_trending.get(lok)
            if not trend_data: st.info(f"Data trending untuk {lok} tidak tersedia."); continue
            st.markdown('<div class="sec-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sec-title">📈 {lok}</div>', unsafe_allow_html=True)
            bulan, topik_data = trend_data.get('bulan', []), trend_data.get('topik', {})
            if bulan and topik_data:
                fig_trend = go.Figure()
                for idx, (topic_name, values) in enumerate(topik_data.items()):
                    fig_trend.add_trace(go.Scatter(x=bulan, y=values, mode='lines+markers', name=topic_name, line=dict(color=COLORS_TOPIC[idx % len(COLORS_TOPIC)], width=2.5), marker=dict(size=8)))
                fig_trend.update_layout(height=450, plot_bgcolor='white', paper_bgcolor='white', title=dict(text=f'Trending Topik — {lok}', font=dict(size=14, weight='bold'), x=0.5), xaxis=dict(title='Bulan', gridcolor='#E2E8F0'), yaxis=dict(title='Jumlah Review', gridcolor='#E2E8F0'), legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center'), margin=dict(l=50, r=20, t=60, b=80), hovermode='x unified')
                st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Data trending bulanan tidak tersedia.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Data trending topik tidak tersedia.")

# ══════════════════════════════════════════════════════════
# HALAMAN: WORDCLOUD
# ══════════════════════════════════════════════════════════
elif halaman == "wordcloud":
    page_header("WordCloud Masalah", "Visualisasi kata-kata dalam ulasan negatif")
    for lok in lokasi_list:
        negatif_words = data_ulasan.get(lok, {}).get('wordcloud_negatif', {})
        st.markdown('<div class="sec-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-title">☁️ {lok} — Kata dalam Ulasan Negatif</div>', unsafe_allow_html=True)
        if negatif_words and len(negatif_words) > 0:
            try:
                wc = WordCloud(width=800, height=400, background_color='white', colormap='Reds', max_words=100, prefer_horizontal=0.7).generate_from_frequencies(negatif_words)
                fig_wc, ax_wc = plt.subplots(figsize=(10, 5))
                ax_wc.imshow(wc, interpolation='bilinear'); ax_wc.axis('off')
                ax_wc.set_title(f'WordCloud Ulasan Negatif — {lok}', fontsize=12, fontweight='bold')
                plt.tight_layout(); st.pyplot(fig_wc); plt.close(fig_wc)
            except Exception as e:
                st.error(f"Gagal membuat wordcloud: {e}")
        else:
            st.info("Data wordcloud tidak tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN: JARINGAN
# ══════════════════════════════════════════════════════════
elif halaman == "jaringan":
    page_header("Jaringan Antar Destinasi", "Visualisasi hubungan berdasarkan kesamaan topik")
    st.markdown('<div class="sec-card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title">🔗 Network Graph</div>', unsafe_allow_html=True)
    try:
        G = nx.Graph()
        for r in ringkasan:
            G.add_node(r.get('lokasi', ''), size=r.get('total_ulasan', 100))
        if bridge:
            for key, val in bridge.items():
                if 'to' in key:
                    parts = key.split('_to_')
                    if len(parts) == 2:
                        loc1 = next((r['lokasi'] for r in ringkasan if parts[0].replace('_', ' ').title().lower() in r['lokasi'].lower()), parts[0].replace('_', ' ').title())
                        loc2 = next((r['lokasi'] for r in ringkasan if parts[1].replace('_', ' ').title().lower() in r['lokasi'].lower()), parts[1].replace('_', ' ').title())
                        G.add_edge(loc1, loc2, weight=val.get('similarity', 0.5))
        if G.number_of_nodes() > 0:
            fig_net, ax_net = plt.subplots(figsize=(10, 8))
            ax_net.set_facecolor('#F8FAFC')
            pos = nx.spring_layout(G, k=2, seed=42)
            node_sizes = [G.nodes[n].get('size', 100) / 5 for n in G.nodes()]
            node_colors = [LOC_COLOR.get(n, '#2563EB') for n in G.nodes()]
            nx.draw_networkx_nodes(G, pos, ax=ax_net, node_size=node_sizes, node_color=node_colors, alpha=0.8, edgecolors='white', linewidths=2)
            nx.draw_networkx_edges(G, pos, ax=ax_net, width=3, edge_color='#94A3B8', alpha=0.6, style='dashed')
            nx.draw_networkx_labels(G, pos, ax=ax_net, font_size=11, font_weight='bold', font_color='#0F172A')
            edge_labels = {(u, v): f"{G[u][v].get('weight', 0):.2f}" for u, v in G.edges()}
            nx.draw_networkx_edge_labels(G, pos, ax=ax_net, edge_labels=edge_labels, font_size=9, font_color='#64748B')
            ax_net.set_title('Jaringan Kesamaan Topik Antar Destinasi', fontsize=13, fontweight='bold', pad=15)
            ax_net.axis('off'); plt.tight_layout(); st.pyplot(fig_net); plt.close(fig_net)
            if bridge:
                for key, val in bridge.items():
                    st.markdown(f"- Similarity: **{val.get('similarity', 0):.2f}** | Topik Bersama: {', '.join(val.get('common_topics', []))}")
        else:
            st.info("Tidak ada data jaringan.")
    except Exception as e:
        st.error(f"Gagal memuat jaringan: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
