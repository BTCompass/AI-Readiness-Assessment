# Context Management Design
# BT Compass AI Infrastructure Assessment
# Generated: June 15, 2026 | context_management workflow

---

## llm_call_inventory

### llm_call_analysis

Your architecture has **3 LLM calls**. The original 6-call plan collapsed because the scoring engine (n8n) took over 4 of those responsibilities deterministically.

---

**Call 1: Intake Agent**
- **Status:** ✅ Essential
- **Core purpose:** Run an adaptive intake conversation — ask questions from question_bank.json, adapt follow-ups based on what the operator says, surface the right depth without being a rigid form
- **Why LLM is required:** Simple logic can't adapt to answers. A CIO saying "we have a governance committee but it's never blocked anything" requires follow-up reasoning, not a fixed next-question rule. The intake only has value if it adjusts to what the operator actually tells it.
- **Success criteria:** Operator completes the intake in under 10 minutes; all 8 domain signal areas are addressed; adaptive follow-ups fire when answers are vague or revealing
- **Failure modes:** Asking redundant questions; ignoring a revealing answer; moving on when a follow-up was clearly warranted; never reaching low-priority domains; timing out the n8n webhook
- **Quality risk connection:** 8/10. The intake is the only source of organization-specific input. If intake is shallow, generic, or fails to surface key gaps, every downstream output is compromised — you can't recover quality at the scoring or interpretation stage.
- **Edge cases:** Operator says "I don't know" to multiple signals; operator gives contradictory answers; operator pastes a long paragraph instead of answering directly; webhook timeout at 30 seconds cuts conversation mid-stream

---

**Call 2: Signal Extraction (scoring_prompt.md)**
- **Status:** ✅ Essential
- **Core purpose:** Read the full intake transcript and convert it into structured JSON — one stated_level and evidence_level per signal, per domain — that the n8n scoring engine can process deterministically
- **Why LLM is required:** The intake is a free-text conversation. n8n's If/Switch scoring nodes can't read prose — they need structured signal values. This call bridges conversational output to deterministic input. Simple parsing can't handle ambiguous answers ("we kind of have a governance process, sort of").
- **Success criteria:** Every signal has a stated_level from the defined vocabulary (none/vague/partial/defined/specific_with_metrics); every evidence_level is an integer 0–5; no PHI in the output; contradictions are flagged; output is valid JSON
- **Failure modes:** Inferring signal values that weren't stated; over-promoting vague answers to "defined"; hallucinating evidence that wasn't provided; missing signals; invalid JSON that breaks the n8n scoring step
- **Quality risk connection:** 9/10. This is the gate between the conversation and the score. If signal extraction is wrong, scores are wrong. There's no human review checkpoint between this call and n8n scoring — the structured JSON goes straight into the rules engine.
- **Edge cases:** Operator didn't address a signal at all; operator gave conflicting answers on the same signal at different points in the conversation; document was uploaded without PHI attestation

---

**Call 3: Report Generation (interpretation_prompt.md)**
- **Status:** ✅ Essential
- **Core purpose:** Receive n8n's structured scoring output (domain scores, evidence scores, credibility gaps, decision-readiness status, color ratings) and generate the full 9-section assessment report — specific to this organization, not generic
- **Why LLM is required:** Deterministic scoring produces numbers and colors. The CIO needs to know what those numbers mean for their specific situation — their EHR, their governance posture, their use cases, their constraints. That synthesis requires reasoning over the full context.
- **Success criteria:** Every interpretation sentence contains at least one organization-specific detail; vendor recommendations reference the correct EHR and cloud alignment rules; contradictions are surfaced; RFP language is testable, not aspirational; 90-day roadmap actions have named roles and specific outputs
- **Failure modes:** Generic sentences that could apply to any health system; ignoring the n8n scores and re-scoring independently; softening gating rule language; generating vendor recommendations that contradict the matching logic; producing RFP language that is aspirational rather than testable
- **Quality risk connection:** 10/10. This is the primary output of the entire system. If this call produces generic output, the whole assessment fails the quality test ("a HIMSS survey would have been more useful").
- **Edge cases:** n8n scoring output is incomplete or malformed; all domains are Red (hard interpretation challenge); operator provided no evidence at all (all evidence scores = 0); critical gating domain has a contradiction that hasn't been resolved

