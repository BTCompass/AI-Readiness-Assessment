# MVP Technical Specifications
# BT Compass AI Infrastructure Assessment — June 19 Demo Build

---

## development_requirements

**Platform stack:**
- Frontend: Lovable.dev (React app, deployed to custom domain)
- Orchestration: n8n.cloud (managed, no server required)
- AI: Anthropic Claude API (model: claude-sonnet-4-6)
- PDF: PDFco API (or html2pdf.app as fallback)
- DNS: Cloudflare — btcompass.ai → Lovable deployment

**Accounts needed before building:**
1. n8n.cloud account (free trial or starter plan)
2. Anthropic API account + API key
3. Lovable.dev account
4. PDFco account (free tier)
5. Cloudflare account (btcompass.ai DNS management)

**Demo scenario (hardcoded):**
Southside Academic Health Network — synthetic academic medical center. Epic EHR, mature research data assets, smart-room/edge AI ambition, ambient documentation, radiology AI, fragmented governance, recent third-party cybersecurity breach, margin pressure, cancer pavilion timeline. Preloaded public profile used by the intake agent.

---

## integration_specifications

### Claude API (via n8n Anthropic node)
- Authentication: API key stored as n8n credential (never exposed to frontend)
- Model: claude-sonnet-4-6
- Two separate calls:
  1. **Intake Agent call** — conversational, uses n8n AI Agent node with window buffer memory
  2. **Interpretation + Brief call** — single structured HTTP request with full scoring context

### n8n Webhook (frontend ↔ backend)
- Endpoint: POST `https://[n8n-instance]/webhook/btcompass-chat`
- Request body: `{ "session_id": "string", "message": "string", "stage": "intake|complete" }`
- Response body: `{ "response": "string", "intake_complete": boolean, "scores": object|null, "brief": object|null }`

### PDFco API
- Input: HTML string of formatted Scenario Brief + Scorecard
- Output: PDF download URL (valid for 24 hours)
- Called by n8n HTTP Request node after output is compiled

### Frontend ↔ n8n communication
- Frontend sends each chat message via fetch POST to n8n webhook URL
- n8n responds synchronously (within n8n 30s timeout) or via polling
- If response time > 15 seconds: show "Analyzing..." loading state in frontend

---

## data_flow_specifications

### Session initialization
```
Operator loads btcompass.ai/assessment
→ Frontend generates unique session_id (UUID)
→ Frontend sends first message: "Start assessment for [health system name]"
→ n8n initializes session, loads Southside preloaded profile
→ AI Agent responds with welcome + first intake question
```

### Intake phase (Stage 1)
```
Operator sends message
→ n8n webhook receives {session_id, message, stage: "intake"}
→ n8n AI Agent node (Claude, window buffer memory):
    - Reads full conversation history
    - Generates next question or follow-up
    - Detects when all required fields are answered
    - When complete: outputs {intake_complete: true, structured_fields: {...}}
→ n8n checks: is intake_complete == true?
    - No: return {response: "next question", intake_complete: false}
    - Yes: proceed to scoring engine
```

### Scoring engine (Stage 2 — n8n nodes)
```
n8n receives structured_fields from intake agent
→ For each of 8 domains:
    - Evaluate 3–5 rubric signals from structured_fields (If/Switch nodes)
    - Assign signal value (0–4) to each signal
    - Calculate domain score = weighted average of signals (Set node)
    - Assign readiness color (If node):
        0–1.0 → Red
        1.1–2.0 → Orange
        2.1–3.0 → Yellow
        3.1–3.5 → Yellow-Green
        3.6–4.0 → Green
    - Assign confidence level (If node):
        ≥80% direct answers → High
        50–79% direct answers → Medium
        <50% direct answers → Low
→ Compile scoring_data object (all 8 domains with scores, colors, confidence)
```

### Interpretation + Brief generation (Stage 3 — Claude API call)
```
n8n HTTP Request node → Claude API
System prompt: [see prompt specifications below]
User message: JSON containing:
    - health_system_profile (Southside preloaded data)
    - intake_responses (structured fields from Stage 1)
    - scoring_data (all 8 domain scores, colors, confidence from Stage 2)

Claude outputs JSON:
{
  "domain_interpretations": [
    {
      "domain": "Governance and Accountability",
      "score": 1.8,
      "color": "Orange",
      "confidence": "Medium",
      "interpretation": "...",
      "evidence_gaps": ["...", "..."],
      "recommended_next_action": "...",
      "rfp_requirement_categories": ["...", "..."]
    },
    ... (8 domains total)
  ],
  "workload_classification": "Enterprise AI Foundation",
  "scenario_brief": {
    "current_state_summary": "...",
    "scenario_1": { "name": "Controlled Pilot Acceleration", ... },
    "scenario_2": { "name": "Department/Service-Line Scale", ... },
    "scenario_3": { "name": "Enterprise AI Foundation", ... },
    "scenario_comparison_table": { ... },
    "recommended_path": { "scenario": "...", "rationale": "...", "prerequisites": [...], "avoid": [...] }
  },
  "executive_summary": "...",
  "rfp_starter_categories": ["...", "...", "...", "...", "..."]
}
```

