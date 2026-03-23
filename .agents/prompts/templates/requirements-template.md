# Data Product Requirements Template

Use this template to gather requirements before starting a build. Replace all `[PLACEHOLDER]` values.

## Data Product Definition

**Product name:**
[e.g. Customer360, FraudDetection]

**Business purpose:**
[What problem does this data product solve?]

**Primary consumers:**
[Who or what uses this — agents, applications, analysts, APIs?]

**Top use cases:**
[3-5 specific use cases, e.g. "Customer churn prediction", "Similar product discovery"]

## Modules Needed

- [ ] Domain/Subject Data — always required
- [ ] Semantic — always required
- [ ] Prediction (Feature Store)
- [ ] Search (Vector Embeddings)
- [ ] Observability (Monitoring & Audit)
- [ ] Memory (Agent State & Learning)

## Technical Context

**Data sources:**
[Source systems that feed this product, e.g. CRM, ERP, event stream]

**Approximate data volumes:**
[Estimated row counts and growth rate for primary entities]

**Latency requirements:**
[Batch / near-real-time / real-time scoring]

**Database layout preference:**
[Separate database per module (enterprise default) or single database with module prefixes (simpler)]
