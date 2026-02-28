import streamlit as st
import pandas as pd
import requests
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import SessionLocal
from models.domain import Submission, ModelSuggestion
from dashboard.translations import t, TRANSLATIONS

st.set_page_config(page_title="ELS JUDGE", layout="wide", initial_sidebar_state="collapsed")

# --- Dark Pink Theme CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --pink: #d6336c;
        --pink-dark: #a61e4d;
        --pink-light: #f06595;
        --pink-glow: rgba(214, 51, 108, 0.25);
        --bg-dark: #0c0c12;
        --bg-card: #131320;
        --bg-input: #1a1a2e;
        --border: rgba(214, 51, 108, 0.18);
        --text: #eee;
        --text-dim: rgba(238,238,238,0.45);
    }

    .stApp {
        background: var(--bg-dark) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    .block-container { padding: 1rem 2rem 2rem 2rem !important; max-width: 1400px; }

    .site-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.8rem 0 1.2rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }
    .hdr-left { display: flex; align-items: center; gap: 12px; }
    .hdr-logo {
        width: 36px; height: 36px;
        background: var(--pink); border-radius: 9px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 3px 16px var(--pink-glow);
    }
    .hdr-logo svg { width: 20px; height: 20px; fill: white; }
    .hdr-title { font-size: 1.2rem; font-weight: 700; color: var(--pink-light); }
    .hdr-right { display: flex; align-items: center; gap: 16px; font-size: 0.75rem; color: var(--text-dim); }
    .hdr-right .dot {
        width: 6px; height: 6px; background: #22c55e; border-radius: 50%;
        display: inline-block; margin-right: 4px; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

    .section-label {
        font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.1em; color: var(--pink-light);
        margin-bottom: 0.8rem; display: flex; align-items: center; gap: 8px;
    }
    .section-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }

    .stat-row { display: flex; gap: 14px; margin-bottom: 1.5rem; }
    .stat-card {
        flex: 1; background: var(--bg-card); border: 1px solid var(--border);
        border-radius: 12px; padding: 1rem 1.2rem;
    }
    .stat-card .stat-label {
        font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em;
        color: var(--text-dim); margin-bottom: 4px;
    }
    .stat-card .stat-value { font-size: 1.4rem; font-weight: 700; color: var(--pink-light); }
    .stat-card .stat-sub { font-size: 0.7rem; color: var(--text-dim); margin-top: 3px; }

    [data-testid="stForm"] {
        border: 1px solid var(--border) !important; border-radius: 12px !important;
        padding: 1.3rem !important; background: var(--bg-card) !important;
    }
    .stTextArea textarea, .stTextInput input {
        background: var(--bg-input) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important; font-size: 0.82rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--pink) !important;
        box-shadow: 0 0 0 3px var(--pink-glow) !important;
    }
    .stTextArea label, .stTextInput label {
        color: var(--text-dim) !important; font-size: 0.78rem !important; font-weight: 500 !important;
    }

    .stFormSubmitButton button {
        background: var(--pink) !important; color: white !important;
        border: none !important; border-radius: 9px !important;
        font-weight: 600 !important; font-size: 0.88rem !important;
        padding: 0.65rem 2rem !important;
        box-shadow: 0 4px 16px var(--pink-glow) !important;
        transition: all 0.2s ease !important;
    }
    .stFormSubmitButton button:hover {
        background: var(--pink-dark) !important;
        transform: translateY(-1px) !important;
    }

    .stSelectbox > div > div {
        background: var(--bg-input) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text) !important;
    }
    .stSelectbox label { color: var(--text-dim) !important; font-size: 0.78rem !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--bg-card);
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-dim) !important;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: var(--pink) !important;
        color: white !important;
    }

    .stAlert { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
    .streamlit-expanderHeader { background: var(--bg-card) !important; border-radius: 10px !important; color: var(--text) !important; }
    .streamlit-expanderContent { background: var(--bg-input) !important; border: 1px solid var(--border) !important; }

    .empty-state {
        text-align: center; padding: 2.5rem 1.5rem;
        background: var(--bg-card); border: 1px dashed var(--border);
        border-radius: 12px; color: var(--text-dim); font-size: 0.85rem;
    }

    .how-row { display: flex; gap: 14px; margin-top: 1rem; }
    .how-card {
        flex: 1; background: var(--bg-card); border: 1px solid var(--border);
        border-radius: 12px; padding: 1rem 1.1rem;
    }
    .how-card .hw-step { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--pink); font-weight: 700; margin-bottom: 4px; }
    .how-card .hw-title { font-size: 0.85rem; font-weight: 600; color: var(--text); margin-bottom: 3px; }
    .how-card .hw-desc { font-size: 0.73rem; color: var(--text-dim); line-height: 1.4; }

    .site-footer {
        text-align: center; padding: 1.5rem 0 0.5rem 0;
        margin-top: 2rem; border-top: 1px solid var(--border);
        font-size: 0.72rem; color: var(--text-dim);
    }
    .site-footer a { color: var(--pink-light); text-decoration: none; }

    h2, h3, p, li { color: var(--text) !important; }

    /* Change card */
    .change-card {
        background: var(--bg-input);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .change-card .cc-header {
        font-size: 0.78rem;
        font-weight: 600;
        color: var(--pink-light);
        margin-bottom: 0.5rem;
    }
    .change-card .cc-reason {
        font-size: 0.76rem;
        color: var(--text-dim);
        margin-bottom: 0.6rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# --- Language Selector ---
lang_options = {"EN": "en", "TR": "tr"}
_, lang_col = st.columns([16, 1])
with lang_col:
    selected_lang_label = st.selectbox("Lang", options=list(lang_options.keys()), index=0, label_visibility="collapsed")
lang = lang_options[selected_lang_label]

# --- Header ---
st.markdown(f"""
<div class="site-header">
    <div class="hdr-left">
        <div class="hdr-logo">
            <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        </div>
        <span class="hdr-title">{t("title", lang)}</span>
    </div>
    <div class="hdr-right">
        <span>{t("subtitle", lang)}</span>
        <span><span class="dot"></span> Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Stats ---
@st.cache_data(ttl=5)
def get_stats():
    db = SessionLocal()
    try:
        total = db.query(Submission).count()
        return total
    except Exception:
        return 0
    finally:
        db.close()

total_analyses = get_stats()
sl = {
    "en": ["Total Analyses", "Active Models"],
    "tr": ["Toplam Analiz", "Aktif Modeller"]
}
labels = sl.get(lang, sl["en"])

st.markdown(f"""
<div class="stat-row">
    <div class="stat-card">
        <div class="stat-label">{labels[0]}</div>
        <div class="stat-value">{total_analyses}</div>
        <div class="stat-sub">All time</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">{labels[1]}</div>
        <div class="stat-value">3</div>
        <div class="stat-sub">GPT-4o / Claude / Gemini</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ========== MAIN FORM ==========
st.markdown(f'<div class="section-label">{t("submit_header", lang)}</div>', unsafe_allow_html=True)

with st.form("submission_form"):
    code_input = st.text_area(
        t("your_code", lang),
        height=200,
        placeholder="def hello_world():\n    pass"
    )
    prompt_input = st.text_input(
        t("your_prompt", lang),
        placeholder=t("prompt_placeholder", lang)
    )
    submit = st.form_submit_button(t("run_pipeline", lang), use_container_width=True)

    if submit:
        if not code_input or not prompt_input:
            st.warning(t("warning_both", lang))
        else:
            with st.spinner(t("spinner", lang)):
                try:
                    res = requests.post("http://localhost:8000/api/submit-code", json={
                        "code": code_input,
                        "prompt": prompt_input
                    }, timeout=120)

                    if res.status_code == 200:
                        st.success(t("success", lang))
                        data = res.json()

                        # Show per-model results as tabs
                        model_results = data.get("model_results", [])
                        if model_results:
                            tab_names = [r["model_name"].split("/")[-1] for r in model_results]
                            tabs = st.tabs(tab_names)

                            for tab, result in zip(tabs, model_results):
                                with tab:
                                    model_name = result['model_name']
                                    st.markdown(f"**{t('ai_prompt_sent', lang).format(model=model_name)}**")
                                    st.info(prompt_input)
                                    st.markdown(f"**{t('ai_response_received', lang).format(model=model_name)}**")
                                    st.markdown(f"**{t('explanation', lang)}:** {result['explanation']}")

                                    # Show changes
                                    changes = result.get("changes", [])
                                    if changes:
                                        st.markdown(f"**{t('changes_made', lang)}:**")
                                        for i, change in enumerate(changes, 1):
                                            st.markdown(f"""
<div class="change-card">
    <div class="cc-header">{i}. {change['line_range']}</div>
    <div class="cc-reason">{change['reason']}</div>
</div>
""", unsafe_allow_html=True)
                                            col_before, col_after = st.columns(2)
                                            with col_before:
                                                st.code(change["original"], language="python")
                                            with col_after:
                                                st.code(change["improved"], language="python")

                                    # Diff
                                    with st.expander(t("diff_view", lang)):
                                        st.code(result.get("diff_text", ""), language="diff")

                                    # Full improved code
                                    with st.expander(t("improved_code", lang)):
                                        st.code(result["improved_code"], language="python")

                        # Full report
                        with st.expander(t("show_report", lang)):
                            st.markdown(data.get("markdown_report", ""))

                    else:
                        st.error(f"{t('error_prefix', lang)} {res.status_code}: {res.text}")
                except requests.exceptions.ConnectionError:
                    st.error(t("connection_error", lang))
                except Exception as e:
                    st.error(f"{t('unexpected_error', lang)}: {e}")


# --- How It Works ---
ht = {
    "en": [t("step1_title", lang), t("step2_title", lang), t("step3_title", lang), t("step4_title", lang)],
    "tr": [t("step1_title", lang), t("step2_title", lang), t("step3_title", lang), t("step4_title", lang)]
}
hd = {
    "en": [t("step1_desc", lang), t("step2_desc", lang), t("step3_desc", lang), t("step4_desc", lang)],
    "tr": [t("step1_desc", lang), t("step2_desc", lang), t("step3_desc", lang), t("step4_desc", lang)]
}
titles = ht.get(lang, ht["en"])
descs = hd.get(lang, hd["en"])

st.markdown(f'<div class="section-label" style="margin-top:1.5rem;">{t("how_works", lang)}</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="how-row">
    <div class="how-card"><div class="hw-step">Step 1</div><div class="hw-title">{titles[0]}</div><div class="hw-desc">{descs[0]}</div></div>
    <div class="how-card"><div class="hw-step">Step 2</div><div class="hw-title">{titles[1]}</div><div class="hw-desc">{descs[1]}</div></div>
    <div class="how-card"><div class="hw-step">Step 3</div><div class="hw-title">{titles[2]}</div><div class="hw-desc">{descs[2]}</div></div>
    <div class="how-card"><div class="hw-step">Step 4</div><div class="hw-title">{titles[3]}</div><div class="hw-desc">{descs[3]}</div></div>
</div>
""", unsafe_allow_html=True)

# --- Footer ---
st.markdown("""
<div class="site-footer">
    Built by <a href="https://github.com/codedbyelif" target="_blank">codedbyelif</a> &middot; ELS JUDGE v1.0
</div>
""", unsafe_allow_html=True)