### Output delivery (Stage 4)
```
n8n compiles complete output object
→ n8n HTTP Request → PDFco API → generates PDF → returns download_url
→ n8n webhook response to frontend:
{
  "intake_complete": true,
  "scores": { scoring_data },
  "brief": { complete brief object },
  "pdf_url": "https://..."
}
→ Frontend navigates to output page
→ Displays: Scorecard + Scenario Brief + Executive Summary + RFP Categories
→ PDF download button uses pdf_url
```

---

## platform_implementation_requirements

### n8n Workflow Structure (nodes in order)

1. **Webhook Trigger** — POST /btcompass-chat, responds immediately
2. **Switch node** — routes by `stage` field (intake vs. scoring)
3. **AI Agent node** (intake stage)
   - Model: Anthropic Claude (claude-sonnet-4-6)
   - Memory: Window Buffer Memory (last 20 messages)
   - System prompt: intake system prompt (see below)
   - Output parser: JSON parser to detect intake_complete flag
4. **If node** — checks intake_complete == true
5. **Set nodes** (one per domain × 8 domains) — scoring signal evaluation
6. **Set node** — compiles scoring_data object
7. **HTTP Request node** — calls Claude API for interpretation + brief
8. **HTTP Request node** — calls PDFco API for PDF generation
9. **Respond to Webhook** — returns complete output

### n8n Credentials to configure
- Anthropic API: add as "Anthropic" credential with API key
- PDFco API: add as HTTP Header Auth credential
- No database credentials needed for demo (in-memory session)

### n8n AI Agent system prompt (intake)

```
You are an AI Infrastructure Assessment Advisor for health systems. You are helping a health system IT leader complete a structured intake assessment that will produce a readiness scorecard and AI Infrastructure Investment Scenario Brief.

HEALTH SYSTEM PROFILE (preloaded):
Southside Academic Health Network
- 847-bed academic medical center, Level I trauma, NCI-designated cancer center
- Epic EHR (live 4 years), Clarity analytics, Interconnect API enabled
- AWS primary cloud (mature), Azure secondary (research), on-prem legacy remaining
- Research data infrastructure: institutional data warehouse, REDCap, OMOP CDR
- AI currently active: ambient documentation (nuance DAX), radiology AI (3 FDA-cleared tools), early smart-room/Artisight pilot (12 rooms)
- Recent event: third-party vendor cybersecurity breach (6 months ago, contained but unresolved vendor liability)
- Cancer pavilion opening: 18 months, driving infrastructure decisions
- Budget signal: $12M-$18M planning envelope for AI infrastructure
- Governance: AI steering committee formed but no formal approval process; CISO engaged post-breach; no CMIO clinical AI policy
- Margin pressure: -2.3% operating margin, CFO scrutiny on technology ROI

BEHAVIOR RULES:
1. Ask ONE question at a time. Wait for the answer.
2. Adapt based on answers — reference Epic, the cybersecurity breach, the cancer pavilion when relevant.
3. Skip questions already answered by the preloaded profile.
4. Do NOT ask for PHI, patient data, employee personal data, or NDA-restricted information.
5. When all required fields are answered, output a JSON object with intake_complete: true.

REQUIRED INTAKE FIELDS:
- confirmed_ai_ambition: pilot | service_line_scale | enterprise_foundation
- priority_workloads: list of active or priority AI use cases
- governance_state: none | forming | partial | operational
- ciso_involvement: none | reactive | active
- clinical_ai_oversight: none | informal | formal
- model_inventory_exists: true | false | unknown
- post_deployment_monitoring: none | partial | formal
- data_readiness: poor | partial | good | strong
- interoperability_gaps: list or none
- infrastructure_scalability: limited | moderate | strong
- edge_device_readiness: none | pilot | scaling
- operating_model_readiness: low | medium | high
- change_management_capacity: low | medium | high
- rfp_experience: none | limited | experienced
- procurement_requirements_defined: true | false | partial
- budget_range: confirmed or revised from preloaded signal
- hard_constraints: list (e.g., margin_pressure, cancer_pavilion_timeline, breach_liability)
- strategic_urgency: low | medium | high

COMPLETION OUTPUT FORMAT:
When all fields are answered, respond with:
"Thank you — I have enough to generate your assessment. Here is my summary of what I've confirmed: [2-3 sentence summary]. Generating your readiness scorecard and Scenario Brief now."

Then output (as the final part of your message):
```json
{
  "intake_complete": true,
  "structured_fields": { [all required fields with values] }
}
```
```