---

### calls_to_remove_or_defer

No calls removed. All three are essential. The original 6 calls collapsed because:
- Calls 2 (profile_enrichment), 3 (workload_classifier), and 4 (vendor_pattern_matcher) are now handled by n8n deterministic logic + the interpretation prompt's vendor matching rules
- Call 6 (brief_formatter) was merged into Call 3 (interpretation_prompt Section 9 — Recommended Path and Scenario Summary)
- Call 1 (intake_question_generator) became a stateful Claude AI Agent in n8n rather than a per-question API call

This is a cleaner architecture. 3 well-scoped LLM calls with clear responsibility boundaries is better than 6 overlapping calls with hand-off complexity.

---

## context_schemas

### Call 1 — Intake Agent

```json
[
  {
    "context_variable_name": "session_id",
    "relevance_to_quality": "Links conversation to scoring engine output; required for n8n session routing",
    "required": true,
    "type": "string",
    "source": "system",
    "acquire_source": "n8n webhook trigger — generated at session start as UUID",
    "retention_policy": "session",
    "shape_transformation": "None — passed as-is",
    "deliver_format": "Not an LLM output — passed through to downstream calls via n8n session state"
  },
  {
    "context_variable_name": "health_system_name",
    "relevance_to_quality": "Initializes the intake; names the organization throughout the report",
    "required": true,
    "type": "string",
    "source": "user",
    "acquire_source": "Operator types into frontend chat or web intake form field",
    "retention_policy": "session",
    "shape_transformation": "None — stored verbatim as confirmed by operator",
    "deliver_format": "String field in operator_confirmed_baseline object passed to all downstream calls"
  },
  {
    "context_variable_name": "assessment_mode",
    "relevance_to_quality": "Shapes which questions are prioritized and how deep each domain goes",
    "required": true,
    "type": "string",
    "source": "user",
    "acquire_source": "Operator selects from 4 options presented by the intake agent (Proposal / Enterprise Foundation / Departmental / Scale Readiness)",
    "retention_policy": "session",
    "shape_transformation": "Operator selection mapped to one of 4 canonical mode labels — stored in n8n Set node",
    "deliver_format": "String field in operator_confirmed_baseline passed to Call 2 and Call 3"
  },
  {
    "context_variable_name": "conversation_history",
    "relevance_to_quality": "Required for adaptive follow-ups — without prior turns, the agent cannot detect vague answers or avoid repetition",
    "required": true,
    "type": "array[object]",
    "source": "system",
    "acquire_source": "n8n built-in window buffer memory — auto-appended each turn",
    "retention_policy": "session",
    "shape_transformation": "n8n window buffer memory automatically formats as role/content pairs — no manual transformation needed",
    "deliver_format": "Passed as messages array to Claude AI Agent node in n8n — not extracted as standalone output"
  },
  {
    "context_variable_name": "question_bank",
    "relevance_to_quality": "Source of domain-specific questions with standards alignment and evidence validation prompts — without this, questions are generic",
    "required": true,
    "type": "object",
    "source": "system",
    "acquire_source": "scoring/question_bank.json — loaded once at session start via n8n Read File node or embedded in system prompt",
    "retention_policy": "call_only",
    "shape_transformation": "JSON file read and passed into the intake agent system prompt as context — not stored in session state after intake completes",
    "deliver_format": "Embedded in system prompt — not a separate output"
  },
  {
    "context_variable_name": "public_profile_data",
    "relevance_to_quality": "Preloaded baseline (EHR, beds, known AI activity) that the operator confirms or corrects — reduces intake time and improves starting signal confidence",
    "required": false,
    "type": "object",
    "source": "system",
    "acquire_source": "For demo: preloaded Southside Academic Health Network JSON in n8n. Production: web search or CMS database lookup triggered by health_system_name",
    "retention_policy": "session",
    "shape_transformation": "Raw profile data structured into confirmed / corrected / unverified fields after operator validation checkpoint",
    "deliver_format": "Stored in n8n session state; operator-confirmed fields merged into operator_confirmed_baseline"
  },
  {
    "context_variable_name": "phi_safety_attestation_confirmed",
    "relevance_to_quality": "Gate that must be true before any document upload is processed",
    "required": true,
    "type": "boolean",
    "source": "user",
    "acquire_source": "Operator clicks attestation checkbox in frontend — frontend sends confirmed=true in webhook payload",
    "retention_policy": "session",
    "shape_transformation": "Boolean flag stored in n8n session state — upload endpoint is blocked until this is true",
    "deliver_format": "Passed to Call 2 as field in global_flags"
  }
]
```

