# Context Management Design
# Note: Derived from ideation/problem_definition — context_management workflow not yet run

## implementation_reality_check

See architecture_spec.md > implementation_update.

## llm_call_inventory

| # | Call Name | Purpose | Input Fields | Output Fields |
|---|-----------|---------|-------------|--------------|
| 1 | intake_question_generator | Generate next adaptive intake question based on prior answers | conversation_history, remaining_fields, health_system_name | next_question, field_targeted |
| 2 | profile_enrichment | Interpret and summarize preloaded public health system profile data | health_system_name, raw_profile_data | profile_summary (beds, EHR, specialties, AI signals) |
| 3 | workload_classifier | Classify AI workload type and draft confirmation message for operator | intake_responses, profile_summary | workload_classification (pilot/dept/enterprise), confidence, confirmation_prompt |
| 4 | vendor_pattern_matcher | Match organization's ambition + workload type to curated vendor reference patterns | workload_classification, ambition_level, curated_library | relevant_vendor_patterns (2–4 patterns with rationale) |
| 5 | scenario_generator | Generate three investment scenarios with full detail | intake_responses, profile_summary, workload_classification, vendor_patterns | three_scenarios (each: infrastructure implications, governance requirements, risks, budget fit, vendor patterns, RFP implications) |
| 6 | brief_formatter | Assemble and format the complete CIO-ready Scenario Brief | all prior outputs, health_system_name | final_brief (executive language, all sections) |

## context_schemas

### Shared intake context (written by call 1, read by calls 3, 5, 6)
- health_system_name
- ai_ambition_level (pilot / department_scale / enterprise)
- workload_types (list)
- readiness_responses (governance, data, infrastructure, budget posture)
- budget_range
- constraints (regulatory, organizational, timeline)
- optional_pasted_summary

### Profile context (written by call 2, read by calls 3, 4, 5, 6)
- profile_summary (beds, EHR vendor, specialties, patient volume, existing AI use cases, public AI signals)

### Classification context (written by call 3, read by calls 4, 5, 6)
- workload_classification
- classification_confidence
- operator_confirmation_status

### Vendor pattern context (written by call 4, read by calls 5, 6)
- relevant_vendor_patterns

### Scenario context (written by call 5, read by call 6)
- three_scenarios
