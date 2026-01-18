import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import feedparser
import urllib.parse
from datetime import datetime
from xgboost import XGBClassifier
from tradingview_ta import TA_Handler, Interval, Exchange
import warnings
import time

warnings.filterwarnings("ignore")

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Ortak Sinyalci v28.2",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SABİTLER & LİSTELER (KAYA GİBİ SAĞLAM TANIMLAR) ---
BIST_30 = ['AKBNK', 'ARCLK', 'ASELS', 'ASTOR', 'BIMAS', 'BRISA', 'DOAS', 'EKGYO', 'ENKAI', 'EREGL', 'FROTO', 'GARAN', 'GUBRF', 'HEKTS', 'ISCTR', 'KCHOL', 'KONTR', 'KOZAL', 'KRDMD', 'ODAS', 'OYAKC', 'PETKM', 'PGSUS', 'SAHOL', 'SASA', 'SISE', 'TAVHL', 'TCELL', 'THYAO', 'TOASO', 'TUPRS', 'YKBNK']

BIST_50 = sorted(list(set(BIST_30 + ['AEFES', 'AGHOL', 'AKCNS', 'AKSA', 'AKSEN', 'ALARK', 'ALFAS', 'BERA', 'CANTE', 'CIMSA', 'CWENE', 'DOHOL', 'EGEEN', 'ENJSA', 'EUPWR', 'EUREN', 'GESAN', 'GLYHO', 'GWIND', 'HALKB', 'ISGYO', 'ISMEN', 'KLSER', 'KMPUR', 'KONYA', 'KORDS', 'KOZAA', 'MAVI', 'MGROS', 'MIATK', 'OTKAR', 'PENTA', 'QUAGR', 'REEDR', 'SDTTR', 'SKBNK', 'SMRTG', 'SOKM', 'TABGD', 'TKFEN', 'TTKOM', 'TTRAK', 'TUKAS', 'TURSG', 'ULKER', 'VAKBN', 'VESBE', 'VESTL', 'YEOTK', 'YYLGD', 'ZOREN'])))

