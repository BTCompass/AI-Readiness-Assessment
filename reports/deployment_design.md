# First Deployment Design

## testing_reality_check

**Who has tested it:** Dana only. No external testers.

**How testing happened:** Synthetic data scenarios run by Dana in her development environment (Claude Code + MCP server). Two health system profiles tested: Ridgeline Health System and one other.

**What scenarios were covered:** Structured intake responses fed into the scoring engine. Output reviewed for correctness against rubric logic.

**Gap between theoretical coverage and reality:** Dana knows the domain deeply (25 years HP, 5 years HIMSS). She writes synthetic inputs that match the scoring model's expectations. A real user — a CIO's IT director or VP of Infrastructure — would answer intake questions in their own language, may not know what "stated level" or "evidence confidence" means, and may interpret output labels differently than intended.

---

## deployment_purpose

**Quality risk:** Output language and intake question framing are calibrated to Dana's domain expertise, not validated by real target users.

**Why current testing hasn't exposed this:** Dana runs all tests herself. She unconsciously avoids edge cases and interprets outputs generously. No external perspective has touched the tool.

**How deployment helps:** Putting the tool in front of one real CIO or health IT delegate — without Dana coaching them through it — will reveal whether the intake questions are clear, whether the output language resonates, and whether the readiness labels match their mental model.
