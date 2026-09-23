"""utils/theme.py — Shared PPS4027 design-system CSS injector."""
import streamlit as st

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:ital,wght@0,400;0,500;1,400&display=swap');
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif;color:#191c1f;}
.block-container{padding-top:1.4rem!important;padding-bottom:2rem!important;max-width:1140px;}
[data-testid="stSidebar"]{background:#f2f3f7!important;border-right:1px solid #c2c7cd;}
[data-testid="stSidebar"] .stMarkdown p{color:#42474c;font-size:.8125rem;}
.pps-card{background:#fff;border:1px solid #c2c7cd;border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.pps-card-low{background:#f2f3f7;border:1px solid #c2c7cd;border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.pps-section-title{font-size:.6875rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#72787d;margin:0 0 .75rem 0;}
.pps-stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.75rem;margin-bottom:1rem;}
.pps-stat{background:#fff;border:1px solid #c2c7cd;border-radius:10px;padding:1rem 1.25rem;}
.pps-stat-label{font-size:.72rem;font-weight:600;color:#72787d;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.25rem;}
.pps-stat-value{font-size:1.9rem;font-weight:700;color:#191c1f;line-height:1.1;}
.pps-stat-sub{font-size:.73rem;color:#42474c;margin-top:.25rem;}
.badge{display:inline-flex;align-items:center;gap:.25rem;padding:.15rem .6rem;border-radius:999px;font-size:.72rem;font-weight:600;line-height:1.6;white-space:nowrap;}
.badge-complete{background:#d1fae5;color:#065f46;}
.badge-pending{background:#e7e8ec;color:#42474c;}
.badge-waiting{background:#fef3c7;color:#92400e;}
.badge-error{background:#ffdad6;color:#ba1a1a;}
.badge-active{background:#c3e4fe;color:#315369;}
.badge-new{background:#c3e4fe;color:#436278;}
.badge-primary{background:#315369;color:#fff;}
.badge-notopen{background:#e7e8ec;color:#72787d;}
.pps-steps{display:flex;align-items:center;flex-wrap:wrap;margin-bottom:1.5rem;}
.pps-step{display:flex;align-items:center;gap:.4rem;font-size:.73rem;font-weight:600;color:#72787d;padding:.4rem .9rem;background:#f2f3f7;border:1px solid #c2c7cd;border-right:none;}
.pps-step:first-child{border-radius:6px 0 0 6px;}
.pps-step:last-child{border-radius:0 6px 6px 0;border-right:1px solid #c2c7cd;}
.pps-step.done{background:#e7e8ec;color:#42474c;}
.pps-step.active{background:#315369;color:#fff;border-color:#315369;}
.pps-step-num{width:18px;height:18px;border-radius:50%;background:rgba(255,255,255,.25);display:inline-flex;align-items:center;justify-content:center;font-size:.65rem;}
.pps-step.done .pps-step-num{background:#d1fae5;color:#065f46;}
.pps-score-row{display:flex;align-items:center;gap:.75rem;margin-bottom:.85rem;}
.pps-score-label{font-size:.82rem;font-weight:500;color:#191c1f;width:150px;flex-shrink:0;}
.pps-score-bar-bg{flex:1;height:8px;background:#e7e8ec;border-radius:99px;overflow:hidden;}
.pps-score-bar-fill{height:100%;background:#4a6b82;border-radius:99px;}
.pps-score-val{font-size:.82rem;font-weight:700;color:#191c1f;width:48px;text-align:right;}
.pps-row{display:flex;align-items:center;gap:.75rem;padding:.6rem 0;border-bottom:1px solid #e7e8ec;}
.pps-row:last-child{border-bottom:none;}
.pps-row-icon{width:32px;height:32px;border-radius:8px;background:#eceef2;display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0;}
.pps-row-main{flex:1;min-width:0;}
.pps-row-title{font-size:.875rem;font-weight:600;color:#191c1f;}
.pps-row-sub{font-size:.75rem;color:#42474c;}
.signin-wrap{display:flex;min-height:86vh;border-radius:14px;overflow:hidden;border:1px solid #c2c7cd;background:#fff;box-shadow:0 4px 24px rgba(0,0,0,.07);}
.signin-left{flex:0 0 38%;background:#f2f3f7;padding:2.5rem 2rem;display:flex;flex-direction:column;gap:1.5rem;border-right:1px solid #c2c7cd;}
.signin-right{flex:1;padding:2.5rem 2.5rem;display:flex;flex-direction:column;justify-content:center;gap:1rem;}
.signin-brand-chip{display:inline-flex;align-items:center;gap:.4rem;background:#c3e4fe;color:#315369;padding:.25rem .75rem;border-radius:6px;font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;}
.signin-headline{font-family:'Newsreader',Georgia,serif;font-size:1.9rem;font-weight:400;color:#191c1f;line-height:1.25;margin:.5rem 0 .25rem;}
.signin-sub{font-size:.875rem;color:#42474c;line-height:1.6;}
.signin-notice{background:#eceef2;border-radius:8px;padding:.75rem 1rem;font-size:.8rem;color:#42474c;border-left:3px solid #436278;margin:.25rem 0;}
.signin-footer{font-size:.72rem;color:#72787d;line-height:1.5;border-top:1px solid #c2c7cd;padding-top:.75rem;margin-top:auto;}
.pps-announce{background:#f2f3f7;border:1px solid #c2c7cd;border-left:4px solid #436278;border-radius:8px;padding:.85rem 1rem;font-size:.82rem;color:#42474c;margin-bottom:.75rem;}
.pps-announce strong{color:#191c1f;}
.pps-page-head{border-bottom:1px solid #c2c7cd;padding-bottom:1rem;margin-bottom:1.25rem;}
.pps-page-title{font-family:'Newsreader',Georgia,serif;font-size:1.7rem;font-weight:400;color:#191c1f;margin:0 0 .25rem;}
.pps-page-sub{font-size:.875rem;color:#42474c;}
.pps-consent{background:#f2f3f7;border:1px solid #c2c7cd;border-radius:10px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.pps-consent-title{font-weight:600;font-size:.95rem;color:#191c1f;margin-bottom:.5rem;}
.pps-consent-body{font-size:.82rem;color:#42474c;line-height:1.6;}
.pps-info-item{display:flex;gap:.75rem;align-items:flex-start;padding:.9rem 0;border-bottom:1px solid #e7e8ec;}
.pps-info-item:last-child{border-bottom:none;}
.pps-info-icon{width:36px;height:36px;border-radius:9px;background:#eceef2;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:1rem;}
.pps-info-title{font-size:.875rem;font-weight:600;color:#191c1f;}
.pps-info-desc{font-size:.78rem;color:#42474c;line-height:1.5;margin-top:.2rem;}
.pps-greeting{margin-bottom:1.25rem;}
.pps-greeting-hi{font-family:'Newsreader',Georgia,serif;font-size:1.6rem;font-weight:400;color:#191c1f;}
.pps-greeting-sub{font-size:.82rem;color:#42474c;margin-top:.15rem;}
.pps-tag{display:inline-block;padding:.1rem .5rem;border-radius:4px;font-size:.72rem;font-weight:500;background:#eceef2;color:#42474c;margin:.1rem .15rem;}
</style>"""


def inject_css():
    """Inject the shared design-system CSS into the current page."""
    st.markdown(_CSS, unsafe_allow_html=True)


def stat_card(label: str, value: str, sub: str = "") -> str:
    sub_html = f"<div class='pps-stat-sub'>{sub}</div>" if sub else ""
    return (
        f"<div class='pps-stat'>"
        f"<div class='pps-stat-label'>{label}</div>"
        f"<div class='pps-stat-value'>{value}</div>"
        f"{sub_html}</div>"
    )


def stat_grid(*cards: str) -> None:
    st.markdown(
        f"<div class='pps-stat-grid'>{''.join(cards)}</div>",
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str = "pending") -> str:
    return f"<span class='badge badge-{kind}'>{text}</span>"


def score_bar(label: str, score: int) -> str:
    pct = max(0, min(100, score))
    return (
        f"<div class='pps-score-row'>"
        f"<div class='pps-score-label'>{label}</div>"
        f"<div class='pps-score-bar-bg'>"
        f"<div class='pps-score-bar-fill' style='width:{pct}%'></div>"
        f"</div><div class='pps-score-val'>{score}/100</div></div>"
    )


def step_strip(steps: list) -> None:
    html = "<div class='pps-steps'>"
    for i, (label, state) in enumerate(steps, 1):
        icon = "&#10003;" if state == "done" else str(i)
        html += (
            f"<div class='pps-step {state}'>"
            f"<span class='pps-step-num'>{icon}</span>{label}</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<div class='pps-page-sub'>{subtitle}</div>" if subtitle else ""
    st.markdown(
        f"<div class='pps-page-head'><div class='pps-page-title'>{title}</div>{sub}</div>",
        unsafe_allow_html=True,
    )


def greeting(name: str, sub: str = "") -> None:
    s = f"<div class='pps-greeting-sub'>{sub}</div>" if sub else ""
    st.markdown(
        f"<div class='pps-greeting'><div class='pps-greeting-hi'>Good day, {name}</div>{s}</div>",
        unsafe_allow_html=True,
    )


def announce(message: str, bold_prefix: str = "") -> None:
    p = f"<strong>{bold_prefix}</strong> " if bold_prefix else ""
    st.markdown(
        f"<div class='pps-announce'>{p}{message}</div>",
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(
        f"<div class='pps-section-title'>{text}</div>",
        unsafe_allow_html=True,
    )