BIST_100 = sorted(list(set(BIST_50 + ['ADEL', 'AGESA', 'AKFGY', 'AKFYE', 'AKGRT', 'AKYHO', 'ALBRK', 'ALCTL', 'ALGYO', 'ALKA', 'ALKIM', 'ANELE', 'ANGEN', 'ANHYT', 'ANSGR', 'ARZUM', 'ASGYO', 'ATAKP', 'AVOD', 'AVPGY', 'AYDEM', 'AYEN', 'AYGAZ', 'BAGFS', 'BAKAB', 'BALAT', 'BANVT', 'BARMA', 'BASCM', 'BASGZ', 'BAYRK', 'BEGYO', 'BEYAZ', 'BFREN', 'BIZIM', 'BJKAS', 'BLCYT', 'BMSCH', 'BMSTL', 'BNTAS', 'BOBET', 'BOSSA', 'BRKO', 'BRKSN', 'BRMEN', 'BRSAN', 'BRYAT', 'BSOKE', 'BTCIM', 'BUCIM', 'BURCE', 'BURVA', 'BVSAN', 'BYDNR', 'CEOEM', 'CUSAN', 'CVKMD', 'DAGHL', 'DAPGM', 'DARDL', 'DENGE', 'DERHL', 'DERIM', 'DESA', 'DESPC', 'DEVA', 'DGATE', 'DGGYO', 'DGNMO', 'DIRIT', 'DITAS', 'DMSAS', 'DNISI', 'DOBUR', 'DOCO', 'DOGUB', 'DOKTA', 'DURDO', 'DYOBY', 'DZGYO', 'ECILC', 'ECZYT', 'EDATA', 'EDIP', 'EGGUB', 'EGPRO', 'EGSER', 'EKIZ', 'EKSUN', 'ELITE', 'EMKEL', 'EMNIS', 'ENSRI', 'EPLAS', 'ERBOS', 'ERCB', 'ERSU', 'ESCAR', 'ESCOM', 'ESEN', 'ETILR', 'ETYAT', 'EUHOL', 'EUKYO', 'EUPWR', 'EUREN', 'EUYO', 'FADE', 'FENER', 'FLAP', 'FMIZP', 'FONET', 'FORMT', 'FRIGO', 'FZLGY', 'GARFA', 'GEDIK', 'GEDZA', 'GENIL', 'GENTS', 'GEREL', 'GESAN', 'GLBMD', 'GLRYH', 'GLYHO', 'GOKNR', 'GOLTS', 'GOODY', 'GOZDE', 'GRNYO', 'GRSEL', 'GSDDE', 'GSDHO', 'GSRAY', 'GWIND', 'GZNMI', 'HALKB', 'HATEK', 'HATSN', 'HDFGS', 'HEDEF', 'HEKTS', 'HKTM', 'HLGYO', 'HUBVC', 'HUNER', 'HURGZ', 'ICBCT', 'ICUGS', 'IDGYO', 'IEYHO', 'IHAAS', 'IHEVA', 'IHGZT', 'IHLGM', 'IHYAY', 'IMASM', 'INDES', 'INFO', 'INTEM', 'INVEO', 'INVES', 'IPEKE', 'ISATR', 'ISBIR', 'ISBTR', 'ISCTR', 'ISDMR', 'ISFIN', 'ISGSY', 'ISGYO', 'ISKPL', 'ISMEN', 'ISYAT', 'IZFAS', 'IZINV', 'IZMDC', 'JANTS', 'KAPLM', 'KAREL', 'KARSN', 'KARTN', 'KATMR', 'KAYSE', 'KCAER', 'KFEIN', 'KGYO', 'KIMMR', 'KLGYO', 'KLKIM', 'KLMSN', 'KLNMA', 'KLRHO', 'KLSER', 'KMPUR', 'KNFRT', 'KONTR', 'KONYA', 'KORDS', 'KOZAA', 'KOZAL', 'KRDMA', 'KRDMB', 'KRDMD', 'KRGYO', 'KRONT', 'KRPLS', 'KRSTL', 'KRTEK', 'KRVGD', 'KSTUR', 'KTLEV', 'KTSKR', 'KUTPO', 'KUYAS', 'KZBGY', 'KZGYO', 'LIDFA', 'LIDER', 'LINK', 'LKMNH', 'LMKDC', 'LOGO', 'LUKSK', 'MAALT', 'MACKO', 'MAGEN', 'MAKIM', 'MAKTK', 'MANAS', 'MARBL', 'MARKA', 'MARTI', 'MAVI', 'MEDTR', 'MEGAP', 'MEPET', 'MERCN', 'MERIT', 'MERKO', 'METRO', 'MGROS', 'MIATK', 'MMCAS', 'MNDRS', 'MNDTR', 'MOBTL', 'MPARK', 'MRGYO', 'MRSHL', 'MSGYO', 'MTRKS', 'MTRYO', 'MZHLD', 'NATEN', 'NETAS', 'NIBAS', 'NTGAZ', 'NTHOL', 'NUGYO', 'NUHCM', 'OBASE', 'OBAMS', 'ODAS', 'OFSYM', 'ONCSM', 'ORCAY', 'ORGE', 'ORMA', 'OSMEN', 'OSTIM', 'OTKAR', 'OTTO', 'OYAKC', 'OYAYO', 'OYLUM', 'OYYAT', 'OZGYO', 'OZKGY', 'OZRDN', 'OZSUB', 'PAGYO', 'PAMEL', 'PAPIL', 'PARSN', 'PASEU', 'PASYU', 'PCILT', 'PEGYO', 'PEKGY', 'PENGD', 'PENTA', 'PETKM', 'PETUN', 'PGSUS', 'PINSU', 'PKART', 'PKENT', 'PLAT', 'PNLSN', 'POLHO', 'POLTK', 'PRDGS', 'PRKAB', 'PRKME', 'PRZMA', 'PSDTC', 'QNBFB', 'QUAGR', 'RALYH', 'RAYSG', 'REEDR', 'RNPOL', 'RODRG', 'ROYAL', 'RTALB', 'RUBNS', 'RYGYO', 'RYSAS', 'SAFKR', 'SAHOL', 'SAMAT', 'SANEL', 'SANFM', 'SANKO', 'SASA', 'SAYAS', 'SDTTR', 'SEKFK', 'SEKUR', 'SELEC', 'SELVA', 'SEYKM', 'SILVR', 'SISE', 'SKBNK', 'SKTAS', 'SKYMD', 'SMART', 'SMRTG', 'SNGYO', 'SNKRN', 'SNPAM', 'SODSN', 'SOKE', 'SOKM', 'SONME', 'SRVGY', 'SUMAS', 'SUNTK', 'SURGY', 'SUWEN', 'TABGD', 'TARGET', 'TATGD', 'TAVHL', 'TBORG', 'TCELL', 'TDGYO', 'TEKTU', 'TERA', 'TGSAS', 'THYAO', 'TKFEN', 'TKNSA', 'TLMAN', 'TMPOL', 'TMSN', 'TNZTP', 'TOASO', 'TRCAS', 'TRGYO', 'TRILC', 'TSGYO', 'TSKB', 'TSPOR', 'TTKOM', 'TTRAK', 'TUCLK', 'TUKAS', 'TUPRS', 'TUREX', 'TURGG', 'TURSG', 'UFUK', 'ULAS', 'ULKER', 'ULUFA', 'ULUSE', 'ULUUN', 'UMPAS', 'UNLU', 'USAK', 'VAKBN', 'VAKFN', 'VAKKO', 'VANGD', 'VBTYZ', 'VERUS', 'VESBE', 'VESTL', 'VKFYO', 'VKGYO', 'VKING', 'YAPRK', 'YATAS', 'YAYLA', 'YEOTK', 'YESIL', 'YGGYO', 'YGYO', 'YKBNK', 'YKSLN', 'YONGA', 'YUNSA', 'YYAPI', 'YYLGD', 'ZEDUR', 'ZOREN', 'ZRGYO'])))

