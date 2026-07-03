# Skill: dpds-generate

Generate or refresh a valid Open Data Mesh Data Product Descriptor Specification (DPDS 1.0.0)
document for a deployed AI-Native Data Product. The descriptor is a **living artefact** —
derived entirely from the product's Semantic and Memory modules. It is never manually
authored. Run at product creation and whenever the product structure changes.

---

## When to Invoke

- After Deliverable 7 completes, if the customer uses Open Data Mesh or requires a DPDS
  descriptor
- When a customer or partner asks for a mesh-compliant descriptor or data contract document
- After new modules or entities are added to a deployed product
- Trigger phrases: "generate DPDS", "create Open Data Mesh descriptor", "make this product
  mesh-compatible", "update the descriptor", "generate the data contract"

---

## Inputs Required

Confirm these before starting. Ask if any are missing.

| Input | Source |
|-------|--------|
| `{ProductName}` | Provided by user (e.g. `MortgagePlatform`) |
| `{ProductDomain}` | Provided by user (e.g. `Financial Services / Mortgage Lending`) |
| `{ProductOwner}` | Provided by user (name + contact) |
| `{org}` | From `config/` or provided by user |

---

## Phase 1 — Bootstrap from Live Metadata

Query the Semantic and Memory modules. Do not hardcode any product-specific content.

### 1.1 Confirm deployed modules

```sql
SELECT module_name, database_name, module_purpose, agent_entry_view
FROM {ProductName}_Semantic.data_product_map
WHERE is_active = 1
ORDER BY module_name;
```

If this query fails, stop and ask the user to confirm the product name and that the product
is deployed.

### 1.2 Get all active entities

```sql
SELECT entity_name, module_name, database_name,
       table_name, view_name, entity_description,
       natural_key_column, surrogate_key_column
FROM {ProductName}_Semantic.entity_metadata
WHERE is_active = 1
ORDER BY module_name, entity_name;
```

Classify each entity into its DPDS port role:

| Entity Module | View Name Pattern | DPDS Port Role |
|---------------|-------------------|----------------|
| STAGING | any | Input Port |
| DOMAIN | ends `_Current` or `_Enriched` | Output Port |
| SEMANTIC | entry view | Discovery Port |
| OBSERVABILITY | `v_quality_failures`, `v_recent_changes` | Observability Port |
| MEMORY | `agent_session` | Control Port |

Reference tables (`_R`) and history tables (`_H`) without views are internal storage
components — not ports.

### 1.3 Pull data contract content from Memory

```sql
SELECT term, definition, business_context, related_table, related_column
FROM {ProductName}_Memory.Business_Glossary
WHERE is_active = 1
ORDER BY term;
```

```sql
SELECT decision_id, decision_title, rationale, consequences
FROM {ProductName}_Memory.Design_Decision
WHERE is_current = 1
ORDER BY decision_id;
```

### 1.4 Pull ETL lineage for application components

```sql
SELECT source_table, target_table, transformation_logic
FROM {ProductName}_Observability.data_lineage
WHERE is_active = 1
ORDER BY source_table, target_table;
```

If `data_lineage` is empty, omit `applicationComponents` and note the gap in the summary.

### 1.5 Check for existing quality SLAs

```sql
SELECT database_name, table_name, metric_name, metric_value, threshold_value
FROM {ProductName}_Observability.data_quality_metric
WHERE measured_at = (
    SELECT MAX(measured_at)
    FROM {ProductName}_Observability.data_quality_metric
)
ORDER BY table_name, metric_name;
```

If empty, include an `x-quality-sla` note in the descriptor that thresholds are pending
first production ETL run.

---

## Phase 2 — Compose the DPDS Descriptor

Build the JSON document using Phase 1 data. The structure below is the required skeleton —
populate all fields from live metadata.

### Top-level structure

```json
{
  "dataProductDescriptor": "1.0.0",
  "info": {
    "name": "{ProductName}",
    "fullyQualifiedName": "urn:dpds:{org}:{domain-slug}:{ProductName}:1",
    "version": "1.0.0",
    "domain": "{ProductDomain}",
    "owner": { "id": "{owner-id}", "displayName": "{ProductOwner}" }
  },
  "interfaceComponents": {
    "inputPorts": [...],
    "outputPorts": [...],
    "discoveryPort": {...},
    "observabilityPort": {...},
    "controlPort": {...}
  },
  "internalComponents": {
    "applicationComponents": [...],
    "infrastructuralComponents": [...]
  }
}
```

### Port construction rules

**Input Ports** — one per entity in STAGING module:
- `id` and `name`: kebab-case of staging table name
- `description`: from `entity_description` in entity_metadata
- `offeredApi.definition`: DatastoreAPI (DSAS) referencing the staging table and natural key

**Output Ports** — one per DOMAIN entity with a `_Current` or `_Enriched` view:
- `id` and `name`: kebab-case of entity name (e.g. `loan-current`)
- `description`: BIAN service domain + entity description from entity_metadata
- `offeredApi.definition`: DatastoreAPI referencing the view, noting natural key, surrogate
  key, and whether append-only
