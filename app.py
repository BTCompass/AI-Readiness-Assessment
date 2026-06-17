import streamlit as st
import json
from pathlib import Path

BASE = Path(__file__).parent
RUBRIC = json.loads((BASE / "specs/rubric.json").read_text())
QUESTION_BANK = json.loads((BASE / "scoring/question_bank.json").read_text())

STATED_LEVEL_SCORES = {
    "none": 1.0, "vague": 1.5, "partial": 2.5, "defined": 3.5, "specific_with_metrics": 4.5,
}
DISPLAY_OPTIONS = {
    "Not yet in place": "none",
    "Discussed but not defined": "vague",
    "Partially defined": "partial",
    "Clearly defined": "defined",
    "Defined with specific metrics": "specific_with_metrics",
}
DOMAIN_IDS = [
    "strategic_intent_use_case_scope",
    "data_readiness_governance",
    "infrastructure_architecture_readiness",
    "security_privacy_compliance",
    "ai_governance_operating_model",
    "workflow_adoption_change_readiness",
    "procurement_vendor_readiness",
    "budget_investment_readiness",
]
CRITICAL_GATING = {"security_privacy_compliance", "data_readiness_governance", "ai_governance_operating_model"}
SECONDARY_GATING = {"infrastructure_architecture_readiness", "procurement_vendor_readiness", "budget_investment_readiness"}


def _build_domain_questions():
    qb_domains = QUESTION_BANK["domains"]
    result = {}
    for i, domain_id in enumerate(DOMAIN_IDS):
        dom = qb_domains.get(f"domain_{i+1}", {})
        qs = dom.get("questions", {})
        result[domain_id] = {
            "name": dom.get("name", domain_id),
            "questions": [
                {"signal_id": q["signal_id"], "signal_name": q["signal_name"], "question": q["question"]}
                for q in list(qs.values())[:2]
            ],
        }
    return result


def _color(score):
    if score <= 2.4:
        return "Red"
    if score <= 3.4:
        return "Yellow"
    return "Green"


def _decision_readiness_status(domain_scores):
    colors = {d: s["color"] for d, s in domain_scores.items()}
    critical_red = any(colors.get(d) == "Red" for d in CRITICAL_GATING)
    secondary_red = any(colors.get(d) == "Red" for d in SECONDARY_GATING)
    total_red = sum(1 for c in colors.values() if c == "Red")
    total_green = sum(1 for c in colors.values() if c == "Green")
    critical_evidence_ok = all(
        domain_scores.get(d, {}).get("evidence_confidence_score", 0) >= 3 for d in CRITICAL_GATING
    )
    if critical_red or total_red >= 2:
        key = "1_not_ready"
    elif not critical_red and (total_red >= 1 or total_green <= 2):
        key = "2_ready_internal_alignment"
    elif not critical_red and not secondary_red and total_red == 0 and total_green <= 3:
        key = "3_ready_vendor_discovery"
    elif not critical_red and not secondary_red and total_red == 0 and critical_evidence_ok and total_green >= 6:
        key = "7_ready_for_rfp"
    elif not critical_red and total_green >= 5:
        key = "6_ready_enterprise_planning"
    elif not critical_red and not secondary_red and total_green >= 3:
        key = "5_ready_service_line_scale"
    else:
        key = "4_ready_targeted_pilot"
    status = RUBRIC["decision_readiness_statuses"][key]
    warnings = []
    if critical_red:
        warnings.append(RUBRIC["gating_model"]["critical_gating_domains"]["red_override_message"])
    if secondary_red:
        warnings.append(RUBRIC["gating_model"]["secondary_gating_domains"]["red_override_message"])
    return {
        "label": status["label"],
        "guidance": status["guidance"],
        "allowed_next_steps": status["allowed_next_steps"],
        "gating_warnings": warnings,
    }


def score_responses(responses):
    domain_scores = {}
    for domain_id in DOMAIN_IDS:
        signals = responses.get(domain_id, {})
        if not signals:
            domain_scores[domain_id] = {"readiness_score": 1.0, "evidence_confidence_score": 0.0, "color": "Red"}
            continue
        scores = [STATED_LEVEL_SCORES.get(level, 1.0) for level in signals.values()]
        avg = sum(scores) / len(scores)
        domain_scores[domain_id] = {
            "readiness_score": round(avg, 2),
            "evidence_confidence_score": 0.0,
            "color": _color(avg),
        }
    return domain_scores, _decision_readiness_status(domain_scores)


