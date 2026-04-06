import re
import io
import base64
import collections
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
from scipy import stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ThreatScan · Job Fraud Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme toggle ──────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

DARK = st.session_state.theme == "dark"

# Theme palettes
if DARK:
    PAGE_BG = "#08090d"; CARD_BG = "#0d1117"; PAN_BG = "#0f1520"
    BORDER   = "#1a2535"; TXT_PRI = "#f1f5f9"; TXT_SEC = "#7a92aa"
    TXT_MUT  = "#3d5470"; GRID_C  = "#1a2535"
    CSS_PAGE = "#08090d"; CSS_CARD = "#0d1117"
    HERO_GRAD = "linear-gradient(135deg,#0d1117 0%,#0f1923 60%,#0a1520 100%)"
    IB_BG = "rgba(249,115,22,.05)"; IB_BOR = "rgba(249,115,22,.18)"
    CTRL_BG = "#0d1117"
else:
    PAGE_BG = "#f0f4f8"; CARD_BG = "#ffffff"; PAN_BG = "#f8fafc"
    BORDER   = "#dde3ec"; TXT_PRI = "#0f172a"; TXT_SEC = "#475569"
    TXT_MUT  = "#94a3b8"; GRID_C  = "#e2e8f0"
    CSS_PAGE = "#f0f4f8"; CSS_CARD = "#ffffff"
    HERO_GRAD = "linear-gradient(135deg,#fff7ed 0%,#fef3c7 60%,#fff 100%)"
    IB_BG = "rgba(249,115,22,.06)"; IB_BOR = "rgba(249,115,22,.25)"
    CTRL_BG = "#ffffff"

ACCENT = "#f97316"; BLUE = "#38bdf8"; GREEN = "#34d399"; ROSE = "#fb7185"
PURPLE = "#c084fc"; YELLOW = "#fbbf24"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {{
    background-color: {CSS_PAGE} !important;
    color: {TXT_SEC} !important;
    font-family: 'JetBrains Mono', monospace;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
.block-container {{ padding: 1.6rem 2.2rem 4rem 2.2rem !important; max-width: 1600px; }}

/* ── Hero ── */
.hero {{
    background: {HERO_GRAD};
    border: 1px solid {BORDER};
    border-left: 5px solid {ACCENT};
    border-radius: 8px;
    padding: 2rem 2.6rem;
    margin-bottom: 1.4rem;
    position: relative; overflow: hidden;
}}
.hero::before {{
    content:''; position:absolute; bottom:-40px; left:-40px;
    width:200px; height:200px; border-radius:50%;
    background:radial-gradient(circle,rgba(56,189,248,.05) 0%,transparent 70%);
}}
.hero::after {{
    content:''; position:absolute; top:-80px; right:-80px;
    width:280px; height:280px; border-radius:50%;
    background:radial-gradient(circle,rgba(249,115,22,.07) 0%,transparent 70%);
}}
.hero-row {{ display:flex; justify-content:space-between; align-items:flex-start; }}
.hero-title {{
    font-family:'Syne',sans-serif; font-size:2.3rem; font-weight:800;
    letter-spacing:-.02em; color:{TXT_PRI}; line-height:1.1; margin:0 0 .3rem;
}}
.hero-title span {{ color:{ACCENT}; }}
.hero-sub {{
    font-size:.66rem; color:{TXT_MUT}; letter-spacing:.14em;
    text-transform:uppercase; margin:0 0 .8rem;
}}
.hero-badge {{
    display:inline-block; background:rgba(249,115,22,.1);
    border:1px solid rgba(249,115,22,.3); color:{ACCENT};
    font-size:.6rem; letter-spacing:.1em; padding:.16rem .6rem;
    border-radius:2px; margin-right:.5rem;
}}
.theme-btn {{
    background:{CARD_BG}; border:1px solid {BORDER}; color:{TXT_SEC};
    font-family:'JetBrains Mono',monospace; font-size:.65rem;
    letter-spacing:.08em; padding:.4rem .9rem; border-radius:4px;
    cursor:pointer; transition:all .2s; white-space:nowrap;
}}

/* ── Control panel ── */
.ctrl-panel {{
    background:{CTRL_BG}; border:1px solid {BORDER};
    border-top:2px solid {ACCENT}; border-radius:6px;
    padding:1.1rem 1.4rem; margin-bottom:1.6rem;
}}
.ctrl-title {{
    font-family:'Syne',sans-serif; font-size:.6rem; font-weight:700;
    letter-spacing:.18em; text-transform:uppercase; color:{ACCENT};
    margin-bottom:.9rem; border-bottom:1px solid {BORDER}; padding-bottom:.45rem;
}}

/* ── KPI cards ── */
.kpi-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:.9rem; margin-bottom:1.6rem; }}
.kpi-card {{
    background:{CARD_BG}; border:1px solid {BORDER}; border-top:2px solid;
    border-radius:6px; padding:1.2rem 1.4rem;
    transition:transform .15s,box-shadow .15s;
}}
.kpi-card:hover {{ transform:translateY(-2px); box-shadow:0 8px 28px rgba(0,0,0,.18); }}
.kpi-card.or{{border-top-color:{ACCENT};}} .kpi-card.ro{{border-top-color:{ROSE};}}
.kpi-card.em{{border-top-color:{GREEN};}} .kpi-card.bl{{border-top-color:{BLUE};}}
.kpi-card.pu{{border-top-color:{PURPLE};}}
.kpi-label {{ font-size:.56rem; letter-spacing:.14em; text-transform:uppercase; color:{TXT_MUT}; margin-bottom:.35rem; }}
.kpi-value {{ font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:{TXT_PRI}; line-height:1; }}
.kpi-sub   {{ font-size:.6rem; color:{TXT_MUT}; margin-top:.28rem; }}

/* ── Section headers ── */
.sec {{
    font-family:'Syne',sans-serif; font-size:.6rem; font-weight:700;
    letter-spacing:.2em; text-transform:uppercase; color:{ACCENT};
    border-bottom:1px solid {BORDER}; padding-bottom:.45rem; margin:2rem 0 1rem;
    display:flex; align-items:center; gap:.6rem;
}}
.sec-num {{ color:{TXT_MUT}; font-size:.55rem; }}

/* ── Insight box ── */
.ib {{
    background:{IB_BG}; border:1px solid {IB_BOR};
    border-left:3px solid {ACCENT}; border-radius:4px;
    padding:.75rem 1rem; margin:.7rem 0; font-size:.7rem;
    line-height:1.8; color:{TXT_SEC};
}}
.ib strong {{ color:{TXT_PRI}; }}
.ib.blue {{ border-left-color:{BLUE}; background:rgba(56,189,248,.04); border-color:rgba(56,189,248,.18); }}
.ib.green {{ border-left-color:{GREEN}; background:rgba(52,211,153,.04); border-color:rgba(52,211,153,.18); }}
.ib.rose {{ border-left-color:{ROSE}; background:rgba(251,113,133,.04); border-color:rgba(251,113,133,.18); }}

/* ── Suspicious table ── */
.sus-bar  {{ display:flex; align-items:center; gap:.6rem; margin-bottom:.65rem; }}
.sus-dot  {{ width:8px; height:8px; border-radius:50%; background:{ROSE};
            box-shadow:0 0 8px {ROSE}; animation:blink 1.8s infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1;}} 50%{{opacity:.2;}} }}
.sus-lbl  {{ font-family:'Syne',sans-serif; font-size:.7rem; font-weight:700;
            letter-spacing:.12em; text-transform:uppercase; color:{ROSE}; }}

/* ── Comparison cards ── */
.cmp-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin:.8rem 0; }}
.cmp-card {{
    background:{CARD_BG}; border:1px solid {BORDER}; border-radius:6px;
    padding:1.1rem 1.3rem;
}}
.cmp-card.legit {{ border-top:2px solid {GREEN}; }}
.cmp-card.fraud {{ border-top:2px solid {ROSE}; }}
.cmp-title {{ font-family:'Syne',sans-serif; font-size:.7rem; font-weight:700;
              letter-spacing:.1em; text-transform:uppercase; margin-bottom:.7rem; }}
