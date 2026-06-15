# Reference Design: Epic AI Ecosystem

## metadata

| Field | Value |
|---|---|
| Vendor | Epic Systems |
| Reference design version | 1.0 |
| Last updated | 2026-06-15 |
| Source | Epic public documentation, Epic App Orchard, Epic AI Marketplace public materials, industry coverage |
| Evidence strength | High — Epic's AI portfolio is extensively documented through public channels, customer conferences (Epic UGM), and third-party reporting |
| Confidence note | Feature availability varies by Epic version, customer agreement, and module licensing. Validate against the health system's current Epic contract and active module list. |

---

## product_portfolio

### Core AI and Cognitive Computing

**Epic Cognitive Computing**
Epic's native AI layer embedded across clinical workflows. Applies machine learning models trained on Epic's multi-organization dataset. Capabilities include: deterioration index (sepsis, deterioration early warning), readmission risk, LOS prediction, and no-show prediction. Models run within the Epic environment — no separate compute required. Most capabilities are included in Epic base licensing; some require activation.

**Epic AI Marketplace / App Orchard AI**
Epic's vendor partner ecosystem. Third-party AI vendors whose models have been integrated and tested against Epic's API surface. Health systems can activate approved third-party AI tools (imaging AI, documentation, revenue cycle) within the Epic workflow. Integration is standardized; data flows do not leave the Epic environment unless the third-party tool requires external compute. Governance and security vetting is shared between Epic and the partner vendor.

**DAX Copilot (Nuance/Microsoft integration)**
Ambient clinical documentation. Physician speaks with patient; DAX transcribes and generates structured clinical note draft in Epic. Requires Microsoft/Nuance licensing (separate from Epic) and integration configuration. DAX uses cloud-based processing (Azure). Note: DAX is the Microsoft product — Epic integrates it; it is not Epic-native.

**Cheers**
Epic's patient engagement and consumer AI layer. Personalized health recommendations, care gap notifications, and preventive care outreach. Runs within MyChart and Epic's patient-facing products. Best suited for organizations with strong MyChart adoption and population health programs.

**NLP and Unstructured Data Models**
Epic's clinical NLP capabilities. Extracts structured signals from clinical notes, problem lists, and documentation. Used to power quality measure automation, care gap detection, and registry population. Increasingly used to feed downstream AI models. Activation varies by Epic version and module configuration.

---

## deployment_models

| Model | Description | Applicability |
|---|---|---|
| Native Epic (on-prem or Epic-managed) | AI runs within the Epic instance — no external compute, no data leaves the Epic environment | Default for Epic Cognitive Computing and NLP; lowest additional infrastructure burden |
| App Orchard / Marketplace integration | Third-party AI runs in partner environment; data passes through Epic APIs | Requires HIPAA BAA with each partner; security vetting via Epic App Orchard process |
| Cloud-integrated (DAX / Azure) | DAX requires Azure cloud processing; PHI transmitted to Microsoft Azure | Requires Microsoft Azure tenant, Nuance agreement, and data processing agreement |
| Epic-hosted (managed hosting) | Epic hosts the EHR environment for the health system | Reduces internal infrastructure burden; AI activation governed by Epic |

---

## ehr_and_integration_dependencies

- **Requires:** Active Epic customer with current maintenance contract
- **Version sensitivity:** Many AI capabilities require Epic 2020 or later; some features tied to specific quarterly releases (e.g., 2023 or 2024 release cycle)
- **Module dependencies:** Specific AI capabilities are tied to licensed Epic modules (e.g., Cheers requires MyChart; readmission models may require specific clinical modules)
- **FHIR API:** Epic supports FHIR R4; third-party AI vendors typically integrate via FHIR APIs or Epic-certified integration methods
- **Integration effort (native AI):** Low — native models activate through Epic configuration, not custom integration
- **Integration effort (App Orchard):** Medium — requires partner activation, HIPAA BAA, and workflow configuration; IT and clinical informatics involvement required
- **Integration effort (DAX):** Medium-High — requires Microsoft/Nuance licensing, Azure tenant configuration, SSO setup, and workflow training

---

## governance_prerequisites

