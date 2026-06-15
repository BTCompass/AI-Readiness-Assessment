# Vendor Evaluation Criteria — BT Compass AI Reference Library

## purpose

This file defines the standardized evaluation dimensions used across all four vendor reference designs in this library. When Agent 2 (Scenario Reasoning) matches a health system's profile against vendor reference designs, it evaluates each vendor across these criteria. The criteria are also used to generate vendor comparison language in the Scenario Brief and RFP requirement categories.

---

## evaluation_dimensions

### 1. EHR Compatibility

**What it measures:** How well the vendor's AI products integrate with the health system's current EHR platform without requiring a data platform migration.

| Score | Description |
|---|---|
| Native | AI is built into the EHR itself (Epic AI Marketplace) — no separate integration required |
| Certified | EHR integration is tested, documented, and supported by both vendors |
| Standard FHIR | Integrates via FHIR R4 API — requires integration design but is EHR-agnostic |
| Custom / Complex | Requires custom integration work; no published certified path |

| Vendor | Score |
|---|---|
| Epic AI Ecosystem | Native (for Epic organizations) |
| AWS Health AI | Standard FHIR |
| Azure Health Foundation | Certified (DAX with Epic/Cerner); Standard FHIR for AHDS |
| Google Cloud Health AI | Standard FHIR; Certified for Care Studio with Epic/Cerner |

---

### 2. Deployment Model

**What it measures:** Whether the vendor's AI products can be deployed in a way that is compatible with the health system's infrastructure posture (cloud, on-prem, hybrid) and data governance requirements.

| Vendor | Deployment options | PHI in cloud? |
|---|---|---|
| Epic AI Ecosystem | On-prem (native Epic) / Epic-managed / Cloud (DAX/Azure) | Only for DAX/Azure path |
| AWS Health AI | Cloud (AWS) / Hybrid | Yes — AWS HIPAA-eligible |
| Azure Health Foundation | Cloud (Azure) / Hybrid (Arc) | Yes — Azure HIPAA-eligible |
| Google Cloud Health AI | Cloud (GCP) / Hybrid | Yes — GCP HIPAA-eligible |

---

### 3. HIPAA Eligibility and BAA Coverage

**What it measures:** Whether the vendor's AI products can be used with PHI under a signed Business Associate Agreement.

| Vendor | BAA available? | Coverage notes |
|---|---|---|
| Epic AI Ecosystem | Yes — Epic BAA | Covers Epic-native; DAX requires separate Microsoft BAA |
| AWS Health AI | Yes — AWS BAA | Verify specific services on HIPAA-eligible list |
| Azure Health Foundation | Yes — Microsoft BAA | Verify specific services; DAX audio covered under Microsoft BAA |
| Google Cloud Health AI | Yes — Google BAA | Verify specific services; MedLM via Vertex AI covered |

---

### 4. Clinical Validation Maturity

**What it measures:** The depth of published evidence that the vendor's AI tools perform accurately and safely in clinical settings.

| Score | Description |
|---|---|
| Strong | Published peer-reviewed evidence; KLAS validation; large health system case studies; FDA clearance where applicable |
| Moderate | Published white papers or vendor case studies; limited peer-reviewed evidence; adoption in pilot health systems |
| Emerging | New product; primarily research evidence or early pilot data; limited enterprise deployment evidence |

| Vendor | Representative product | Validation maturity |
|---|---|---|
| Epic AI Ecosystem | Sepsis deterioration index | Strong |
| Epic AI Ecosystem | App Orchard partners | Varies by partner — evaluate individually |
| AWS Health AI | Comprehend Medical | Moderate — NLP accuracy published; clinical outcome evidence limited |
| Azure Health Foundation | DAX Copilot | Strong — largest ambient documentation customer base; published time-savings and adoption data |
| Azure Health Foundation | Azure OpenAI for health | Emerging — context-dependent; health system must validate |
| Google Cloud Health AI | MedLM | Emerging-to-Moderate — research evidence (Med-PaLM 2) is strong; enterprise deployment evidence is building |
| Google Cloud Health AI | Care Studio | Emerging — early large-system pilots; limited published outcome data |

---

### 5. Data Platform Requirement

**What it measures:** How much data infrastructure the health system must build or buy to activate the vendor's AI capabilities.

| Score | Description |
|---|---|
| Low | AI activates within existing EHR or cloud environment with minimal additional data infrastructure |
| Medium | FHIR integration pipeline required; existing cloud environment needed; modest data engineering effort |
| High | Enterprise data platform required; significant data engineering, quality validation, and de-identification work before AI can operate |