- `promises.deprecationPolicy`: `SUPPORTED_UNTIL_FURTHER_NOTICE`
- `promises.lifecycle.status`: `ACTIVE`
- `expectations.audience`: `["data-engineers", "analysts", "ai-agents"]` — extend with
  `"compliance-teams"` or `"risk-teams"` where relevant based on entity content
- `expectations.usage`: derived from entity_description and any relevant Business_Glossary
  terms for that entity's key columns
- Add `obligations.termsAndConditions` for entities containing PII or regulated data — check
  `column_metadata.is_pii` and `column_metadata.is_sensitive` flags

**Discovery Port** — one port named `semantic-discovery`:
- `servicesEndpointUrl`: points to the Semantic module entry view from `data_product_map`
- `offeredApi.definition`: DatastoreAPI listing the key Semantic entry points:
  `data_product_map`, `entity_metadata`, `column_metadata`, `v_relationship_paths`
- `expectations.usage`: bootstrap sequence — query `data_product_map` first, then
  `entity_metadata`, then on-demand resources

**Observability Port** — one port named `observability`:
- Exposes `v_quality_failures` and `v_recent_changes` as monitoring endpoints
- Include the `x-quality-sla` extension with threshold data from Phase 1.5 (or pending note)
- Note any regulatory audit trail requirements from Design_Decision records

**Control Port** — one port named `agent-control`:
- Exposes `agent_session` and `agent_interaction` from the Memory module

### Internal components

**`applicationComponents`** — one per row in `data_lineage`:
- `id`: kebab-case of `source_table → target_table`
- `description`: from `transformation_logic`
- `sourceTable` and `targetTables` populated from the lineage row

**`infrastructuralComponents`** — one per deployed database from `data_product_map`:
- `id`: kebab-case of database name
- `platform`: `"Teradata Vantage"`
- `infrastructureType`: `"storage"`
- `description`: from `module_purpose`

### Custom extension

Include `x-ai-native-data-product` at the top level:

```json
"x-ai-native-data-product": {
  "designStandard": "https://github.com/Teradata/ai-native-data-products",
  "modules": [...],
  "deferredModules": [...],
  "agentBootstrapQuery": "SELECT module_name, database_name, agent_entry_view FROM {ProductName}_Semantic.data_product_map WHERE is_active = 1 ORDER BY module_name",
  "generatedAt": "{CURRENT_DATE}",
  "generatedBy": "dpds-generate skill — derived from {ProductName}_Semantic and {ProductName}_Memory"
}
```

Populate `modules` and `deferredModules` from `data_product_map`.

---

## Phase 3 — Output and Registration

### Write the descriptor

Save the completed JSON to:

```
workspace/docs/{product-name}/dpds-descriptor.json
```

Validate that the JSON is well-formed before writing. If invalid, fix before saving.

### Register in Memory

Insert a Design Decision record:

```sql
INSERT INTO {ProductName}_Memory.Design_Decision (
    decision_id, decision_title, decision_status,
    rationale, consequences, affects_table,
    valid_from, valid_to, is_current
) VALUES (
    'DD-DPDS-001',
    'Open Data Mesh DPDS Descriptor Generated',
    'ACCEPTED',
    'DPDS 1.0.0 descriptor auto-generated from Semantic and Memory modules to enable Open Data Mesh interoperability. Descriptor reflects live product state at time of generation.',
    'Descriptor must be regenerated (re-run dpds-generate skill) whenever entity structure, port views, or data contract terms change. Do not manually edit dpds-descriptor.json — it is a derived artefact.',
    'ALL',
    CURRENT_DATE, DATE ''9999-12-31'', 1
);
```

If a `DD-DPDS-NNN` record already exists with `is_current = 1`, set it to `is_current = 0`
and insert the next sequence number.

### Summary report

Report to the user:
- Descriptor file path
- Port counts: input / output / discovery / observability / control
- Number of application components and infrastructural components
- Any entities skipped (explain why — e.g. reference tables, `_H` tables without views)
- Any gaps: empty lineage table, empty quality metrics, missing views
- Whether this was a first-time generation or a refresh

---

## Refresh Behaviour

When run on a product where `dpds-descriptor.json` already exists:

1. Read the existing file and note the `info.version`
2. Re-run Phase 1 queries
3. Compare module count and entity count against the existing descriptor
4. If structure has changed: regenerate fully and increment the patch version
   (e.g. `1.0.0` → `1.0.1`)
5. If no structural change: report "Descriptor is current — no changes detected" and exit
   without writing

---

## Error Handling

| Condition | Action |
|-----------|--------|
| `{ProductName}_Semantic` not found | Stop — confirm product name and deployment status with user |
| `data_product_map` returns 0 rows | Warn; attempt `entity_metadata` directly as fallback |
| No DOMAIN entities have a `view_name` | Warn — no output ports can be mapped; list entities found and suggest adding views |
| `data_lineage` empty | Omit `applicationComponents`; note in summary |
| Quality metrics empty | Include `x-quality-sla` pending note; do not block generation |
| JSON validation fails | Show invalid fragment; fix before writing |
