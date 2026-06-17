import streamlit as st
import json
from pathlib import Path
from datetime import date

BASE = Path(__file__).parent
RUBRIC = json.loads((BASE / "specs/rubric.json").read_text())
QUESTION_BANK = json.loads((BASE / "scoring/question_bank.json").read_text())
SIGNAL_OPTIONS = json.loads((BASE / "scoring/signal_options.json").read_text())

# Overrides for signals where the interview question doesn't describe what's being rated
FORM_HINTS = {
    "s1_1": "Rate how specifically your target AI use cases are defined, scoped, and prioritized",
    "s1_2": "Rate the formality and authority of executive sponsorship for this AI initiative",
    "s1_3": "Rate how well your stated AI ambition matches your organization's actual capacity, budget, and capabilities",
    "s1_4": "Rate whether measurable success metrics are defined for your AI initiative",
    "s1_5": "How defined is the implementation timeline and urgency drivers for this AI initiative?",
    "s2_2": "Rate the quality of your data for the domains required by your AI use cases",
    "s2_3": "Rate your interoperability maturity — FHIR/HL7 standards, API capabilities, and cross-system data exchange",
    "s3_3": "Rate your network infrastructure's readiness for AI workloads — bandwidth, latency for real-time inference, and security segmentation",
    "s3_5": "Rate your infrastructure's readiness for scalable AI workload growth AND disaster recovery / business continuity coverage of AI-dependent clinical workflows",
    "s4_3": "Rate the maturity of your AI-specific incident response readiness and cybersecurity posture",
    "s4_4": "Rate how thoroughly your regulatory compliance requirements have been assessed for AI workloads — including cloud-based AI processing, third-party model training restrictions, and FDA AI/ML guidance (this is an assessment of readiness, not a compliance certification)",
    "s4_5": "Rate your requirements around how AI vendors may USE, store, and share your data — training restrictions, retention limits, residency, and subprocessor controls",
    "s4_6": "Rate your vendor contract requirements around security controls, SLAs, penetration testing rights, and breach notification — distinct from data-use restrictions",
    "s7_2": "Rate how well-defined your AI infrastructure requirements are before vendor conversations begin",
    "s7_3": "Rate your organization's competency to evaluate AI vendors — including formal scoring criteria, reference checks, and ability to design and run vendor proof-of-concepts",
    "s8_1": "Rate whether a realistic budget is allocated, approved, or fundable — covering licensing, implementation, integration, training, and ongoing operations",
    "s8_2": "Rate how well your available budget matches your stated AI ambition",
    "s8_3": "Rate how comprehensively your budget model accounts for total cost of ownership — licensing, implementation, integration, training, ongoing operations, support, and technology refresh",
}

NA_OPTION = "Not applicable — this area has not been assessed or does not apply to our organization"

STATED_LEVEL_SCORES = {
    "none": 1.0, "vague": 1.5, "partial": 2.5, "defined": 3.5, "specific_with_metrics": 4.5,
}
LEVEL_KEYS = ["none", "vague", "partial", "defined", "specific_with_metrics"]
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
PHI_ATTESTATION_TEXT = QUESTION_BANK["metadata"]["safety_attestation_text"]