### Claude interpretation prompt (HTTP Request node)

```
You are producing a structured AI infrastructure readiness assessment for a health system CIO.

You will receive:
1. Health system profile (confirmed baseline)
2. Intake responses (operator-provided)
3. Domain scores calculated by the scoring engine (DO NOT recalculate scores — use these exactly)

Your job is to write:
- One interpretation paragraph per domain (3-5 sentences, specific to this organization)
- Evidence gaps per domain (2-4 specific questions that remain unanswered)
- Recommended next action per domain (one concrete action)
- RFP requirement categories per domain (2-3 specific categories)
- Three investment scenarios (Controlled Pilot Acceleration, Department/Service-Line Scale, Enterprise AI Foundation)
- Recommended path with rationale specific to this organization's inputs
- Executive summary (3-4 sentences, CIO-ready language)
- RFP starter categories (5-7 high-level requirement categories)

RULES:
- Use the scores exactly as provided. Do not revise them.
- Be specific to this organization. Do not write generic statements that could apply to any hospital.
- Acknowledge the cybersecurity breach and governance gaps in the interpretation.
- Acknowledge the cancer pavilion timeline as a constraint.
- The recommended path should be honest — if the organization is not ready for the recommended scenario, say so and name the prerequisites.
- Write in CIO-ready language: concise, executive-readable, practical.
- Output valid JSON matching the schema provided.

[Attach scoring_data and intake_responses as JSON in the user message]
```

---

## scoring_rubric_signals

### Domain 1: AI Strategy and Use-Case Clarity
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Ambition clarity | confirmed_ai_ambition | not_stated | vague | pilot | service_line | enterprise |
| Workload prioritization | priority_workloads | none | 1 vague | 1-2 specific | 3-4 specific | 5+ prioritized |
| Strategic urgency | strategic_urgency | low | low | medium | medium | high |

### Domain 2: Governance and Accountability
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Governance state | governance_state | none | forming | partial | partial | operational |
| CISO involvement | ciso_involvement | none | none | reactive | active | active |
| Clinical oversight | clinical_ai_oversight | none | none | informal | formal | formal |
| Model inventory | model_inventory_exists | false | false | unknown | true | true |
| Post-deployment monitoring | post_deployment_monitoring | none | none | partial | partial | formal |

### Domain 3: Data Readiness and Interoperability
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Data readiness | data_readiness | poor | poor | partial | good | strong |
| Interoperability gaps | interoperability_gaps | many | several | some | few | none |
| EHR platform maturity | (from profile: Epic live 4 years) | — | — | — | 3 | — |

### Domain 4: Cybersecurity and Third-Party/Vendor Risk
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Recent incident | (from profile: breach 6mo ago) | — | 0 | — | — | — |
| CISO involvement | ciso_involvement | none | reactive | reactive | active | active |
| Third-party risk process | (inferred from governance_state) | none→0 | forming→1 | partial→2 | partial→2 | operational→4 |

### Domain 5: Clinical Safety and Oversight
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Clinical oversight | clinical_ai_oversight | none | none | informal | formal | formal |
| CMIO involvement | (inferred from governance_state + clinical_ai_oversight) | — | — | — | — | — |
| Human-in-loop requirements | (inferred from governance_state) | none→0 | forming→1 | partial→2 | partial→2 | operational→4 |

### Domain 6: Infrastructure Scalability
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Infrastructure scalability | infrastructure_scalability | limited | limited | moderate | strong | strong |
| Edge device readiness | edge_device_readiness | none | none | pilot | pilot | scaling |
| Cloud maturity | (from profile: AWS mature) | — | — | — | 3 | — |

### Domain 7: Operating Model and Change Readiness
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| Operating model readiness | operating_model_readiness | low | low | medium | medium | high |
| Change management capacity | change_management_capacity | low | low | medium | medium | high |
| Hard constraints | hard_constraints | many→0 | several→1 | some→2 | few→3 | none→4 |

### Domain 8: RFP/Procurement Readiness
| Signal | Intake field | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| RFP experience | rfp_experience | none | none | limited | limited | experienced |
| Requirements defined | procurement_requirements_defined | false | false | partial | partial | true |
| Governance gate for procurement | (inferred from governance_state) | none→0 | forming→1 | partial→2 | partial→2 | operational→4 |

---

## frontend_implementation_requirements

### Page 1: Landing (btcompass.ai)
- BT Compass AI logo + tagline
- Problem statement: "Health system CIOs are making AI infrastructure decisions without a structured framework."
- CTA button: "Start Your AI Infrastructure Assessment"
- Brief credibility copy (domain expertise, not generic AI tool)
- Link to breakthroughcompass.com for full company context