TUM_HISSELER = sorted(list(set(BIST_100 + [
    'A1CAP', 'ACSEL', 'ADESE', 'ADGYO', 'AFYON', 'AGROT', 'AGYO', 'AKYHO', 'ALCAR', 'ALTNY', 'ARASE', 'ARDYZ', 'ARENA', 'ARSAN', 'ASUZU', 'ATATP', 'ATEKS', 'ATLAS', 'ATSYH', 'AVGYO', 'AVHOL', 'AVTUR', 'AYCES', 'AZTEK', 
    'BIGCH', 'BINHO', 'BRKVY', 'CATES', 'CLEBI', 'CMBTN', 'CMENT', 'CONSE', 'COSMO', 'CRDFA', 'CRFSA', 'CVKMD', 
    'DEMISA', 'DGNMO', 'DIRIT', 'DITAS', 'DMSAS', 'DNISI', 'DOCO', 'DOGUB', 'DYOBY', 
    'EBEBK', 'EKOS', 'EYGYO', 'FORTE', 
    'GIPTA', 'GMTAS', 'HATSN', 'ICUGS', 'IDGYO', 'ISATR', 'ISKUR', 'IZENR', 
    'KOCMT', 'KONKA', 'KOPOL', 'LIDER', 'LMKDC', 
    'MAKTK', 'MARBL', 'MEKAG', 'MHRGY', 'OFSYM', 
    'PASEU', 'PNLSN', 'RALYH', 'RNPOL', 'SAFKR', 'SKYMD', 'SURGY', 'TARGET', 
    'VRGYO', 'CEMZY', 'MARMR', 'ENTRA', 'LILAK', 'KOTON', 'RGYAS', 'ALVES', 'ARTMS', 'MOGAN', 'OBAMS', 'KBORU'
])))

# --- FONKSİYONLAR ---
@st.cache_data(ttl=300)
def veri_cek_motoru(hisse_kodu, interval="1d"):
    hisse_kodu = hisse_kodu.upper().strip()
    try:
        arama_kodu = hisse_kodu + ".IS"
        period = "2y"
        if interval in ["1m", "5m", "15m"]: period = "5d"
        try:
            data = yf.download(arama_kodu, period=period, interval=interval, progress=False, auto_adjust=False, threads=False, ignore_tz=True)
        except Exception: return None

        if data is None or data.empty or len(data) < 5: return None
        if isinstance(data.columns, pd.MultiIndex): 
            try: data.columns = data.columns.get_level_values(0)
            except: pass
        data.columns = [c.strip().title() for c in data.columns]
        if 'Close' not in data.columns: return None
        if 'Adj Close' in data.columns: data['Close'] = data['Adj Close']
        if 'Open' not in data.columns: data['Open'] = data['Close'].shift(1).fillna(data['Close'])
        data.sort_index(inplace=True)
        return data
    except: return None

