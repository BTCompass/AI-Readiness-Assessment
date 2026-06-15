# Reference Design: Google Cloud Health AI

## metadata

| Field | Value |
|---|---|
| Vendor | Google Cloud (Alphabet) |
| Reference design version | 1.0 |
| Last updated | 2026-06-15 |
| Source | Google Cloud public documentation, Google Cloud Healthcare API documentation, Vertex AI documentation, MedLM product announcements, Care Studio documentation, industry analyst coverage |
| Evidence strength | Medium-High — Google Cloud health AI portfolio is documented; MedLM and Care Studio are newer and clinical validation evidence is still emerging |
| Confidence note | Google Cloud health AI is rapidly evolving. MedLM and Care Studio are relatively new products (2023–2024 launch). Validate current product availability, HIPAA eligibility, and clinical validation status before procurement. |

---

## product_portfolio

### Core Health AI Services

**Healthcare Data Engine (HDE)**
Google Cloud's managed FHIR-native health data platform. Stores, harmonizes, and queries clinical data in FHIR R4 format. Ingests data from EHRs, claims systems, and other clinical data sources via FHIR APIs. Applies de-identification pipelines, data harmonization, and clinical NLP. Designed to serve as the enterprise health data foundation for AI and analytics workloads. Closest Google equivalent to AWS HealthLake or Azure Health Data Services — with stronger built-in de-identification and data harmonization capabilities than either.

**Google Cloud Healthcare API**
The underlying API layer for FHIR, DICOM, and HL7v2 data storage and exchange on Google Cloud. HIPAA eligible. Used for standards-based interoperability — receiving data from EHRs, sending data to analytics and AI systems. Can be used standalone or as the data layer under Healthcare Data Engine. More accessible to organizations that want FHIR API capability without the full HDE platform.

**Vertex AI (Health Applications)**
Google Cloud's managed ML platform. Used for building, training, and deploying custom AI and ML models. Google has published health-specific reference architectures and model gardens relevant to clinical AI. Supports fine-tuning of foundation models on health-specific data. Requires data science expertise. Best suited for organizations with internal data science teams or research programs that want to build and own custom models.

**MedLM**
Google's suite of medical foundation models, built on PaLM 2 architecture and optimized for healthcare use cases. Available through Vertex AI. Designed for: medical question answering, clinical summarization, clinical note drafting, medical coding assistance, and consumer health applications. MedLM-Medium for high-volume summarization and consumer use cases; MedLM-Large for complex clinical reasoning tasks. HIPAA eligibility: available under Google BAA on Vertex AI. Clinical validation: published research on Med-PaLM 2 (academic/research), but enterprise clinical validation evidence is still building compared to DAX or Epic's native AI.

**Care Studio**
Google's clinical search and workflow tool. Surfaces relevant patient information across fragmented data sources in a unified clinical view. Integrates with Epic, Cerner, and other EHRs. Designed to reduce the time clinicians spend searching for patient information across systems. Primarily targeted at large health systems with complex multi-system data environments. Pilots completed at large academic medical centers; broader commercial deployment is in progress.

**FHIR-Native De-identification Pipeline**
A distinct Google Cloud capability: purpose-built de-identification within Healthcare Data Engine, with configurable Safe Harbor and Expert Determination methods. Particularly valuable for health systems that want to use clinical data for AI training or research — de-identification is built into the data pipeline rather than requiring a separate vendor or manual process.

---

## deployment_models

| Model | Description | Applicability |
|---|---|---|
| Google Cloud managed (HDE, Healthcare API, Vertex AI) | Fully managed services on Google Cloud; HIPAA eligible under Google BAA | Standard for cloud-forward organizations or Google Workspace organizations |
| Vertex AI custom model | Health system builds and deploys custom models on Google's managed ML infrastructure | Requires data science capability; highest flexibility |
| MedLM API (via Vertex AI) | Access to Google's medical foundation models via API | For organizations building health AI applications without training custom models from scratch |
| Hybrid (on-prem EHR + GCP data layer) | EHR remains on-prem; data flows to Google Cloud for AI and analytics | Common for large academic medical centers with on-prem Epic but desire for cloud AI capability |

