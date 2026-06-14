# Implementation Design

## delivery_context_design

### workflow_analysis

**Target operator:** Senior IT individual contributor or first/second-line manager delegated by CIO. Currently starts from a blank page — no structured tool exists. Pain is real: vendor discovery happens before internal requirements are clear; governance is reviewed too late; every AI decision cycle restarts from scratch.

**Pain points:**
- Blank page every time a new AI decision cycle opens
- Vendor conversations happen before the operator has a structured internal view
- No output the CIO can use in governance or board conversations without significant manual effort
- Expensive consultants or biased vendor assessments are the current alternative

**Flow points:**
- Operators are comfortable with structured intake (surveys, forms, advisory conversations)
- CIOs are comfortable receiving structured briefing documents
- The output format (Scenario Brief + scorecard) maps to formats they already use in governance conversations

### delivery_mechanism

**Primary product URL:** btcompass.ai (or app.btcompass.ai)
**Parent/credibility site:** breakthroughcompass.com (services, thought leadership, bio, conversion into paid assessment)
**Product name:** BT Compass AI Infrastructure Assessment

**Flow:** Landing page → secure client intake → guided AI chat assessment → Scenario Brief preview → readiness scorecard → PDF/web report → RFP requirements starter output

**Feel:** Paid advisory application, not a document portal. The guided conversation is part of the value — the tool should feel like it is helping the operator think, not just collecting fields.

**Document upload:** Optional. Requires explicit user attestation that no confidential, sensitive, or unredacted PII/PHI is included before upload proceeds.

### interaction_model

**Chat-first operator workflow.** The guided conversation is the product. A static form would flatten the agent behavior.

**Entry:** Lightweight web intake form to initialize session context (health system name, user role, AI priorities, optional constraints, optional upload intent). Chat experience takes over after initialization.

**Demo arc (June 19, 8 minutes):**
- Min 1: Show the problem ("board/CEO/vendor pressure before CIO has structured view")
- Min 2–4: Show the guided intake (org type, EHR/data platform, AI use cases, governance, cybersecurity, budget, constraints, strategic urgency)
- Min 4–6: Show agent synthesis (Scenario Brief, known facts, assumptions, constraints, evidence gaps, maturity interpretation)
- Min 6–7: Show readiness scorecard (8 domains, 0–4 scores, traffic-light colors, confidence levels, evidence gaps, next actions)
- Min 7–8: Show RFP translation (sample requirement categories — not full library, not backend logic)

**Demo scenario:** Southside Academic Health Network (synthetic) — AI-forward academic medical center, Epic, mature research data, smart-room/edge ambition, ambient documentation, radiology AI, fragmented governance, recent third-party cybersecurity breach, margin pressure, cancer pavilion timeline.
**Demo question:** "Is this organization ready to issue an AI infrastructure RFP, or does it need governance and architecture remediation first?"
**Demo answer:** "Proceed toward RFP, but only if mandatory requirements are included for AI governance, cyber/vendor risk, Epic/data integration, edge-device AI, clinical validation, post-deployment monitoring, and change management."

**IP protection:** Show intake experience, Scenario Brief, scorecard, high-level RFP categories. Do not show full prompt chain, scoring algorithm, weighting model, full rubric library, or n8n workflow details.

### agency_vs_autonomy

| Task | Agency or Autonomy | Rationale |
|---|---|---|
| Generate public health system profile | Autonomy | Deterministic lookup from preloaded data |
| Profile validation/correction | Agency | Operator confirms, corrects, or overrides |
| PHI/PII acknowledgment | Agency | Must be explicit human action |
| Document upload decision | Agency | Operator judgment on what is safe to share |
| Intake questioning | Autonomy + Agency | AI decides next question; operator answers |
| Workload classification | Agency | Operator confirms or revises before proceeding |
| Scenario generation | Autonomy | AI generates all three scenarios from confirmed context |
| Maturity scoring per domain | Autonomy | AI scores based on intake + evidence; shown to operator |
| Final brief review | Agency | Operator reviews before download/share |

### user_touchpoints

**Input:** btcompass.ai → lightweight web intake → chat session start
**Intermediate:** Profile validation, PHI acknowledgment, optional document upload, workload classification confirmation
**Output:** Web-displayed Scenario Brief + readiness scorecard + downloadable PDF + RFP starter requirements

### maturity_scoring_rubric

**Scale:** 0–4 Likert, domain-level scoring

| Score | Label | Definition |
|---|---|---|
| 0 | Not Started | No formal activity or evidence |
| 1 | Ad Hoc | Activity exists but inconsistent, undocumented, or individual-dependent |
| 2 | Defined | Process exists but adoption, authority, or enforcement is limited |
| 3 | Operational | Process is used, governed, repeatable, tied to accountable owners |
| 4 | Scaled/Optimized | Enterprise-wide, measured, continuously improved, board-ready |

