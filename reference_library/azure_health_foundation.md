# Reference Design: Microsoft Azure Health Foundation

## metadata

| Field | Value |
|---|---|
| Vendor | Microsoft (Azure + Nuance + Microsoft Health) |
| Reference design version | 1.0 |
| Last updated | 2026-06-15 |
| Source | Microsoft public documentation, Azure Health Data Services product pages, Nuance DAX product documentation, Microsoft Cloud for Healthcare documentation, industry coverage |
| Evidence strength | High — Microsoft's health AI portfolio is extensively documented; DAX Copilot adoption is widely reported |
| Confidence note | Microsoft frequently consolidates or renames health products (e.g., Nuance rebranding into Microsoft Health and Life Sciences). Validate product names and licensing paths against current Microsoft agreements. |

---

## product_portfolio

### Core Health AI Services

**Azure Health Data Services**
Microsoft's HIPAA-eligible managed FHIR and DICOM service on Azure. Supports FHIR R4 natively — ingests, stores, and queries clinical data in standard format. Integrates with Epic, Cerner, and other EHR FHIR APIs. Used as the health data interoperability layer for downstream AI services. Replaces earlier Azure API for FHIR and Azure DICOM Service under a unified service. Key capability: unified FHIR + DICOM storage in one HIPAA-eligible managed service.

**DAX Copilot (Nuance, now Microsoft)**
Ambient clinical documentation. Physician sees patient; DAX listens to the clinical encounter, generates a structured clinical note draft. Note is reviewed and signed by the physician in the EHR. Integrates with Epic, Cerner, and major EHRs. Uses Azure cloud processing for audio transcription and note generation. DAX is Microsoft's flagship health AI product — it has the deepest health system customer base of any ambient documentation tool as of 2025–2026. Evidence of physician time savings and burnout reduction is strong. Licensing is through Microsoft/Nuance separately from EHR agreements.

**Azure OpenAI Service for Health**
HIPAA-eligible access to OpenAI models (GPT-4, GPT-4o) via Microsoft Azure. Enables health-specific generative AI applications: clinical summarization, care coordination drafting, patient communication, coding assistance, prior authorization support. Differs from OpenAI's direct API in that Azure OpenAI is covered under Microsoft's BAA and operates within the customer's Azure environment. Data does not flow to OpenAI's training data.

**Microsoft Health Bot**
HIPAA-eligible conversational AI service for patient-facing applications. Used for symptom checking, appointment scheduling, care navigation, and patient onboarding. Integrates with EHR patient portals. Best suited for organizations building patient-facing automation or digital front door experiences.

**Azure Machine Learning for Health**
Microsoft's managed ML platform. Used for building, training, and deploying custom health AI models. Similar to AWS SageMaker in purpose. Health-specific accelerators available. Requires data science expertise. Best suited for organizations with internal ML capability or system integrator partnerships.

**Microsoft Cloud for Healthcare**
A bundled solution layer combining Azure, Microsoft 365, Teams, and Dynamics 365 configured for healthcare use cases. Includes patient engagement, care team collaboration, data and analytics, and clinical and operational AI. Designed for organizations that are deeply Microsoft-integrated (Teams, Exchange, SharePoint) and want a unified Microsoft health platform rather than point AI solutions.

---

## deployment_models

| Model | Description | Applicability |
|---|---|---|
| Azure cloud (AHDS, DAX, Azure OpenAI) | Fully managed services on Microsoft Azure; PHI processed in Azure HIPAA-eligible environment | Standard for Microsoft-aligned organizations; cloud-forward shops |
| DAX Copilot (cloud-processing) | Audio captured in clinical encounter; processed on Azure; note delivered to EHR | Compatible with any EHR with DAX integration (Epic, Cerner, and others) |
| Azure hybrid (Arc-enabled) | Some Azure services extended to on-prem or edge environments via Azure Arc | For organizations with on-prem infrastructure requirements that want Azure management plane |
| Microsoft Cloud for Healthcare (bundled) | Full Microsoft stack; Teams-integrated care team collaboration + Azure AI | Best for Microsoft 365-heavy organizations; more complex licensing |

---

## ehr_and_integration_dependencies

- **EHR compatibility:** Azure Health Data Services and DAX Copilot are EHR-agnostic; Epic, Cerner, and major EHRs support DAX integration
- **Epic + DAX:** Epic has deep DAX integration; DAX note drafts surface in Epic's documentation workflow; configuration is Epic-supported
- **FHIR API:** Azure Health Data Services supports FHIR R4; connects to Epic FHIR API, Cerner FHIR API, and others
- **Microsoft 365 dependency:** Microsoft Cloud for Healthcare requires Microsoft 365 licensing; Teams-integrated features require active Teams deployment
- **Azure Active Directory / Entra ID:** Single sign-on for Azure health services typically uses Microsoft Entra ID (formerly Azure AD); organizations already using Microsoft SSO have the lowest integration friction
- **Integration effort (DAX):** Medium — requires Microsoft/Nuance licensing, EHR configuration, Azure tenant setup, and physician training
- **Integration effort (AHDS):** Medium — FHIR ingestion pipeline setup required; data quality validation adds time
- **Integration effort (Microsoft Cloud for Healthcare):** High — bundled platform requires significant configuration across multiple Microsoft products

---

## governance_prerequisites