# ── UI ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="BT Compass Assessment", page_icon="🧭", layout="wide")

st.title("🧭 BT Compass AI Infrastructure Assessment")
st.caption("Health AI Readiness for CIOs · breakthroughcompass.com")

with st.sidebar:
    st.header("About Your Organization")
    org_name = st.text_input("Health System Name", placeholder="e.g. Atlantic Health System")
    operator_role = st.text_input("Your Role", placeholder="e.g. VP of IT Infrastructure")
    st.selectbox("Primary EHR", ["Epic", "Cerner / Oracle Health", "Meditech", "CPSI", "Other"])
    st.selectbox("Primary Cloud", ["Azure", "AWS", "Google Cloud", "On-premise", "Hybrid / Mixed"])
    st.divider()
    st.caption(
        "BT Compass scores AI readiness across 8 domains using a deterministic rubric "
        "aligned to NIST AI RMF, WHO Ethics, and CHAI Blueprint standards."
    )

DOMAINS = _build_domain_questions()
SCALE_OPTIONS = list(DISPLAY_OPTIONS.keys())
COLOR_EMOJI = {"Red": "🔴", "Yellow": "🟡", "Green": "🟢"}

st.markdown("### Complete each section, then click **Run Assessment** at the bottom.")
st.markdown("*Critical Gate domains (marked 🔴) can block decision-readiness regardless of other scores.*")
st.markdown("---")

responses = {}
for domain_id in DOMAIN_IDS:
    dom = DOMAINS[domain_id]
    if domain_id in CRITICAL_GATING:
        badge = "  🔴 *Critical Gate*"
    elif domain_id in SECONDARY_GATING:
        badge = "  🟡 *Secondary Gate*"
    else:
        badge = ""

    with st.expander(f"**{dom['name']}**{badge}", expanded=True):
        responses[domain_id] = {}
        for q in dom["questions"]:
            choice = st.selectbox(
                f"**{q['signal_name']}** — {q['question']}",
                SCALE_OPTIONS,
                key=f"{domain_id}_{q['signal_id']}",
            )
            responses[domain_id][q["signal_id"]] = DISPLAY_OPTIONS[choice]

st.markdown("---")

if st.button("🧭 Run Assessment", type="primary", use_container_width=True):
    if not org_name:
        st.warning("Please enter your Health System Name in the sidebar before running.")
    else:
        domain_scores, decision = score_responses(responses)

        st.markdown(f"## Results — {org_name}")
        st.markdown(f"*Role: {operator_role}*" if operator_role else "")

        # Decision-readiness status
        st.markdown("### Decision-Readiness Status")
        label = decision["label"]
        guidance = decision["guidance"]

        not_ready_labels = {"Not Ready", "Ready for Internal Alignment"}
        if label in not_ready_labels:
            st.error(f"**{label}**\n\n{guidance}")
        elif "Discovery" in label or "Pilot" in label:
            st.warning(f"**{label}**\n\n{guidance}")
        else:
            st.success(f"**{label}**\n\n{guidance}")

        for warning in decision.get("gating_warnings", []):
            st.warning(f"⚠️ {warning}")

        col_steps, col_spacer = st.columns([2, 1])
        with col_steps:
            st.markdown("**Recommended Next Steps:**")
            for step in decision.get("allowed_next_steps", []):
                st.markdown(f"- {step}")

        # Domain scorecard
        st.markdown("---")
        st.markdown("### Domain Scorecard")

        header = st.columns([4, 1, 1, 2])
        header[0].markdown("**Domain**")
        header[1].markdown("**Score**")
        header[2].markdown("**Status**")
        header[3].markdown("**Gate Type**")
        st.markdown("---")

        for domain_id in DOMAIN_IDS:
            ds = domain_scores[domain_id]
            dom = DOMAINS[domain_id]
            color = ds["color"]
            emoji = COLOR_EMOJI[color]

            if domain_id in CRITICAL_GATING:
                gate = "Critical"
            elif domain_id in SECONDARY_GATING:
                gate = "Secondary"
            else:
                gate = "—"

            row = st.columns([4, 1, 1, 2])
            row[0].write(dom["name"])
            row[1].write(f"{ds['readiness_score']:.1f} / 5.0")
            row[2].write(f"{emoji} {color}")
            row[3].write(gate)

        st.markdown("---")
        st.caption(
            "Scored by BT Compass deterministic rubric engine · "
            "Evidence confidence scoring requires document upload, available in the full assessment."
        )