def tradingview_sinyal_al(sembol, interval_str="1d"):
    try:
        screener = "turkey"; exchange = "BIST"
        tv_interval = Interval.INTERVAL_1_DAY
        if interval_str == "5m": tv_interval = Interval.INTERVAL_5_MINUTES
        elif interval_str == "15m": tv_interval = Interval.INTERVAL_15_MINUTES
        elif interval_str == "1h": tv_interval = Interval.INTERVAL_1_HOUR
        handler = TA_Handler(symbol=sembol, screener=screener, exchange=exchange, interval=tv_interval)
        return handler.get_analysis().summary.get('RECOMMENDATION', 'NÖTR')
    except: return "NÖTR"

def buffett_puanla(sembol, teknik_sinyal):
    try:
        ticker = yf.Ticker(sembol + ".IS")
        info = ticker.info
        fk = info.get('trailingPE', None); pd_dd = info.get('priceToBook', 99); roe = info.get('returnOnEquity', 0)
        puan = 0
        if fk is not None:
            if fk < 10: puan += 25
            elif fk < 20: puan += 15
        if pd_dd is not None and pd_dd < 1.5: puan += 25
        if roe is not None and roe > 0.20: puan += 25 
        if "BUY" in teknik_sinyal: puan += 25
        return puan, fk
    except: return 0, None

def ai_tahmin_yap(sembol):
    try:
        ticker = f"{sembol}.IS"
        all_data = yf.download(ticker, period="2y", interval="1d", progress=False, threads=False, ignore_tz=True)
        if all_data is None or all_data.empty: return None, "Veri Yok"
        if len(all_data) < 60: return None, "Yetersiz Veri"
        df = all_data.copy()
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [c.strip().title() for c in df.columns]
        if 'Close' not in df.columns: return None, "Fiyat Hatası"
        ai_df = pd.DataFrame({"Target": df['Close']}); ai_df.dropna(inplace=True)
        ai_df["Yarin"] = ai_df["Target"].shift(-1); ai_df["Hedef"] = (ai_df["Yarin"] > ai_df["Target"]).astype(int)
        try:
            ai_df["SMA_10"] = ai_df["Target"] / ai_df["Target"].rolling(10).mean()
            ai_df["SMA_50"] = ai_df["Target"] / ai_df["Target"].rolling(50).mean()
            delta = ai_df["Target"].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); loss = loss.replace(0, 0.001)
            ai_df["RSI"] = 100 - (100 / (1 + (gain / loss)))
        except: return None, "İndikatör Hatası"
        ai_df.replace([np.inf, -np.inf], np.nan, inplace=True); ai_df.dropna(inplace=True)
        if len(ai_df) < 30: return None, "Veri Yetersiz"
        model = XGBClassifier(n_estimators=100, max_depth=3, eval_metric='logloss', random_state=42)
        predictors = ["SMA_10", "SMA_50", "RSI"]
        model.fit(ai_df.iloc[:-1][predictors], ai_df.iloc[:-1]["Hedef"])
        son_veri = ai_df.iloc[[-1]][predictors]; prob = model.predict_proba(son_veri)[0][1]
        onemler = model.feature_importances_; en_onemli_index = np.argmax(onemler); en_onemli_faktor = predictors[en_onemli_index]
        return prob, en_onemli_faktor
    except Exception as e: return None, f"Hata: {str(e)}"

# --- YAN MENÜ ---
st.sidebar.title("🦅 Ortak Sinyalci v28.2")
st.sidebar.write("7b Slayer Final Fix")

mod = st.sidebar.radio("Mod Seçimi:", ["Analiz Tablosu", "AI Kahini 🤖", "Haber Casusu 📰", "Ayarlar ⚙️"])

# --- HAFIZA YÖNETİMİ (SESSION STATE) ---
if 'ozel_hisseler' not in st.session_state:
    st.session_state.ozel_hisseler = []