- Microsoft BAA must be in place before any PHI is processed in Azure — including DAX audio processing
- DAX audio data: clinical encounter audio is processed in Azure; health system must confirm this is covered under their Microsoft BAA and consistent with their privacy policy
- Azure OpenAI for health: data submitted to Azure OpenAI is not used for model training by default — confirm this in the Microsoft data processing agreement; do not use direct OpenAI API for PHI workloads
- Entra ID / IAM: access control to Azure health services must be managed; review privileged identity management policies
- Clinical validation: DAX generates note drafts — physicians review and sign; this is an approved human-in-the-loop pattern, but the health system must define oversight policy for note accuracy and accountability
- Teams-integrated care: if clinical communication occurs via Teams, message retention and e-discovery policies must be configured per organizational policy
- AI governance: Microsoft does not validate clinical performance of AI outputs; health system is responsible for clinical oversight and post-deployment monitoring

---

## security_and_privacy_assumptions

- Azure Health Data Services and DAX are HIPAA eligible under a Microsoft BAA — verify the BAA covers specific services in scope
- Data residency: Azure regions are configurable; select US-based regions (East US, West US) for data residency requirements; confirm in service configuration
- DAX audio processing: audio is transmitted to Azure, transcribed, and used to generate note drafts; confirm Microsoft's data retention and deletion policies for audio data
- Azure OpenAI for health: PHI processed in Azure OpenAI stays within the customer's Azure environment under the BAA; not shared with OpenAI
- Microsoft Defender for Cloud: recommended for security posture management across Azure health workloads
- Encryption: Azure encrypts data at rest and in transit by default; customer-managed keys (CMK) available for higher-assurance requirements
- Incident response: Microsoft publishes breach notification obligations under the BAA; health system must have its own breach response plan

---

## best_fit_profile

**Strongest match when:**
- Organization is deeply Microsoft-aligned: Microsoft 365, Teams, Outlook, Azure Active Directory / Entra ID are core infrastructure
- CIO wants ambient documentation (DAX) — Microsoft has the largest DAX customer base and the most mature implementation track record
- Organization is on Epic or Cerner — DAX integration with both is well-established
- CISO has existing Azure cloud security policies — reduces security review burden for AI services
- Population is engaged through Microsoft Teams or Microsoft patient portal technologies
- Budget includes Microsoft enterprise agreement — health AI services may be includable in EA negotiations
- Organization wants a unified Microsoft platform rather than point AI solutions

**Secondary match:**
- Multi-EHR environments where Azure Health Data Services can serve as a neutral FHIR aggregation layer
- Organizations building patient-facing AI (Health Bot) as a digital front door initiative
- Organizations with existing Nuance speech recognition investments (migration to DAX is smoother)

---

## contraindications

**Poor fit when:**
- Organization is Google-workspace-aligned (Gmail, Google Workspace) with no Microsoft infrastructure — integration friction is high
- CISO is not familiar with Azure and has no existing cloud security policies for Azure workloads
- Organization prefers custom AI model development with full data control — Microsoft Cloud for Healthcare is a bundled platform approach, less flexible for custom development than SageMaker or Vertex AI
- Budget for ambient documentation (DAX) is not supported — DAX carries per-provider licensing costs that can be significant at scale
- Organization is fully on-prem with no cloud strategy and leadership resistance to cloud processing of clinical audio
- Governance is immature — DAX adoption at scale without clinical oversight policy is a governance risk

---

## typical_procurement_requirements

### Microsoft enterprise agreement / Azure BAA
- Execute Microsoft BAA or confirm PHI is covered under existing Microsoft enterprise agreement
- Confirm BAA coverage for specific services (AHDS, DAX, Azure OpenAI, Health Bot)
- Establish Azure region selection and data residency commitment
- Define Microsoft's breach notification timeline and process under the agreement
- Request Microsoft's subprocessor list for services handling PHI

### DAX Copilot
- Nuance/Microsoft licensing agreement (separate from Epic agreement if applicable)
- Confirm DAX integration path with EHR vendor (Epic, Cerner)
- Clinical champion identified: physician adoption depends on executive clinical sponsorship
- Training plan: DAX ROI depends on physician adoption — training and change management plan required
- Performance metrics: documentation time reduction, physician satisfaction, note quality acceptance rate
- Retention policy for audio data: confirm Microsoft's data retention and deletion schedule for clinical audio

### Azure Health Data Services
- FHIR R4 compatibility confirmation with EHR vendor
- Data pipeline design and data quality standards documentation
- Access control and audit logging configuration
- SLA requirements for availability of FHIR API in production clinical workflows

### RFP requirement categories (if issuing an Azure health AI or DAX expansion RFP)
- Microsoft BAA scope and subprocessor disclosure
- FHIR R4 interoperability and integration methodology
- DAX clinical adoption metrics and benchmarks from comparable organizations
- Audio data retention, deletion, and de-identification policies
- Azure security posture and compliance documentation (FedRAMP if applicable)
- Clinical validation methodology for AI-generated note content
- Equity and bias testing in ambient documentation models
- Physician training and change management requirements

---

## evidence_basis_and_source

| Claim | Source |
|---|---|
| Azure Health Data Services product scope | Microsoft Azure documentation (learn.microsoft.com/azure/healthcare-apis) |
| DAX Copilot product scope and EHR integration | Nuance/Microsoft DAX documentation; Epic-DAX integration documentation |
| Azure OpenAI for health | Microsoft Azure OpenAI documentation; Microsoft Health and Life Sciences blog |
| Microsoft Cloud for Healthcare | Microsoft Cloud for Healthcare documentation |
| Microsoft BAA coverage | Microsoft Trust Center (microsoft.com/trust-center/compliance/hipaa) |
| DAX customer adoption data | Published health system case studies; KLAS Research coverage of ambient documentation market |

*Last verified: June 2026. Microsoft frequently updates product naming and licensing in the health portfolio — validate current product names and BAA coverage before procurement.*
