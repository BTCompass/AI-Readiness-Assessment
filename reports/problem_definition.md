# Problem Definition

## problem_statement
Health system CIOs are making AI infrastructure investment, governance, and procurement decisions without a structured intelligence framework — entering vendor conversations, budget discussions, and RFP processes from a blank page. The gap is not awareness of AI; it's the absence of a current-state readiness picture, market-informed reference patterns, and governance-grounded investment scenarios before commitments are made. We have not found a purpose-built tool that combines these capabilities for health-system CIOs.

## target_users
- **Primary operator:** Senior individual contributor, first or second line manager within IT/digital/strategy — the person delegated to do the prep work for the CIO
- **Primary beneficiary:** The CIO, who consumes the Decision Pack outputs and uses them in executive, vendor, and governance conversations
- Role: Health system IT/digital leader or trusted senior IC within a hospital, health system, or integrated delivery network
- Context: Tasked by the CIO to assess AI infrastructure readiness and produce a structured decision package before vendor, governance, or procurement conversations
- Technical level: Operationally sophisticated, familiar with internal systems and stakeholders, but may not be AI-infrastructure experts
- Specific needs: A structured workflow to gather inputs, assess readiness, and produce CIO-ready outputs without starting from scratch

## current_state

### user_process
1. CEO/board/clinical leader/vendor triggers AI interest
2. CIO identifies whether this is a pilot, scale-up, or enterprise strategy
3. IT/digital team inventories existing AI use cases and vendor activity
4. Governance group reviews risk, privacy, security, clinical impact
5. Architecture/data teams assess current environment
6. Vendor discovery begins — often too early
7. Finance asks for ROI, budget, and prioritization
8. CIO narrows to scenarios: pilot, department scale, or enterprise foundation
9. Procurement/legal/security translate needs into requirements
10. RFP/vendor evaluation begins — if the organization is ready
11. Pilot/deployment requires continuous monitoring, evaluation, feedback, and controls