### Page 2: Intake chat (/assessment)
- Session initialized on page load (generate UUID, store in sessionStorage)
- Chat interface: user message input at bottom, conversation history above
- Organization name pre-populated from URL param if provided (?org=Southside)
- Each message: POST to n8n webhook, display response when received
- Loading indicator while waiting for n8n response
- PHI attestation banner (always visible): "Do not enter patient data, PHI, employee data, or NDA-restricted information."
- When intake_complete = true: show "Assessment complete — generating your scorecard" → navigate to output page

### Page 3: Output (/results?session=[id])
**Section 1: Executive Summary**
- 3-4 sentence summary at top, large readable font

**Section 2: Readiness Scorecard**
- 8 domain cards in 2×4 grid
- Each card: domain name, score (X.X / 4), color badge, confidence level, 1-line interpretation
- Click to expand: full interpretation, evidence gaps, next action, RFP categories

**Section 3: Scenario Brief**
- Three scenario cards (Pilot Acceleration, Service-Line Scale, Enterprise Foundation)
- Recommended path highlighted with rationale
- Comparison table (6 dimensions × 3 scenarios)

**Section 4: RFP Starter Categories**
- 5-7 requirement categories listed with brief description

**Section 5: Actions**
- "Download Full Brief (PDF)" button → triggers pdf_url download
- "Start New Assessment" link

### Page 4: No separate page needed — PDF download from output page

---

## human_in_loop_requirements

| Gate | Implementation | Behavior |
|---|---|---|
| PHI acknowledgment | Banner on chat page (always visible) + confirmation on any document-related question | Claude is instructed to never accept PHI; banner is always shown |
| Workload classification confirmation | Claude asks "I'm classifying this as [X] — confirm or revise?" before generating | n8n waits for confirmation response before triggering scoring |
| Output review | Output page is shown before PDF is offered | Operator sees full scorecard before downloading |

---

## quality_risk_testing_specifications

### Test scenario: Southside Academic Health Network
**Input:** Fragmented governance + recent cybersecurity breach + high AI ambition + cancer pavilion timeline + margin pressure
**Expected scoring:**
- Governance: ≤2.0 (Orange) — fragmented governance
- Cybersecurity: ≤1.5 (Orange/Red) — recent breach
- Infrastructure: ~3.0 (Yellow) — AWS mature, but edge pilot only
- RFP Readiness: ≤2.0 (Orange) — no formal procurement process

**Pass criteria:**
- [ ] Governance domain scores Orange or Red (not Green)
- [ ] Cybersecurity domain scores Orange or Red
- [ ] Recommended path surfaces governance as a prerequisite, not an afterthought
- [ ] Three scenarios are meaningfully differentiated (not three versions of the same advice)
- [ ] Domain expert reviewing output would say "this is more specific and useful than HIMSS INFRAM"

### Quality risk validation questions (show to advisor after demo)
1. Does anything feel fatally wrong about how health systems work?
2. Are the domain scores calibrated correctly for this type of organization?
3. Would a CIO find the scorecard useful in a governance or board conversation?
4. Is the Scenario Brief specific enough to this organization, or does it feel generic?

---

## error_handling_requirements

| Error condition | Handling |
|---|---|
| n8n webhook timeout (>30s) | Frontend shows retry button; n8n logs error |
| Claude API failure | n8n catches error, returns "Assessment temporarily unavailable — please retry" |
| PDF generation failure | Skip PDF, show "PDF unavailable — copy output manually" message; assessment still usable |
| Incomplete intake (user abandons mid-session) | No scoring triggered; session data not persisted |
| Claude returns invalid JSON | n8n code node validates JSON before passing to scoring; fallback to raw text display |

---

## success_criteria_and_testing

**Pre-demo checklist:**
- [ ] btcompass.ai loads branded landing page
- [ ] "Start Assessment" navigates to chat page
- [ ] Chat message sends and receives Claude response in <15 seconds
- [ ] Intake completes in 8–12 exchanges for the Southside scenario
- [ ] Scoring engine calculates all 8 domain scores correctly
- [ ] Output page displays scorecard with correct colors
- [ ] Scenario Brief contains three distinct scenarios
- [ ] PDF downloads successfully
- [ ] Full demo arc (problem → intake → scorecard → brief → PDF) runs in under 10 minutes

**Demo run checklist (June 18 dry run):**
- [ ] Run full Southside scenario end-to-end
- [ ] Verify governance and cybersecurity domains score Orange or Red
- [ ] Verify recommended path mentions governance prerequisites
- [ ] Verify PDF is readable and CIO-ready
- [ ] Verify 8-minute demo arc fits the presentation
- [ ] Prepare fallback: screenshot of output page if live demo has connectivity issues
