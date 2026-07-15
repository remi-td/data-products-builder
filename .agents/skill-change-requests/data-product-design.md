# Change Request: data-product-design skill

**Source skill:** `.agents/skills/data-product-design/SKILL.md`  
**Derived from:** generic source-image build
**Status:** Ready to submit

---

## CR-1: Profiling Fallback for Wide Tables

**Insert before `## Key Constraints`**

**Motivation:** Live SQL profiling of a very wide table (391 columns × 12M rows) timed out after 2 hours and caused AMP contention that interfered with concurrent staging loads. The build was unblocked by switching to codebook-inferred types (enumerate-size heuristic + VARCHAR fallback). This heuristic should be a first-class recommendation rather than an undocumented emergency workaround.

Also: the initial attempt ran profiling concurrently with a FastLoad, which caused both to contend for AMP resources and eventually caused a staging load failure. These operations must be serialized.

**Text to add:**

```markdown
## Profiling Fallback for Wide Tables

Live SQL profiling of wide tables (300+ columns × 10M+ rows) commonly times out or causes AMP contention on trial and bandwidth-limited environments. When profiling stalls:

1. **Enumerate-size heuristic:** If the source codebook lists fewer than 30 distinct enumerated values for a column, infer `BYTEINT` or `SMALLINT`. If it lists a date-like label (e.g. "incident date", "date of birth"), infer `VARCHAR(8)` or `VARCHAR(10)`.
2. **Fallback default:** Use `VARCHAR(1000) CHARACTER SET LATIN` for all columns where the codebook is ambiguous or unavailable. This is always safe — no cast failures, preserves leading zeros and mixed content.
3. **Never block a build on profiling.** Generate DDL from the lossless fallback, document the decision in `Memory.Design_Decision`, and profile in the background after deployment. Type narrowing can be applied in a later Semantic or Prediction layer.
4. **Separate profiling from DDL deployment.** Never run profiling queries on the critical path while staging loads are in flight — they compete for the same AMP resources and can cause both to time out.
```