if 'secilen_hisseler_state' not in st.session_state:
    st.session_state.secilen_hisseler_state = BIST_30 # Başlangıçta BIST 30 seçili gelsin

# --- MANUEL EKLEME KUTUSU ---
st.sidebar.markdown("---")
st.sidebar.write("🔎 **Manuel Hisse Ekle:**")
yeni_hisse = st.sidebar.text_input("Sembol (Örn: MARMR, CEMZY)", key="yeni_hisse_input")

if st.sidebar.button("Listeye Ekle +"):
    if yeni_hisse:
        sembol_upper = yeni_hisse.upper().strip()
        
        # 1. Özel hafızaya ekle
        if sembol_upper not in st.session_state.ozel_hisseler:
            st.session_state.ozel_hisseler.append(sembol_upper)
        
        # 2. Aktif listeye zorla ekle (Zaten varsa eklemez, yoksa ekler)
        if sembol_upper not in st.session_state.secilen_hisseler_state:
            st.session_state.secilen_hisseler_state.append(sembol_upper)
            
        st.sidebar.success(f"{sembol_upper} eklendi!")
        time.sleep(0.5)
        st.rerun()

st.sidebar.markdown("---")

# --- OTOMATİK LİSTE SEÇİMİ (MAGIC HAPPENS HERE) ---
# Callback fonksiyonu: Radio butonu değiştiğinde çalışır
def liste_guncelle():
    secim = st.session_state.liste_tipi_radio
    if secim == "BIST 30":
        yeni_liste = BIST_30
    elif secim == "BIST 50":
        yeni_liste = BIST_50
    elif secim == "BIST 100":
        yeni_liste = BIST_100
    else:
        yeni_liste = TUM_HISSELER
    
    # Manuel eklenenleri koru ve yeni listeyle birleştir
    st.session_state.secilen_hisseler_state = sorted(list(set(yeni_liste + st.session_state.ozel_hisseler)))

liste_tipi = st.sidebar.radio(
    "Hisse Grubu (Otomatik Doldur):", 
    ["BIST 30", "BIST 50", "BIST 100", "TÜM HİSSELER"],
    key="liste_tipi_radio",
    on_change=liste_guncelle # Değişiklik anında fonksiyonu çalıştır
)

# Havuz: Şu anki seçime göre tüm olası hisseler + manuel eklenenler
if liste_tipi == "BIST 30": temel_havuz = BIST_30
elif liste_tipi == "BIST 50": temel_havuz = BIST_50
elif liste_tipi == "BIST 100": temel_havuz = BIST_100
else: temel_havuz = TUM_HISSELER

genel_havuz = sorted(list(set(temel_havuz + st.session_state.ozel_hisseler)))

def temizle_callback():
    st.session_state.secilen_hisseler_state = []

if st.sidebar.button("Listeyi Temizle", on_click=temizle_callback):
    pass

secilen_liste = st.sidebar.multiselect(
    "Takip Listesi:",
    options=genel_havuz,
    default=st.session_state.secilen_hisseler_state,
    key="secilen_hisseler_widget"
)

# Widget ile state senkronizasyonu
if secilen_liste != st.session_state.secilen_hisseler_state:
    st.session_state.secilen_hisseler_state = secilen_liste

interval_secim = st.sidebar.selectbox("Zaman Dilimi:", ["1d", "5m", "15m", "1h"])

# --- ANA EKRAN ---
st.title("Borsa Kontrol Merkezi 🚀")