---

### Call 2 — Signal Extraction (scoring_prompt.md)

```json
[
  {
    "context_variable_name": "session_id",
    "relevance_to_quality": "Links extraction output to the correct n8n scoring workflow instance",
    "required": true,
    "type": "string",
    "source": "system",
    "acquire_source": "n8n session state — same ID generated at session start",
    "retention_policy": "session",
    "shape_transformation": "None",
    "deliver_format": "Field in the JSON output object returned by this call"
  },
  {
    "context_variable_name": "full_intake_transcript",
    "relevance_to_quality": "The complete source material for signal extraction — missing turns = missing signal coverage",
    "required": true,
    "type": "string",
    "source": "system",
    "acquire_source": "n8n window buffer memory — exported as full conversation string after intake is flagged complete",
    "retention_policy": "call_only",
    "shape_transformation": "Buffer memory messages joined as formatted transcript (role: content pairs) — NOT summarized or truncated. Must be complete.",
    "deliver_format": "Not an output — consumed only by this call; structured extraction JSON is the output"
  },
  {
    "context_variable_name": "operator_confirmed_baseline",
    "relevance_to_quality": "Required for domain_intake_summary specificity and global_flags — determines what the operator confirmed vs. what is uncertain",
    "required": true,
    "type": "object",
    "source": "system",
    "acquire_source": "n8n session state — built during intake from operator confirmations and corrections to public profile",
    "retention_policy": "session",
    "shape_transformation": "Structured as JSON object with fields: health_system_name, operator_role_title, assessment_mode, ehr_platform, primary_cloud_provider, primary_ai_use_cases[], stated_budget_range, hard_constraints_identified[]",
    "deliver_format": "Preserved in extraction JSON output under operator_confirmed_baseline — passed unchanged to Call 3"
  },
  {
    "context_variable_name": "evidence_uploads",
    "relevance_to_quality": "Required to assign evidence_level > 1; absence means all signals default to level 1 (self-reported)",
    "required": false,
    "type": "array[object]",
    "source": "system",
    "acquire_source": "n8n document handling step — operator uploads via frontend; n8n receives file content after attestation gate passes",
    "retention_policy": "call_only",
    "shape_transformation": "Each upload structured as: {signal_id, document_name, document_content_summary, upload_timestamp, attestation_confirmed}. Full document content is read by Claude; only summary is stored.",
    "deliver_format": "Evidence levels appear in signal extraction JSON output per signal; document summaries NOT persisted after this call"
  },
  {
    "context_variable_name": "phi_safety_attestation_confirmed",
    "relevance_to_quality": "If false, no document content is processed — all evidence defaults to level 0",
    "required": true,
    "type": "boolean",
    "source": "system",
    "acquire_source": "n8n session state — set by operator attestation in Call 1",
    "retention_policy": "session",
    "shape_transformation": "None",
    "deliver_format": "Field in global_flags of extraction JSON output"
  }
]
```

**Output of Call 2:** Structured JSON matching the schema in `prompts/scoring_prompt.md` — one signal block per signal per domain, with stated_level, evidence_level, contradiction_flag, and domain summaries. This JSON is passed directly to n8n scoring engine nodes (If/Switch).

---

### Call 3 — Report Generation (interpretation_prompt.md)

