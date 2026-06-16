"""
BT Compass AI Infrastructure Assessment — MCP Server
Deterministic scoring engine + question bank + reference library
"""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BT Compass Assessment")

BASE = Path(__file__).parent.parent
RUBRIC = json.loads((BASE / "specs/rubric.json").read_text())
QUESTION_BANK = json.loads((BASE / "scoring/question_bank.json").read_text())
REFERENCE_DIR = BASE / "reference_library"

# stated_level → numeric score
STATED_LEVEL_SCORES = {
    "none": 1.0,
    "vague": 1.5,
    "partial": 2.5,
    "defined": 3.5,
    "specific_with_metrics": 4.5,
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
STRATEGIC_ADOPTION = {"strategic_intent_use_case_scope", "workflow_adoption_change_readiness"}


def _color(score: float) -> str:
    if score <= 2.4:
        return "Red"
    if score <= 3.4:
        return "Yellow"
    return "Green"


def _credibility_gap_label(gap: float) -> str:
    if gap <= 0.5:
        return "Well-Supported"
    if gap <= 1.2:
        return "Some Validation Needed"
    if gap <= 2.0:
        return "Material Evidence Gap"
    return "High Self-Report Risk"


def _confidence_label(ratio: float) -> str:
    if ratio >= 0.8:
        return "High"
    if ratio >= 0.5:
        return "Medium"
    return "Low"


def _decision_readiness_status(domain_scores: dict) -> dict:
    colors = {d: s["color"] for d, s in domain_scores.items()}

    critical_red = any(colors.get(d) == "Red" for d in CRITICAL_GATING)
    secondary_red = any(colors.get(d) == "Red" for d in SECONDARY_GATING)
    total_red = sum(1 for c in colors.values() if c == "Red")
    total_green = sum(1 for c in colors.values() if c == "Green")
    strategic_red = any(colors.get(d) == "Red" for d in STRATEGIC_ADOPTION)

    critical_evidence_ok = all(
        domain_scores.get(d, {}).get("evidence_confidence_score", 0) >= 3
        for d in CRITICAL_GATING
    )

    if critical_red or total_red >= 2:
        status_key = "1_not_ready"
    elif not critical_red and (total_red >= 1 or total_green <= 2):
        status_key = "2_ready_internal_alignment"
    elif not critical_red and not secondary_red and total_red == 0 and total_green <= 3:
        status_key = "3_ready_vendor_discovery"
    elif not critical_red and not secondary_red and total_red == 0 and critical_evidence_ok and total_green >= 6:
        status_key = "7_ready_for_rfp"
    elif not critical_red and total_green >= 5:
        status_key = "6_ready_enterprise_planning"
    elif not critical_red and not secondary_red and total_green >= 3:
        status_key = "5_ready_service_line_scale"
    else:
        status_key = "4_ready_targeted_pilot"

    status = RUBRIC["decision_readiness_statuses"][status_key]
    warnings = []
    if critical_red:
        warnings.append(RUBRIC["gating_model"]["critical_gating_domains"]["red_override_message"])
    if secondary_red:
        warnings.append(RUBRIC["gating_model"]["secondary_gating_domains"]["red_override_message"])
    if strategic_red:
        warnings.append(RUBRIC["gating_model"]["strategic_adoption_domains"]["red_warning_message"])

    return {
        "status_key": status_key,
        "label": status["label"],
        "guidance": status["guidance"],
        "allowed_next_steps": status["allowed_next_steps"],
        "gating_warnings": warnings,
    }


@mcp.tool()
def score_assessment(signal_extraction_json: str) -> str:
    """
    Apply deterministic rubric rules to signal extraction output.
    Input: JSON string from the scoring prompt (Call 2).
    Returns: Domain scores, evidence confidence, credibility gaps, colors, and decision-readiness status.
    """
    try:
        data = json.loads(signal_extraction_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {e}"})

    domains_input = data.get("domains", {})
    domain_scores = {}

    for domain_id in DOMAIN_IDS:
        domain_data = domains_input.get(domain_id, {})
        signals = domain_data.get("signals", {})

        if not signals:
            domain_scores[domain_id] = {
                "readiness_score": 1.0,
                "evidence_confidence_score": 0.0,
                "credibility_gap": 1.0,
                "color": "Red",
                "credibility_gap_label": "High Self-Report Risk",
                "confidence_label": "Low",
                "unanswered_signals": domain_data.get("unanswered_signals", []),
                "note": "No signals provided for this domain.",
            }
            continue

        readiness_scores = []
        evidence_scores = []
        credibility_gap_warnings = []
        phi_confirmed = data.get("global_flags", {}).get("phi_safety_attestation_confirmed", False)

        for signal_id, signal in signals.items():
            stated = signal.get("stated_level", "none")
            score = STATED_LEVEL_SCORES.get(stated, 1.0)
            readiness_scores.append(score)

            ev_level = float(signal.get("evidence_level", 0))
            if not phi_confirmed:
                ev_level = 0.0
            evidence_scores.append(ev_level)

            gap = score - ev_level
            if gap > 1.3 and domain_id in CRITICAL_GATING:
                credibility_gap_warnings.append(
                    f"{signal_id}: readiness {score} vs evidence {ev_level} — validate before use in procurement decisions."
                )

        readiness_avg = sum(readiness_scores) / len(readiness_scores)
        evidence_avg = sum(evidence_scores) / len(evidence_scores)
        gap = readiness_avg - evidence_avg

        effective_color = _color(readiness_avg)
        if effective_color == "Green" and gap > 2.0:
            effective_color = "Yellow"

        signal_count = len(signals)
        answered = sum(1 for s in signals.values() if s.get("stated_level", "none") != "none")
        confidence_ratio = answered / signal_count if signal_count > 0 else 0

        domain_scores[domain_id] = {
            "readiness_score": round(readiness_avg, 2),
            "evidence_confidence_score": round(evidence_avg, 2),
            "credibility_gap": round(gap, 2),
            "color": effective_color,
            "credibility_gap_label": _credibility_gap_label(gap),
            "confidence_label": _confidence_label(confidence_ratio),
            "signals_answered": answered,
            "signals_total": signal_count,
            "credibility_gap_warnings": credibility_gap_warnings,
            "unanswered_signals": domain_data.get("unanswered_signals", []),
            "domain_summary": domain_data.get("domain_intake_summary", ""),
        }

    decision_readiness = _decision_readiness_status(domain_scores)

    return json.dumps({
        "session_id": data.get("session_id", ""),
        "operator_confirmed_baseline": data.get("operator_confirmed_baseline", {}),
        "domain_scores": domain_scores,
        "decision_readiness": decision_readiness,
        "global_flags": data.get("global_flags", {}),
        "scorer": "BT Compass MCP scoring engine — deterministic rules, not Claude",
    }, indent=2)


@mcp.tool()
def get_domain_questions(domain_id: str) -> str:
    """
    Return intake questions for a specific assessment domain.
    Valid domain_ids: strategic_intent_use_case_scope, data_readiness_governance,
    infrastructure_architecture_readiness, security_privacy_compliance,
    ai_governance_operating_model, workflow_adoption_change_readiness,
    procurement_vendor_readiness, budget_investment_readiness
    """
    domain_key_map = {did: f"domain_{i+1}" for i, did in enumerate(DOMAIN_IDS)}
    domain_key = domain_key_map.get(domain_id)
    if not domain_key:
        return json.dumps({"error": f"Unknown domain_id: {domain_id}. Valid ids: {DOMAIN_IDS}"})

    domain_data = QUESTION_BANK["domains"].get(domain_key, {})
    questions = domain_data.get("questions", {})

    return json.dumps({
        "domain_id": domain_id,
        "domain_name": domain_data.get("name", ""),
        "gate_type": domain_data.get("gate_type", ""),
        "questions": [
            {
                "question_id": qid,
                "signal_id": q.get("signal_id", ""),
                "signal_name": q.get("signal_name", ""),
                "question": q.get("question", ""),
                "follow_ups": q.get("follow_ups", []),
                "accepted_evidence_types": q.get("evidenceValidation", {}).get("acceptedEvidenceTypes", []),
            }
            for qid, q in questions.items()
        ],
    }, indent=2)


@mcp.tool()
def get_vendor_reference(vendor: str) -> str:
    """
    Return the vendor reference design for matching to an organization's profile.
    Valid vendors: epic, aws, azure, google
    """
    vendor_files = {
        "epic": "epic_ai_ecosystem.md",
        "aws": "aws_health_ai.md",
        "azure": "azure_health_foundation.md",
        "google": "google_cloud_health_ai.md",
    }
    filename = vendor_files.get(vendor.lower())
    if not filename:
        return json.dumps({"error": f"Unknown vendor: {vendor}. Valid options: {list(vendor_files.keys())}"})

    filepath = REFERENCE_DIR / filename
    if not filepath.exists():
        return json.dumps({"error": f"Reference file not found: {filename}"})

    return filepath.read_text()


@mcp.resource("btcompass://rubric")
def get_rubric() -> str:
    """BT Compass scoring rubric — scale definitions, color mapping, gating rules, decision-readiness statuses."""
    return (BASE / "specs/rubric.json").read_text()


@mcp.resource("btcompass://question-bank")
def get_question_bank() -> str:
    """BT Compass question bank — 43 adaptive intake questions across 8 domains."""
    return (BASE / "scoring/question_bank.json").read_text()


@mcp.resource("btcompass://evidence-rules")
def get_evidence_rules() -> str:
    """Evidence confidence rules, credibility gap formula, and gating interactions."""
    return (BASE / "scoring/evidence_confidence_rules.md").read_text()


if __name__ == "__main__":
    mcp.run()