**Domains:**
1. AI Strategy and Use-Case Clarity
2. Governance and Accountability
3. Data Readiness and Interoperability
4. Cybersecurity and Third-Party/Vendor Risk
5. Clinical Safety and Oversight
6. Infrastructure Scalability
7. Operating Model and Change Readiness
8. RFP/Procurement Readiness

**Per-domain output:**
- 0–4 maturity score
- Traffic-light color (0–1.0 Red; 1.1–2.0 Orange; 2.1–3.0 Yellow; 3.1–3.5 Yellow-Green; 3.6–4.0 Green)
- Confidence level (separate from maturity)
- Short interpretation
- Evidence gaps
- Recommended next action
- Related RFP requirement categories

**Example:** AI Governance: 2.5 / 4 — Yellow — Medium Confidence. "Governance appears partially defined, but evidence is missing for model inventory, risk-tiering, escalation authority, and post-deployment monitoring."

### brand_structure

- **Breakthrough Compass:** Company / advisory brand (breakthroughcompass.com)
- **BT Compass AI:** Product / application brand (btcompass.ai)
- **Positioning:** "BT Compass AI helps health systems convert AI ambition, vendor pressure, and fragmented governance into a structured infrastructure readiness assessment and RFP decision brief."

---

## backend_design

### technical_approach

Platform: n8n (cloud-hosted) for orchestration and scoring. Lovable.dev or v0.dev for branded custom frontend (React, generated from natural language — no coding required). Claude API for all AI reasoning. Frontend and backend communicate via webhooks.

Design principle: Frontend = branded experience. n8n = intelligence and scoring. They talk to each other; neither is exposed to the end user's eye.

### data_flow_architecture

```
Operator → btcompass.ai (branded frontend)
  → Landing page → Start Assessment → Intake chat page
  → Each message → [Webhook POST] → n8n
  → n8n AI Agent (Claude): conversation, remembers history
  → When intake complete: extracts structured fields as JSON
  → n8n Scoring Engine: calculates 8 domain scores (rules-based)
  → n8n assigns readiness colors + confidence levels
  → n8n passes structured scores + context → Claude
  → Claude: writes interpretations, evidence gaps, Scenario Brief, executive summary, RFP starter categories
  → n8n formats complete output → [Webhook response] → Frontend
  → Output page: Scenario Brief + Scorecard displayed
  → PDF export: n8n generates PDF → returns download link
```

### integration_points

| Component | Role | Tool |
|---|---|---|
| Branded frontend | Landing, chat UI, output display, PDF download | Lovable.dev or v0.dev (React, no-code generated) |
| Orchestration | Session routing, scoring engine, API calls, output formatting | n8n.cloud |
| AI reasoning | Intake conversation, interpretation, Scenario Brief, RFP categories | Claude API via n8n Anthropic node |
| Session memory | Remembers full conversation within a session | n8n built-in window buffer memory |
| Session persistence | Stores completed assessment data | Airtable or Supabase (free tier) |
| PDF generation | Formats brief → downloadable PDF | PDFco or html2pdf via n8n HTTP call |
| Hosting/DNS | btcompass.ai → frontend; n8n on cloud | Cloudflare DNS + Lovable hosting + n8n.cloud |

### integration_notes

- No authentication for demo. Session initialized with unique session ID at start. Full auth (login, client workspaces) is post-demo.
- n8n webhook: Frontend posts `{session_id, message, timestamp}`. n8n responds with `{response, stage, scores, brief}` based on current workflow stage.
- Claude API key stored as n8n credential — never exposed to frontend.
- Document upload (optional): Operator must confirm PHI/PII attestation before upload button activates. n8n enforces this gate — upload is blocked until attestation flag is set to true.
- PDF: n8n formats Scenario Brief as HTML → calls PDF service → returns download URL to frontend.

### scoring_engine_design

**Rules-based scoring in n8n. Claude writes the interpretation.**

| Layer | Who does it | What they produce |
|---|---|---|
| Signal evaluation | n8n (If/Switch nodes) | Each intake answer mapped to 0–4 signal value |
| Domain score calculation | n8n (Set nodes) | Weighted average of 3–5 signals per domain |
| Color assignment | n8n | 0–1.0 Red · 1.1–2.0 Orange · 2.1–3.0 Yellow · 3.1–3.5 Yellow-Green · 3.6–4.0 Green |
| Confidence assignment | n8n | Based on % of direct answers vs. inferred — High/Medium/Low |
| Interpretation | Claude | Receives structured scores, writes explanation, evidence gaps, next action, RFP categories |
| Scenario Brief | Claude | Receives all scores + intake context, generates full narrative |