```json
[
  {
    "context_variable_name": "session_id",
    "relevance_to_quality": "Output file routing",
    "required": true,
    "type": "string",
    "source": "system",
    "acquire_source": "n8n session state",
    "retention_policy": "session",
    "shape_transformation": "None",
    "deliver_format": "Field in report output metadata"
  },
  {
    "context_variable_name": "n8n_scoring_output",
    "relevance_to_quality": "The deterministic scoring engine output — domain readiness scores (1–5), evidence confidence scores (0–5), credibility gaps, color assignments, decision-readiness status, gating flags; report cannot be written without this",
    "required": true,
    "type": "object",
    "source": "system",
    "acquire_source": "n8n scoring engine — If/Switch/Set nodes calculate scores from Call 2 signal extraction JSON; passed to Claude via n8n HTTP call or Anthropic node",
    "retention_policy": "session",
    "shape_transformation": "n8n calculates: per-signal scores → domain averages → evidence confidence averages → credibility gaps → color mapping → decision-readiness status. Output structured as JSON object with 8 domain blocks.",
    "deliver_format": "Consumed by this call — scores appear in report sections verbatim (not recalculated)"
  },
  {
    "context_variable_name": "signal_extraction_output",
    "relevance_to_quality": "Provides stated_level per signal, key intake evidence, and contradiction flags for domain interpretations and Section 6 contradictions log",
    "required": true,
    "type": "object",
    "source": "system",
    "acquire_source": "Call 2 output — stored in n8n session state after signal extraction completes",
    "retention_policy": "session",
    "shape_transformation": "Passed as-is from Call 2 output — not re-processed. The contradiction_log is extracted from this object as a separate field for clarity.",
    "deliver_format": "Consumed by this call — key_intake_evidence fields appear in domain interpretation blocks"
  },
  {
    "context_variable_name": "operator_confirmed_baseline",
    "relevance_to_quality": "Every interpretation sentence must reference at least one field from this object — without it, output is generic and fails the specificity requirement",
    "required": true,
    "type": "object",
    "source": "system",
    "acquire_source": "n8n session state — set during Call 1, preserved through Call 2, passed explicitly to Call 3",
    "retention_policy": "session",
    "shape_transformation": "None — same object used in all three calls; no transformation",
    "deliver_format": "Referenced inline throughout the 9-section report — not output as a separate field"
  },
  {
    "context_variable_name": "evidence_inventory",
    "relevance_to_quality": "Required for per-domain evidence provided/gaps lists and the credibility gap table",
    "required": false,
    "type": "array[object]",
    "source": "system",
    "acquire_source": "Extracted from signal_extraction_output — each signal block with evidence_provided=true is summarized into the inventory",
    "retention_policy": "call_only",
    "shape_transformation": "n8n extracts evidence fields from signal extraction JSON: {domain, signal_name, document_name, evidence_level} — produces flat list for easier rendering",
    "deliver_format": "Appears in Section 2 (per domain) and Section 5 (credibility gap table) of the report"
  },
  {
    "context_variable_name": "contradiction_log",
    "relevance_to_quality": "Required for Section 6 — if lost in handoff from Call 2, contradictions are silently dropped from the report",
    "required": false,
    "type": "array[object]",
    "source": "system",
    "acquire_source": "Extracted from signal_extraction_output — all signal blocks where contradiction_flag=true",
    "retention_policy": "call_only",
    "shape_transformation": "n8n filters signal extraction JSON for contradiction_flag=true; structures as: {domain, signal_name, self_reported, evidence_shows, contradiction_detail}",
    "deliver_format": "Appears verbatim in Section 6 of the report"
  },
  {
    "context_variable_name": "reference_library_summary",
    "relevance_to_quality": "Required for Section 4 vendor recommendations — without curated library facts, vendor matching defaults to Claude's training data, not BT Compass's differentiated reference designs",
    "required": true,
    "type": "object",
    "source": "system",
    "acquire_source": "reference_library/ directory — 4 markdown files (epic, aws, azure, google) + vendor_evaluation_criteria.md",
    "retention_policy": "call_only",
    "shape_transformation": "IMPORTANT: Do not pass full reference design files — this causes context bloat. Extract only: best_fit_profile, contraindications, ehr_alignment, cloud_alignment, clinical_validation_maturity per vendor. ~500 words total, not ~5000.",
    "deliver_format": "Consumed by this call only — vendor recommendations in Section 4 reference these facts"
  }
]
```

**Output of Call 3:** Full 9-section markdown report written to `/output/` directory. Structured sections (not JSON) — markdown with tables, headers, and formatted text suitable for PDF conversion.

---

## context_waste_analysis

### Issues Found and Resolutions

---

**Issue 1: question_bank loaded on every intake turn — severe context bloat**

