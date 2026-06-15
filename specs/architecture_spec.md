# Agent Architecture Specification
# BT Compass AI Infrastructure Assessment
# Updated: June 15, 2026 — reflects actual build, supersedes original design

---

## system_overview

**What the system does:** Guides a health system CIO or senior IT leader through a structured 8-domain AI readiness assessment, scores their responses, and generates a complete assessment report with vendor recommendations, RFP language, and a 90-day roadmap.

**Platform:** n8n (orchestration + scoring engine) + Claude API (intake conversation, signal extraction, report generation) + Lovable.dev or v0.dev (branded frontend)

**LLM call count:** 3 (down from original 6-call design)

**Scorer:** n8n (deterministic rules engine) — not Claude. Claude guides, extracts, and interprets. n8n scores and decides.

---

## llm_call_architecture

Three LLM calls run in sequence. n8n orchestrates the transitions and does all scoring between Call 2 and Call 3.

```
[Operator] → Intake conversation → [Call 1: Intake Agent]
                                          ↓
                             Structured JSON (signal extraction)
                                          ↓
                             [n8n Scoring Engine]
                             - Applies rubric rules per signal
                             - Calculates domain Readiness Scores (1–5)
                             - Calculates Evidence Confidence Scores (0–5)
                             - Computes Credibility Gaps
                             - Assigns colors + decision-readiness status
                             - Flags gating domain violations
                                          ↓
                             [Call 3: Report Generation]
                                          ↓
                             9-section Assessment Report → PDF
```

---

## llm_call_inventory

### Call 1 — Intake Agent
- **Status:** Essential
- **Role:** Run the adaptive intake conversation. Ask questions from question_bank.json. Follow up on vague or revealing answers. Collect the operator's confirmed baseline. Gate evidence uploads behind PHI attestation.
- **System prompt:** Embedded in n8n AI Agent node system prompt; draws questions from question_bank.json
- **Human touchpoints:** Profile confirmation, mode selection, PHI attestation, baseline confirmation before scoring
- **Ends when:** Operator confirms the baseline summary is accurate and all 8 domains have been addressed
- **Quality risk connection (8/10):** Intake is the only source of org-specific input. Shallow intake = compromised output at every downstream step.

### Call 2 — Signal Extraction (scoring_prompt.md)
- **Status:** Essential
- **Role:** Read the complete intake transcript and convert it into structured JSON — one stated_level and evidence_level per signal per domain — that n8n's scoring engine can process deterministically.
- **System prompt:** `prompts/scoring_prompt.md`
- **Human touchpoints:** None — automated step between intake completion and n8n scoring
- **Output format:** Valid JSON matching the schema defined in scoring_prompt.md
- **Quality risk connection (9/10):** This is the gate between the conversation and the score. Wrong signal extraction = wrong scores with no recovery path.

### Call 3 — Report Generation (interpretation_prompt.md)
- **Status:** Essential
- **Role:** Receive n8n's structured scoring output and generate the complete 9-section assessment report. Every sentence must be specific to this organization — not generic.
- **System prompt:** `prompts/interpretation_prompt.md`
- **Human touchpoints:** Operator reviews report before PDF export
- **Output format:** Markdown report (9 sections) written to `/output/` directory; converted to PDF locally
- **Quality risk connection (10/10):** This is the primary deliverable. Generic output = failed assessment.

---

## scoring_architecture

**Scorer:** n8n deterministic rules engine (not Claude)

### Dual-Score Model

Every domain produces two scores — always displayed together, never collapsed:

| Score | Scale | What it measures |
|---|---|---|
| Readiness Score | 1.0–5.0 | Apparent preparedness based on intake responses |
| Evidence Confidence Score | 0–5 | How well the readiness score is supported by uploaded evidence |

### Signal Extraction Vocabulary (from Call 2 → n8n input)

| stated_level | Meaning | Maps to Readiness Score |
|---|---|---|
| `none` | No information provided | 1 |
| `vague` | Topic acknowledged, no specific practice | 1–2 |
| `partial` | Practice exists but informal or inconsistent | 2–3 |
| `defined` | Formally defined but not consistently operating | 3–4 |
| `specific_with_metrics` | Mature practice with named owners and measurable outcomes | 4–5 |

### Evidence Confidence Scale