### user_existing_tools
- Generic AI maturity surveys (e.g., HIMSS INFRAM — focused on technology/clinician intersection, not AI infrastructure)
- Vendor-provided readiness assessments (biased toward vendor's own products)
- Internal ad hoc assessments by IT/architecture teams
- Consultant-led discovery engagements (expensive, slow, not repeatable)
- We have not found a purpose-built tool that combines these capabilities for health-system CIOs

### trigger
CEO, board, clinical leader, or vendor creates pressure to act on AI — often before the CIO has a structured view of their own environment or readiness.

### frequency
Major AI infrastructure decisions happen 1–2x per year per organization, but the pressure to engage is constant and building. Each decision cycle is high-stakes and largely non-repeatable with current approaches.

### friction_points
1. **Vendor discovery starts before internal requirements are mature** — CIOs sit through vendor pitches without knowing what questions to ask or what their own workload portfolio looks like
2. **Governance/risk review is too shallow or too late** — clinical oversight, privacy posture, and equity considerations are reviewed after momentum is already built
3. **Infrastructure/budget decisions are made before the CIO understands the AI workload portfolio** — investments are misaligned to actual use case demands

## assumptions_analysis

### Initial Assumptions Identified
1. The CIO will operate this tool directly
2. Public data alone can build a meaningful health system profile
3. The MVP needs to produce all 10 components of the CIO Decision Pack
4. Vendor reference pattern intelligence requires live web search at runtime

### Validated Constraints
- No PHI or patient-level data may be accepted under any circumstances
- No HIPAA compliance claims in MVP unless technical, legal, and operational controls are verified
- Tool provides readiness analysis and draft considerations — not legal, clinical, or final procurement advice
- All data sources must carry metadata: source type, name, date, confidence level, and user confirmation status
- Outputs are internal-only by default; vendor-facing exports require a separate sanitized export step
- The MVP output is a single artifact: the **AI Infrastructure Investment Scenario Brief** — not the full 10-component Decision Pack

### Flexible Assumptions
- **CIO as primary operator → Refined:** The actual operator is a senior IC or first/second line manager delegated by the CIO. The CIO is the primary beneficiary and consumer of outputs
- **20-minute intake → Refined:** Full intake is under 2 hours — more realistic for meaningful inputs without being burdensome
- **Full Decision Pack for MVP → Refined:** All intelligence (profile, readiness, vendor patterns, risk/gaps, governance, RFP considerations) is embedded inside the single Scenario Brief — not built as separate deliverables
- **Live web search as primary vendor intelligence engine → Refined:** A small curated library of public vendor reference patterns is the primary source, updated periodically; live web search is an optional "refresh/check for newer evidence" function only

### Beliefs to Test
- CIOs and senior ICs will trust AI-generated investment scenarios enough to use them as a basis for executive, board, and vendor conversations
- The agent can accurately classify AI workloads (pilot vs. department scale vs. enterprise foundation) from lightweight intake responses
- Public data sources (CMS, state filings, hospital compare, annual reports, vendor websites) are rich enough to seed a meaningful health system profile without extensive manual research
- A curated vendor reference library can be kept current and credible enough that CIOs won't question its relevance

## solution_hypotheses

### Hypothesis 1
**Name:** AI as Guided Form (Level 1 — AI as Assistant)
**What AI does autonomously:** Pulls public profile data by health system name, maps inputs to scenario templates, generates scenario narrative and comparison table, formats the brief
**Human touchpoints:** Operator completes intake form, reviews and edits output, approves before sharing
**Interaction pattern:** Form → generate → review → export
**Scope boundaries:** Does not ask follow-up questions or adapt mid-session based on operator responses

### Hypothesis 2
**Name:** AI as Conversational Interviewer (Level 2 — AI as Collaborator) ✅ Selected
**What AI does autonomously:** Asks tailored intake questions one at a time, adapts based on answers, drafts sections progressively, flags gaps, confirms key classifications before generating, integrates curated vendor reference patterns into scenarios
**Human touchpoints:** Operator responds to questions, confirms key classification (e.g., "I'm classifying this as Department/Service-Line Scale — confirm or revise?"), reviews and approves final brief
**Interaction pattern:** Conversation → structured field capture → assumption confirmation → scenario generation → operator review → final brief
**Scope boundaries:** No live web search; no real document uploads (operator may paste a short summary or use sanitized sample text); recommendation is a draft starting point, not a final decision

### Hypothesis 3
**Name:** AI as Autonomous Analyst (Level 3 — AI as Agent)
**What AI does autonomously:** Full public data lookup, workload classification, vendor pattern matching, scenario generation, recommendation with rationale, brief formatting — from minimal inputs
**Human touchpoints:** Minimal intake (3–5 inputs), final review and export approval
**Interaction pattern:** Minimal input → autonomous research + generation → output delivery → human review
**Scope boundaries:** No document uploads; no governance interviews; operates with limited human interaction during generation

## selected_solution

### chosen_hypothesis
Hypothesis 2: AI as Conversational Interviewer (Level 2 — AI as Collaborator). Selected because it balances autonomy with operator control, is feasible for a no-code build in 7 days, produces a demo-able artifact a CIO would recognize as genuinely useful, and naturally mirrors how Claude Code and n8n workflows operate.

### solution_logic
If we implement a conversational AI interviewer that guides a health system operator through structured intake and generates an AI Infrastructure Investment Scenario Brief, it will produce a buyer-owned investment decision artifact before the CIO commits to vendors, budget, or RFPs — because the AI handles the research synthesis, workload classification, and scenario generation that currently has no structured process, while keeping the human in control of key classifications and final review.

### autonomous_capabilities
- Ask one structured intake question at a time, adapting lightly based on operator responses
- Look up preloaded public health system profile data by organization name
- Store responses in a structured schema: health system identity, AI ambition level, workload types, current-state readiness, budget range, constraints
- Classify AI workload type (pilot / department scale / enterprise) and surface for operator confirmation before proceeding
- Match ambition and workload type to relevant patterns in the curated vendor reference library
- Generate three investment scenarios: Controlled Pilot Acceleration, Department/Service-Line Scale, Enterprise AI Foundation
- For each scenario: infrastructure implications, governance requirements, risks, budget fit, vendor reference patterns, procurement/RFP implications
- Make a recommended path with rationale
- Format the complete AI Infrastructure Investment Scenario Brief in CIO-ready language

### human_touchpoints
- Operator answers intake questions one at a time (approximately 2-hour session)
- Operator may paste a short document summary in lieu of a file upload
- Operator confirms or revises AI's workload classification before scenario generation begins
- Operator reviews completed Scenario Brief before export
- Operator approves any vendor-safe sanitized export as a separate step

### interaction_pattern
Conversation → structured field capture → assumption confirmation ("I'm classifying this as Department/Service-Line Scale — confirm or revise?") → scenario generation → operator review → final brief

### success_metrics
- Complete Scenario Brief generated from a ~2-hour intake session
- CIO can use the brief in executive, board, and vendor conversations without starting from scratch
- Time from AI interest trigger to structured decision artifact: days instead of months
- Demonstrable end-to-end in 8 minutes for the Final Demo on June 19

### scope_boundaries
**Included:**
- Guided intake conversation (one question at a time)
- Public health system profile lookup from preloaded data
- Workload classification with operator confirmation
- Curated vendor reference pattern matching
- Three-scenario generation with full detail per scenario
- Recommended path with rationale
- CIO-ready formatted brief

**Excluded (Phase 2):**
- Real internal document uploads (operator may paste a short summary)
- Live web search as primary engine (only as optional refresh)
- Legal, clinical, or final procurement advice
- Full 10-component CIO Decision Pack
- HIPAA compliance claims

## process_requirements

### process_inputs
- Health system name (used for public profile lookup)
- AI ambition level (operator-stated: pilot, department scale, or enterprise)
- AI workload types (e.g., ambient AI, clinical decision support, imaging, revenue cycle)
- Current-state readiness responses (lightweight: governance, data, infrastructure, budget posture)
- Budget range (rough order of magnitude)
- Constraints (regulatory, organizational, timeline)
- Optional: pasted short document summary (strategy excerpt, architecture note, etc.)

### process_outputs
AI Infrastructure Investment Scenario Brief containing:
1. Current-state summary (health system profile + ambition + readiness posture)
2. Three investment scenarios with: infrastructure implications, governance requirements, risks, budget fit, vendor/reference-pattern implications, procurement/RFP implications
3. Recommended path with rationale and prerequisites
4. CIO-ready executive language throughout

## experiment_design

### core_assumption
The AI can take lightweight intake answers — health system public profile, AI ambition level, workload type, readiness posture, and budget range — and generate three credible, differentiated investment scenarios with enough specificity that a health system expert would find them useful and not fatally wrong.

### test_approach
1. Select one real health system with a publicly available profile (mid-size regional system or academic medical center)
2. Simulate the intake conversation with plausible answers based on public signals
3. Run the test prompt through Claude to generate the AI Infrastructure Investment Scenario Brief
4. Send the brief to 2–3 expert advisors from Dana's network (HP/HIMSS contacts with health system exposure) within 24 hours, with 4 structured review questions
5. Incorporate feedback to identify gaps, wrong assumptions, and language that doesn't land

### mock_data_examples
Representative test inputs to use:
- **Typical case:** Mid-size regional health system (400–800 beds, Epic EHR, AWS partnership, 2–3 existing AI pilots in radiology or revenue cycle, moderate AI ambition, $2–5M budget range, governance in early stages)
- **Edge case:** Large academic medical center with aggressive AI ambition but fragmented governance and a recent cybersecurity incident — tests whether the AI correctly surfaces governance as a prerequisite rather than jumping to Enterprise Foundation

### test_scenarios
- Basic functionality: Does the AI generate three meaningfully differentiated scenarios (not three versions of the same advice)?
- Classification accuracy: Does the AI correctly map the inputs to the right starting scenario (pilot vs. scale vs. enterprise)?
- Specificity: Are vendor reference patterns and infrastructure implications specific enough to be actionable, not generic?
- Executive readiness: Would a CIO read this language and find it credible, or does it sound like a generic AI output?

### success_criteria
Advisors review the Scenario Brief and answer four questions:
1. Does anything feel fatally wrong or dangerously naive about how health systems actually work?
2. Would a CIO find this useful, or would they dismiss it as generic?
3. What's missing that would make this credible?
4. Would you be comfortable if a senior IT leader at your organization received this?

**Acceptable threshold:** 2 of 3 advisors confirm nothing is fatally wrong AND at least one output section would be useful to a CIO as a starting point. Any fatal gaps identified become fixes before the full build.

### learning_goals
- Validate Dana's domain model — surface any critical assumptions about health system operations that are wrong or missing
- Confirm the AI can differentiate scenarios based on inputs, not just produce generic advice
- Identify which sections of the Scenario Brief need the most domain refinement (governance language, vendor patterns, procurement implications)
- Determine whether the output tone is executive-ready or needs significant editing

## desired_state

### user_success_criteria
The CIO walks into AI infrastructure investment, governance, vendor, and procurement conversations with a structured CIO AI Infrastructure Decision Pack that includes:
- Health system profile (size, specialties, patient volume, workforce, AI ambition)
- AI ambition classification and workload map
- Vendor reference design intelligence (normalized from public sources)
- Readiness assessment across 7–8 governance and infrastructure domains
- Risk and gap register
- Governance readiness map
- Investment scenarios (pilot, department scale, enterprise foundation) with trade-offs and prerequisites
- RFP considerations memo
- Executive-ready PowerPoint scenario deck
- Role-based outputs: CIO executive deck, governance/risk brief, technical appendix, procurement/RFP memo, vendor-safe export

### expected_impact
- CIO enters vendor conversations with a prepared buyer's position, not a blank page
- Governance reviews happen before commitments, not after
- Infrastructure and budget decisions are grounded in the organization's actual workload portfolio and readiness gaps
- RFP language reflects the organization's specific requirements, not generic boilerplate
- Time from AI interest trigger to structured decision is compressed from months to days

### constraints
1. No PHI or patient-level data — tool must not require or accept it
2. Data sources: public hospital data, CIO/team-entered organizational data, approved non-PHI uploaded documents, public vendor reference designs only
3. Upload workflow must warn against PHI, employee personal data, and NDA-restricted materials; sensitive-data screening required before agent analysis
4. Data source separation required with metadata: source type, source name, date, confidence level, user confirmation status
5. Outputs are role-based and internal-only by default; vendor-facing exports require a separate sanitized export step
6. MVP must not claim HIPAA compliance unless technical, legal, and operational controls are verified
7. Tool provides readiness analysis, scenarios, risks, gaps, and draft considerations — not legal, clinical, or final procurement advice
8. Low organizational lift: full intake under 2 hours, document prep under 1–2 hours, stakeholder questions under 45 minutes per group