**Confidence is separate from maturity.** Confidence reflects evidence quality and completeness, not readiness level. A domain can score 3.5 (Green) with Low confidence if the score was inferred rather than directly answered.

**Demo scope:** 3–5 scoring signals per domain. Full rubric library built post-demo.

### claude_vs_n8n_responsibility

**Claude's role:**
- Ask intelligent intake questions one at a time, adapt based on answers
- Summarize confirmed baseline at end of intake
- Identify assumptions and evidence gaps
- Interpret domain scores (narrative explanation per domain)
- Classify workload type (pilot / service-line / enterprise)
- Generate three-scenario Scenario Brief
- Write executive summary
- Generate RFP starter requirement categories (not full library)

**n8n's role:**
- Manage session flow and conversation stages
- Store and structure intake answers
- Enforce document upload PHI/PII attestation gate
- Call Claude API at the right moments
- Calculate rules-based domain scores
- Assign readiness colors and confidence levels
- Pass structured scoring data to output templates
- Generate PDF and return download link

### human_judgment_points

| Touchpoint | What operator sees | What they decide |
|---|---|---|
| Profile validation | AI summary of known public facts | Confirm, correct, or flag as unknown |
| PHI attestation | Confirmation required before upload activates | Acknowledge or decline |
| Workload classification | "I'm classifying this as [X] — confirm or revise?" | Confirm or override before scenario generation begins |
| Brief review | Full Scenario Brief + scorecard displayed | Review before PDF download |

### ip_protection

**Show in demo:** Branded intake experience · AI-guided conversation · confirmed baseline · Scenario Brief · readiness scorecard · sample RFP requirement categories · PDF export

**Do not show:** Full scoring formula · full prompt chain · full maturity rubric library · full RFP requirements library · backend n8n workflow

**Safe demo language:** "For the demo, we are showing the operator experience and executive outputs. The proprietary scoring logic, maturity model, and requirement-generation library sit behind the workflow."

### fallback

If custom frontend cannot be completed before June 19: use n8n's built-in chat UI wrapped inside a branded page at btcompass.ai. Add logo, brand colors, and introductory copy. Do not position it as the final product experience — label it clearly as the beta/prototype version.

---

## mvp_scope_definition

### first_implementation_target

One complete path: Southside Academic Health Network intake → 8-domain scoring → Scenario Brief → scorecard → PDF. Tests all three confirmed quality risks in a single demo run.

### core_path_only

**Input:** Operator enters "Southside Academic Health Network" → intake begins
**Flow:** Claude-guided intake conversation → n8n scoring engine → Claude interpretation + Scenario Brief → scorecard display → PDF export
**Output:** Branded output page with scored 8-domain readiness scorecard + three-scenario Scenario Brief + downloadable PDF

### hardcoded_elements

- Southside Academic Health Network public profile (preloaded, no live public data lookup)
- Vendor reference library (3 hardcoded reference patterns)
- Scoring rubric (3–5 signals per domain × 8 domains — full library post-demo)
- Session storage (in-memory for demo, no Airtable/Supabase)
- Single session, no authentication

### definition_of_done

- [ ] Operator types "Southside Academic Health Network" and intake begins in branded chat interface
- [ ] Claude asks adaptive questions and completes intake in under 10 minutes
- [ ] n8n calculates all 8 domain scores with colors and confidence levels
- [ ] Scorecard displays on screen with traffic-light indicators and domain interpretations
- [ ] Scenario Brief generates three differentiated scenarios with recommended path
- [ ] PDF downloads successfully with full brief and scorecard
- [ ] A domain expert watching the demo would say "this is more useful than what HIMSS gives me"

### deferred_features

| Feature | Reason deferred |
|---|---|
| Document upload + PHI attestation | Intake-only path sufficient to test quality risk |
| Real public profile lookup | Preloaded Southside data is faster and more reliable for demo |
| Session persistence (Airtable/Supabase) | Single-session demo doesn't require persistence |
| Authentication / client accounts | Not needed to test quality risk |
| Admin dashboard | Post-demo |
| Full 40+ signal rubric library | 3–5 signals per domain sufficient for demo |
| Full vendor reference library | 3 hardcoded patterns sufficient for demo |
| Multiple user support | Single operator demo |

### build_sequence

- June 14: n8n workflow skeleton + Claude intake agent working end-to-end
- June 15: Scoring engine (8 domains, 3–5 signals each) + Claude domain interpretations
- June 16: Lovable.dev frontend (4 pages) + webhook connection live at btcompass.ai
- June 17: PDF generation + full output page with scorecard display
- June 18: Full demo run-through + refinement + fallback check
- June 19: Demo