if mod == "Analiz Tablosu":
    st.subheader(f"Piyasa Analizi ({interval_secim})")
    
    if st.button("Taramayı Başlat 🔥"):
        if not secilen_liste:
            st.warning("⚠️ Lütfen yan menüden en az bir hisse seçin.")
        else:
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, sembol in enumerate(secilen_liste):
                status_text.text(f"Analiz ediliyor: {sembol}...")
                df = veri_cek_motoru(sembol, interval=interval_secim)
                
                if df is not None and not df.empty:
                    try:
                        son = df.iloc[-1]
                        sma20 = df['Close'].rolling(20).mean().iloc[-1]
                        trend = "YÜKSELİŞ 🟢" if son['Close'] > sma20 else "DÜŞÜŞ 🔴"
                        tv_sinyal = tradingview_sinyal_al(sembol, interval_secim)
                        delta = df['Close'].diff(); gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(14).mean(); loss = loss.replace(0, 0.001)
                        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
                        puan, fk = buffett_puanla(sembol, tv_sinyal)
                        karar = "BEKLE"
                        if "BUY" in tv_sinyal and trend == "YÜKSELİŞ 🟢": karar = "AL 🚀"
                        elif "SELL" in tv_sinyal: karar = "SAT 🔻"
                        results.append({
                            "Sembol": sembol, "Fiyat": round(son['Close'], 2), "Sinyal": karar,
                            "TV_Özet": tv_sinyal, "Trend": trend, "RSI": round(rsi, 1),
                            "F/K": f"{fk:.2f}" if fk else "-", "Puan": puan
                        })
                    except: pass 
                progress_bar.progress((i + 1) / len(secilen_liste))
            
            status_text.success("Tarama Tamamlandı!")
            time.sleep(1)
            status_text.empty(); progress_bar.empty()

            if results:
                df_res = pd.DataFrame(results)
                def highlight_vals(val):
                    color = ''
                    if 'AL 🚀' in str(val): color = 'background-color: #004d00; color: white'
                    elif 'SAT 🔻' in str(val): color = 'background-color: #660000; color: white'
                    elif 'STRONG_BUY' in str(val): color = 'color: #00E676; font-weight: bold'
                    elif 'STRONG_SELL' in str(val): color = 'color: #FF5252; font-weight: bold'
                    return color
                st.dataframe(df_res.style.applymap(highlight_vals), use_container_width=True, height=600)
            else: st.error("Veri alınamadı veya piyasa kapalı olabilir.")

elif mod == "AI Kahini 🤖":
    st.subheader("Yapay Zeka (XGBoost) Tahmincisi")
    if not secilen_liste: st.warning("⚠️ Önce sol menüden hisse seçmelisin!")
    else:
        target_stock = st.selectbox("Analiz Edilecek Hisse:", secilen_liste)
        if st.button("AI Analizi Başlat 🧠"):
            with st.spinner(f"{target_stock} için veriler işleniyor..."):
                prob, mesaj = ai_tahmin_yap(target_stock)
                if prob is None:
                    st.error(f"⚠️ {mesaj}"); st.info("Bu hisse yeni olabilir.")
                else:
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Hisse", target_stock)
                    col1.metric("Yükseliş İhtimali", f"%{prob*100:.1f}")
                    if prob > 0.60: col2.success("### KARAR: GÜÇLÜ AL 🚀"); st.balloons()
                    elif prob < 0.40: col2.error("### KARAR: SAT / DÜŞÜŞ 🔻")
                    else: col2.warning("### KARAR: NÖTR / BEKLE ⚖️")
                    col3.info(f"🔑 Ana Faktör: {mesaj}")

elif mod == "Haber Casusu 📰":
    st.subheader("Haber Merkezi (Google News)")
    if not secilen_liste: st.warning("Hisse seçin.")
    else:
        news_stock = st.selectbox("Haberleri Getir:", secilen_liste)
        if st.button("Haberleri Tara 🕵️‍♂️"):
            try:
                arama_metni = news_stock + " hisse"
                encoded = urllib.parse.quote(arama_metni)
                rss = f"https://news.google.com/rss/search?q={encoded}&hl=tr&gl=TR&ceid=TR:tr"
                feed = feedparser.parse(rss)
                if not feed.entries: st.info("Güncel haber bulunamadı.")
                for entry in feed.entries[:10]:
                    with st.expander(f"{entry.title} ({entry.published[:16]})"):
                        st.write(f"Kaynak: {entry.source.title}"); st.markdown(f"[Habere Git 🔗]({entry.link})", unsafe_allow_html=True)
            except: st.error("Bağlantı hatası.")

elif mod == "Ayarlar ⚙️":
    st.write("Risk Yönetimi")
    kasa = st.number_input("Toplam Kasa (TL):", value=100000, step=1000)
    risk_yuzde = st.slider("Risk İştahı (%)", 0.5, 5.0, 2.0, 0.1)
    st.info(f"✅ İşlem Başına Önerilen Maksimum Risk Tutarı: **{kasa * (risk_yuzde/100):,.0f} TL**")