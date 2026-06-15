# Reference Design: AWS Health AI

## metadata

| Field | Value |
|---|---|
| Vendor | Amazon Web Services (AWS) |
| Reference design version | 1.0 |
| Last updated | 2026-06-15 |
| Source | AWS public documentation, AWS HealthLake product pages, AWS Architecture Center, AWS re:Invent sessions, industry analyst coverage |
| Evidence strength | High — AWS Health AI portfolio is extensively documented; reference architectures are publicly available |
| Confidence note | AWS service availability, pricing, and HIPAA eligibility status can change. Validate against current AWS service terms and HIPAA Business Associate Agreement before procurement. |

---

## product_portfolio

### Core Health AI Services

**AWS HealthLake**
HIPAA-eligible managed service for storing, transforming, and analyzing health data at scale. Ingests data in HL7 FHIR R4 format; applies integrated medical NLP to extract structured clinical entities (diagnoses, medications, procedures, lab results) from unstructured clinical text. Supports real-time and batch queries. Designed as the data foundation layer for AI workloads — other AWS AI services can read from HealthLake. Key differentiator: FHIR-native storage with built-in clinical NLP; reduces the data preparation burden for downstream AI.

**Amazon Comprehend Medical**
Clinical NLP service. Extracts medical entities (conditions, medications, dosages, anatomy, test results) and relationships from unstructured clinical text. HIPAA eligible. Can be called as a standalone API or embedded within a larger workflow (e.g., process discharge summaries before ingesting into HealthLake). Commonly used for: CDI (clinical documentation improvement), care gap identification from notes, prior authorization automation, and research cohort identification.

**Amazon Bedrock for Health**
AWS's managed generative AI service with health-specific configurations. Access to foundation models (Claude, Llama, Titan, and others) via API. Supports RAG (retrieval-augmented generation) patterns for health documentation, clinical summarization, and care coordination workflows. HIPAA-eligible when configured correctly. Increasingly used for: ambient documentation, clinical summarization, payer/prior auth automation, patient communication drafting.

**Amazon SageMaker (Health Patterns)**
AWS's ML development and deployment platform. Used for building, training, and deploying custom ML models. AWS publishes health-specific reference architectures: readmission risk, patient deterioration, imaging AI workflows, population health. Requires data science expertise to implement (not no-code). Best suited for organizations with internal data science capability or a system integrator relationship. HIPAA eligible.

**AWS HealthImaging**
Purpose-built DICOM image storage and retrieval service. Optimized for medical imaging data at scale. Integrates with SageMaker for imaging AI model development and deployment. Alternative to on-prem PACS or vendor-specific cloud PACS solutions. HIPAA eligible.

**Amazon Transcribe Medical**
ASR (automatic speech recognition) for clinical dictation and documentation. HIPAA eligible. Produces medical-grade transcriptions with clinical vocabulary support. Used as a component in ambient documentation workflows (often paired with Bedrock for note drafting). Not a full ambient documentation solution by itself — typically integrated with a documentation layer.

---

## deployment_models

| Model | Description | Applicability |
|---|---|---|
| AWS-managed cloud (HealthLake, Comprehend Medical, Bedrock) | Fully managed services; AWS manages infrastructure; health system manages data and configurations | Standard for cloud-forward organizations; lowest operational burden |
| Custom model on SageMaker | Health system (or SI partner) builds, trains, and deploys custom models on AWS managed ML infrastructure | Requires data science capability; highest flexibility and specificity |
| Hybrid (on-prem EHR + AWS data layer) | EHR stays on-prem; data is extracted, de-identified, and sent to AWS for AI processing | Common for Epic/Cerner shops adding AWS analytics/AI without moving the EHR |
| AWS GovCloud / private region | High-compliance environments requiring US-sovereignty data boundaries | Applicable for federal health systems, VA/DoD, or organizations with specific data residency requirements |

---

## ehr_and_integration_dependencies

- **EHR-agnostic:** AWS Health AI services work with any EHR that can export FHIR R4 or HL7 data — including Epic, Cerner/Oracle Health, Meditech, Allscripts
- **Epic integration path:** Epic's FHIR R4 API → AWS HealthLake ingestion pipeline → downstream AI services. AWS has published Epic integration reference architectures.
- **Cerner/Oracle Health integration:** Similar FHIR export path; Oracle Health has cloud partnerships (including OCI) that may affect integration design
- **Data extraction complexity:** Clinical data is rarely clean at export — de-identification, normalization, and quality validation add to integration effort; plan for 3–6 months for a full data pipeline
- **HealthLake as FHIR store:** Can serve as an enterprise FHIR server separate from the EHR; health systems sometimes use HealthLake as a clinical data repository layer for AI workloads without replacing the EHR
- **FHIR version:** HealthLake supports FHIR R4; validate EHR FHIR export version compatibility

---

## governance_prerequisites