---

## implementation_platform_selection

### platform
n8n.cloud (orchestration + scoring engine) + Lovable.dev (branded frontend) + Claude API (Anthropic)

### platform_rationale
n8n chosen for visual workflow builder, built-in Anthropic node, no server management, and fast iteration. Lovable.dev chosen for no-code React app generation — Dana can describe pages in plain language and get a deployable app without writing code. Claude API chosen as the AI reasoning layer for both intake conversation and output generation.

### platform_tradeoffs
**n8n pros:** Visual debugging, built-in Claude integration, webhook support, no infrastructure to manage, fast to iterate
**n8n cons:** 30-second webhook timeout requires fast processing; complex scoring logic needs careful node design; limited native PDF generation (requires external service)
**Lovable.dev pros:** No-code, generates React app from natural language, deployable to custom domain, handles frontend without engineering
**Lovable.dev cons:** Less control over exact UI behavior; may require iteration to get chat interface right

### alternative_platforms_considered
LangGraph (too code-heavy for 5-day no-code build), Make.com (weaker AI Agent support), pure n8n chat UI (insufficient branded experience for paid advisory product feel)

---

## implementation_approach

### technical_approach_summary
Lovable.dev generates the branded 4-page React frontend. n8n.cloud hosts the orchestration workflow with Claude AI Agent for intake, rules-based scoring engine, Claude HTTP call for interpretation and Scenario Brief, and PDF generation. Frontend and backend communicate via n8n webhook. Full specs in specs/mvp_specs.md.

### implementation_timeline_considerations
5 days (June 14–18) to working demo. Aggressive but achievable with this stack. Critical path: n8n intake agent working by end of June 14; scoring engine by June 15; frontend connected by June 16. Buffer on June 18 for full dry run. Fallback: n8n built-in chat UI wrapped in branded page if Lovable.dev integration takes longer than expected.

---

## learning_since_last_interaction

### user_research_insights
No formal user research conducted yet. Advisor review of experiment 1 not yet completed.

### evaluation_testing_results

**Experiment 1 (completed — mid-size regional health system):**
- Output felt more qualitative than quantitative
- Narratives without enough numerical specificity (budget ranges, infrastructure sizing, readiness scores)
- Classification logic not fully evaluated in experiment 1

**Experiment 2 (completed — UChicago Medicine, large academic medical center):**
- Edge case designed to test: does the AI correctly surface governance as a prerequisite rather than jumping to Enterprise Foundation?
- Result: Classification of Enterprise AI Foundation was CORRECT for this organization (already operating at enterprise scale)
- Governance surfaced correctly as prerequisite — "cyber incident makes cyber-resilient governance a core investment requirement, not a footnote"
- Classification logic: PASSED
- New findings from experiment 2:
  - Output is extremely text-heavy — 6 dense sections, no visuals
  - No readiness scoring rubric — no HIMSS-style 0-7 scale per dimension
  - Diagnostics feel underwhelming vs. competitors who provide structured maturity scores
  - CIO cannot quickly answer "where do we stand?" from prose alone

### prompt_experimentation_findings
- Testing prompt from ideation workflow has been run twice
- The AI adapts to organization-specific inputs (UChicago Medicine brief was org-specific, not generic)
- The qualitative/quantitative gap persists — rich narrative but no scored dimensions
- Format gap confirmed: no visuals, charts, or traffic-light indicators

### implementation_progress_status
- Architecture fully designed (architecture workflow complete)
- Testing prompt exists and has been tested twice
- Nothing built in n8n yet
- 5 days remain before June 19 demo

### updated_quality_risk_focus

**Resolved risk:** Classification logic — AI correctly classifies and surfaces governance as prerequisite ✓

**Confirmed risk #1:** Output is qualitative, not quantitative — no scored readiness dimensions per domain
- This is the primary output quality gap
- Affects: Agent 2 (scenario reasoning) and Call 6 (brief formatter)

**Confirmed risk #2:** No maturity scoring rubric
- Health systems cannot see "we are a 3 of 7 on governance readiness"
- Competitors (HIMSS INFRAM) provide structured scores — tool needs equivalent diagnostic layer
- Does not need to replicate HIMSS; needs a simpler, AI-generated readiness score per assessment domain

**Confirmed risk #3:** Output format too text-heavy
- No visuals, spider charts, traffic-light indicators, or comparison matrices
- CIO cannot quickly orient before a board meeting
- Affects: Call 6 (brief formatter) and output design

**Priority for implementation:** Build the scoring/readiness rubric into Agent 2's reasoning output so Call 6 can render it as both a scored diagnostic and a visual summary.