---

## ehr_and_integration_dependencies

- **EHR-agnostic at the data layer:** Healthcare Data Engine and Healthcare API work with any EHR that exports FHIR R4 or HL7 data
- **Epic integration:** Epic's FHIR R4 API → Google Healthcare API or HDE. Google has published Epic integration reference architectures. Care Studio has a certified Epic integration.
- **Cerner/Oracle Health integration:** FHIR R4 export path; Care Studio has Cerner integration capability
- **Multi-EHR environments:** Google's strength — HDE is designed to harmonize data from multiple EHR sources into a single FHIR data layer; well-suited for health systems with Epic in some facilities and Cerner or Meditech in others
- **FHIR version:** Healthcare Data Engine supports FHIR R4; validate EHR FHIR export version compatibility
- **Data engineering requirement:** Like AWS and Azure, Google Cloud health AI requires a data pipeline from EHR to cloud; plan for 3–6 months for a full data pipeline with quality validation
- **Integration effort (Healthcare API/HDE):** Medium — FHIR ingestion design required; de-identification pipeline adds configuration time but reduces downstream effort
- **Integration effort (Care Studio):** Medium — certified EHR integration available; clinical champion and workflow configuration required
- **Integration effort (MedLM via Vertex AI):** Medium-High — requires Vertex AI setup, prompt engineering, and integration into clinical workflows

---

## governance_prerequisites

- Google BAA must be in place before any PHI is processed on Google Cloud — including data sent to Vertex AI or MedLM
- Verify HIPAA eligibility of specific services: not all Google Cloud services are HIPAA eligible; validate against Google's current HIPAA-eligible services list
- MedLM clinical validation: MedLM is not an FDA-cleared clinical decision support tool (as of 2025–2026); health system is responsible for clinical validation before clinical deployment
- De-identification: if using Google's de-identification pipeline for training data or analytics, validate the de-identification method meets HIPAA Safe Harbor or Expert Determination requirements — and document this decision
- AI governance: Google does not manage clinical oversight of AI outputs; health system must define clinical review, accountability, and post-deployment monitoring policies
- Data residency: confirm Google Cloud region selection and whether data residency commitments are available in the BAA or service terms
- Third-party risk: CISO review of Google Cloud required if not already covered under an existing cloud security policy for GCP

---

## security_and_privacy_assumptions

- Google Cloud Healthcare API and Healthcare Data Engine are HIPAA eligible under a signed Google BAA — verify BAA covers all specific services in use
- Vertex AI with MedLM: PHI processed within the customer's Google Cloud environment under the BAA; data is not used for Google model training under the BAA (confirm in current agreement)
- De-identification pipeline: Google's built-in de-identification creates de-identified data sets; health system must validate de-identification method before using data for training or research
- Data residency: Google Cloud allows region selection; US-based regions (us-central1, us-east1) are standard; multi-region options available
- VPC Service Controls: recommended for high-assurance environments; restricts data movement within the Google Cloud environment to prevent exfiltration
- Encryption: Google Cloud encrypts data at rest and in transit by default; customer-managed encryption keys (CMEK) available
- IAM: Google Cloud IAM requires careful design; principle of least privilege; audit logs (Cloud Audit Logs) must be enabled

---

## best_fit_profile

**Strongest match when:**
- Organization is data-mature with a strong analytics or research function — Google Cloud's data platform and de-identification capabilities are most valuable to organizations that actively analyze clinical data
- Research hospital or academic medical center with data science program — Vertex AI + MedLM are suited to organizations that want to build or fine-tune models, not just consume vendor AI
- Multi-EHR environment — HDE's data harmonization across multiple EHR systems is a genuine differentiator vs. Epic AI Marketplace (Epic-only) or single-EHR assumptions in AWS/Azure reference architectures
- Population health or de-identification use cases — Google's FHIR-native de-identification is best-in-class among the major clouds
- Google Workspace organization — SSO, IAM, and administrative integration is seamless for Google Workspace users
- Interest in Care Studio — large health systems with complex multi-system data environments where clinical search and data surfacing is a priority