| Level | Label | Examples |
|---|---|---|
| 0 | No Evidence | Nothing uploaded; score is self-reported only |
| 1 | Self-Reported | Intake answer only — no document |
| 2 | Static Document | Policy, charter, roadmap, architecture diagram |
| 3 | Operating Artifact | Meeting minutes, signed BAA, completed vendor risk assessment |
| 4 | Quantitative Report | KPI dashboard, audit log, performance report with trend data |
| 5 | Audited / Externally Validated | Third-party audit, HITRUST, FDA clearance, penetration test |

### Credibility Gap

`Credibility Gap = Readiness Score − Evidence Confidence Score`

| Gap | Interpretation |
|---|---|
| 0.0–0.5 | Well-Supported |
| 0.6–1.2 | Some Validation Needed |
| 1.3–2.0 | Material Evidence Gap |
| >2.0 | High Self-Report Risk |

### Color Mapping (n8n assigns)

| Readiness Score | Color |
|---|---|
| 1.0–2.4 | Red — Critical gap |
| 2.5–3.4 | Yellow — Developing |
| 3.5–5.0 | Green — Ready |

### Decision-Readiness Status (n8n assigns — 8 levels)

n8n produces one of 8 decision-readiness statuses based on domain scores and gating rules. Critical gating domains (Security, Data, AI Governance) can block progression regardless of scores in other domains. See `specs/rubric.json` for full gating logic.

---

## assessment_domains

8 domains. Each domain has 4–6 signals. Signal IDs in `scoring/question_bank.json` and `specs/rubric.json`.

| # | Domain | Gate Type |
|---|---|---|
| 1 | Strategic Intent & Use Case Scope | Secondary |
| 2 | Data Readiness & Governance | Critical |
| 3 | Infrastructure & Architecture Readiness | Secondary |
| 4 | Security, Privacy & Compliance | Critical |
| 5 | AI Governance & Operating Model | Critical |
| 6 | Workflow Adoption & Change Readiness | Strategic Adoption |
| 7 | Procurement & Vendor Readiness | Strategic Adoption |
| 8 | Budget & Investment Readiness | Strategic Adoption |

---

## context_schemas

### Shared Context Object (operator_confirmed_baseline)

Written by Call 1, read by Call 2 and Call 3. Stored in n8n session state.

```json
{
  "health_system_name": "string",
  "operator_role_title": "string",
  "assessment_mode": "Proposal | Enterprise Foundation | Departmental or Pilot | Scale Readiness",
  "ehr_platform": "string",
  "primary_cloud_provider": "AWS | Azure | Google | None | Mixed",
  "primary_ai_use_cases": ["string"],
  "stated_budget_range": "string",
  "hard_constraints_identified": ["string"]
}
```

### Call 1 — Intake Agent Context Variables

| Variable | Type | Source | Retention | Notes |
|---|---|---|---|---|
| `session_id` | string | system (n8n) | session | UUID generated at session start |
| `health_system_name` | string | user | session | Typed into frontend |
| `assessment_mode` | string | user | session | Selected from 4 options |
| `conversation_history` | array[object] | system (n8n buffer) | session | Max 60 message pairs; full transcript saved separately before buffer prunes |
| `current_domain_questions` | object | system (filtered from question_bank.json) | call_only | 5–7 questions per turn — NOT full 163KB file per turn |
| `public_profile_data` | object | system (preloaded) | session | For demo: hardcoded Southside Academic Health Network profile |
| `phi_safety_attestation_confirmed` | boolean | user | session | Blocks evidence upload until true |

### Call 2 — Signal Extraction Context Variables

| Variable | Type | Source | Retention | Notes |
|---|---|---|---|---|
| `session_id` | string | system | session | — |
| `full_intake_transcript` | string | system (n8n exports buffer) | session | Complete conversation string — NOT truncated. Saved separately from buffer. |
| `operator_confirmed_baseline` | object | system (session state) | session | Same object from Call 1 |
| `evidence_uploads` | array[object] | system (n8n document handler) | call_only | Raw content read; only evidence levels stored after this call |
| `phi_safety_attestation_confirmed` | boolean | system (session state) | session | If false: all evidence defaults to level 0 |

**Output:** Structured JSON per `prompts/scoring_prompt.md` schema — stated_level and evidence_level per signal, contradiction flags, domain summaries, global flags.

### Call 3 — Report Generation Context Variables

