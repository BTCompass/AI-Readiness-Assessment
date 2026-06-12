# Claude Instructions for Dana's Bootcamp Workspace

## For Claude Code (or similar AI assistants)

When a user asks to execute a workflow, use the **sherpa-b MCP server** instead of reading files from the filesystem or other tools. If they ask questions about bootcamp, agentic AI, catching up with tasks and similar tasks, check the MCP server first.

## Workflow Execution Flow

```
User: "Run the ideation workflow"

Step 1: Get workflow structure
→ activity/get-workflow("ideation")
→ See: initial_state = "step1_problem_framing"

Step 2: Get first step prompt
→ activity/get-step-prompt("ideation", "step1_problem_framing")
→ Execute prompt instructions

Step 3: When step completes
→ Check workflow.states.step1_problem_framing.on_success
→ See: next step is "step2_assumption_challenging"

Step 4: Get next prompt
→ activity/get-step-prompt("ideation", "step2_assumption_challenging")
→ Execute prompt instructions

Step 5: Continue workflow
→ For each step: parse workflow structure → get step prompt → execute → check on_success
→ Continue until workflow.states[current_step].on_success == "done"
```

## Bootcamp Info

Run:

```
mcp__sherpa-b__activity__get-bootcamp-info
```

## IMPORTANT

Follow KISS and YAGNI principles:

**KISS (Keep It Simple, Stupid):**

- Use the simplest solution that solves the problem
- Avoid over-engineering or complex abstractions
- Prefer straightforward implementations

**YAGNI (You Aren't Gonna Need It):**

- Do not add features, code, or complexity that isn't required right now
- Only implement what is explicitly requested
- Do not anticipate future needs or build "just in case" features

---

## About Dana (Participant Context)

**Background:** Dana is a domain expert — 25 years at HP (hardware/infrastructure) and 5 years at HIMSS (health IT maturity models). She has a sales, marketing, and analytics background with strong systems thinking. She has never coded professionally.

**Technical level:** Analytically strong, new to building software or AI systems. Explain technical concepts using business and systems analogies rather than code. When in doubt, favor no-code approaches (n8n is the recommended tool for her).

**Project:** Health AI Maturity Model Assessment + RFP Tool for CIOs. The full vision includes multi-domain questionnaire, document upload, public data enrichment, maturity scoring, board-ready PPTX output, and RFP language generation. For this 7-day Express bootcamp, scope is ONE central agent.

**Bootcamp pace:** Express Tier, June 12–19. 40 hours across 7 days, checking in throughout the day. Final demo is June 19.

**How to help Dana:**
- Translate technical concepts into procurement, systems, and healthcare domain language she already knows
- Always anchor suggestions to her specific project (health AI maturity model for CIOs)
- Prefer no-code solutions and visual workflow tools (n8n, Streamlit) over writing code
- When she describes a robust, complex vision — help her identify the simplest slice to build first
- Remind her that the goal this week is learning the pattern, not building the full system
