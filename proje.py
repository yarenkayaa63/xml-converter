import streamlit as st
import pandas as pd
from lxml import etree
import io
from datetime import datetime
import getpass

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="XML Architect Pro", page_icon="🛡️", layout="wide")

# 2. LİLA / MOR TEMA - ÖZEL CSS
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #0b0c10; }
    
    /* Header Paneli */
    .main-header {
        background-color: #1a1a2e;
        padding: 20px;
        border-radius: 0px 0px 10px 10px;
        border-bottom: 2px solid #6c5ce7;
        margin-bottom: 40px;
    }
    
    /* Kart Tasarımları */
    .file-card {
        background-color: #1a1a2e;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2d3436;
        margin-bottom: 10px;
    }
    
    .card-title {
        color: #a29bfe; 
        font-weight: bold;
        font-size: 11px;
        letter-spacing: 0.5px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    /* Analytics Metrik Kutuları */
    .metric-box {
        background-color: #2d3436;
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #6c5ce7;
        margin-bottom: 8px;
    }
    .metric-val { color: #81ecec; font-weight: bold; font-size: 18px; }
    .metric-lbl { color: #b2bec3; font-size: 10px; text-transform: uppercase; }

    /* Input ve Yükleme Bölümleri */
    .stTextInput input, .stFileUploader section {
        background-color: #0b0c10 !important;
        border: 1px solid #4a4e69 !important;
        color: #a29bfe !important;
    }

    /* İşlem Butonu (Lila) */
    div.stButton > button {
        background-color: #6c5ce7 !important;
        color: white !important;
        font-weight: bold !important;
        height: 45px !important;
        border-radius: 6px !important;
        border: none !important;
        transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #a29bfe !important; transform: translateY(-2px); }
    
    /* İndirme Butonu (Turkuaz) */
    .stDownloadButton > button {
        background-color: #00cec9 !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a1a2e; border-right: 1px solid #2d3436; }
    h1, h2, h3, p, span, label { color: #dfe6e9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ÜST PANEL ---
st.markdown(f"""
    <div class="main-header">
        <h1 style='margin:0; color:#a29bfe !important; font-size: 26px; font-weight: 800;'>XML ARCHITECT PRO</h1>
        <p style='margin:0; color:#b2bec3 !important; font-size: 11px;'>ENTERPRISE ANALYTICS ENGINE v7.4 | {getpass.getuser().upper()}</p>
    </div>
    """, unsafe_allow_html=True)

# --- ARŞİV PANELİ (SIDEBAR) ---
if 'history' not in st.session_state: st.session_state.history = []
with st.sidebar:
    st.markdown("<h2 style='color:#a29bfe !important; font-size: 16px;'>📂 ARCHIVE</h2>", unsafe_allow_html=True)
    search_query = st.text_input("Filter...", placeholder="Search history...")
    st.write("---")
    for item in st.session_state.history:
        if search_query.lower() in item.lower(): st.code(item, language="text")

# --- ANA İÇERİK ---
col_left, col_right = st.columns([2, 1])

with col_left:
    # DOSYA GİRİŞLERİ
    st.markdown('<div class="file-card"><div class="card-title">📊 EXCEL DATA SOURCE</div>', unsafe_allow_html=True)
    excel_file = st.file_uploader("XLSX", type=['xlsx'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="file-card"><div class="card-title">🛡️ XSD SECURITY SCHEMA</div>', unsafe_allow_html=True)
    xsd_file = st.file_uploader("XSD", type=['xsd'], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="file-card"><div class="card-title">✍️ FILENAME</div>', unsafe_allow_html=True)
    custom_filename = st.text_input("Filename", placeholder="Enter XML name (e.g. Export_Data)", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if excel_file:
        try:
            xls = pd.ExcelFile(excel_file)
            # Sayfa isimlerini kontrol ederek yükle
            df_genel = pd.read_excel(xls, 'GenelBilgiler')
            df_urun = pd.read_excel(xls, 'UrunBilgileri')
            df_hammadde = pd.read_excel(xls, 'HamMadde')
            
            with st.expander("🔍 DATA PREVIEW"):
                t1, t2, t3 = st.tabs(["General", "Products", "Materials"])
                t1.dataframe(df_genel.head())
                t2.dataframe(df_urun.head())
                t3.dataframe(df_hammadde.head())

            # XML ÜRETME BUTONU
            if st.button("🚀 EXECUTE GENERATION"):
                root = etree.Element("UretimBildirimFormu")
                
                # Metadata
                genel = etree.SubElement(root, "GenelBilgiler")
                for c in df_genel.columns:
                    val = df_genel.iloc[0][c]
                    etree.SubElement(genel, c).text = str(val).strip() if pd.notna(val) else ""

                # Ürünler ve Hammaddeler
                urunler = etree.SubElement(root, "Urunler")
                for _, r in df_urun.iterrows():
                    u = etree.SubElement(urunler, "Urun")
                    for c in df_urun.columns: 
                        etree.SubElement(u, c).text = str(r[c]).strip() if pd.notna(r[c]) else ""
                    
                    h_match = df_hammadde[df_hammadde['ReferansSiraNo'] == r['SiraNo']]
                    if not h_match.empty:
                        hm_root = etree.SubElement(u, "Hammaddeler")
                        for _, hr in h_match.iterrows():
                            hm = etree.SubElement(hm_root, "HamMadde")
                            for c in df_hammadde.columns: 
                                etree.SubElement(hm, c).text = str(hr[c]).strip() if pd.notna(hr[c]) else ""

                xml_out = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="ISO-8859-9")
                st.session_state.xml_ready = xml_out
                
                # İsimlendirme
                final_name = custom_filename if custom_filename else f"Output_{datetime.now().strftime('%H%M')}"
                st.session_state.last_filename = f"{final_name}.xml"
                st.session_state.history.append(st.session_state.last_filename)
                st.success(f"✅ Success: {st.session_state.last_filename} generated.")

            # İNDİRME BUTONU
            if 'xml_ready' in st.session_state:
                st.download_button(
                    label=f"💾 SAVE FILE",
                    data=st.session_state.xml_ready,
                    file_name=st.session_state.last_filename,
                    mime="application/xml"
                )

        except Exception as e:
            st.error(f"System Error: {e}")

# --- SAĞ SÜTUN (ANALİZ PANELİ) ---
with col_right:
    st.markdown('<div class="file-card"><div class="card-title">📈 DATA ANALYTICS</div>', unsafe_allow_html=True)
    
    if excel_file:
        try:
            total_products = len(df_urun)
            total_materials = len(df_hammadde)
            
            # Dinamik Kategori Analizi
            if 'UrunTuru' in df_urun.columns:
                unique_categories = df_urun['UrunTuru'].nunique()
            elif len(df_urun.columns) > 1:
                unique_categories = df_urun.iloc[:, 1].nunique()
            else:
                unique_categories = "1"

            # Doluluk Oranı
            total_cells = df_urun.size
            missing_cells = df_urun.isnull().sum().sum()
            data_completeness = int(((total_cells - missing_cells) / total_cells) * 100) if total_cells > 0 else 0

            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-val">{total_products}</div>
                    <div class="metric-lbl">TOTAL PRODUCTS</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{total_materials}</div>
                    <div class="metric-lbl">TOTAL MATERIALS</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{unique_categories}</div>
                    <div class="metric-lbl">UNIQUE CATEGORIES</div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{data_completeness}%</div>
                    <div class="metric-lbl">DATA COMPLETENESS</div>
                </div>
            """, unsafe_allow_html=True)
            
        except:
            st.markdown("<p style='color:#ff7675; font-size:11px;'>Analysis waiting for valid data...</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:11px; color:#888;'>Upload Excel to see insights.</p>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # PARAMETRELER
    st.markdown(f"""
        <div class="file-card">
            <div class="card-title">⚙️ PARAMETERS</div>
            <p style='font-size:11px; color:#b2bec3;'>
                Status: {'🟢 Active' if excel_file else '⚪ Idle'}<br>
                Encoding: ISO-8859-9<br>
                Build: 7.4 Purple Optimized
            </p>
        </div>
    """, unsafe_allow_html=True)