- **What's happening:** question_bank.json is 163KB. If it's included verbatim in the system prompt on every intake turn, every Claude API call pays for 163KB of context that doesn't change.
- **Fix:** Load question_bank.json ONCE at session start. Use an n8n Code node to extract the 5–7 questions relevant to the current domain being discussed, and inject only those questions into the prompt for that turn. The full bank is NOT passed to the Claude AI Agent node per-turn.
- **Schema update:** Removed `question_bank` from Call 1 context variables. Replace with `current_domain_questions` — a filtered subset (5–7 questions) selected by n8n based on intake progress.
- **Retention:** `call_only` — different question subset per turn.

---

**Issue 2: conversation_history window buffer size — transcript completeness risk**

- **What's happening:** n8n's default window buffer memory retains the last N messages. If set too small (default is often 10 messages), early intake turns are dropped before signal extraction reads them. Signal extraction on a truncated transcript produces incomplete stated_level values for early domains.
- **Fix:** Set n8n window buffer to minimum 60 message pairs (covers a 10-minute intake at ~1 exchange every 10 seconds). Additionally, after the operator marks intake complete, n8n must save the full conversation as a separate `full_intake_transcript` string variable in session state — do not rely on the buffer for Call 2.
- **Schema update:** `conversation_history` max_size added: 60 pairs. Pruning strategy: FIFO after limit, BUT: intake is flagged complete before pruning is allowed. `full_intake_transcript` is now explicitly a separate derived variable, not the raw buffer.
- **Retention:** `full_intake_transcript` → `session` (used by Call 2 and potentially available for audit).

---

**Issue 3: reference_library_summary — uncontrolled context bloat risk**

- **What's happening:** The 4 vendor reference design files are ~50KB combined. If passed in full to Call 3, they consume most of Claude's context budget, leaving less space for the scoring output and signal extraction JSON that matters more.
- **Fix:** n8n pre-processes the reference library files at session start into a condensed summary. Extract only: best_fit_profile (3 sentences), contraindications (3 bullets), ehr_alignment label, cloud_alignment label, clinical_validation_maturity label per vendor. Target: ~600 words total across all 4 vendors.
- **Schema update:** `reference_library_summary` type changed to `object` with defined shape — not raw markdown text. Shape: `{epic: {best_fit, contraindications[], ehr_alignment, cloud_alignment, clinical_validation}, aws: {...}, azure: {...}, google: {...}}`.
- **Retention:** `call_only` — vendor library doesn't change across sessions; re-load each call from files.

---

**Issue 4: contradiction_log and evidence_inventory are derived from signal_extraction_output — redundant extraction**

- **What's happening:** Both `contradiction_log` and `evidence_inventory` in Call 3 are subsets of `signal_extraction_output`. Claude could extract them inline, but that requires processing a large JSON blob to find them.
- **Fix:** n8n extracts both after Call 2 completes, using Filter/Code nodes. This is deterministic work that doesn't require Claude — pull contradiction_flag=true records into contradiction_log, pull evidence_provided=true records into evidence_inventory. Pass all three to Call 3 as separate named fields.
- **No schema change needed** — the current schema already treats these as separate fields. This confirms that the n8n intermediate step is required between Call 2 and Call 3.

---

**Issue 5: operator_confirmed_baseline triple-passing — intentional but needs explicit contract**

- **What's happening:** `operator_confirmed_baseline` appears in Call 1 (built), Call 2 (read), and Call 3 (read). This looks redundant but is correct — it's the primary org-specific context that prevents generic output.
- **Resolution:** Not a waste issue — this is required redundancy. The fix is making the data contract explicit so n8n stores it correctly. Exact field list required: `{health_system_name, operator_role_title, assessment_mode, ehr_platform, primary_cloud_provider, primary_ai_use_cases[], stated_budget_range, hard_constraints_identified[]}`.
- **Schema update:** `operator_confirmed_baseline` now has explicit sub-fields documented.

---

**Issue 6: phi_safety_attestation_confirmed source inconsistency**

- **What's happening:** Listed as source=user in Call 1 (correct — operator checks the box) and source=system in Call 2 (correct — n8n reads it from session state). Same value, different source label. This is intentional, not a bug.
- **Resolution:** No change needed. The source label reflects who provides it to THAT call, not where it originated. The data flow notes already explain the source chain.