.cmp-title.legit {{ color:{GREEN}; }}
.cmp-title.fraud {{ color:{ROSE}; }}
.cmp-row {{ display:flex; justify-content:space-between; padding:.25rem 0;
            border-bottom:1px solid {BORDER}; font-size:.65rem; }}
.cmp-key {{ color:{TXT_MUT}; }}
.cmp-val {{ color:{TXT_PRI}; font-weight:500; }}
.cmp-desc {{
    margin-top:.7rem; font-size:.62rem; line-height:1.7; color:{TXT_SEC};
    background:{PAGE_BG}; border-radius:3px; padding:.6rem .8rem;
    max-height:120px; overflow-y:auto;
}}

/* ── Geo bar ── */
.geo-label {{ font-size:.62rem; color:{TXT_MUT}; margin-bottom:.3rem; }}

/* ── Download btn ── */
[data-testid="stDownloadButton"] button {{
    background:{CARD_BG} !important; border:1px solid {BORDER} !important;
    color:{TXT_SEC} !important; font-family:'JetBrains Mono',monospace !important;
    font-size:.65rem !important; letter-spacing:.06em !important;
    transition: border-color .2s, color .2s !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    border-color:{ACCENT} !important; color:{ACCENT} !important;
}}

/* ── Tabs ── */
[data-testid="stTabs"] {{ border-bottom:1px solid {BORDER} !important; }}
button[data-baseweb="tab"] {{
    font-family:'JetBrains Mono',monospace !important;
    font-size:.65rem !important; letter-spacing:.08em !important;
    text-transform:uppercase !important; color:{TXT_MUT} !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color:{ACCENT} !important; border-bottom-color:{ACCENT} !important;
}}

[data-testid="stDataFrame"] {{ border:1px solid {BORDER} !important; border-radius:4px !important; }}
hr {{ border-color:{BORDER} !important; margin:1.1rem 0 !important; }}
label {{ font-size:.63rem !important; letter-spacing:.1em !important;
         text-transform:uppercase !important; color:{TXT_MUT} !important; }}
::-webkit-scrollbar {{ width:4px; height:4px; }}
::-webkit-scrollbar-track {{ background:{PAGE_BG}; }}
::-webkit-scrollbar-thumb {{ background:{BORDER}; border-radius:3px; }}
</style>
""", unsafe_allow_html=True)

# ── Matplotlib theme ──────────────────────────────────────────────────────────
MPL_BG  = CARD_BG if DARK else "#ffffff"
MPL_PAN = PAN_BG  if DARK else "#f8fafc"

matplotlib.rcParams.update({
    "figure.facecolor": MPL_BG, "axes.facecolor": MPL_PAN,
    "axes.edgecolor": GRID_C,   "axes.labelcolor": TXT_SEC,
    "axes.titlecolor": TXT_PRI, "axes.titlesize": 10,
    "axes.titleweight": "bold", "axes.titlepad": 12,
    "axes.grid": True, "grid.color": GRID_C,
    "grid.linewidth": .45, "grid.alpha": .5,
    "xtick.color": TXT_MUT, "ytick.color": TXT_MUT,
    "xtick.labelsize": 8,   "ytick.labelsize": 8,
    "text.color": TXT_SEC,  "legend.framealpha": .12,
    "legend.edgecolor": GRID_C, "legend.fontsize": 8,
    "font.family": "monospace",
})

def sfig(w=7, h=4, subplots=None):
    if subplots:
        fig, axes = plt.subplots(*subplots, figsize=(w, h))
        fig.patch.set_facecolor(MPL_BG)
        for ax in (axes.flat if hasattr(axes,'flat') else [axes]):
            ax.set_facecolor(MPL_PAN)
            for sp in ax.spines.values(): sp.set_edgecolor(GRID_C)
        return fig, axes
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(MPL_BG); ax.set_facecolor(MPL_PAN)
    for sp in ax.spines.values(): sp.set_edgecolor(GRID_C)
    return fig, ax

STOP_WORDS = {
    'the','a','an','and','or','but','in','on','at','to','for','of','with',
    'is','are','was','were','be','been','being','have','has','had','do',
    'does','did','will','would','could','should','may','might','shall',
    'this','that','these','those','it','its','we','you','your','our',
    'their','they','them','he','she','his','her','as','by','from','into',
    'through','during','before','after','above','below','up','down',
    'out','off','over','under','again','further','then','once','not',
    'no','nor','so','yet','both','either','neither','each','few','more',
    'most','other','some','such','than','too','very','just','can','all',
    'also','if','about','which','who','what','how','when','where','any',
    'only','same','own','while','because','however','since','within',
    'without','between','including','must','well','new','work','job','will',
    'experience','strong','skills','ability','team','using','us','amp',
}

def top_ngrams(texts, n=1, topk=20):
    counter = collections.Counter()
    for t in texts:
        words = re.findall(r'\b[a-z]{3,}\b', t.lower())
        if n == 1:
            counter.update(w for w in words if w not in STOP_WORDS)
        else:
            grams = zip(*[words[i:] for i in range(n)])
            counter.update(' '.join(g) for g in grams
                           if not any(w in STOP_WORDS for w in g))
    return counter.most_common(topk)

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ── Hero ──────────────────────────────────────────────────────────────────────
hero_l, hero_r = st.columns([5, 1])
with hero_l:
    st.markdown(f"""
    <div class='hero'>
        <div class='hero-row'>
            <div>
                <div class='hero-title'>Job Fraud <span>Intelligence</span> Dashboard</div>
                <p class='hero-sub'>EDA · NLP · Pattern Detection · Risk Profiling · Signal Analysis</p>
                <div class='hero-badge'>🔍 THREATSCAN v4</div>
                <div class='hero-badge'>EMSCAD Dataset</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_r:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    if st.button("☀️ Light" if DARK else "🌑 Dark", key="theme_toggle",
                 use_container_width=True):
        st.session_state.theme = "light" if DARK else "dark"
        st.rerun()

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload fake_job_postings.csv", type=["csv"],
                             help="EMSCAD dataset · CSV format")

