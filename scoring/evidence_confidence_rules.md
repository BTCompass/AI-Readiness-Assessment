# Evidence Confidence Rules
# BT Compass AI Infrastructure Assessment

---

## dual_score_architecture

Every domain in the BT Compass assessment produces two visible scores:

| Score | What it measures |
|---|---|
| **Readiness Score** (1.0–5.0) | Apparent preparedness based on intake responses |
| **Evidence Confidence Score** (0–5) | How well the readiness score is validated by evidence |

These two scores are always displayed together, never collapsed into a single number.

**Why two scores?**
A health system that says "we have strong AI governance" (readiness = 4) but can provide no documents, artifacts, or data to support that claim has a very different risk profile than a health system with a governance charter, committee minutes, and a KPI dashboard showing review cadence. The Evidence Confidence Score makes that difference visible — to the CIO, to the board, and to the assessment itself.

---

## report_language

Include the following text in every assessment output, before domain scores are displayed:

> **How to read your scores**
>
> Your **Readiness Score** reflects apparent preparedness based on your responses to this assessment. Your **Evidence Confidence Score** reflects how well your readiness is supported by validated evidence — documents, operating artifacts, quantitative data, or external validation you have provided.
>
> Evidence-backed scores are more credible for executive decision-making, internal business-case development, governance review, and future peer benchmarking. A high readiness score with low evidence confidence should be treated as a self-assessment hypothesis, not a confirmed finding.

---

## evidence_confidence_scale

| Level | Label | Definition | Examples |
|---|---|---|---|
| **0** | No Evidence | No supporting evidence of any kind. Score is based entirely on self-reported description. | Question answered verbally or in writing; no documents, data, or artifacts available |
| **1** | Self-Reported / Stated Practice | Operator describes a practice or capability but provides no document or data to support it. The intake answer itself is the only evidence. | "We have an AI governance committee" — no charter, no minutes, no roster |
| **2** | Static Document | A document that describes intent, structure, or policy exists but does not demonstrate active use or operation. | Governance charter, AI roadmap, data governance policy, architecture diagram, cloud strategy document, written approval process |
| **3** | Operating Artifact | A document or artifact that demonstrates the practice is actively operating — not just defined on paper. | Committee meeting minutes, completed vendor risk assessment, AI approval intake form, workflow diagram used in production, signed BAA, data quality report from a completed project |
| **4** | Quantitative Report | Measured data demonstrating performance, usage, or outcomes over time. | KPI dashboard, usage metrics, documentation time reduction data, AI model performance report, denial trend analysis, data quality audit log, clinical outcome data from AI tool |
| **5** | Audited / Externally Validated | Evidence has been reviewed by an external party or meets an external standard. | Third-party security audit, HIMSS INFRAM assessment, HITRUST certification, FDA cleared AI tool with published validation study, penetration test report, external governance review |

---

## evidence_confidence_calculation

**Per domain:**

1. For each signal in the domain, the operator's response starts at evidence level 1 (self-reported).
2. If the operator uploads supporting evidence, the scoring engine assigns an evidence level (2–5) based on the evidence type, per the table above.
3. The domain Evidence Confidence Score = the **average evidence level across all signals** with evidence provided, normalized to the 0–5 scale.
4. Signals with no evidence provided contribute level 0 to the domain average.

**Deterministic rules for evidence type classification:**

| Document type | Evidence level assigned |
|---|---|
| Policy, charter, roadmap, architecture diagram | 2 |
| Meeting minutes, completed risk assessment, signed BAA, vendor assessment | 3 |
| Workflow diagram used in production | 3 |
| KPI dashboard, usage metrics, performance reports | 4 |
| Data quality audit log, model performance report with time-series data | 4 |
| Third-party audit, external certification, FDA clearance documentation | 5 |

**Claude's role in evidence processing:**
- Claude may summarize uploaded evidence and extract key metrics
- Claude may flag contradictions between self-reported answers and uploaded evidence
- Claude does NOT assign the evidence confidence level — the scoring engine assigns it deterministically based on evidence type
- When a document's type is ambiguous, the scoring engine defaults to the lower level

---

## credibility_gap

