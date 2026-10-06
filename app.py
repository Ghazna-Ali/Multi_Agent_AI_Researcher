import re
import time

import streamlit as st

from crew import create_research_crew, AGENT_STAGES
from model_manager import (
    MODEL_OPTIONS,
    DEFAULT_MODEL,
    create_llm,
    model_id,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchOS AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_model" not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL

if "research_started" not in st.session_state:
    st.session_state.research_started = False

if "current_agent" not in st.session_state:
    st.session_state.current_agent = None

if "result" not in st.session_state:
    st.session_state.result = None

if "research_time" not in st.session_state:
    st.session_state.research_time = 0


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --bg: #070b14;
        --panel: #0d1321;
        --panel-2: #111827;
        --border: rgba(255,255,255,.08);
        --text: #f5f7fb;
        --muted: #8f9bb0;
        --accent: #7c5cff;
        --accent-2: #23c4ff;
        --success: #39d98a;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(124,92,255,.16),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(35,196,255,.10),
                transparent 25%
            ),
            var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Sidebar */

    [data-testid="stSidebar"] {
        background: #080d18;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 2rem;
    }

    .brand-icon {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: linear-gradient(
            135deg,
            var(--accent),
            var(--accent-2)
        );
        font-size: 21px;
        box-shadow: 0 8px 30px rgba(124,92,255,.28);
    }

    .brand-title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -.4px;
    }

    .brand-subtitle {
        font-size: 11px;
        color: var(--muted);
        margin-top: 2px;
    }

    /* Hero */

    .hero {
        position: relative;
        overflow: hidden;
        padding: 42px;
        border-radius: 28px;
        border: 1px solid var(--border);
        background:
            linear-gradient(
                135deg,
                rgba(124,92,255,.14),
                rgba(17,24,39,.80)
            );
        box-shadow: 0 25px 70px rgba(0,0,0,.22);
        margin-bottom: 24px;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        right: -100px;
        top: -140px;
        background: rgba(35,196,255,.12);
        border-radius: 50%;
        filter: blur(30px);
    }

    .eyebrow {
        color: #a99bff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 13px;
    }

    .hero h1 {
        font-size: clamp(36px, 5vw, 62px);
        line-height: 1;
        letter-spacing: -3px;
        margin: 0;
        font-weight: 800;
    }

    .hero p {
        max-width: 760px;
        color: #aeb8ca;
        font-size: 16px;
        line-height: 1.7;
        margin-top: 18px;
        margin-bottom: 0;
    }

    /* Cards */

    .card {
        background: rgba(13,19,33,.78);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 15px 50px rgba(0,0,0,.15);
    }

    .metric-label {
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .metric-value {
        font-size: 25px;
        font-weight: 800;
        margin-top: 7px;
    }

    /* Agent status */

    .working {
        display: flex;
        align-items: center;
        gap: 13px;
        padding: 16px 18px;
        border-radius: 16px;
        border: 1px solid rgba(124,92,255,.30);
        background:
            linear-gradient(
                135deg,
                rgba(124,92,255,.12),
                rgba(35,196,255,.05)
            );
        margin: 14px 0 20px;
    }

    .pulse {
        width: 11px;
        height: 11px;
        border-radius: 50%;
        background: #39d98a;
        box-shadow:
            0 0 0 0 rgba(57,217,138,.7);
        animation: pulse 1.7s infinite;
    }

    @keyframes pulse {
        70% {
            box-shadow:
                0 0 0 9px rgba(57,217,138,0);
        }
        100% {
            box-shadow:
                0 0 0 0 rgba(57,217,138,0);
        }
    }

    .working-title {
        font-size: 12px;
        color: var(--muted);
    }

    .working-agent {
        font-weight: 800;
        margin-top: 2px;
    }

    /* Timeline */

    .stage {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 0;
    }

    .stage-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .stage-done {
        background: var(--success);
        box-shadow: 0 0 15px rgba(57,217,138,.35);
    }

    .stage-active {
        background: #7c5cff;
        box-shadow: 0 0 16px rgba(124,92,255,.65);
    }

    .stage-pending {
        background: #30394b;
    }

    .stage-text {
        font-size: 13px;
    }

    .stage-muted {
        color: var(--muted);
    }

    /* Report */

    .report {
        background: rgba(13,19,33,.72);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 30px;
    }

    /* Buttons */

    .stButton > button {
        border-radius: 13px !important;
        border: 1px solid rgba(255,255,255,.10) !important;
        font-weight: 700 !important;
        min-height: 46px !important;
        transition: all .2s ease !important;
    }

    .stButton > button:hover {
        border-color: rgba(124,92,255,.55) !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 30px rgba(124,92,255,.16);
    }

    /* Text area */

    textarea {
        border-radius: 17px !important;
    }

    /* Hide Streamlit branding */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🔬</div>
            <div>
                <div class="brand-title">ResearchOS AI</div>
                <div class="brand-subtitle">Multi-Agent Research Lab</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ Model")

    selected_model = st.selectbox(
        "Groq model",
        list(MODEL_OPTIONS.keys()),
        index=list(MODEL_OPTIONS.keys()).index(
            st.session_state.selected_model
        ),
        label_visibility="collapsed",
    )

    st.session_state.selected_model = selected_model

    st.caption(
        f"Model ID: `{model_id(selected_model)}`"
    )

    st.success("Groq API configured through Streamlit Secrets")

    st.divider()

    st.markdown("### 🧠 Research Team")

    for stage in AGENT_STAGES:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:9px;
                padding:7px 0;
                color:#9aa6ba;
                font-size:13px;
            ">
                <span style="font-size:15px;">●</span>
                <span>{stage}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        """
        <div style="
            color:#738097;
            font-size:11px;
            line-height:1.6;
        ">
        CrewAI orchestration<br>
        Groq inference<br>
        Open research sources
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI RESEARCH OPERATIONS</div>
        <h1>Research, coordinated.</h1>
        <p>
            Five specialized AI agents investigate your question,
            gather web and academic evidence, verify findings,
            and synthesize everything into one research report.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INPUT
# ============================================================

st.markdown("### What should the team investigate?")

research_question = st.text_area(
    "Research question",
    placeholder=(
        "Example: How is generative AI changing software engineering "
        "jobs, and what skills will become more important?"
    ),
    height=130,
    label_visibility="collapsed",
)


col1, col2 = st.columns([5, 1])

with col2:
    start = st.button(
        "🚀 Start Research",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# RESEARCH EXECUTION
# ============================================================

if start:

    if not research_question.strip():
        st.warning("Please enter a research question first.")
        st.stop()

    st.session_state.research_started = True
    st.session_state.result = None

    progress_box = st.empty()
    working_box = st.empty()
    timeline_box = st.empty()

    started_at = time.time()

    try:
        llm = create_llm(
            st.session_state.selected_model
        )

        crew = create_research_crew(llm)

        progress = 0

        for index, stage in enumerate(AGENT_STAGES):

            progress = int(
                (index / len(AGENT_STAGES)) * 100
            )

            working_box.markdown(
                f"""
                <div class="working">
                    <div class="pulse"></div>
                    <div>
                        <div class="working-title">
                            CURRENTLY WORKING
                        </div>
                        <div class="working-agent">
                            {stage}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            timeline_html = ""

            for j, item in enumerate(AGENT_STAGES):

                if j < index:
                    dot_class = "stage-done"
                    text_class = ""
                    symbol = "✓"

                elif j == index:
                    dot_class = "stage-active"
                    text_class = ""
                    symbol = "●"

                else:
                    dot_class = "stage-pending"
                    text_class = "stage-muted"
                    symbol = "○"

                timeline_html += f"""
                <div class="stage">
                    <div
                        class="stage-dot {dot_class}"
                    ></div>
                    <div class="stage-text {text_class}">
                        {symbol}&nbsp;&nbsp;{item}
                    </div>
                </div>
                """

            timeline_box.markdown(
                f"""
                <div class="card">
                    <div class="metric-label">
                        RESEARCH PIPELINE
                    </div>
                    {timeline_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

            progress_box.progress(
                min(progress + 5, 95),
                text=f"Research pipeline · {min(progress + 5, 95)}%",
            )

            # This delay makes the status visible in the UI.
            # CrewAI itself executes the actual work below.
            if index == 0:
                time.sleep(0.4)

        working_box.markdown(
            """
            <div class="working">
                <div class="pulse"></div>
                <div>
                    <div class="working-title">
                        CURRENTLY WORKING
                    </div>
                    <div class="working-agent">
                        Research Writer · Final synthesis
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        result = crew.kickoff(
            inputs={
                "research_question": research_question.strip()
            }
        )

        elapsed = time.time() - started_at

        st.session_state.result = str(result)
        st.session_state.research_time = elapsed

        progress_box.progress(
            100,
            text="Research complete · 100%",
        )

        working_box.markdown(
            """
            <div class="working">
                <div
                    style="
                        width:11px;
                        height:11px;
                        border-radius:50%;
                        background:#39d98a;
                    "
                ></div>
                <div>
                    <div class="working-title">
                        STATUS
                    </div>
                    <div class="working-agent">
                        Research team completed the investigation
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.success(
            f"Research completed in {elapsed:.1f} seconds."
        )

    except Exception as exc:

        progress_box.empty()

        st.error(
            "The research team could not complete the run."
        )

        with st.expander("Technical details"):
            st.code(str(exc))


# ============================================================
# RESULTS
# ============================================================

if st.session_state.result:

    st.divider()

    st.markdown("## Research Report")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(
            """
            <div class="card">
                <div class="metric-label">AGENTS</div>
                <div class="metric-value">5</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            f"""
            <div class="card">
                <div class="metric-label">MODEL</div>
                <div class="metric-value"
                     style="font-size:17px;">
                    {st.session_state.selected_model}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            f"""
            <div class="card">
                <div class="metric-label">RUN TIME</div>
                <div class="metric-value">
                    {st.session_state.research_time:.1f}s
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    st.markdown(
        '<div class="report">',
        unsafe_allow_html=True,
    )

    st.markdown(
        st.session_state.result
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇️ Download Research Report",
        data=st.session_state.result,
        file_name="research_report.md",
        mime="text/markdown",
        use_container_width=False,
    )