| Variable | Type | Source | Retention | Notes |
|---|---|---|---|---|
| `session_id` | string | system | session | — |
| `n8n_scoring_output` | object | system (n8n scoring engine) | session | Domain scores, evidence scores, credibility gaps, colors, status, gating flags |
| `signal_extraction_output` | object | system (Call 2 output) | session | Full structured JSON from Call 2 |
| `operator_confirmed_baseline` | object | system (session state) | session | Same object from Call 1 — required for specificity |
| `evidence_inventory` | array[object] | system (n8n extracts from Call 2 output) | call_only | n8n pre-extracts: {domain, signal_name, document_name, evidence_level} |
| `contradiction_log` | array[object] | system (n8n extracts from Call 2 output) | call_only | n8n pre-extracts all contradiction_flag=true records |
| `reference_library_summary` | object | system (condensed from reference_library/) | call_only | ~600 words: best_fit, contraindications, ehr_alignment, cloud_alignment per vendor. NOT full files. |

**Output:** 9-section markdown assessment report written to `/output/`.

---

## data_flow_architecture

```
Operator → btcompass.ai frontend
  → [Session start] n8n generates session_id
  → Operator enters health_system_name
  → n8n loads public_profile_data (preloaded for demo)
  → [Call 1: Intake Agent — Claude AI Agent in n8n]
       ↕ Operator validates profile, selects mode, confirms PHI attestation
       ↕ Claude asks adaptive questions from current_domain_questions
       ↕ Operator answers; n8n window buffer stores conversation_history
       ↕ Optional: Operator uploads evidence (after attestation)
       → n8n stores operator_confirmed_baseline in session state
       → n8n exports full_intake_transcript from buffer

  → n8n calls [Call 2: Signal Extraction — scoring_prompt.md via Claude API]
       → Returns signal extraction JSON
       → n8n stores signal_extraction_output in session state

  → [n8n Scoring Engine — If/Switch/Set nodes]
       → Reads signal_extraction_output
       → Calculates Readiness Scores, Evidence Confidence Scores, Credibility Gaps
       → Assigns colors, decision-readiness status, gating flags
       → n8n extracts contradiction_log and evidence_inventory from signal output
       → n8n loads condensed reference_library_summary (~600 words)
       → Stores n8n_scoring_output in session state

  → n8n calls [Call 3: Report Generation — interpretation_prompt.md via Claude API]
       → Receives: n8n_scoring_output + signal_extraction_output + operator_confirmed_baseline
                 + evidence_inventory + contradiction_log + reference_library_summary
       → Returns: 9-section markdown report

  → n8n writes report to /output/
  → n8n generates PDF → returns download link to frontend
  → Frontend displays report + PDF download button
```

---

## n8n_intermediate_steps

Between Call 2 and Call 3, n8n performs these deterministic operations that do NOT require Claude:

| Step | What n8n does | Why |
|---|---|---|
| Transcript export | Joins conversation_history buffer into full_intake_transcript string | Call 2 needs full text, not array of objects |
| Scoring | Applies rubric rules to signal extraction JSON; calculates all scores | Deterministic — not Claude's role |
| Contradiction extraction | Filters signal_extraction_output for contradiction_flag=true | Pre-structures Section 6 input; reduces Call 3 context size |
| Evidence extraction | Filters signal_extraction_output for evidence_provided=true | Pre-structures per-domain evidence lists; reduces Call 3 context size |
| Library condensing | Reads 4 vendor reference design files; extracts ~600-word summary | Prevents context bloat — full files are ~50KB |

---

## external_data_resources

| Resource | For Demo | Production |
|---|---|---|
| `public_profile_data` | Preloaded Southside Academic Health Network JSON in n8n | Web search + CMS lookup triggered by health_system_name |
| `vendor_reference_library` | 4 markdown files in `reference_library/` (Epic, AWS, Azure, Google Cloud) | Same files, versioned; updated as vendor capabilities change |

Both resources carry version metadata. Neither is updated at runtime.

---

## human_judgment_checkpoints

| Checkpoint | What operator sees | What they decide |
|---|---|---|
| Sovereign environment acknowledgment | 5-item checklist at session start | Confirm all five before proceeding |
| Mode selection | 4 assessment modes described | Choose entry point |
| Public data confirmation | Agent presents known profile facts | Confirm, correct, or expand each item |
| PHI attestation | Confirmation required before upload activates | Acknowledge or decline |
| Baseline confirmation | Full summary of intake per domain | Confirm, correct, or add context before scoring begins |
| Report review | Full 9-section report displayed | Review before PDF download |

---