---

### Naming Standardization

| Variable | Calls | Decision |
|---|---|---|
| `conversation_history` (Call 1) → `full_intake_transcript` (Call 2) | 1→2 | Keep distinct — different formats: array[object] vs string. n8n explicitly converts between them. |
| `evidence_uploads` (Call 1, 2) → `evidence_inventory` (Call 3) | 1,2→3 | Keep distinct — uploads=raw, inventory=processed summary. |
| `phi_safety_attestation_confirmed` | 1, 2 | ✓ Consistent name across all uses. |
| `operator_confirmed_baseline` | 1, 2, 3 | ✓ Consistent name across all uses. |
| `session_id` | 1, 2, 3 | ✓ Consistent name across all uses. |

---

### Final Retention Policy Summary

| Variable | Retention | Max Size | Pruning Strategy |
|---|---|---|---|
| `session_id` | session | 36 chars (UUID) | N/A |
| `health_system_name` | session | ~100 chars | N/A |
| `assessment_mode` | session | enum (4 values) | N/A |
| `conversation_history` | session | 60 message pairs | FIFO after limit; intake flagged complete before pruning allowed |
| `current_domain_questions` | call_only | 5–7 questions | Replaced each turn |
| `public_profile_data` | session | ~500 words | N/A |
| `phi_safety_attestation_confirmed` | session | boolean | N/A |
| `full_intake_transcript` | session | ~10,000 chars | None — preserved until session ends |
| `operator_confirmed_baseline` | session | ~500 chars (8 fields) | N/A |
| `evidence_uploads` | call_only | depends on documents | Cleared after Call 2 completes |
| `signal_extraction_output` | session | ~5,000 chars | N/A |
| `n8n_scoring_output` | session | ~2,000 chars | N/A |
| `contradiction_log` | call_only | ≤43 items (one per signal max) | N/A |
| `evidence_inventory` | call_only | ≤43 items | N/A |
| `reference_library_summary` | call_only | ~600 words (condensed) | Re-derived each session; never persisted |

---

## implementation_reality_check

### implementation_reality

**What was planned (mvp_specs.md, June 14):**
The original architecture described 6 sequential LLM calls:
1. intake_question_generator — generate next adaptive intake question
2. profile_enrichment — interpret public health system profile data
3. workload_classifier — classify AI workload type and draft confirmation
4. vendor_pattern_matcher — match ambition + workload to vendor reference patterns
5. scenario_generator — generate three investment scenarios
6. brief_formatter — assemble the complete CIO-ready Scenario Brief

Scoring: 0–4 Likert scale, confidence as 3-level label (High / Medium / Low).

**What was actually built (June 15 session):**
The 6-call chain was replaced with a fundamentally different 2-prompt architecture backed by a deterministic scoring engine (n8n):

| Built artifact | Role in current architecture |
|---|---|
| `scoring/question_bank.json` | 43 questions × 8 domains with standards alignment + evidence validation per question |
| `specs/rubric.json` (v2.0) | Dual-score architecture: Readiness Score (1–5) + Evidence Confidence Score (0–5) |
| `scoring/evidence_confidence_rules.md` | Complete dual-score model, credibility gap formula, gating rules |
| `prompts/scoring_prompt.md` | Claude's role: signal extraction only — outputs structured JSON for n8n |
| `prompts/interpretation_prompt.md` | Claude's role: report generation after n8n scoring — 9-section report |
| `reference_library/` (4 designs + index + criteria) | Epic, AWS, Azure, Google Cloud vendor reference designs |

**Significant deviations from plan:**