**Formula:** `Credibility Gap = Readiness Score − Evidence Confidence Score`

Note: Readiness Score is on a 1–5 scale; Evidence Confidence Score is on a 0–5 scale. A domain where the operator scores themselves a 4 on readiness but provides no evidence has a credibility gap of 4.0 (4 − 0).

| Credibility Gap | Interpretation | Report language |
|---|---|---|
| **0.0–0.5** | Well-supported | "This domain score is well-supported by the evidence provided. High confidence for use in executive decision-making and procurement." |
| **0.6–1.2** | Some validation needed | "This domain score is partially supported. Some evidence has been provided but additional validation would improve confidence before major investment decisions." |
| **1.3–2.0** | Material evidence gap | "This domain score reflects primarily self-reported information. Material evidence gaps exist. This score should be validated before use in executive decision-making, governance review, or procurement." |
| **>2.0** | High self-report / low evidence risk | "This domain score is based almost entirely on self-reported information with little supporting evidence. Use with significant caution. Do not use as a basis for major investment, procurement, or board reporting without validation." |

---

## gating_rule_interaction

The credibility gap interacts with the decision-readiness gating model:

- A domain with a Green readiness score (3.5–5.0) AND a credibility gap > 2.0 is treated as **Yellow-equivalent** for gating purposes.
- A critical gating domain (Security, Data, Governance) with a credibility gap > 1.3 triggers a mandatory note in the report: *"This critical domain score requires evidence validation before use in RFP or procurement decisions."*
- Ready for RFP status (status 7) requires Evidence Confidence Score ≥ 3 (operating artifact level) across all critical gating domains.

---

## safety_attestation

Every evidence upload must be preceded by a user attestation. This attestation is mandatory — the upload mechanism should be blocked until the operator confirms.

**Attestation text (required verbatim):**
> "I confirm this material has been reviewed and does not include PHI, PII, confidential patient information, credentials, proprietary contracts, or unredacted sensitive content."

**Safety reminder displayed on every evidence validation prompt (required verbatim):**
> "Do not upload PHI, PII, confidential patient information, proprietary contracts, credentials, or unredacted sensitive materials."

---

## contradictions_flagging

When Claude processes uploaded evidence, it must flag:

1. **Contradiction between self-report and evidence:** The operator stated X but the uploaded document says Y.
2. **Evidence that is out of scope:** The uploaded document does not address the signal it was submitted for.
3. **Evidence that is outdated:** The document is more than 24 months old — flag as potentially stale but do not auto-disqualify.
4. **Evidence that is incomplete:** The document appears to be a fragment, a draft, or an earlier version.

Contradictions are surfaced in the per-domain output under "Contradictions between self-report and evidence." They are not silently resolved — the operator is asked to clarify.

---

## per_domain_output_format

Each domain in the final report shows:

```
Domain: [Name]
─────────────────────────────────────────────
Readiness Score:          [X.X / 5.0]    [Color]
Evidence Confidence:      [X / 5]         [Level label]
Credibility Gap:          [X.X]           [Interpretation]

Evidence provided:        [List of documents/artifacts uploaded]
Evidence gaps:            [Signals with no supporting evidence]
Contradictions:           [Any contradictions between self-report and evidence]
Standards alignment:      [Frameworks mapped to this domain]

Recommended next action:  [One concrete action]
RFP implications:         [2–3 categories]
```

---

## ninety_day_roadmap_evidence_targets

For each domain where the credibility gap is > 1.2, the 90-day roadmap section of the report should include a specific evidence collection target:

| Domain | Credibility gap > 1.2 | Evidence target for next 90 days |
|---|---|---|
| AI Governance | Yes | Obtain or draft AI governance charter; produce committee meeting minutes for last two meetings |
| Security | Yes | Produce last TPRM review for an AI vendor; CISO sign-off on AI governance policy |
| Data Readiness | Yes | Produce data quality report for target AI use case data domain |
| Infrastructure | Yes | Produce cloud architecture diagram or infrastructure assessment |
| Strategic Intent | Yes | Produce board-approved AI strategy document or use case brief with success metrics |

Specific targets are generated based on which signals have the lowest evidence confidence scores within each domain.