## component_responsibility_matrix

| Responsibility | Claude (Call 1) | n8n | Claude (Call 2) | n8n Scoring | Claude (Call 3) |
|---|---|---|---|---|---|
| Ask intake questions | ✓ | | | | |
| Adapt follow-ups | ✓ | | | | |
| Store conversation history | | ✓ | | | |
| Gate evidence uploads | | ✓ | | | |
| Extract signals from transcript | | | ✓ | | |
| Flag contradictions | | | ✓ | | |
| Assign Readiness Scores | | | | ✓ | |
| Assign Evidence Confidence Scores | | | | ✓ | |
| Compute Credibility Gaps | | | | ✓ | |
| Assign decision-readiness status | | | | ✓ | |
| Write domain interpretations | | | | | ✓ |
| Match vendors to org profile | | | | | ✓ |
| Generate RFP language | | | | | ✓ |
| Generate 90-day roadmap | | | | | ✓ |
| Generate PDF | | ✓ | | | |

**Design principle:** Claude guides and interprets. n8n scores and decides. Do not let Claude become the scorer.

---

## vendor_reference_library

4 reference designs in `reference_library/`:

| Vendor | File | Best-fit EHR | Best-fit Cloud |
|---|---|---|---|
| Epic AI Ecosystem | `epic_ai_ecosystem.md` | Epic only | Any |
| AWS Health AI | `aws_health_ai.md` | Epic + others | AWS |
| Azure Health Foundation | `azure_health_foundation.md` | Any | Azure / Microsoft 365 |
| Google Cloud Health AI | `google_cloud_health_ai.md` | Any (multi-EHR strength) | Google Cloud |

Vendor matching rules are defined in `prompts/interpretation_prompt.md` Section 4 and `reference_library/vendor_evaluation_criteria.md`.

---

## standards_alignment

Every question in question_bank.json maps to 4 frameworks:

| Framework | Scope |
|---|---|
| NIST AI RMF | Govern / Map / Measure / Manage functions |
| WHO Ethics and Governance of AI for Health | 6 principles |
| CHAI Blueprint for Trustworthy AI | Trustworthy AI deployment |
| DiMe AI in Healthcare Playbook | Use case identification and scoping |

Standards alignment appears in per-domain output (Section 2) and the standards summary (Section 3) of the assessment report.

---

## key_files

| File | Purpose |
|---|---|
| `specs/rubric.json` | 8 domains × 43 signals, dual-score architecture metadata, scoring rules |
| `scoring/question_bank.json` | 43 questions with standards alignment and evidence validation per question |
| `scoring/evidence_confidence_rules.md` | Complete dual-score model, credibility gap formula, gating rules |
| `prompts/scoring_prompt.md` | Call 2 system prompt — signal extraction rules and output schema |
| `prompts/interpretation_prompt.md` | Call 3 system prompt — 9-section report structure and quality rules |
| `reference_library/library_index.md` | Vendor library index and usage instructions |
| `reference_library/vendor_evaluation_criteria.md` | 8-dimension cross-vendor comparison |
| `reports/context_management_design.md` | Context schemas, data flow map, context waste analysis |

---

## error_handling

| Situation | Response |
|---|---|
| PHI detected in uploaded document | Stop processing; flag as evidence_level 0; prompt operator to re-upload redacted version |
| PHI attestation not confirmed | Block all evidence uploads; continue intake without document evidence |
| Signal not addressed in intake | Mark as stated_level: none, evidence_level: 0; do not infer |
| Call 2 output is malformed JSON | n8n catches parsing error; retry once; if failure persists, flag session for manual review |
| Critical gating domain scores Red | n8n flags in scoring output; Call 3 states gating rule explicitly in plain language |
| Credibility gap > 2.0 on critical domain | n8n flags; Call 3 adds mandatory warning before that domain's score is used in recommendations |

---

## demo_scope

**Target:** Southside Academic Health Network — one complete end-to-end path for June 19 demo

**Hardcoded for demo:**
- Southside public profile (preloaded in n8n — no live lookup)
- 3–5 scoring signals per domain (full 43-signal bank exists; demo uses subset)
- Single session, no authentication, no Airtable/Supabase persistence

**Deferred post-demo:**
- Live public profile lookup (web search / CMS)
- Full 43-signal scoring in n8n
- Session persistence across sessions
- Multi-user / client accounts
- Document upload in demo (intake-only path sufficient to test quality risk)