- Epic AI Marketplace / App Orchard partners should be reviewed by the CISO and legal team for data handling, subprocessors, and breach notification
- DAX Copilot activation requires a formal data processing agreement with Microsoft covering the Azure processing path
- Clinical AI tools activated through App Orchard require clinical validation — Epic vetting does not substitute for the health system's own clinical safety review
- Post-deployment monitoring: Epic provides some usage and adoption analytics; outcome monitoring (model drift, equity) requires separate governance processes
- An AI inventory should capture all active App Orchard tools — these are often activated by individual departments without central IT visibility

---

## security_and_privacy_assumptions

- Epic's native AI operates within the health system's Epic environment — data does not leave the system boundary for native models
- App Orchard integrations vary: some process data within Epic; others transmit to third-party environments (requires BAA and data flow documentation)
- DAX Copilot transmits clinical audio/transcript data to Microsoft Azure — must be covered under the health system's Microsoft/Azure data processing agreement
- Epic is not a Business Associate for the health system's own data management decisions; the health system remains the covered entity
- HIPAA compliance: Epic's platform meets technical safeguards; governance, access control, and monitoring are health system responsibilities

---

## best_fit_profile

**Strongest match when:**
- Health system is fully on Epic (single EHR environment, no multi-EHR complexity)
- Active Epic optimization and module expansion roadmap
- Clinical informatics team is engaged and has Epic expertise
- Governance appetite for vendor-vetted (App Orchard) AI rather than custom AI development
- Microsoft or Azure relationship already in place (for DAX)
- Strong MyChart adoption (for Cheers and patient-facing AI)
- Desire to minimize additional vendor relationships — consolidate AI under Epic umbrella

**Secondary match (partial Epic, multi-EHR):**
- Epic is the primary EHR but not the only one
- Epic AI applies to Epic workflows; non-Epic workflows require separate AI strategy
- Data integration across EHRs required for enterprise AI — more complex, requires data platform layer

---

## contraindications

**Poor fit when:**
- Health system is not on Epic (Cerner, Meditech, Allscripts, MEDITECH) — none of Epic's AI ecosystem applies
- Organization requires custom AI models trained on their own data — Epic AI Marketplace is a curated vendor set, not a custom development platform
- Organization has strong aversion to cloud processing — DAX requires Azure; some App Orchard tools require external cloud
- Infrastructure readiness is very low — Epic AI activation requires stable Epic operations as a foundation
- Budget is highly constrained — App Orchard and DAX carry additional licensing costs beyond base Epic fees
- Governance is immature — App Orchard partner activation without clinical review is a common governance failure mode

---

## typical_procurement_requirements

### For Epic AI Marketplace / App Orchard
- Verify App Orchard certification status of each target vendor (Epic publishes partner status)
- Require HIPAA Business Associate Agreement from each App Orchard partner
- Require data flow documentation: where does data go, who are the subprocessors, where is it stored
- Require breach notification terms consistent with health system's standard
- Clinical validation plan: who owns it, what metrics define acceptable performance, who approves go-live
- Post-deployment monitoring requirements: frequency, metrics, accountability owner

### For DAX Copilot
- Microsoft Enterprise Agreement or separate Nuance licensing agreement required
- Azure data processing addendum covering clinical audio processing
- Confirm Azure region (US data residency) and data retention policies
- Training requirements: physician adoption rates are the primary risk factor; training plan and change management plan required
- Post-deployment monitoring: note quality metrics, physician satisfaction, documentation time reduction

### RFP requirement categories (if issuing an Epic AI expansion RFP)
- App Orchard certification and maintenance
- HIPAA BAA and data flow transparency
- Clinical validation evidence (peer-reviewed or equivalent)
- Equity and bias testing methodology
- Model performance monitoring and update cadence
- Integration support and implementation timeline
- Pricing model: per-provider, per-activation, or enterprise license

---

## evidence_basis_and_source

| Claim | Source |
|---|---|
| Epic Cognitive Computing portfolio | Epic public product documentation; Epic User Group Meeting (UGM) published materials |
| DAX Copilot architecture | Microsoft/Nuance public documentation; Epic-Nuance integration guides |
| App Orchard governance model | Epic App Orchard public partner portal |
| FHIR API capabilities | Epic on FHIR developer documentation |
| Cheers product scope | Epic public product pages |

*Last verified: June 2026. Validate against current Epic release notes and vendor documentation before procurement.*
