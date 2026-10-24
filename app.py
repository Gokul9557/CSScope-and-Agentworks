from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from agentworks.controller import ToolController
from agentworks.presentation import build_answer_view
from agentworks.registry import ToolRegistry
from csscope.parser import analyze_css
from csscope.reports import format_report, to_json_report


ROOT = Path(__file__).parent
SAMPLE_PATH = ROOT / "sample_styles.css"
SAMPLE_CSS = SAMPLE_PATH.read_text(encoding="utf-8")

st.set_page_config(
    page_title="CSScope + AgentWorks",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
      color-scheme: light;
      --ink: #142d46;
      --muted: #557087;
      --blue: #145ca8;
      --teal: #007f7a;
      --line: #dce7ef;
      --surface: #ffffff;
    }
    .stApp {
      background:
        radial-gradient(ellipse at 90% 0%, #d9f1ed 0, transparent 28rem),
        linear-gradient(145deg, #f4f8fc 0%, #edf4f8 100%);
      color: var(--ink);
    }
    [data-testid="stMainBlockContainer"] {
      max-width: 1500px;
      padding-right: clamp(1rem, 2.5vw, 2.5rem);
      padding-left: clamp(1rem, 2.5vw, 2.5rem);
    }
    [data-testid="stHeader"] { background: rgba(244, 248, 252, .88); }
    [data-testid="stSidebar"] {
      background: linear-gradient(165deg, #102d4a 0%, #123c59 58%, #075b65 100%);
      border-right: 1px solid rgba(255,255,255,.12);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
      color: #e8f4fc;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
      color: #b9d3e4;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
      padding: .55rem .7rem;
      border: 1px solid transparent;
      border-radius: 10px;
      transition: background .16s ease, border-color .16s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
      background: rgba(255,255,255,.09);
      border-color: rgba(255,255,255,.18);
    }
    [data-testid="stSidebar"] [role="radiogroup"] label p {
      color: #edf7ff;
      font-weight: 600;
    }
    [data-testid="stSidebar"] input[type="radio"] { accent-color: #45d8c4; }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
      background: rgba(66, 211, 194, .17);
      border-color: rgba(108, 232, 211, .48);
    }
    [data-testid="stMainBlockContainer"] label,
    [data-testid="stMainBlockContainer"] label p,
    [data-testid="stMainBlockContainer"] [data-testid="stWidgetLabel"] p {
      color: #314d63 !important;
    }
    .brand-lockup {
      display: flex;
      align-items: center;
      gap: .75rem;
      margin: .25rem 0 .3rem;
    }
    .brand-mark {
      display: grid;
      width: 2.7rem;
      height: 2.7rem;
      place-items: center;
      border: 1px solid rgba(255,255,255,.3);
      border-radius: 12px;
      background: linear-gradient(145deg, #39d5c3, #1680bd);
      box-shadow: 0 6px 20px rgba(0,0,0,.2);
      color: white;
      font-size: 1.45rem;
      font-weight: 800;
    }
    .brand-name {
      color: #fff;
      font-size: 1.04rem;
      font-weight: 750;
      letter-spacing: -.02em;
    }
    .brand-subtitle {
      margin-top: .13rem;
      color: #b9d3e4;
      font-size: .73rem;
    }
    .hero {
      position: relative;
      overflow: hidden;
      display: block;
      margin-bottom: 1.4rem;
      padding: 1.65rem 1.9rem;
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 20px;
      color: white;
      background: linear-gradient(112deg, #123d68 0%, #126c82 55%, #078b81 100%);
      box-shadow: 0 14px 34px rgba(20, 65, 98, .18);
    }
    .hero:after {
      position: absolute;
      top: -5rem;
      right: 7rem;
      width: 15rem;
      height: 15rem;
      border: 1px solid rgba(255,255,255,.13);
      border-radius: 50%;
      box-shadow: 0 0 0 2rem rgba(255,255,255,.035), 0 0 0 4rem rgba(255,255,255,.025);
      content: "";
      pointer-events: none;
    }
    .hero-copy { position: relative; z-index: 1; padding-right: 11rem; }
    .hero-kicker {
      margin-bottom: .38rem;
      color: #a9eee2;
      font-size: .72rem;
      font-weight: 800;
      letter-spacing: .15em;
      text-transform: uppercase;
    }
    .hero h1 {
      margin: 0;
      color: #fff;
      font-size: clamp(1.65rem, 3vw, 2.15rem);
      font-weight: 760;
      letter-spacing: -.035em;
    }
    .hero p { margin: .42rem 0 0; color: #e1f2f6; font-size: .98rem; }
    .hero-badge {
      position: relative;
      z-index: 1;
      flex: 0 0 auto;
      position: absolute;
      top: 1.55rem;
      right: 1.6rem;
      padding: .55rem .85rem;
      border: 1px solid rgba(255,255,255,.28);
      border-radius: 999px;
      background: rgba(5, 36, 66, .28);
      color: #f3fffd;
      font-size: .78rem;
      font-weight: 700;
    }
    h2, h3 { color: var(--ink); letter-spacing: -.02em; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    div[data-testid="stMetric"] {
      min-height: 6.15rem;
      border: 1px solid var(--line);
      border-top: 3px solid #168e9a;
      border-radius: 14px;
      background: var(--surface);
      padding: .78rem 1rem;
      box-shadow: 0 5px 18px rgba(20, 49, 73, .055);
      transition: transform .16s ease, box-shadow .16s ease;
    }
    div[data-testid="stMetric"]:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 24px rgba(20, 49, 73, .1);
    }
    div[data-testid="stMetricLabel"] p {
      color: #526b80;
      font-size: .82rem;
      font-weight: 650;
    }
    div[data-testid="stMetricValue"] {
      color: #123957;
      font-weight: 760;
    }
    [data-testid="stTabs"] [role="tablist"] {
      gap: .35rem;
      border-bottom: 1px solid var(--line);
    }
    [data-testid="stTabs"] button[role="tab"] {
      border-radius: 9px 9px 0 0;
      color: #486176;
      font-weight: 650;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
      background: #e5f3f3;
      color: #075e66;
    }
    .stButton > button, .stDownloadButton > button {
      min-height: 2.65rem;
      border: 1px solid #b8cfde;
      border-radius: 10px;
      color: #173b59;
      background: #fff;
      font-weight: 680;
      transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
      border-color: #168e9a;
      color: #075e66;
      background: #effafa;
      box-shadow: 0 5px 14px rgba(16, 117, 126, .12);
      transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
      border-color: #145ca8;
      color: #fff;
      background: linear-gradient(100deg, #145ca8, #087f88);
      box-shadow: 0 5px 14px rgba(20, 92, 168, .2);
    }
    .stButton > button[kind="primary"]:hover {
      border-color: #0d4d88;
      color: #fff;
      background: linear-gradient(100deg, #104e91, #066d76);
    }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
      border-color: #c7d8e3;
      border-radius: 10px;
      background: #fff;
      color: var(--ink);
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
      border-color: #c7d8e3;
      background: #fff;
      color: var(--ink);
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
      border-color: #168e9a;
      box-shadow: 0 0 0 3px rgba(22, 142, 154, .14);
    }
    [data-testid="stFileUploader"] section {
      border: 1px dashed #8fb4c7;
      border-radius: 14px;
      background: #f8fcff;
    }
    [data-testid="stFileUploader"] button {
      border: 1px solid #126c82;
      border-radius: 9px;
      color: #fff;
      background: linear-gradient(105deg, #145ca8, #087f88);
      font-weight: 700;
      box-shadow: 0 4px 12px rgba(20, 92, 168, .18);
      transition: transform .15s ease, box-shadow .15s ease, background .15s ease;
    }
    [data-testid="stFileUploader"] button:hover {
      border-color: #075e66;
      color: #fff;
      background: linear-gradient(105deg, #104e91, #066d76);
      box-shadow: 0 6px 16px rgba(16, 117, 126, .24);
      transform: translateY(-1px);
    }
    [data-testid="stAlert"] { border-radius: 11px; }
    [data-testid="stDataFrame"] {
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 12px;
    }
    [data-testid="stExpander"] {
      overflow: hidden;
      border: 1px solid #d5e3eb !important;
      border-radius: 13px !important;
      background: #fff;
    }
    [data-testid="stExpander"] details > summary {
      color: #173b59 !important;
      background: #eaf3f8 !important;
      font-weight: 700;
    }
    [data-testid="stExpander"] details > summary p { color: #173b59 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] {
      border-color: #dce8ef !important;
      border-radius: 12px !important;
      background: #fff;
    }
    .answer-eyebrow {
      margin-bottom: .25rem;
      color: #087c78;
      font-size: .72rem;
      font-weight: 800;
      letter-spacing: .13em;
    }
    .st-key-css-analysis-card [data-testid="stVerticalBlockBorderWrapper"] {
      overflow: hidden;
      border: 1px solid #b8d4e5 !important;
      border-radius: 20px !important;
      background:
        radial-gradient(ellipse at 100% 0%, rgba(83, 213, 199, .13), transparent 24rem),
        linear-gradient(145deg, #f7fbff 0%, #edf6fc 100%);
      box-shadow: 0 18px 42px rgba(17, 58, 91, .12);
    }
    .st-key-css-analysis-card .answer-eyebrow {
      margin: -.35rem -.35rem .55rem;
      padding: 1rem 1.15rem;
      border: 1px solid rgba(255,255,255,.16);
      border-radius: 14px;
      background: linear-gradient(110deg, #12375b 0%, #155b83 55%, #087f7b 100%);
      box-shadow: 0 8px 20px rgba(14, 65, 95, .2);
      color: #d2fff5;
      font-size: .74rem;
      letter-spacing: .16em;
    }
    .st-key-css-analysis-card [data-testid="stMetric"] {
      min-height: 6.4rem;
      border: 1px solid #d5e6ef;
      border-top: 3px solid #168e9a;
      border-radius: 14px;
      background: linear-gradient(155deg, #fff 0%, #f4faff 100%);
      box-shadow: 0 6px 16px rgba(20, 49, 73, .08);
    }
    .st-key-css-analysis-card [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
      border-top-color: #3676d3;
    }
    .st-key-css-analysis-card [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
      border-top-color: #8158c8;
    }
    .st-key-css-analysis-card [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
      border-top-color: #e05262;
    }
    .st-key-css-analysis-card [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] {
      border-top-color: #e49a28;
    }
    .st-key-css-analysis-card [data-testid="stTabs"] [role="tablist"] {
      padding: .35rem;
      border: 1px solid #d8e7ef;
      border-radius: 12px;
      background: #e8f1f7;
    }
    .st-key-css-analysis-card [data-testid="stTabs"] button[role="tab"] {
      border-radius: 9px;
    }
    .st-key-css-analysis-card [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
      background: linear-gradient(110deg, #155b83, #087f7b);
      box-shadow: 0 4px 12px rgba(8, 94, 112, .2);
      color: #fff;
    }
    .st-key-css-analysis-card [data-testid="stDataFrame"] {
      border-color: #cfe0e9;
      border-radius: 13px;
      box-shadow: 0 5px 14px rgba(20, 49, 73, .055);
    }
    .st-key-css-analysis-report {
      overflow: hidden;
      padding: 1rem 1.15rem;
      border: 1px solid #267b98;
      border-radius: 16px;
      background:
        radial-gradient(ellipse at 100% 0%, rgba(54, 226, 198, .2), transparent 22rem),
        linear-gradient(130deg, #102f52 0%, #124e70 55%, #086d70 100%);
      box-shadow: 0 12px 28px rgba(13, 61, 86, .2);
    }
    .st-key-css-analysis-report [data-testid="stText"] span {
      color: #f1fffd !important;
      font-family: ui-monospace, "Cascadia Code", Consolas, monospace;
      line-height: 1.75;
      text-shadow: 0 1px 1px rgba(0, 0, 0, .18);
    }
    .st-key-agentworks-tool-catalog [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
      min-height: 12rem;
      border: 1px solid #d1e2eb !important;
      border-radius: 14px !important;
      background: linear-gradient(150deg, #fff 0%, #f0f8fc 100%);
      box-shadow: 0 5px 16px rgba(20, 49, 73, .06);
    }
    .st-key-agentworks-tool-catalog [data-testid="stVerticalBlockBorderWrapper"] strong {
      color: #145c77;
      font-size: .98rem;
    }
    .st-key-agentworks-tool-form {
      padding: 1.1rem 1.2rem;
      border: 1px solid #c8dce8;
      border-radius: 18px;
      background:
        radial-gradient(ellipse at 100% 0%, rgba(83, 213, 199, .12), transparent 22rem),
        linear-gradient(145deg, #fff 0%, #f1f8fc 100%);
      box-shadow: 0 12px 28px rgba(17, 58, 91, .09);
    }
    .st-key-agentworks-tool-form .answer-eyebrow {
      color: #087c78;
      letter-spacing: .16em;
    }
    .st-key-agentworks-tool-form [data-testid="stSelectbox"],
    .st-key-agentworks-tool-form [data-testid="stTextInput"],
    .st-key-agentworks-tool-form [data-testid="stTextArea"] {
      margin-bottom: .25rem;
    }
    .st-key-agentworks-tool-form .stButton > button {
      min-width: 10rem;
      box-shadow: 0 6px 16px rgba(20, 92, 168, .18);
    }
    .st-key-agentworks-answer-card {
      padding: 1.1rem 1.2rem;
      border: 1px solid #b8d8e2;
      border-radius: 18px;
      background:
        radial-gradient(ellipse at 100% 0%, rgba(83, 213, 199, .13), transparent 22rem),
        linear-gradient(145deg, #fff 0%, #f0f8fb 100%);
      box-shadow: 0 12px 30px rgba(17, 58, 91, .1);
    }
    .st-key-agentworks-answer-card .answer-eyebrow {
      color: #087c78;
      letter-spacing: .16em;
    }
    .st-key-agentworks-answer-card [data-testid="stMetric"] {
      border-top-color: #168e9a;
      border-radius: 14px;
      background: linear-gradient(155deg, #fff 0%, #f3fbfc 100%);
    }
    .st-key-agentworks-answer-card [data-testid="stDataFrame"] {
      overflow: hidden;
      border: 1px solid #d1e2eb;
      border-radius: 12px;
    }
    .st-key-agentworks-history [data-testid="stDataFrame"] {
      overflow: hidden;
      border: 1px solid #d1e2eb;
      border-radius: 14px;
      box-shadow: 0 6px 18px rgba(20, 49, 73, .06);
    }
    .answer-note {
      padding: .8rem 1rem;
      border-left: 3px solid #15a394;
      border-radius: 0 9px 9px 0;
      background: #eff9f7;
    }
    .answer-note p { margin: 0; color: #1a4357; }
    @media (max-width: 640px) {
      [data-testid="stMainBlockContainer"] {
        padding-right: 1rem;
        padding-left: 1rem;
      }
      .hero { padding: 1.25rem; }
      .hero-copy { padding-right: 0; }
      .hero-badge { display: none; }
    }
    @media (max-width: 1200px) {
      .hero-copy { padding-right: 0; }
      .hero-badge { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "agent_controller" not in st.session_state:
    st.session_state.agent_controller = ToolController()


def clear_inputs() -> None:
    st.session_state.pasted_css = ""
    st.session_state.css_sample_loaded = False


with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark">◈</div>
          <div>
            <div class="brand-name">CSScope <span style="color:#55ddc8">×</span> AgentWorks</div>
            <div class="brand-subtitle">Your local CSS & tool workbench</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    section = st.radio(
        "Workspace",
        ["CSScope Analyzer", "AgentWorks Tool Lab"],
        label_visibility="visible",
        format_func=lambda value: {
            "CSScope Analyzer": "🎨  CSScope Analyzer",
            "AgentWorks Tool Lab": "🧰  AgentWorks Tool Lab",
        }[value],
    )
    st.divider()
    st.caption("🔒  Runs locally · No API key needed")
    st.caption("AgentWorks uses a clear, rule-based tool router.")

section_details = {
    "CSScope Analyzer": (
        "CSS WORKSPACE  /  01",
        "🎨",
        "Inspect styles. Understand every rule.",
        "Parse, explore, and export a clear stylesheet report.",
        "CSS ANALYSIS",
    ),
    "AgentWorks Tool Lab": (
        "TOOL WORKSPACE  /  02",
        "🧰",
        "Small tools. Useful answers.",
        "Run safe calculations, text utilities, and stylesheet checks.",
        "RULE-BASED · LOCAL",
    ),
}
kicker, section_icon, headline, subtitle, badge = section_details[section]

st.markdown(
    f"""
    <div class="hero">
      <div class="hero-copy">
        <div class="hero-kicker">{kicker}</div>
        <h1>{section_icon} &nbsp;{headline}</h1>
        <p>{subtitle}</p>
      </div>
      <div class="hero-badge">{badge}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


def show_analysis(source: str) -> None:
    analysis = analyze_css(source)
    summary = analysis["summary"]
    with st.container(border=True, key="css-analysis-card"):
        st.markdown(
            '<div class="answer-eyebrow">CSSCOPE · ANALYSIS RESULTS</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(5)
        for col, label, key in zip(
            cols,
            ("🎯 Selectors", "🧾 Declarations", "⚡ At-rules", "🚨 Errors", "⚠️ Warnings"),
            ("selectors", "declarations", "at_rules", "errors", "warnings"),
        ):
            col.metric(label, summary[key])
        tab_rules, tab_details, tab_report = st.tabs(
            ["🧩  Rules & declarations", "🔎  Details", "📄  Readable report"]
        )
        with tab_rules:
            if analysis["selectors"]:
                st.subheader("🎯  Qualified rules")
                st.dataframe(
                    [
                        {
                            "Selector": item["selector"],
                            "Selector count": item["selector_count"],
                            "Nested in": " › ".join(item["at_rule_context"]) or "—",
                            "Line": item["line"],
                        }
                        for item in analysis["selectors"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            if analysis["declarations"]:
                st.subheader("🧾  Declarations")
                st.dataframe(
                    [
                        {
                            "Context": item["context"],
                            "Property": item["property"],
                            "Value": item["value"],
                            "Important": item["important"],
                            "Line": item["line"],
                        }
                        for item in analysis["declarations"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            if not analysis["selectors"] and not analysis["declarations"]:
                st.info("No qualified rules or declarations were found.")
        with tab_details:
            st.write(
                {
                    "Comments": summary["comments"],
                    "Custom properties": summary["custom_properties"],
                    "Media queries": summary["media_queries"],
                    "Keyframes": summary["keyframes"],
                }
            )
            if analysis["at_rules"]:
                st.subheader("⚡  At-rules")
                st.dataframe(
                    [
                        {
                            "At-rule": f"@{item['name']}",
                            "Prelude": item["prelude"],
                            "Nested in": " › ".join(item["context"]) or "—",
                            "Line": item["line"],
                        }
                        for item in analysis["at_rules"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            if analysis["custom_properties"]:
                st.subheader("🎨  CSS custom properties")
                st.dataframe(
                    [
                        {"Property": item["property"], "Value": item["value"]}
                        for item in analysis["custom_properties"]
                    ],
                    width="stretch",
                    hide_index=True,
                )
            if analysis["diagnostics"]:
                st.subheader("🩺  Diagnostics")
                st.dataframe(analysis["diagnostics"], width="stretch", hide_index=True)
            else:
                st.success("No parsing errors or warnings.")
        with tab_report:
            with st.container(border=True, key="css-analysis-report"):
                st.text(format_report(analysis))
        st.download_button(
            "⬇️  Download JSON report",
            data=to_json_report(analysis),
            file_name="csscope-report.json",
            mime="application/json",
            key="download_analysis",
        )


if section == "CSScope Analyzer":
    input_tab, paste_tab = st.tabs(["📂  Upload CSS", "✍️  Paste CSS"])
    with input_tab:
        st.markdown("### Bring a stylesheet into focus")
        st.caption("Choose a local CSS file, or try the sample to explore the report.")
        uploaded = st.file_uploader("📁 Choose a .css file", type=["css"])
        left, _ = st.columns([1, 3])
        use_sample = left.button("✨  Load built-in sample", width="stretch")
        if use_sample:
            st.session_state.css_sample_loaded = True
        if uploaded is not None:
            css_source = uploaded.getvalue().decode("utf-8", errors="replace")
            st.caption(f"Loaded {uploaded.name} · {len(uploaded.getvalue()):,} bytes")
            show_analysis(css_source)
        elif st.session_state.get("css_sample_loaded", False):
            show_analysis(SAMPLE_CSS)
    with paste_tab:
        pasted = st.text_area(
            "✍️ CSS source",
            value="",
            height=280,
            placeholder="Paste a stylesheet here...",
            key="pasted_css",
        )
        button_col, clear_col = st.columns([1, 1])
        analyze_clicked = button_col.button("🔍  Analyze CSS", type="primary")
        clear_col.button("🧹  Clear", on_click=clear_inputs)
        if analyze_clicked:
            show_analysis(pasted)

else:
    registry: ToolRegistry = st.session_state.agent_controller.registry
    tools = registry.describe()
    tool_labels = {item["name"]: item["description"] for item in tools}
    task_names = {
        "🧮  Calculate arithmetic": "Calculate arithmetic",
        "🔢  Count words": "Count words",
        "🔤  Count characters": "Count characters",
        "✨  Summarize text": "Summarize text",
        "🎨  Inspect sample CSS file": "Inspect sample CSS file",
    }
    with st.container(key="agentworks-tool-catalog"):
        with st.expander("Available tools", expanded=True):
            tool_icons = {
                "calculator": "🧮",
                "text": "📝",
                "css_inspector": "🎨",
            }
            tool_names = {
                "calculator": "Calculator",
                "text": "Text",
                "css_inspector": "CSS Inspector",
            }
            tool_columns = st.columns(len(tool_labels))
            for column, (name, description) in zip(tool_columns, tool_labels.items()):
                with column.container(border=True):
                    st.markdown(f"**{tool_icons[name]}  {tool_names[name]}**")
                    st.caption(description)

    with st.container(border=True, key="agentworks-tool-form"):
        st.markdown(
            '<div class="answer-eyebrow">AGENTWORKS · TOOL RUNNER</div>',
            unsafe_allow_html=True,
        )
        st.markdown("### 🚀  What would you like to do?")
        selected_task = st.selectbox("Choose a task", list(task_names))
        task = task_names[selected_task]
        request_by_task = {
            "Calculate arithmetic": "calculate",
            "Count words": "word count",
            "Count characters": "character count",
            "Summarize text": "summarize",
            "Inspect sample CSS file": "inspect css file",
        }
        request = request_by_task[task]
        arguments: dict[str, object]
        if task == "Calculate arithmetic":
            expression = st.text_input(
                "🧮 Arithmetic expression",
                placeholder="18 * (4 + 2)",
            )
            arguments = {"expression": expression}
        elif task in ("Count words", "Count characters", "Summarize text"):
            text = st.text_area("📝 Text to process", height=160)
            operation = {
                "Count words": "word_count",
                "Count characters": "character_count",
                "Summarize text": "summary",
            }[task]
            arguments = {"text": text, "operation": operation}
        else:
            st.info(f"📄 Using the included sample: **{SAMPLE_PATH.name}**")
            arguments = {"path": str(SAMPLE_PATH), "sample_dir": str(ROOT)}

        run_clicked = st.button("▶️  Run tool", type="primary")

    if run_clicked:
        output = st.session_state.agent_controller.run(
            request, **arguments
        )
        history_entry = st.session_state.agent_controller.history[-1]
        st.session_state.latest_agent_answer = {
            "task": task,
            "request": request,
            "history_entry": history_entry,
            "output": output,
        }

    latest_answer = st.session_state.get("latest_agent_answer")
    if latest_answer:
        with st.container(border=True, key="agentworks-answer-card"):
            st.markdown('<div class="answer-eyebrow">AGENTWORKS · ANSWER CARD</div>', unsafe_allow_html=True)
            history_entry = latest_answer["history_entry"]
            st.caption(
                f"Run #{history_entry['id']}  ·  {history_entry['timestamp']}  ·  "
                f"{latest_answer['request']}"
            )
            output = latest_answer["output"]
            if output["ok"]:
                answer = build_answer_view(latest_answer["task"], output["data"])
                st.subheader(f"✨  {answer.title}")
                st.metric("Your answer", answer.headline, help=answer.description)
                st.caption(answer.description)
                if answer.metrics:
                    metric_columns = st.columns(len(answer.metrics))
                    for column, (label, value) in zip(metric_columns, answer.metrics):
                        column.metric(label, value)
                if answer.text is not None:
                    st.markdown("#### 🪄  Text snapshot")
                    with st.container(border=True):
                        st.write(answer.text)
                if answer.details:
                    with st.expander("🔎  More useful details", expanded=False):
                        st.dataframe(
                            [
                                {"Detail": label, "Value": value}
                                for label, value in answer.details
                            ],
                            width="stretch",
                            hide_index=True,
                        )
                with st.expander("🧩  Raw structured result", expanded=False):
                    st.json(output["data"])
                st.download_button(
                    "⬇️  Download this result",
                    data=json.dumps(output["data"], indent=2, ensure_ascii=False),
                    file_name=f"agentworks-run-{history_entry['id']}.json",
                    mime="application/json",
                    key=f"download_agent_result_{history_entry['id']}",
                )
            else:
                st.error("⚠️  This request could not be completed.")
                st.write(output["error"])
                st.caption(
                    "Try a valid expression, provide text for a text task, "
                    "or choose the included CSS sample."
                )

    history = st.session_state.agent_controller.history
    st.subheader("🕘  Execution history")
    if history:
        with st.container(key="agentworks-history"):
            st.dataframe(
                [
                    {
                        "ID": item["id"],
                        "Time (UTC)": item["timestamp"],
                        "Request": item["request"],
                        "Tool": item["tool"],
                        "Result": json.dumps(item["result"]["data"] or item["result"]["error"]),
                    }
                    for item in reversed(history)
                ],
                width="stretch",
                hide_index=True,
            )
    else:
        st.caption("Runs from this session will appear here.")