**Secondary match:**
- Organizations that want a non-Epic, non-Microsoft AI path and prefer Google's model ecosystem (Gemini/PaLM family, MedLM) over Azure OpenAI or AWS Bedrock

---

## contraindications

**Poor fit when:**
- Organization needs mature, clinically validated ambient documentation today — DAX Copilot (Microsoft) has a much larger health system customer base and more published clinical evidence than Google's equivalent offerings as of 2025–2026
- Organization is fully Epic-aligned with no interest in building a separate data layer — Epic AI Marketplace and AWS (Epic + AWS reference architecture) are better fits; Google adds data layer complexity without clear Epic AI advantage
- Low data maturity — Google Cloud's health AI strengths are in data platform and custom model development; organizations with weak data foundations will not benefit from the platform until data readiness improves
- No data science capability and no SI partner relationship — MedLM and Vertex AI require technical expertise; this is not a turnkey clinical AI deployment platform
- Budget is very constrained — Google Cloud services are consumption-priced; data pipeline and Vertex AI costs add up; requires cost management planning
- CISO has no GCP cloud security policy and Google Cloud is not in the existing cloud security review scope

---

## typical_procurement_requirements

### Google Cloud agreement / BAA
- Execute Google BAA or confirm PHI coverage under existing Google Cloud enterprise agreement
- Confirm HIPAA eligibility of specific services in scope (verify against current Google HIPAA-eligible products list)
- Establish Google Cloud region selection and data residency commitment
- Define data retention, deletion, and de-identification policies in service terms
- Request Google's subprocessor list for services handling PHI

### Healthcare Data Engine / Healthcare API
- FHIR R4 compatibility confirmation with EHR vendor
- Data pipeline design and data quality standards documentation
- De-identification methodology documentation (Safe Harbor or Expert Determination)
- Access control, VPC Service Controls configuration, and audit logging requirements

### MedLM (via Vertex AI)
- Clinical validation plan: who owns it, what metrics define acceptable clinical performance, who approves deployment
- Confirm data handling under Google BAA (no model training on health system's PHI)
- Prompt engineering and integration design: MedLM requires integration design work; not a plug-and-play clinical tool
- Model performance monitoring: who monitors model performance post-deployment, and at what frequency
- Equity and bias review: confirm Google's published testing against diverse clinical populations; health system-level equity monitoring required

### RFP requirement categories (if issuing a Google Cloud health AI or Care Studio RFP)
- Google BAA scope and HIPAA-eligible service confirmation
- FHIR R4 interoperability and data harmonization standards
- De-identification methodology and validation documentation
- VPC Service Controls and IAM architecture requirements
- MedLM clinical validation evidence and published performance benchmarks
- Data residency and subprocessor disclosure
- Equity and bias testing methodology
- Model monitoring, update cadence, and performance reporting requirements

---

## evidence_basis_and_source

| Claim | Source |
|---|---|
| Healthcare Data Engine product scope | Google Cloud Healthcare Data Engine documentation (cloud.google.com/healthcare-api) |
| Google Cloud Healthcare API | Google Cloud Healthcare API documentation |
| MedLM product scope and availability | Google Cloud MedLM product pages; Google Health AI blog |
| Med-PaLM 2 clinical validation research | Published research (Nature Medicine, 2023); note: research context differs from enterprise deployment |
| Care Studio product scope | Google Health / Care Studio product pages; Google health enterprise announcements |
| Google BAA coverage | Google Cloud HIPAA implementation guide (cloud.google.com/security/compliance/hipaa) |
| De-identification capabilities | Google Cloud Healthcare API de-identification documentation |

*Last verified: June 2026. Google Cloud health AI is evolving rapidly — MedLM and Care Studio have been updated frequently since launch. Validate current product availability, clinical validation status, and HIPAA eligibility before procurement.*
