# BT Compass AI — Vendor Reference Design Library Index

## metadata

| Field | Value |
|---|---|
| Library version | 1.0 |
| Last updated | 2026-06-15 |
| Maintained by | BT Compass |
| Update cadence | Quarterly or on material product release |
| Source types | Vendor public documentation, architecture guides, reference architectures, press releases, analyst coverage |
| Confidence note | All entries reflect publicly available information. Health systems should validate against current vendor contracts, roadmaps, and implementation guides before procurement. |

---

## reference_designs

| File | Vendor | Coverage | Best-fit profile |
|---|---|---|---|
| [epic_ai_ecosystem.md](epic_ai_ecosystem.md) | Epic Systems | Epic Cognitive Computing, AI Marketplace, DAX Copilot, Cheers, NLP models | Health systems already on Epic with active optimization roadmap |
| [aws_health_ai.md](aws_health_ai.md) | Amazon Web Services | HealthLake, SageMaker health patterns, Bedrock for health, AWS reference architectures | Cloud-forward organizations or Epic shops with AWS agreements |
| [azure_health_foundation.md](azure_health_foundation.md) | Microsoft Azure | Azure Health Data Services, Azure AI health patterns, Teams-integrated care, Nuance DAX | Microsoft-aligned organizations; Microsoft 365 or Teams-heavy environments |
| [google_cloud_health_ai.md](google_cloud_health_ai.md) | Google Cloud | Vertex AI, Healthcare Data Engine, FHIR-native data layer, MedLM, Care Studio | Data-mature organizations; research hospitals; orgs with de-identification or population health focus |

---

## vendor_evaluation_criteria

See [vendor_evaluation_criteria.md](vendor_evaluation_criteria.md) for standardized evaluation dimensions used across all four reference designs.

---

## how_to_use_this_library

**For Agent 2 (Scenario Reasoning):** Match the health system's EHR platform, cloud posture, workload type, and governance maturity against the best-fit profiles and contraindications in each reference design. Do not force a match when the contraindication conditions are present.

**For the Scenario Brief:** Reference specific vendor patterns by name when justifying scenario infrastructure implications. Cite the reference design file and version as the evidence basis.

**For procurement:** Use the typical procurement requirements section of each reference design as a starting point for RFP requirement categories. Do not copy verbatim — adapt to the specific health system's assessment outputs.

**Currency:** This library reflects information as of the last-updated date. Material product announcements between updates should be flagged in the Scenario Brief as "pending library update" and noted as unverified.