| Vendor | Data platform requirement | Notes |
|---|---|---|
| Epic AI Ecosystem (native) | Low | AI activates via Epic configuration; no separate data platform |
| Epic AI Ecosystem (App Orchard) | Low-Medium | FHIR API integration with App Orchard partners; varies by partner |
| AWS Health AI | Medium-High | HealthLake pipeline required; data quality and FHIR normalization effort |
| Azure Health Foundation (DAX) | Low-Medium | Audio processing path; EHR integration configuration |
| Azure Health Foundation (AHDS) | Medium | FHIR ingestion pipeline required; similar to HealthLake |
| Google Cloud Health AI | Medium-High | HDE pipeline required; strongest de-identification capability but higher setup effort |

---

### 6. Governance Complexity

**What it measures:** The governance overhead the health system must establish to safely use the vendor's AI products — beyond what would be required for any cloud vendor.

| Score | Description |
|---|---|
| Low | Governance primarily managed within existing EHR governance and clinical informatics processes |
| Medium | Requires expanded AI governance: clinical validation plan, CISO review, BAA review, AI inventory management |
| High | Requires dedicated AI governance framework: clinical validation, equity review, model monitoring, external AI partnership governance |

| Vendor | Governance complexity | Key governance requirements |
|---|---|---|
| Epic AI Ecosystem (native) | Low | Clinical informatics oversight; standard Epic governance |
| Epic AI Ecosystem (App Orchard) | Medium | Per-partner BAA, clinical validation, AI inventory |
| AWS Health AI | Medium-High | CISO cloud review, IAM design, clinical validation per AI service |
| Azure Health Foundation (DAX) | Medium | Clinical oversight for note review policy; Microsoft BAA; physician training plan |
| Azure Health Foundation (Azure OpenAI) | High | Clinical validation required; equity review; model monitoring policy |
| Google Cloud Health AI | High | CISO cloud review; de-identification validation; clinical validation for MedLM; AI governance framework |

---

### 7. Best-Fit Use Case Profile

**What it measures:** The AI use cases each vendor is best positioned to support, given their current product portfolio and clinical validation evidence.

| Use case | Best fit vendor(s) |
|---|---|
| Ambient clinical documentation | Azure (DAX Copilot) — strongest evidence and adoption |
| EHR-embedded predictive analytics (deterioration, readmission) | Epic AI Ecosystem (native) |
| Third-party clinical AI via marketplace | Epic (App Orchard) |
| Population health and care gap analytics | AWS (HealthLake + Comprehend Medical); Google (HDE) |
| Custom ML model development | AWS (SageMaker); Google (Vertex AI) — tie |
| De-identification for research / training data | Google (HDE de-identification pipeline) — strongest capability |
| Multi-EHR data harmonization | Google (HDE) — strongest multi-EHR harmonization |
| Patient-facing AI and digital front door | Azure (Health Bot); Epic (Cheers) |
| Medical imaging AI | AWS (HealthImaging + SageMaker); Epic (App Orchard imaging partners) |
| Clinical generative AI (summarization, drafting) | Azure (Azure OpenAI); Google (MedLM); AWS (Bedrock) — market evolving |

---

### 8. Procurement Risk Profile

**What it measures:** The primary procurement risks associated with each vendor — risks that should be addressed in RFP requirements or contract negotiations.

| Vendor | Primary procurement risks |
|---|---|
| Epic AI Ecosystem | App Orchard partner quality varies widely; clinical validation responsibility falls to health system; governance gaps when departments activate AI without central oversight |
| AWS Health AI | Configuration complexity — misconfigured AWS environments are a leading source of healthcare data exposure; cost management discipline required |
| Azure Health Foundation | DAX per-provider pricing can scale significantly; audio data processing path requires careful BAA and privacy review; Microsoft product naming/bundling changes create procurement confusion |
| Google Cloud Health AI | MedLM and Care Studio are newer products with less enterprise deployment history; de-identification validation is health system responsibility; Google Cloud GCP is less common in healthcare than AWS or Azure — fewer health system references available |

---

## cross_vendor_comparison_summary

| Dimension | Epic | AWS | Azure | Google |
|---|---|---|---|---|
| EHR Compatibility | Native (Epic only) | Standard FHIR | Certified / FHIR | Certified (Care Studio) / FHIR |
| Best for... | Epic optimization | Cloud + data platform | Ambient docs + Microsoft stack | Data platform + research + multi-EHR |
| Data platform burden | Lowest | Medium-High | Medium | Medium-High |
| Clinical validation maturity | Strong (native); varies (App Orchard) | Moderate | Strong (DAX); Emerging (OpenAI) | Emerging-to-Moderate |
| Governance complexity | Low-Medium | Medium-High | Medium-High | High |
| Primary risk | App Orchard oversight | Config complexity | Per-provider cost; naming confusion | Newer products; fewer health references |