- AWS BAA (Business Associate Agreement) must be in place before any PHI is processed in AWS — even for test/dev workloads
- HIPAA eligibility ≠ HIPAA compliance: AWS provides HIPAA-eligible infrastructure; the health system is responsible for configuration, access controls, logging, and policies
- Data classification: identify which workloads involve PHI vs. de-identified data; PHI workloads require HIPAA controls; de-identified workloads may not, depending on de-identification method
- IAM (Identity and Access Management): AWS workloads require careful IAM design; over-permissive IAM is a leading cause of cloud security incidents in healthcare
- Audit logging: CloudTrail must be enabled and retained for audit purposes; log retention policy required
- AI governance: if using Bedrock or SageMaker for clinical decision support, clinical validation and post-deployment monitoring responsibilities belong to the health system — AWS does not validate clinical AI performance
- Vendor risk: AWS is typically covered under a health system's enterprise cloud risk review; individual AI services (Comprehend Medical, HealthLake) may require separate assessment

---

## security_and_privacy_assumptions

- AWS is HIPAA eligible under a signed BAA — verify BAA covers specific services in use (not all AWS services are HIPAA eligible)
- Data residency: AWS regions are US-based (us-east-1, us-west-2 most common for health); confirm region selection against organizational data residency requirements
- Encryption: data encrypted at rest and in transit by default in HIPAA-eligible services; key management (KMS) setup required
- De-identification: HealthLake includes a de-identification capability; validate against HIPAA Safe Harbor or Expert Determination method requirements before using de-identified data downstream
- Network security: workloads should run in private VPCs; public-internet-exposed health data services are a high-risk configuration
- Penetration testing: AWS permits health system-conducted penetration testing with advance notice; may be required by CISO before production deployment

---

## best_fit_profile

**Strongest match when:**
- Organization has an existing AWS enterprise agreement or is cloud-forward with AWS as the preferred platform
- Epic is the EHR and the organization wants to build an analytics/AI layer on top of Epic data without replacing Epic
- Data science capability exists internally or through a system integrator partner
- Population health, predictive analytics, or research AI workloads are the primary use cases
- Organization wants to avoid single-vendor AI lock-in (App Orchard) and retain ability to build or source custom models
- Budget for cloud infrastructure and data engineering exists
- CISO is experienced with AWS and has existing cloud security policies for AWS workloads

**Secondary match:**
- Multi-EHR environment where a neutral FHIR data layer (HealthLake) is valuable
- Organizations considering ambient documentation where Bedrock + Transcribe Medical could serve as a foundation
- Research hospitals or academic medical centers with data science teams

---

## contraindications

**Poor fit when:**
- Organization is fully on-prem with no cloud strategy and no near-term cloud migration plans
- No data engineering or data science capability — AWS Health AI requires significant technical expertise to configure and operate
- CISO has not reviewed AWS and has no existing cloud security policies — configuration errors in AWS are a leading source of healthcare data breaches
- Budget is very constrained — AWS services are consumption-priced; costs can scale unexpectedly without cost management controls
- Desire for turnkey clinical AI without internal technical ownership — AWS provides infrastructure, not complete applications; implementation requires significant internal or SI effort
- Organization is Microsoft-centric (Azure AD, Microsoft 365, Teams) — Azure is a more natural fit for Microsoft-aligned organizations

---

## typical_procurement_requirements

### AWS enterprise agreement / health BAA
- Execute AWS BAA before any PHI workloads begin
- Confirm HIPAA eligibility of all specific services in scope
- Establish data residency (US region) and confirm in BAA or supplemental agreement
- Define audit log retention requirements in service configuration
- Cost management: require budget alerts, cost anomaly detection, and reserved instance planning for predictable workloads

### AI services (HealthLake, Comprehend Medical, Bedrock)
- Data flow documentation: data sources, processing path, output destinations, retention
- Clinical validation plan for any AI service used in clinical decision support
- De-identification documentation if de-identified data will be used for model training or analytics
- SLA requirements: availability targets for production AI services supporting clinical workflows
- Model monitoring: who owns drift detection and retraining for custom SageMaker models

### Integration (EHR → AWS)
- FHIR API integration design and test plan
- Data quality validation requirements before AI processing begins
- HL7/FHIR version compatibility confirmation
- Ongoing data pipeline monitoring and alerting requirements

### RFP requirement categories (if issuing an AWS health AI RFP or SI engagement)
- AWS BAA and HIPAA-eligible service scope
- IAM and VPC architecture requirements
- Data de-identification methodology and validation
- FHIR R4 integration and data quality standards
- Clinical validation evidence for AI services
- Cost management controls and reporting
- Penetration testing rights and schedule
- Incident response and breach notification procedures

---

## evidence_basis_and_source

| Claim | Source |
|---|---|
| HealthLake product scope and FHIR support | AWS HealthLake public documentation (aws.amazon.com/healthlake) |
| Comprehend Medical capabilities | AWS Comprehend Medical product pages |
| Bedrock for health | AWS Bedrock public documentation; AWS Health Blog |
| HIPAA eligibility list | AWS HIPAA Eligible Services list (aws.amazon.com/compliance/hipaa-eligible-services-reference) |
| Epic integration reference architecture | AWS Architecture Center health reference architectures |
| SageMaker health patterns | AWS Machine Learning Blog; AWS Health Day sessions (re:Invent) |

*Last verified: June 2026. AWS HIPAA eligibility list is updated periodically — verify current status before procurement.*