def _truncate(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


def _build_domain_questions():
    qb_domains = QUESTION_BANK["domains"]
    result = {}
    for i, domain_id in enumerate(DOMAIN_IDS):
        dom = qb_domains.get(f"domain_{i+1}", {})
        qs = dom.get("questions", {})
        result[domain_id] = {
            "name": dom.get("name", domain_id),
            "questions": [
                {
                    "signal_id": q["signal_id"],
                    "signal_name": q["signal_name"],
                    "hint": FORM_HINTS.get(q["signal_id"]) or _truncate(q["question"].split("?")[0], 160),
                    "evidence_types": q.get("evidenceValidation", {}).get("acceptedEvidenceTypes", []),
                }
                for q in qs.values()
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


def score_responses(responses, domain_evidence, phi_confirmed):
    domain_scores = {}
    for domain_id in DOMAIN_IDS:
        signals = responses.get(domain_id, {})
        has_evidence = domain_evidence.get(domain_id, False) and phi_confirmed
        if not signals:
            domain_scores[domain_id] = {"readiness_score": 1.0, "evidence_confidence_score": 0.0, "color": "Red"}
            continue
        readiness_scores = [STATED_LEVEL_SCORES.get(str(level), 1.0) for level in signals.values()]
        readiness_avg = sum(readiness_scores) / len(readiness_scores)
        evidence_avg = 3.0 if has_evidence else 0.0
        gap = readiness_avg - evidence_avg
        color = _color(readiness_avg)
        if color == "Green" and gap > 2.0:
            color = "Yellow"
        domain_scores[domain_id] = {
            "readiness_score": round(readiness_avg, 2),
            "evidence_confidence_score": round(evidence_avg, 2),
            "color": color,
        }
    return domain_scores, _decision_readiness_status(domain_scores)


def generate_gamma_prompt(org_name, operator_role, ehr, cloud, domain_scores, decision, responses):
    today = date.today().strftime("%B %Y")
    CE = {"Red": "🔴", "Yellow": "🟡", "Green": "🟢"}

    def gate_label(d):
        if d in CRITICAL_GATING: return "Critical Gate"
        if d in SECONDARY_GATING: return "Secondary Gate"
        return "—"

    def ev_label(d):
        return "✅ Supported" if domain_scores[d].get("evidence_confidence_score", 0) >= 3 else "⚠️ Self-reported"

    def answer_text(signal_id, level_key):
        opts = SIGNAL_OPTIONS.get(signal_id, [])
        idx = LEVEL_KEYS.index(level_key) if level_key in LEVEL_KEYS else 0
        return opts[idx] if idx < len(opts) else level_key

    def signal_emoji(level):
        return "🟢" if level in ("defined", "specific_with_metrics") else ("🟡" if level == "partial" else "🔴")

    L = []

    def line(s=""): L.append(s)
    def slide_break(): L.extend(["", "---", ""])

    # Theme instruction
    line("Create a professional presentation. Dark, modern theme. Healthcare enterprise aesthetic. Clean data visualization. Use icons, callout boxes, and color-coded indicators where appropriate. No clip art.")
    slide_break()

    # Slide 1 — Title
    line(f"# {org_name}")
    line("## AI Infrastructure Readiness Assessment")
    line(f"### IT Lead Findings Brief · {today}")
    if operator_role:
        line(f"### Prepared for: {operator_role}")
    slide_break()

    # Slide 2 — Assessment Overview
    label = decision["label"]
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1]["readiness_score"])
    worst = DOMAINS[sorted_domains[0][0]]["name"]
    best = DOMAINS[sorted_domains[-1][0]]["name"]
    line("# Assessment Overview")
    line("")
    line(f"Scored {org_name}'s AI infrastructure readiness across 8 domains against NIST AI RMF, WHO Ethics, and CHAI Blueprint standards.")
    line("")
    line("| | |")
    line("|---|---|")
    line(f"| **Decision-Readiness Status** | **{label}** |")
    line(f"| **EHR Platform** | {ehr} |")
    line(f"| **Primary Cloud** | {cloud} |")
    line(f"| **Biggest Strength** | {best} |")
    line(f"| **Biggest Blocker** | {worst} |")
    line("")
    line(f"> {decision['guidance']}")
    slide_break()

    # Slide 3 — Domain Scorecard
    line("# Domain Scorecard")
    line("")
    line("| Domain | Score | Status | Evidence | Gate |")
    line("|---|---|---|---|---|")
    for d in DOMAIN_IDS:
        ds = domain_scores[d]
        line(f"| {DOMAINS[d]['name']} | {ds['readiness_score']:.1f} / 5.0 | {CE[ds['color']]} {ds['color']} | {ev_label(d)} | {gate_label(d)} |")
    slide_break()

    # Conditional Slide A — Gating (if any critical gate is Red)
    red_critical = [d for d in CRITICAL_GATING if domain_scores.get(d, {}).get("color") == "Red"]
    red_secondary = [d for d in SECONDARY_GATING if domain_scores.get(d, {}).get("color") == "Red"]
    if red_critical:
        line("# Gating Rules — Action Required")
        line("")
        line("**These critical gate domains scored Red. No vendor engagement, RFP, or procurement is permitted until resolved.**")
        line("")
        for d in red_critical:
            line(f"- 🔴 **{DOMAINS[d]['name']}** — Critical Gate · Score: {domain_scores[d]['readiness_score']:.1f} / 5.0")
        for d in red_secondary:
            line(f"- 🟡 **{DOMAINS[d]['name']}** — Secondary Gate · Score: {domain_scores[d]['readiness_score']:.1f} / 5.0")
        line("")
        for w in decision.get("gating_warnings", []):
            line(f"> ⚠️ {w}")
        slide_break()

    # Slides 4–11 — One per domain
    for i, domain_id in enumerate(DOMAIN_IDS):
        ds = domain_scores[domain_id]
        dom = DOMAINS[domain_id]
        line(f"# Domain {i + 1}: {dom['name']}")
        line(f"## {gate_label(domain_id)} · {CE[ds['color']]} {ds['color']} · {ds['readiness_score']:.1f} / 5.0 · {ev_label(domain_id)}")
        line("")
        for q in dom["questions"]:
            level = responses.get(domain_id, {}).get(q["signal_id"], "none")
            text = answer_text(q["signal_id"], level)
            line(f"- {signal_emoji(level)} **{q['signal_name']}:** {text}")
        slide_break()

    # Slide 12 — Credibility Gap
    line("# Credibility Gap & Evidence Priorities")
    line("")
    line("| Domain | Readiness | Evidence | Gap | Interpretation |")
    line("|---|---|---|---|---|")
    for d in DOMAIN_IDS:
        ds = domain_scores[d]
        gap = ds["readiness_score"] - ds["evidence_confidence_score"]
        if gap > 2.0: interp = "High Self-Report Risk"
        elif gap > 1.2: interp = "Material Evidence Gap"
        elif gap > 0.5: interp = "Some Validation Needed"
        else: interp = "Well-Supported"
        line(f"| {DOMAINS[d]['name']} | {ds['readiness_score']:.1f} | {ds['evidence_confidence_score']:.1f} | {gap:.1f} | {interp} |")
    slide_break()

    # Slide 13 — Recommended Path
    line("# Recommended Path")
    line(f"## Decision-Readiness Status: {label}")
    line("")
    line(decision["guidance"])
    line("")
    line("**Allowed next steps:**")
    for step in decision.get("allowed_next_steps", []):
        line(f"- {step}")
    slide_break()

    # Slide 14 — Disclaimer
    line("# Scope & Disclaimer")
    line("")
    line("**What this assessment cannot determine:**")
    line("- Legal or regulatory compliance status")
    line("- Clinical safety or efficacy of any AI tool")
    line("- Vendor pricing or availability")
    line("")
    line(f"*{org_name} · BT Compass AI Infrastructure Assessment · {today}*")
    line("*For internal planning purposes only. Not legal, clinical, compliance, or procurement advice.*")

    return "\n".join(L)


# ── UI ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="BT Compass Assessment", page_icon="🧭", layout="wide")

st.title("🧭 BT Compass AI Infrastructure Assessment")
st.caption("Health AI Readiness for CIOs · breakthroughcompass.com")

with st.sidebar:
    st.header("About Your Organization")
    org_name = st.text_input("Health System Name", placeholder="e.g. Atlantic Health System")
    operator_role = st.text_input("Your Role", placeholder="e.g. VP of IT Infrastructure")
    ehr = st.selectbox("Primary EHR", ["Epic", "Cerner / Oracle Health", "Meditech", "CPSI", "Other"])
    cloud = st.selectbox("Primary Cloud", ["Azure", "AWS", "Google Cloud", "On-premise", "Hybrid / Mixed"])
    st.divider()
    st.caption(
        "BT Compass scores AI readiness across 8 domains using a deterministic rubric "
        "aligned to NIST AI RMF, WHO Ethics, and CHAI Blueprint standards."
    )

DOMAINS = _build_domain_questions()
COLOR_EMOJI = {"Red": "🔴", "Yellow": "🟡", "Green": "🟢"}

st.markdown("### Complete each section, then click **Run Assessment** at the bottom.")
st.markdown("*Critical Gate domains (marked 🔴) can block decision-readiness regardless of other scores.*")

# PHI attestation — required before evidence uploads are enabled
st.markdown("---")
phi_confirmed = st.checkbox(
    f"**Evidence upload attestation:** {PHI_ATTESTATION_TEXT}",
    value=False,
    help="You must confirm this before uploading any supporting documents.",
)
if phi_confirmed:
    st.success("Attestation confirmed. You may upload supporting evidence in each domain below.")
else:
    st.info("Check the box above to enable evidence uploads. Evidence improves your score confidence.")
st.markdown("---")

responses = {}
domain_evidence = {}

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
            options = SIGNAL_OPTIONS.get(q["signal_id"], [
                "Not in place",
                "Informal — discussed but not documented",
                "Partially in place — some elements exist",
                "Formally defined and documented",
                "Formally defined with measurable targets or metrics",
            ]) + [NA_OPTION]
            choice_idx = st.selectbox(
                f"**{q['signal_name']}**  \n*{q['hint']}*",
                range(len(options)),
                format_func=lambda i, opts=options: opts[i],
                key=f"{domain_id}_{q['signal_id']}",
            )
            responses[domain_id][q["signal_id"]] = LEVEL_KEYS[choice_idx] if choice_idx < len(LEVEL_KEYS) else "none"

        # Evidence upload for this domain
        st.markdown("---")
        all_evidence_types = []
        for q in dom["questions"]:
            all_evidence_types.extend(q["evidence_types"])
        unique_types = list(dict.fromkeys(all_evidence_types))

        if phi_confirmed:
            uploaded = st.file_uploader(
                "Upload supporting evidence for this domain (optional — redacted documents only)",
                key=f"upload_{domain_id}",
                accept_multiple_files=False,
                help="Accepted: " + " · ".join(unique_types[:4]),
            )
            domain_evidence[domain_id] = uploaded is not None
            if unique_types:
                st.caption("Accepted evidence: " + "  ·  ".join(unique_types))
        else:
            st.caption("*Enable evidence uploads by confirming the attestation above.*")
            domain_evidence[domain_id] = False

st.markdown("---")

if st.button("🧭 Run Assessment", type="primary", use_container_width=True):
    if not org_name:
        st.warning("Please enter your Health System Name in the sidebar before running.")
    else:
        domain_scores, decision = score_responses(responses, domain_evidence, phi_confirmed)
        st.session_state["results"] = {
            "org_name": org_name, "operator_role": operator_role, "ehr": ehr, "cloud": cloud,
            "domain_scores": domain_scores, "decision": decision, "responses": responses,
        }

        st.markdown(f"## Results — {org_name}")
        if operator_role:
            st.markdown(f"*{operator_role}  ·  {ehr}  ·  {cloud}*")

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

        header = st.columns([4, 1, 1, 1, 2])
        header[0].markdown("**Domain**")
        header[1].markdown("**Score**")
        header[2].markdown("**Status**")
        header[3].markdown("**Evidence**")
        header[4].markdown("**Gate Type**")
        st.markdown("---")

        for domain_id in DOMAIN_IDS:
            ds = domain_scores[domain_id]
            dom = DOMAINS[domain_id]
            color = ds["color"]
            emoji = COLOR_EMOJI[color]
            ev_score = ds.get("evidence_confidence_score", 0.0)
            ev_label = "Supported" if ev_score >= 3.0 else "Self-reported"

            if domain_id in CRITICAL_GATING:
                gate = "Critical"
            elif domain_id in SECONDARY_GATING:
                gate = "Secondary"
            else:
                gate = "—"

            row = st.columns([4, 1, 1, 1, 2])
            row[0].write(dom["name"])
            row[1].write(f"{ds['readiness_score']:.1f} / 5.0")
            row[2].write(f"{emoji} {color}")
            row[3].write(ev_label)
            row[4].write(gate)

        st.markdown("---")
        st.caption(
            "Scored by BT Compass deterministic rubric engine · "
            "NIST AI RMF · WHO Ethics · CHAI Blueprint · breakthroughcompass.com"
        )

# ── Gamma Button — shown after any completed assessment ──────────────────────
if "results" in st.session_state:
    r = st.session_state["results"]
    st.markdown("---")
    st.markdown("### Generate Board Presentation")
    st.markdown("Paste the output below directly into **[Gamma.app](https://gamma.app)** to generate a slide deck from your assessment results.")
    if st.button("📊 Generate Gamma Presentation Outline", use_container_width=True):
        gamma_text = generate_gamma_prompt(
            r["org_name"], r["operator_role"], r["ehr"], r["cloud"],
            r["domain_scores"], r["decision"], r["responses"],
        )
        st.text_area("Gamma-ready outline — copy and paste into Gamma.app", gamma_text, height=400)
        st.caption("In Gamma.app: click 'Create new' → 'Paste in text' → paste this outline → Generate.")