if not uploaded:
    st.markdown(f"""
    <div style='text-align:center;padding:4rem 2rem;border:1px dashed {BORDER};
         border-radius:8px;background:{CARD_BG};margin-top:1.2rem;'>
        <div style='font-size:2.6rem;margin-bottom:.8rem;'>📂</div>
        <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:{TXT_PRI};'>
            Drop your dataset above to begin analysis
        </div>
        <div style='font-size:.66rem;color:{TXT_MUT};margin-top:.4rem;letter-spacing:.06em;'>
            CSV · EMSCAD compatible · fraudulent / description / has_company_logo / telecommuting
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Load & engineer ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Analysing dataset…")
def load_and_engineer(file_bytes):
    df = pd.read_csv(io.BytesIO(file_bytes))
    df["description"]     = df["description"].fillna("").astype(str)
    df["company_profile"] = df["company_profile"].fillna("").astype(str) \
                            if "company_profile" in df.columns else pd.Series([""] * len(df))
    df["requirements"]    = df["requirements"].fillna("").astype(str) \
                            if "requirements" in df.columns else pd.Series([""] * len(df))
    df["benefits"]        = df["benefits"].fillna("").astype(str) \
                            if "benefits" in df.columns else pd.Series([""] * len(df))
    df["title"]           = df["title"].fillna("Unknown").astype(str)
    df["location"]        = df["location"].fillna("Unknown").astype(str) \
                            if "location" in df.columns else pd.Series(["Unknown"] * len(df))
    df["desc_len"]        = df["description"].apply(len)
    df["desc_words"]      = df["description"].apply(lambda x: len(x.split()))
    df["company_len"]     = df["company_profile"].apply(len)
    df["req_len"]         = df["requirements"].apply(len)
    df["benefits_len"]    = df["benefits"].apply(len)
    df["has_salary"]      = df["salary_range"].notna().astype(int) \
                            if "salary_range" in df.columns else 0
    df["has_questions"]   = df["description"].str.count(r'\?')
    df["has_exclamation"] = df["description"].str.count(r'!')
    df["caps_ratio"]      = df["description"].apply(
        lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1))
    df["url_count"]       = df["description"].str.count(r'http|www\.')
    # Suspicious score (aligned with main.py: desc_len, company_len, req_len, has_company_logo)
    df["suspicious_score"] = (
        (df["desc_len"]    < 200).astype(int) +
        (df["company_len"] < 50).astype(int)  +
        (df["req_len"]     < 50).astype(int)  +
        (df["has_company_logo"] == 0).astype(int)
    )
    df["fraud_label"] = df["fraudulent"].map({0: "Legitimate", 1: "Fraudulent"})
    # Simulated time index (from main.py)
    df["index_time"] = np.arange(len(df))
    # Extract country from location
    df["country"] = df["location"].apply(
        lambda x: x.split(",")[-1].strip() if "," in x else x.strip())
    return df

raw_bytes = uploaded.read()
df = load_and_engineer(raw_bytes)

# ── Data Merging (from main.py academic requirement) ─────────────────────────
@st.cache_data(show_spinner=False)
def get_merged(file_bytes):
    _df = pd.read_csv(io.BytesIO(file_bytes))
    _df["title"] = _df["title"].fillna("Unknown").astype(str)
    temp = _df[["title", "fraudulent"]].copy()
    merged = pd.merge(_df, temp, on="title", how="left",
                      suffixes=("", "_merged"))
    return merged

merged_df = get_merged(raw_bytes)

# ── Filter controls ───────────────────────────────────────────────────────────
st.markdown(f"<div class='ctrl-panel'><div class='ctrl-title'>🎛 Filter Controls</div>",
            unsafe_allow_html=True)
fc1,fc2,fc3,fc4,fc5,fc6 = st.columns([1,1,1,1,1,1.6])
with fc1: fraud_filter  = st.selectbox("Job Type",   ["All","Real Only","Fake Only"])
with fc2: logo_filter   = st.selectbox("Company Logo",["All","Has Logo","No Logo"])
with fc3: remote_filter = st.selectbox("Remote",     ["All","Remote Only","Non Remote"])
with fc4: score_min     = st.selectbox("Min Score",  [0,1,2,3,4])
with fc5:
    emp_opts = ["All"] + sorted(df["employment_type"].dropna().unique().tolist()) \
               if "employment_type" in df.columns else ["All"]
    emp_filter = st.selectbox("Employment", emp_opts)
with fc6: search = st.text_input("🔍  Search Title / Location",
                                  placeholder="e.g. data analyst, New York…")
st.markdown("</div>", unsafe_allow_html=True)

filt = df.copy()
if fraud_filter  == "Fake Only":   filt = filt[filt["fraudulent"] == 1]
if fraud_filter  == "Real Only":   filt = filt[filt["fraudulent"] == 0]
if logo_filter   == "Has Logo":    filt = filt[filt["has_company_logo"] == 1]
if logo_filter   == "No Logo":     filt = filt[filt["has_company_logo"] == 0]
if remote_filter == "Remote Only": filt = filt[filt["telecommuting"] == 1]
if remote_filter == "Non Remote":  filt = filt[filt["telecommuting"] == 0]
filt = filt[filt["suspicious_score"] >= score_min]
if "employment_type" in df.columns and emp_filter != "All":
    filt = filt[filt["employment_type"] == emp_filter]
if search:
    mask = (filt["title"].str.contains(search, case=False, na=False) |
            filt["location"].str.contains(search, case=False, na=False))
    filt = filt[mask]

total     = len(filt)
fraud_n   = int(filt["fraudulent"].sum())
legit_n   = total - fraud_n
fraud_pct = fraud_n / max(total, 1) * 100
avg_score = filt["suspicious_score"].mean() if total else 0
avg_desc  = filt["desc_words"].mean() if total else 0

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='kpi-grid'>
  <div class='kpi-card or'>
    <div class='kpi-label'>Total Postings</div>
    <div class='kpi-value'>{total:,}</div>
    <div class='kpi-sub'>After active filters</div>
  </div>
  <div class='kpi-card ro'>
    <div class='kpi-label'>Fraudulent</div>
    <div class='kpi-value'>{fraud_n:,}</div>
    <div class='kpi-sub'>{fraud_pct:.1f}% · HIGH RISK</div>
  </div>
  <div class='kpi-card em'>
    <div class='kpi-label'>Legitimate</div>
    <div class='kpi-value'>{legit_n:,}</div>
    <div class='kpi-sub'>{100-fraud_pct:.1f}% of filtered</div>
  </div>
  <div class='kpi-card bl'>
    <div class='kpi-label'>Avg Suspicious Score</div>
    <div class='kpi-value'>{avg_score:.2f}</div>
    <div class='kpi-sub'>Max possible: 4</div>
  </div>
  <div class='kpi-card pu'>
    <div class='kpi-label'>Avg Words / Posting</div>
    <div class='kpi-value'>{avg_desc:.0f}</div>
    <div class='kpi-sub'>Description word count</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Overview",
    "🔤 NLP & Text",
    "🌍 Geography",
    "📋 Categories",
    "⚖️ Compare",
    "🚨 Threat Feed",
    "🔬 Statistics",   # ← NEW tab (from main.py)
    "🗂 Raw Data",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 · OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown(f"<div class='sec'><span class='sec-num'>01</span> Class Distribution & Description Length</div>",
                unsafe_allow_html=True)

    ca, cb = st.columns([1, 2])
    with ca:
        counts = filt["fraud_label"].value_counts()
        fig, ax = sfig(5, 4)
        cols_bar = [GREEN if l == "Legitimate" else ROSE for l in counts.index]
        bars = ax.bar(counts.index, counts.values, color=cols_bar,
                      width=.5, edgecolor=MPL_BG, linewidth=.8)
        for b, v in zip(bars, counts.values):
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+total*.004,
                    f"{v:,}\n({v/max(total,1)*100:.1f}%)",
                    ha='center', va='bottom', fontsize=8, color=TXT_SEC)
        ax.set_title("Legitimate vs. Fraudulent"); ax.set_ylabel("Count")
        ax.set_ylim(0, counts.max()*1.22); fig.tight_layout()
        st.pyplot(fig); plt.close()

    with cb:
        med_l = filt[filt["fraudulent"]==0]["desc_len"].median()
        med_f = filt[filt["fraudulent"]==1]["desc_len"].median()
        fig, ax = sfig(9, 4)
        for lbl, col in [("Legitimate", GREEN), ("Fraudulent", ROSE)]:
            sub = filt[filt["fraud_label"]==lbl]["desc_len"]
            ax.hist(sub, bins=60, color=col, alpha=.45, label=lbl, edgecolor='none')
        for med, col, nm in [(med_l, GREEN,"Legit"),(med_f, ROSE,"Fraud")]:
            ax.axvline(med, color=col, linestyle='--', linewidth=1.3, alpha=.9)
            ypos = ax.get_ylim()[1]*(.82 if col==GREEN else .62)
            ax.text(med+120, ypos, f"{nm}\n{med:.0f} chars", color=col, fontsize=7.5)
        ax.set_title("Description Character Length by Class")
        ax.set_xlabel("Characters"); ax.set_ylabel("Frequency")
        ax.legend(); fig.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown(f"""<div class='ib'>
      <strong>Key Signal:</strong> Fraudulent postings have a median length of
      <strong>{med_f:.0f} chars</strong> vs <strong>{med_l:.0f}</strong> for legitimate —
      <strong>{(med_l/max(med_f,1)-1)*100:.0f}% shorter on average</strong>.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"<div class='sec'><span class='sec-num'>02</span> Word Count · Score Distribution · Signals</div>",
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        fig, ax = sfig(5, 4)
        d0 = filt[filt["fraudulent"]==0]["desc_words"].dropna()
        d1 = filt[filt["fraudulent"]==1]["desc_words"].dropna()
        bp = ax.boxplot([d0, d1], patch_artist=True, widths=.45,
                        medianprops=dict(color=TXT_PRI, linewidth=2),
                        whiskerprops=dict(color=TXT_MUT),
                        capprops=dict(color=TXT_MUT),
                        flierprops=dict(marker='.', color=TXT_MUT, alpha=.3, markersize=3))
        bp["boxes"][0].set_facecolor(GREEN+"30"); bp["boxes"][0].set_edgecolor(GREEN)
        bp["boxes"][1].set_facecolor(ROSE+"30");  bp["boxes"][1].set_edgecolor(ROSE)
        ax.set_xticks([1,2]); ax.set_xticklabels(["Legitimate","Fraudulent"], color=TXT_PRI)
        ax.set_title("Word Count by Class"); ax.set_ylabel("Words")
        fig.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        sc = filt["suspicious_score"].value_counts().sort_index()
        sc_colors = [GREEN, BLUE, ACCENT, ROSE, PURPLE]
        fig, ax = sfig(5, 4)
        bars2 = ax.bar(sc.index.astype(str), sc.values,
                       color=[sc_colors[min(i,4)] for i in sc.index],
                       edgecolor=MPL_BG, linewidth=.6, width=.55)
        for b, v in zip(bars2, sc.values):
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+total*.003,
                    f"{v:,}", ha='center', va='bottom', fontsize=8, color=TXT_SEC)
        ax.set_title("Suspicious Score Distribution (0–4)")
        ax.set_xlabel("Score"); ax.set_ylabel("Count")
        fig.tight_layout(); st.pyplot(fig); plt.close()

    with c3:
        sr = filt.groupby("suspicious_score")["fraudulent"].mean()*100
        fig, ax = sfig(5, 4)
        lc = ax.plot(sr.index, sr.values, color=ROSE, linewidth=2.5,
                     marker='o', markersize=7, markerfacecolor=MPL_BG,
                     markeredgecolor=ROSE, markeredgewidth=2)
        ax.fill_between(sr.index, sr.values, alpha=.1, color=ROSE)
        for x, y in zip(sr.index, sr.values):
            ax.text(x, y+1.2, f"{y:.0f}%", ha='center', fontsize=8, color=ROSE)
        ax.set_title("Fraud Rate by Suspicious Score")
        ax.set_xlabel("Score"); ax.set_ylabel("Fraud Rate %")
        ax.set_xticks(sr.index); fig.tight_layout()
        st.pyplot(fig); plt.close()

    st.markdown(f"<div class='sec'><span class='sec-num'>03</span> Signal Analysis — Logo & Remote + Risk Matrix</div>",
                unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)

    def grouped_bar_3(col_name, xlabels, title, col_obj):
        with col_obj:
            grp = filt.groupby([col_name,"fraud_label"]).size().unstack(fill_value=0)
            x, w = np.arange(len(grp)), 0.36
            fig, ax = sfig(5, 4)
            for i,(lbl,col) in enumerate(zip(["Legitimate","Fraudulent"],[GREEN,ROSE])):
                if lbl in grp.columns:
                    bs = ax.bar(x+i*w-w/2, grp[lbl].values, width=w, color=col,
                                alpha=.8, label=lbl, edgecolor=MPL_BG, linewidth=.4)
                    for b in bs:
                        h = b.get_height()
                        if h: ax.text(b.get_x()+b.get_width()/2, h+4, f"{h:,}",
                                      ha='center', va='bottom', fontsize=7, color=TXT_SEC)
            ax.set_xticks(x); ax.set_xticklabels(xlabels, color=TXT_PRI)
            ax.set_title(title); ax.set_ylabel("Count"); ax.legend()
            fig.tight_layout(); st.pyplot(fig); plt.close()

    grouped_bar_3("has_company_logo", ["No Logo","Has Logo"], "Logo vs Fraud", c4)
    grouped_bar_3("telecommuting",    ["On-Site","Remote"],   "Remote vs Fraud", c5)

    with c6:
        pivot = filt.pivot_table(index="has_company_logo", columns="telecommuting",
                                  values="fraudulent", aggfunc="mean")*100
        ri = ["No Logo","Has Logo"][:len(pivot)]
        ci = ["On-Site","Remote"][:len(pivot.columns)]
        pivot.index = ri; pivot.columns = ci
        fig, ax = sfig(5, 4)
        im = ax.imshow(pivot.values, cmap="RdYlGn_r", aspect="auto", vmin=0, vmax=30)
        ax.set_xticks(range(len(ci))); ax.set_xticklabels(ci, color=TXT_PRI)
        ax.set_yticks(range(len(ri))); ax.set_yticklabels(ri, color=TXT_PRI)
        for i in range(len(ri)):
            for j in range(len(ci)):
                ax.text(j, i, f"{pivot.values[i,j]:.1f}%",
                        ha='center', va='center', fontsize=13,
                        fontweight='bold', color=TXT_PRI)
        plt.colorbar(im, ax=ax, fraction=.04, pad=.03).ax.tick_params(
            colors=TXT_MUT, labelsize=7)
        ax.set_title("Risk Heatmap: Logo × Remote"); ax.grid(False)
        fig.tight_layout(); st.pyplot(fig); plt.close()

    no_lr = filt[filt["has_company_logo"]==0]["fraudulent"].mean()*100 if total else 0
    hl_r  = filt[filt["has_company_logo"]==1]["fraudulent"].mean()*100 if total else 0
    rm_r  = filt[filt["telecommuting"]==1]["fraudulent"].mean()*100    if total else 0
    os_r  = filt[filt["telecommuting"]==0]["fraudulent"].mean()*100    if total else 0
    st.markdown(f"""<div class='ib'>
      <strong>Logo:</strong> No-logo fraud rate <strong>{no_lr:.1f}%</strong> vs
      <strong>{hl_r:.1f}%</strong> with logo ({no_lr/max(hl_r,.01):.1f}× risk). &nbsp;|&nbsp;
      <strong>Remote:</strong> Remote <strong>{rm_r:.1f}%</strong> vs
      on-site <strong>{os_r:.1f}%</strong>.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"<div class='sec'><span class='sec-num'>04</span> Correlation Heatmap</div>",
                unsafe_allow_html=True)
    num_df = filt.select_dtypes(include=np.number)
    if len(num_df.columns) > 1:
        fig, ax = sfig(13, 5)
        corr = num_df.corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "ts", [BLUE, MPL_BG, ROSE])
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap=cmap,
                    ax=ax, linewidths=.35, linecolor=GRID_C,
                    annot_kws={"size":8,"color":TXT_PRI},
                    cbar_kws={"shrink":.55})
        ax.set_title("Feature Correlation Matrix (lower triangle)")
        ax.tick_params(colors=TXT_PRI, labelsize=8)
        fig.tight_layout(); st.pyplot(fig); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 · NLP & TEXT
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown(f"<div class='sec'><span class='sec-num'>05</span> Top Keywords — Fraudulent vs Legitimate</div>",
                unsafe_allow_html=True)

    fraud_texts = filt[filt["fraudulent"]==1]["description"].tolist()
    legit_texts = filt[filt["fraudulent"]==0]["description"].tolist()

    nlp_col1, nlp_col2 = st.columns(2)

    def keyword_chart(texts, label, color, col_obj, topk=20):
        with col_obj:
            if not texts:
                st.info(f"No {label} postings in current filter.")
                return
            ngrams = top_ngrams(texts, n=1, topk=topk)
            words, counts = zip(*ngrams) if ngrams else ([], [])
            fig, ax = sfig(6, 6)
            y = np.arange(len(words))
            bars = ax.barh(y, counts, color=color, alpha=.78,
                           edgecolor=MPL_BG, linewidth=.4, height=.65)
            for b in bars:
                w = b.get_width()
                ax.text(w+0.3, b.get_y()+b.get_height()/2, f"{w:,}",
                        va='center', fontsize=7.5, color=TXT_SEC)
            ax.set_yticks(y); ax.set_yticklabels(words, fontsize=8.5, color=TXT_PRI)
            ax.set_title(f"Top {topk} Keywords — {label}")
            ax.set_xlabel("Frequency"); ax.invert_yaxis()
            fig.tight_layout(); st.pyplot(fig); plt.close()

    keyword_chart(fraud_texts, "Fraudulent", ROSE,  nlp_col1)
    keyword_chart(legit_texts, "Legitimate", GREEN, nlp_col2)

    st.markdown(f"<div class='sec'><span class='sec-num'>06</span> Top Bigrams (2-Word Phrases)</div>",
                unsafe_allow_html=True)

    bi1, bi2 = st.columns(2)

    def bigram_chart(texts, label, color, col_obj, topk=15):
        with col_obj:
            if not texts:
                return
            ngrams = top_ngrams(texts, n=2, topk=topk)
            if not ngrams: return
            phrases, counts = zip(*ngrams)
            fig, ax = sfig(6, 5)
            y = np.arange(len(phrases))
            ax.barh(y, counts, color=color, alpha=.72,
                    edgecolor=MPL_BG, linewidth=.4, height=.6)
            for i,(b,v) in enumerate(zip(ax.patches, counts)):
                ax.text(b.get_width()+.2, b.get_y()+b.get_height()/2,
                        f"{v:,}", va='center', fontsize=7, color=TXT_SEC)
            ax.set_yticks(y); ax.set_yticklabels(phrases, fontsize=8, color=TXT_PRI)
            ax.set_title(f"Top Bigrams — {label}")
            ax.set_xlabel("Frequency"); ax.invert_yaxis()
            fig.tight_layout(); st.pyplot(fig); plt.close()

    bigram_chart(fraud_texts, "Fraudulent", ROSE,  bi1)
    bigram_chart(legit_texts, "Legitimate", GREEN, bi2)

    st.markdown(f"<div class='sec'><span class='sec-num'>07</span> Exclusive Keywords (Fraud-Only vs Legit-Only)</div>",
                unsafe_allow_html=True)

    if fraud_texts and legit_texts:
        fraud_wc = dict(top_ngrams(fraud_texts, n=1, topk=200))
        legit_wc = dict(top_ngrams(legit_texts, n=1, topk=200))
        fraud_only = {w: c for w,c in fraud_wc.items() if w not in legit_wc}
        legit_only = {w: c for w,c in legit_wc.items() if w not in fraud_wc}
        fo_top = sorted(fraud_only.items(), key=lambda x:-x[1])[:15]
        lo_top = sorted(legit_only.items(), key=lambda x:-x[1])[:15]

        ex1, ex2 = st.columns(2)
        for top, label, color, col_obj in [
            (fo_top,"Fraud-Exclusive Words",ROSE,ex1),
            (lo_top,"Legit-Exclusive Words",GREEN,ex2)
        ]:
            with col_obj:
                if top:
                    ws, cs = zip(*top)
                    fig, ax = sfig(6, 4.5)
                    y = np.arange(len(ws))
                    ax.barh(y, cs, color=color, alpha=.75,
                            edgecolor=MPL_BG, linewidth=.4, height=.6)
                    for b in ax.patches:
                        ax.text(b.get_width()+.1, b.get_y()+b.get_height()/2,
                                f"{b.get_width():.0f}", va='center',
                                fontsize=7.5, color=TXT_SEC)
                    ax.set_yticks(y); ax.set_yticklabels(ws, fontsize=8.5, color=TXT_PRI)
                    ax.set_title(label); ax.set_xlabel("Frequency"); ax.invert_yaxis()
                    fig.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown(f"<div class='sec'><span class='sec-num'>08</span> Text Feature Distributions</div>",
                unsafe_allow_html=True)

    tf1, tf2, tf3 = st.columns(3)
    for feature, title, col_obj in [
        ("has_questions",   "Question Marks per Posting", tf1),
        ("has_exclamation", "Exclamation Marks per Posting", tf2),
        ("caps_ratio",      "Caps Ratio (ALL CAPS fraction)", tf3),
    ]:
        with col_obj:
            fig, ax = sfig(5, 3.5)
            for lbl, col in [("Legitimate",GREEN),("Fraudulent",ROSE)]:
                sub = filt[filt["fraud_label"]==lbl][feature].dropna()
                ax.hist(sub, bins=30, color=col, alpha=.5, label=lbl, edgecolor='none')
            ax.set_title(title); ax.set_xlabel(feature.replace("_"," ").title())
            ax.set_ylabel("Count"); ax.legend()
            fig.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown(f"<div class='sec'><span class='sec-num'>09</span> Top Fake Job Titles</div>",
                unsafe_allow_html=True)
    fake_df = filt[filt["fraudulent"]==1]
    if len(fake_df):
        top_titles = fake_df["title"].value_counts().head(15)
        fig, ax = sfig(13, 4.5)
        y = np.arange(len(top_titles))
        ax.barh(y, top_titles.values[::-1], color=ROSE, alpha=.75,
                edgecolor=MPL_BG, linewidth=.4, height=.65)
        ax.set_yticks(y)
        ax.set_yticklabels(top_titles.index[::-1], fontsize=8.5, color=TXT_PRI)
        for b in ax.patches:
            ax.text(b.get_width()+.1, b.get_y()+b.get_height()/2,
                    f"{b.get_width():.0f}", va='center', fontsize=8, color=TXT_SEC)
        ax.set_title("Most Frequent Fraudulent Job Titles (Top 15)")
        ax.set_xlabel("Count"); fig.tight_layout(); st.pyplot(fig); plt.close()
    else:
        st.info("No fraudulent postings in current selection.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 · GEOGRAPHY
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown(f"<div class='sec'><span class='sec-num'>10</span> Geographic Fraud Distribution</div>",
                unsafe_allow_html=True)

    geo = filt.groupby("country")["fraudulent"].agg(["sum","count","mean"]).reset_index()
    geo.columns = ["country","fraud_count","total","fraud_rate"]
    geo["fraud_rate"] *= 100
    geo = geo[geo["total"] >= 10].sort_values("fraud_count", ascending=False)

    g1, g2 = st.columns(2)

    with g1:
        top_geo = geo.head(20)
        fig, ax = sfig(7, 6)
        y = np.arange(len(top_geo))
        colors_geo = [ROSE if r > fraud_pct else BLUE for r in top_geo["fraud_rate"]]
        ax.barh(y, top_geo["fraud_count"].values[::-1],
                color=colors_geo[::-1], alpha=.78,
                edgecolor=MPL_BG, linewidth=.4, height=.65)
        ax.set_yticks(y)
        ax.set_yticklabels(top_geo["country"].values[::-1], fontsize=8, color=TXT_PRI)
        for b in ax.patches:
            ax.text(b.get_width()+.2, b.get_y()+b.get_height()/2,
                    f"{b.get_width():.0f}", va='center', fontsize=7, color=TXT_SEC)
        ax.set_title("Top 20 Countries by Fraud Count")
        ax.set_xlabel("Fraud Postings Count")
        fig.tight_layout(); st.pyplot(fig); plt.close()

    with g2:
        top_rate = geo[geo["total"] >= 30].sort_values("fraud_rate", ascending=False).head(20)
        fig, ax = sfig(7, 6)
        y = np.arange(len(top_rate))
        ax.barh(y, top_rate["fraud_rate"].values[::-1],
                color=ROSE, alpha=.72,
                edgecolor=MPL_BG, linewidth=.4, height=.65)
        ax.axvline(fraud_pct, color=ACCENT, linestyle='--', linewidth=1.2)
        ax.text(fraud_pct+.3, len(top_rate)*.95, f"avg {fraud_pct:.1f}%",
                color=ACCENT, fontsize=7.5)
        ax.set_yticks(y)
        ax.set_yticklabels(top_rate["country"].values[::-1], fontsize=8, color=TXT_PRI)
        for b in ax.patches:
            ax.text(b.get_width()+.3, b.get_y()+b.get_height()/2,
                    f"{b.get_width():.1f}%", va='center', fontsize=7, color=TXT_SEC)
        ax.set_title("Top 20 Countries by Fraud Rate % (min 30 postings)")
        ax.set_xlabel("Fraud Rate (%)")
        fig.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown(f"<div class='sec'><span class='sec-num'>11</span> Country Fraud Rate vs Volume Scatter</div>",
                unsafe_allow_html=True)

    scatter_geo = geo[geo["total"] >= 20].copy()
    fig, ax = sfig(13, 5)
    scatter = ax.scatter(scatter_geo["total"], scatter_geo["fraud_rate"],
                         c=scatter_geo["fraud_rate"],
                         cmap=matplotlib.colors.LinearSegmentedColormap.from_list(
                             "rg", [GREEN, YELLOW, ROSE]),
                         s=scatter_geo["fraud_count"]/scatter_geo["fraud_count"].max()*400+30,
                         alpha=.75, edgecolors=MPL_BG, linewidths=.5)
    for _, row in scatter_geo.nlargest(10, "fraud_count").iterrows():
        ax.annotate(row["country"],
                    (row["total"], row["fraud_rate"]),
                    fontsize=7, color=TXT_SEC,
                    xytext=(5, 3), textcoords='offset points')
    plt.colorbar(scatter, ax=ax, label="Fraud Rate %",
                 fraction=.025).ax.tick_params(colors=TXT_MUT, labelsize=7)
    ax.set_title("Country: Volume vs Fraud Rate  (bubble size = fraud count)")
    ax.set_xlabel("Total Postings"); ax.set_ylabel("Fraud Rate (%)")
    fig.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown(f"""<div class='ib blue'>
      <strong>Geographic Insight:</strong> Bubble size = number of fraudulent postings.
      Countries in the top-right have both high volume <em>and</em> high fraud rate —
      the highest-risk origin zones. Countries far right but low = high volume, low fraud.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 · CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    cat_cols = [c for c in ["employment_type","required_experience",
                             "required_education","industry","function"]
                if c in filt.columns]
    if not cat_cols:
        st.info("No categorical columns detected in dataset.")
    else:
        for i, cname in enumerate(cat_cols):
            st.markdown(f"<div class='sec'><span class='sec-num'>{12+i:02d}</span> Fraud Rate by {cname.replace('_',' ').title()}</div>",
                        unsafe_allow_html=True)
            grp = filt.groupby(cname)["fraudulent"].agg(["mean","count","sum"]).reset_index()
            grp.columns = [cname,"fraud_rate","total","fraud_n"]
            grp = grp[grp["total"]>20].sort_values("fraud_rate", ascending=False).head(12)
            if grp.empty: continue

            cc1, cc2 = st.columns(2)
            with cc1:
                fig, ax = sfig(7, 4.5)
                bc = [ROSE if v > fraud_pct/100 else BLUE for v in grp["fraud_rate"]]
                ax.barh(grp[cname].astype(str), grp["fraud_rate"]*100,
                        color=bc, edgecolor=MPL_BG, linewidth=.4, height=.55)
                ax.axvline(fraud_pct, color=ACCENT, linestyle='--', linewidth=1.1)
                ax.text(fraud_pct+.2, len(grp)-.7, f"avg {fraud_pct:.1f}%",
                        color=ACCENT, fontsize=7.5)
                for b in ax.patches:
                    ax.text(b.get_width()+.2, b.get_y()+b.get_height()/2,
                            f"{b.get_width():.1f}%", va='center', fontsize=7.5, color=TXT_SEC)
                ax.set_title(f"Fraud Rate by {cname.replace('_',' ').title()}")
                ax.set_xlabel("Fraud Rate (%)"); ax.invert_yaxis()
                fig.tight_layout(); st.pyplot(fig); plt.close()

            with cc2:
                fig, ax = sfig(7, 4.5)
                x = np.arange(len(grp)); w = .38
                b1 = ax.bar(x-w/2, grp["total"], width=w, color=BLUE, alpha=.7,
                            label="Total", edgecolor=MPL_BG, linewidth=.4)
                b2 = ax.bar(x+w/2, grp["fraud_n"], width=w, color=ROSE, alpha=.7,
                            label="Fraud", edgecolor=MPL_BG, linewidth=.4)
                ax.set_xticks(x)
                ax.set_xticklabels(grp[cname].astype(str), rotation=35,
                                   ha='right', fontsize=7.5, color=TXT_PRI)
                ax.set_title(f"Volume: Total vs Fraud by {cname.replace('_',' ').title()}")
                ax.set_ylabel("Count"); ax.legend()
                fig.tight_layout(); st.pyplot(fig); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 · COMPARE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown(f"<div class='sec'><span class='sec-num'>★</span> Side-by-Side Job Comparison</div>",
                unsafe_allow_html=True)
    st.markdown(f"""<div class='ib blue'>
      Pick any real and any fake posting to compare them directly.
      Observe how description depth, company presence, and language differ.
    </div>""", unsafe_allow_html=True)

    real_df = filt[filt["fraudulent"]==0].reset_index(drop=True)
    fake_df_cmp = filt[filt["fraudulent"]==1].reset_index(drop=True)

    if real_df.empty or fake_df_cmp.empty:
        st.warning("Need both legitimate and fraudulent postings in current filter to compare.")
    else:
        cmp_c1, cmp_c2 = st.columns(2)
        with cmp_c1:
            real_idx = st.slider("Legitimate posting #", 0, min(len(real_df)-1, 500), 0, key="real_idx")
        with cmp_c2:
            fake_idx = st.slider("Fraudulent posting #", 0, min(len(fake_df_cmp)-1, 500), 0, key="fake_idx")

        r = real_df.iloc[real_idx]
        f = fake_df_cmp.iloc[fake_idx]

        def cmp_card(row, kind):
            label_cls = "legit" if kind=="Legitimate" else "fraud"
            color     = GREEN   if kind=="Legitimate" else ROSE
            fields = [
                ("Title",      row.get("title","—")),
                ("Location",   row.get("location","—")),
                ("Employment", row.get("employment_type","—")),
                ("Company",    row.get("company_profile","—")[:80]+"…"
                               if len(str(row.get("company_profile","")))>80
                               else row.get("company_profile","—")),
                ("Has Logo",   "✅ Yes" if row.get("has_company_logo",0)==1 else "❌ No"),
                ("Remote",     "✅ Yes" if row.get("telecommuting",0)==1 else "❌ No"),
                ("Desc Words", f"{row.get('desc_words',0):,}"),
                ("Desc Chars", f"{row.get('desc_len',0):,}"),
                ("Susp. Score",f"{row.get('suspicious_score',0)} / 4"),
                ("Salary",     row.get("salary_range","Not listed") or "Not listed"),
            ]
            rows_html = "".join(
                f"<div class='cmp-row'><span class='cmp-key'>{k}</span>"
                f"<span class='cmp-val'>{v}</span></div>"
                for k, v in fields
            )
            desc = str(row.get("description",""))[:600]
            if len(str(row.get("description",""))) > 600: desc += "…"
            return f"""
            <div class='cmp-card {label_cls}'>
                <div class='cmp-title {label_cls}'>{kind} Posting</div>
                {rows_html}
                <div class='cmp-desc'>{desc}</div>
            </div>"""

        st.markdown(f"""
        <div class='cmp-grid'>
            {cmp_card(r, "Legitimate")}
            {cmp_card(f, "Fraudulent")}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<div class='sec'><span class='sec-num'>★</span> Feature Comparison</div>",
                    unsafe_allow_html=True)

        features_cmp = {
            "Desc Length (chars)": ("desc_len", 5000),
            "Word Count":          ("desc_words", 800),
            "Company Profile Len": ("company_len", 2000),
            "Questions (?)":       ("has_questions", 20),
            "Exclamations (!)":    ("has_exclamation", 20),
            "Caps Ratio %":        ("caps_ratio", 0.15),
        }

        fig, ax = sfig(12, 3.5)
        cats  = list(features_cmp.keys())
        r_vals = [min(r.get(v,0)/n, 1) for v,n in features_cmp.values()]
        f_vals = [min(f.get(v,0)/n, 1) for v,n in features_cmp.values()]
        x2 = np.arange(len(cats)); w2 = .35
        ax.bar(x2-w2/2, r_vals, width=w2, color=GREEN, alpha=.75, label="Legitimate",
               edgecolor=MPL_BG, linewidth=.4)
        ax.bar(x2+w2/2, f_vals, width=w2, color=ROSE,  alpha=.75, label="Fraudulent",
               edgecolor=MPL_BG, linewidth=.4)
        ax.set_xticks(x2); ax.set_xticklabels(cats, rotation=18, ha='right',
                                               fontsize=8, color=TXT_PRI)
        ax.set_ylabel("Normalised (0–1)"); ax.set_title("Feature Comparison (normalised)")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_: f"{v:.0%}"))
        ax.legend(); fig.tight_layout(); st.pyplot(fig); plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 · THREAT FEED
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown(f"<div class='sec'><span class='sec-num'>★</span> Flagged Suspicious Listings</div>",
                unsafe_allow_html=True)

    sus_df = filt.sort_values("suspicious_score", ascending=False)
    sus_n  = int((sus_df["suspicious_score"] >= 3).sum())

    st.markdown(f"""
    <div class='sus-bar'>
        <div class='sus-dot'></div>
        <div class='sus-lbl'>Live threat feed · {sus_n} postings with score ≥ 3</div>
    </div>""", unsafe_allow_html=True)

    sc1,sc2,sc3,sc4 = st.columns(4)
    for s, label, col_obj, color in [
        (1,"Score 1",sc1,BLUE),(2,"Score 2",sc2,ACCENT),
        (3,"Score 3",sc3,ROSE),(4,"Score 4",sc4,PURPLE)
    ]:
        n = int((filt["suspicious_score"]==s).sum())
        fr = filt[filt["suspicious_score"]==s]["fraudulent"].mean()*100 if n else 0
        with col_obj:
            st.markdown(f"""
            <div class='kpi-card' style='border-top-color:{color};'>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value' style='font-size:1.4rem;'>{n:,}</div>
                <div class='kpi-sub'>{fr:.1f}% confirmed fraud</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

    disp_cols = [c for c in ["title","location","employment_type","company_profile",
                               "desc_len","desc_words","suspicious_score",
                               "fraudulent","fraud_label"]
                 if c in sus_df.columns]

    def highlight_row(row):
        s = row.get("suspicious_score", 0)
        if s == 4: return [f"background-color:rgba(192,132,252,.12);color:#c084fc"]*len(row)
        if s == 3: return [f"background-color:rgba(251,113,133,.1);color:#fb7185"]*len(row)
        return [""]*len(row)

    st.dataframe(sus_df[disp_cols].head(50).style.apply(highlight_row, axis=1),
                 use_container_width=True, height=450)

    dl_col1, dl_col2, dl_col3 = st.columns(3)
    with dl_col1:
        st.download_button("⬇  Download All Filtered",
                           filt.to_csv(index=False),
                           file_name="filtered_jobs.csv", mime="text/csv")
    with dl_col2:
        st.download_button("⬇  Download Suspicious (score≥3)",
                           sus_df[sus_df["suspicious_score"]>=3].to_csv(index=False),
                           file_name="suspicious_jobs.csv", mime="text/csv")
    with dl_col3:
        st.download_button("⬇  Download Confirmed Fraud",
                           filt[filt["fraudulent"]==1].to_csv(index=False),
                           file_name="confirmed_fraud.csv", mime="text/csv")

    conf_n = int(sus_df[sus_df["suspicious_score"]>=3]["fraudulent"].sum())
    conf_r = conf_n / max(sus_n, 1) * 100
    st.markdown(f"""<div class='ib rose'>
      <strong>{sus_n}</strong> postings scored ≥ 3.
      Of these, <strong>{conf_n}</strong> ({conf_r:.1f}%) are confirmed fraud
      — <strong>{conf_r/max(fraud_pct,.01):.1f}× the baseline rate</strong>.
      Score-4 postings (purple) are the highest-priority investigation targets.
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 7 · STATISTICS  ← NEW: merging, time-variant, hypothesis test (from main.py)
# ─────────────────────────────────────────────────────────────────────────────
with tabs[6]:

    # ── Section A: Data Merging ───────────────────────────────────────────────
    st.markdown(f"<div class='sec'><span class='sec-num'>A</span> Data Merging</div>",
                unsafe_allow_html=True)
    st.markdown(f"""<div class='ib blue'>
      A self-join on <strong>title</strong> produces a <code>fraudulent_merged</code> column
      alongside the original. This mirrors the academic <code>pd.merge()</code> requirement
      from <code>main.py</code> and is useful for cross-referencing repeated titles.
    </div>""", unsafe_allow_html=True)

    merge_preview_cols = [c for c in ["title", "fraudulent", "fraudulent_merged"]
                          if c in merged_df.columns]
    st.dataframe(merged_df[merge_preview_cols].head(20),
                 use_container_width=True, height=280)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class='kpi-card or'>
          <div class='kpi-label'>Merged Rows</div>
          <div class='kpi-value'>{len(merged_df):,}</div>
          <div class='kpi-sub'>Left join on title</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class='kpi-card bl'>
          <div class='kpi-label'>Original Columns</div>
          <div class='kpi-value'>{len(merged_df.columns):,}</div>
          <div class='kpi-sub'>Including _merged suffix</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        dup_titles = int((merged_df["title"].value_counts() > 1).sum())
        st.markdown(f"""
        <div class='kpi-card em'>
          <div class='kpi-label'>Duplicate Titles</div>
          <div class='kpi-value'>{dup_titles:,}</div>
          <div class='kpi-sub'>Titles appearing 2+ times</div>
        </div>""", unsafe_allow_html=True)

    # OLAP pivot from main.py
    st.markdown(f"<div class='sec'><span class='sec-num'>A2</span> OLAP Pivot — Avg Description Length</div>",
                unsafe_allow_html=True)
    olap_pivot = pd.pivot_table(
        filt,
        values="desc_len",
        index="has_company_logo",
        columns="fraudulent",
        aggfunc=np.mean
    ).round(1)
    olap_pivot.index = ["No Logo" if i == 0 else "Has Logo" for i in olap_pivot.index]
    olap_pivot.columns = ["Legitimate" if c == 0 else "Fraudulent" for c in olap_pivot.columns]
    st.dataframe(olap_pivot, use_container_width=True)
    st.markdown(f"""<div class='ib'>
      Fraud rate by remote: <strong>{filt.groupby("telecommuting")["fraudulent"].mean().to_dict()}</strong> &nbsp;|&nbsp;
      Fraud rate by logo: <strong>{filt.groupby("has_company_logo")["fraudulent"].mean().to_dict()}</strong>
    </div>""", unsafe_allow_html=True)

    # ── Section B: Time-Variant Analysis ─────────────────────────────────────
    st.markdown(f"<div class='sec'><span class='sec-num'>B</span> Time-Variant Analysis (Simulated)</div>",
                unsafe_allow_html=True)
    st.markdown(f"""<div class='ib'>
      The dataset has no real timestamp column. A sequential <strong>index_time</strong> is
      simulated (row order) to show how description length varies across the dataset —
      a proxy for temporal drift or data collection batches.
    </div>""", unsafe_allow_html=True)

    tv1, tv2 = st.columns([2, 1])
    with tv1:
        # Full time-variant line (desc_len over index)
        plot_df = filt[["index_time", "desc_len", "fraudulent"]].copy()
        fig, ax = sfig(10, 4)
        for fraud_val, col, lbl in [(0, GREEN, "Legitimate"), (1, ROSE, "Fraudulent")]:
            sub = plot_df[plot_df["fraudulent"] == fraud_val].sort_values("index_time")
            if len(sub) > 500:
                # Downsample for performance
                sub = sub.iloc[::max(1, len(sub)//500)]
            ax.plot(sub["index_time"], sub["desc_len"],
                    color=col, alpha=.55, linewidth=.8, label=lbl)
        ax.set_title("Description Length over Dataset Index (Time-Variant Proxy)")
        ax.set_xlabel("Index (simulated time)"); ax.set_ylabel("Description Characters")
        ax.legend(); fig.tight_layout(); st.pyplot(fig); plt.close()

    with tv2:
        # Rolling mean (window=200) on full df for smoother trend
        roll_df = filt.sort_values("index_time")[["index_time","desc_len"]].copy()
        roll_df["rolling_mean"] = roll_df["desc_len"].rolling(window=200, min_periods=10).mean()
        fig, ax = sfig(5, 4)
        ax.plot(roll_df["index_time"], roll_df["rolling_mean"],
                color=ACCENT, linewidth=1.8, label="Rolling mean (200)")
        ax.set_title("Rolling Mean — Description Length")
        ax.set_xlabel("Index"); ax.set_ylabel("Chars")
        ax.legend(); fig.tight_layout(); st.pyplot(fig); plt.close()

    # ── Section C: Hypothesis Testing ────────────────────────────────────────
    st.markdown(f"<div class='sec'><span class='sec-num'>C</span> Hypothesis Testing — Description Length</div>",
                unsafe_allow_html=True)
    st.markdown(f"""<div class='ib'>
      <strong>H₀:</strong> Fake and real job postings have the <em>same</em> mean description length.<br>
      <strong>H₁:</strong> Fake job postings have a <em>different</em> mean description length.
    </div>""", unsafe_allow_html=True)

    fake_lens = filt[filt["fraudulent"] == 1]["desc_len"].dropna()
    real_lens = filt[filt["fraudulent"] == 0]["desc_len"].dropna()

    if len(fake_lens) > 1 and len(real_lens) > 1:
        t_stat, p_value = stats.ttest_ind(fake_lens, real_lens)
        reject = p_value < 0.05

        ht1, ht2, ht3, ht4 = st.columns(4)
        ht_cards = [
            ("T-Statistic",  f"{t_stat:.4f}", "Welch's two-sample t-test", BLUE),
            ("P-Value",      f"{p_value:.2e}", "α = 0.05 threshold",        ROSE if reject else GREEN),
            ("Fake Mean",    f"{fake_lens.mean():.0f} chars", f"n = {len(fake_lens):,}", ROSE),
            ("Legit Mean",   f"{real_lens.mean():.0f} chars", f"n = {len(real_lens):,}", GREEN),
        ]
        for (lbl, val, sub, col), col_obj in zip(ht_cards, [ht1, ht2, ht3, ht4]):
            with col_obj:
                st.markdown(f"""
                <div class='kpi-card' style='border-top-color:{col};'>
                  <div class='kpi-label'>{lbl}</div>
                  <div class='kpi-value' style='font-size:1.3rem;'>{val}</div>
                  <div class='kpi-sub'>{sub}</div>
                </div>""", unsafe_allow_html=True)

        verdict_color = ROSE if reject else GREEN
        verdict_text  = "✗ Reject H₀" if reject else "✓ Fail to Reject H₀"
        verdict_msg   = (
            f"p = {p_value:.2e} &lt; 0.05 — statistically significant difference. "
            f"Fake postings are <strong>{abs(real_lens.mean() - fake_lens.mean()):.0f} chars shorter</strong> on average."
            if reject else
            f"p = {p_value:.2e} ≥ 0.05 — no statistically significant difference detected."
        )
        st.markdown(f"""<div class='ib' style='border-left-color:{verdict_color};background:rgba(0,0,0,.03);'>
          <strong style='color:{verdict_color};font-size:.8rem;'>{verdict_text}</strong><br>{verdict_msg}
        </div>""", unsafe_allow_html=True)

        # Visualise the distributions side by side
        ht_v1, ht_v2 = st.columns(2)
        with ht_v1:
            fig, ax = sfig(6, 4)
            ax.hist(fake_lens, bins=50, color=ROSE,  alpha=.6, label="Fraudulent", edgecolor='none')
            ax.hist(real_lens, bins=50, color=GREEN, alpha=.5, label="Legitimate", edgecolor='none')
            ax.axvline(fake_lens.mean(), color=ROSE,  linestyle='--', linewidth=1.4,
                       label=f"Fake μ={fake_lens.mean():.0f}")
            ax.axvline(real_lens.mean(), color=GREEN, linestyle='--', linewidth=1.4,
                       label=f"Legit μ={real_lens.mean():.0f}")
            ax.set_title("Desc Length Distribution (Hypothesis Test)")
            ax.set_xlabel("Characters"); ax.set_ylabel("Frequency")
            ax.legend(fontsize=7); fig.tight_layout(); st.pyplot(fig); plt.close()

        with ht_v2:
            fig, ax = sfig(6, 4)
            bp = ax.boxplot([fake_lens, real_lens], patch_artist=True, widths=.45,
                            medianprops=dict(color=TXT_PRI, linewidth=2),
                            whiskerprops=dict(color=TXT_MUT),
                            capprops=dict(color=TXT_MUT),
                            flierprops=dict(marker='.', color=TXT_MUT, alpha=.2, markersize=2))
            bp["boxes"][0].set_facecolor(ROSE+"30");  bp["boxes"][0].set_edgecolor(ROSE)
            bp["boxes"][1].set_facecolor(GREEN+"30"); bp["boxes"][1].set_edgecolor(GREEN)
            ax.set_xticks([1,2]); ax.set_xticklabels(["Fraudulent","Legitimate"], color=TXT_PRI)
            ax.set_title("Boxplot — Desc Length by Class")
            ax.set_ylabel("Characters"); fig.tight_layout(); st.pyplot(fig); plt.close()
    else:
        st.info("Not enough data in current filter for hypothesis testing (need both classes).")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 8 · RAW DATA
# ─────────────────────────────────────────────────────────────────────────────
with tabs[7]:
    st.markdown(f"<div class='sec'><span class='sec-num'>★</span> Dataset Preview & Summary</div>",
                unsafe_allow_html=True)

    r1, r2 = st.columns([2,1])
    with r1:
        st.dataframe(filt.head(100), use_container_width=True, height=380)
    with r2:
        st.markdown(f"<div class='sec' style='margin-top:0'>EMSCAD Breakdown</div>",
                    unsafe_allow_html=True)
        tbl = filt["fraudulent"].value_counts(normalize=True).mul(100).reset_index()
        tbl.columns = ["Class","Percentage"]
        tbl["Class"] = tbl["Class"].map({0:"Legitimate",1:"Fraudulent"})
        tbl["Percentage"] = tbl["Percentage"].round(2).astype(str) + " %"
        st.dataframe(tbl, use_container_width=True, hide_index=True)

        st.markdown(f"""<div class='ib' style='margin-top:.8rem;'>
          Of <strong>{total:,}</strong> filtered postings,
          <strong style='color:{ROSE};'>{fraud_n:,} ({fraud_pct:.2f}%)</strong> are fraudulent and
          <strong style='color:{GREEN};'>{legit_n:,} ({100-fraud_pct:.2f}%)</strong> are legitimate.
          This ~5% fraud rate is characteristic of the EMSCAD dataset and reflects
          real-world job board distributions.
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<div class='sec' style='margin-top:1.2rem'>Numeric Summary</div>",
                    unsafe_allow_html=True)
        st.dataframe(filt.select_dtypes(include=np.number).describe().round(2),
                     use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='display:flex;justify-content:space-between;align-items:center;padding:.3rem 0;'>
  <div style='font-size:.56rem;color:{TXT_MUT};letter-spacing:.1em;'>
    THREATSCAN · JOB FRAUD INTELLIGENCE ENGINE · EDA v4
  </div>
  <div style='font-size:.56rem;color:{TXT_MUT};'>
    EMSCAD · Matplotlib + Seaborn + Streamlit · {'🌑 Dark' if DARK else '☀️ Light'} Mode
  </div>
</div>""", unsafe_allow_html=True)