| Area | Original plan | What was built | Why it changed |
|---|---|---|---|
| Scoring scale | 0–4 Likert | 1–5 (Readiness) + 0–5 (Evidence Confidence) | Dual-score model separates claim from evidence |
| Confidence model | High / Medium / Low label | 0–5 numeric Evidence Confidence Score | Makes evidence quality visible and gradable |
| LLM call count | 6 sequential calls | 2 prompt files (scoring + interpretation) | n8n does deterministic scoring; Claude guides + interprets |
| Scorer identity | Claude scores | n8n scores; Claude extracts and interprets | "Do not make GPT the sole scorer" — deterministic architecture |
| Scenario Brief | Separate LLM call (#6) | Integrated as Section 9 of interpretation_prompt | Collapsed to reduce call count and context hand-off risk |
| Vendor library | 3 designs (Epic, AWS, Azure) | 4 designs (added Google Cloud Health AI) | CIO audience requires Google Cloud coverage |
| Evidence model | Document signals upgrade confidence | Per-question evidence validation + safety attestation | Evidence Confidence Score requires structured per-signal tracking |
| Standards alignment | Not in original plan | 4 frameworks per question (NIST AI RMF, WHO Ethics, CHAI, DiMe) | Credibility with health IT governance audience |

**What has NOT been built yet:**
- n8n scoring engine workflow (the deterministic scorer exists only in spec)
- `prompts/scenario_brief_prompt.md` (June 16 build item)
- `templates/` directory (4 template files — June 16 build item)
- No code: no .py, .js, no n8n workflow JSON exported
- End-to-end run-through has not yet occurred

**Current implementation state:** Prompt + specification architecture. Claude runs the intake conversation and signal extraction. n8n handles scoring (not yet built). The full loop has not been tested end-to-end.

---

### user_context_flow_analysis

**How information currently flows through the system (as designed):**

```
[Operator] → intake conversation → [Claude: scoring_prompt.md]
                                           ↓
                              structured JSON signal extraction
                                           ↓
                              [n8n scoring engine — not yet built]
                                           ↓
                      domain scores + evidence scores + gating flags
                                           ↓
                    [Claude: interpretation_prompt.md] + [n8n output]
                                           ↓
                           9-section assessment report
```

**Context that must flow between steps:**
- Intake transcript → scoring_prompt → structured JSON (evidence levels, stated_level per signal, contradictions)
- Scoring JSON + n8n output → interpretation_prompt → final report
- operator_confirmed_baseline is required by BOTH prompts independently

**Current context risk:** The handoff from scoring_prompt output to interpretation_prompt input is defined by schema (structured JSON) but no mechanism exists yet to pass that output to n8n or back to Claude. The data flow between prompts is specified but not wired.

---

### quality_risk_connection

**Original quality risk identified in evaluation design:** Vague, generic, non-specific assessment outputs — scores and recommendations that could apply to any health system.

**How the architectural upgrades address this:**
- Evidence Confidence Score prevents high readiness claims from being taken at face value
- Credibility Gap formula (Readiness − Evidence) makes the gap between claim and evidence visible in every domain
- interpretation_prompt.md enforces a hard specificity rule: every interpretation sentence must contain at least one of the organization's name, EHR, cloud provider, named use cases, governance posture, budget range, or a specific named gap
- Contradiction flagging in scoring_prompt.md surfaces claim-vs-evidence mismatches before the report is written

**New quality risk introduced by architectural change:** The n8n scoring engine does not exist yet. Until it is built, the deterministic scoring step cannot run. If Claude is used as a substitute scorer during testing, the scorer responsibility separation is violated — and the assessment reverts to the original quality risk.

---

### discovered_context_patterns

**Pattern 1: Two-phase context boundary**
The system has a hard boundary at the n8n scoring step. Everything before it (intake → signal extraction) is conversational and qualitative. Everything after it (interpretation → report) is deterministic + interpretive. Context does not naturally flow across this boundary without an explicit data hand-off mechanism.

**Pattern 2: operator_confirmed_baseline is used twice**
The operator's confirmed baseline (EHR, cloud, use cases, mode, budget, constraints) is needed by both the scoring_prompt and the interpretation_prompt. It is not generated by either — it comes from the intake conversation. This is a shared context object that must be explicitly passed to both prompts.

**Pattern 3: evidence_level per signal vs. domain-level aggregation**
The scoring engine needs per-signal evidence levels to compute domain Evidence Confidence Scores. The interpretation prompt receives domain-level aggregates. The per-signal granularity is only relevant to the scorer — the interpreter needs the aggregate + the list of gaps.

**Pattern 4: Contradiction log as a passed artifact**
Contradictions detected in scoring_prompt must survive to interpretation_prompt (Section 6: Contradictions Log). This is currently a field in the signal extraction JSON. It must be preserved through the n8n step and explicitly included in what gets passed to interpretation_prompt.

