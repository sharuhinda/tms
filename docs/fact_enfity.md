# Fact Entity

## Purpose

`Fact` is the repository's primary knowledge record. It represents a directed statement in the form:

```text
subject --relation--> value
```

For example, `person:alice --works_at--> company:acme` can be stored as one fact. Facts are held by `KnowledgeBase`, keyed by their generated IDs. A fact can be deactivated without being deleted, which lets the truth-maintenance logic preserve history while revising the currently accepted set of beliefs.

Implementation: [`src/core/facts.py`](../src/core/facts.py). Storage and lifecycle behavior: [`src/core/knowledge_base.py`](../src/core/knowledge_base.py).

## Properties

| Property | Type | Default | Purpose |
| --- | --- | --- | --- |
| `id` | `str` | UUID4 hexadecimal string | Stable identifier used by the knowledge base and justification graph. Callers may supply their own value. |
| `subject` | `str` | `""` | Entity or concept about which the statement is made. |
| `relation` | `str` | `""` | Predicate connecting `subject` to `value`. Relations are currently plain strings. |
| `value` | `str` | `""` | Object or value asserted by the statement. |
| `confidence` | `float` | `0.0` | Confidence score constrained by Pydantic to the inclusive range `[0.0, 1.0]`. Used during conflict resolution. |
| `is_active` | `bool` | `True` | Soft-deletion flag. Inactive facts remain stored but are excluded from the active belief set. |
| `created_at` | `datetime` | `datetime.now()` | Creation time. It is currently a naive local datetime. |
| `valid_from` | `datetime` | `datetime.now()` | Intended start of the fact's validity interval. |
| `valid_until` | `Optional[datetime]` | `None` | Intended end of the validity interval; `None` means no declared end. |
| `discourse_role` | `str` | `"nucleus"` | Reserved Rhetorical Structure Theory role, currently expected informally to be `nucleus` or `satellite`. |
| `discourse_weight` | `float` | `1.0` | Reserved rhetorical-importance weight. It currently has no effect on TMS decisions. |

`created_at` and `valid_from` use separate default factories, so their values may differ slightly.

## Construction and validation

`Fact` extends Pydantic's `BaseModel`. Pydantic validates declared types and the bounds on `confidence`. No model-level validator currently enforces:

- non-empty `subject`, `relation`, or `value`;
- uniqueness of a statement;
- a controlled relation vocabulary;
- timezone-aware timestamps;
- `valid_until >= valid_from`;
- allowed discourse roles or bounds for `discourse_weight`.

`KnowledgeBase.add_fact(...)` is the usual construction path. It strips outer whitespace from `subject`, `relation`, and `value`, creates the model, stores it in `facts[id]`, and optionally registers a justification. Direct construction with `Fact(...)` does not strip strings.

A notable default difference exists: `Fact()` defaults `confidence` to `0.0`, while `KnowledgeBase.add_fact(...)` defaults it to `1.0`.

## Methods

### `__repr__()`

Returns a compact debugging representation containing:

- the first six characters of the ID;
- `ACT` for an active fact or `DEL` for an inactive fact;
- the subject-relation-value triple;
- confidence rounded to two decimal places;
- the discourse role.

Example shape:

```text
Fact[a1b2c3][ACT] (Alice --works_at--> Acme) [conf=0.90, rst=nucleus]
```

All serialization, copying, schema generation, and general validation methods are inherited from Pydantic `BaseModel`.

## Algorithms involving facts

### Active-set selection

A fact belongs to the active belief set if and only if `is_active` is true. The current implementation does not evaluate `valid_from` or `valid_until`.

```text
active facts = every stored fact where fact.is_active is true
active IDs   = IDs of those facts
```

### Conflict detection

Conflicts are detected only for relation names listed in `KnowledgeBase.functional_relations`. The initial set is:

- `works_at`
- `lives_in`
- `has_gout_diagnosis`

Given a candidate fact:

1. If its relation is not functional, return no conflicts.
2. Iterate over active facts.
3. Select facts whose subject and relation exactly match the candidate.
4. Treat different values as conflicting, comparing values case-insensitively.

Subject and relation comparisons are case-sensitive. Temporal validity is ignored, so values intended for different time periods can still conflict.

### Conflict resolution

For each conflicting old fact, the implementation compares confidence:

```text
if new confidence >= old confidence:
    cascade-retract the old fact
else:
    cascade-retract the new fact
```

The new fact wins a tie. Despite the method description mentioning a latest-value-wins policy, only confidence-based arbitration is implemented. Conflict detection and resolution are not called automatically by `add_fact`; a caller must invoke them explicitly.

### Cascade retraction

`KnowledgeBase.retract_fact_cascade(fact_id)` performs belief revision:

1. Stop if the fact does not exist or is already inactive.
2. Set `is_active` to `False` rather than deleting the fact.
3. Use the TMS reverse index to find consequences that depend on the retracted fact.
4. For each active consequence, ask whether at least one complete justification remains satisfied by active facts.
5. Recursively retract a consequence when no alternative justification remains.

Justifications and dependency-index entries are retained after retraction, preserving dependency history.

## Interactions with other components

- `KnowledgeBase.facts` stores `Fact` instances by ID.
- `Justification.consequence_id` and `premise_ids` refer to facts by ID; they do not embed fact objects.
- `TruthMaintenanceSystem` determines support from the caller-provided set of active fact IDs.
- Relation semantics are supplied by `KnowledgeBase.functional_relations`, not by a separate relation object.

## Current implementation constraints

- The README mentions vector representations, but `Fact` has no embedding or vector field.
- The distinction between ontology facts and knowledge-graph facts is explicitly unresolved in the model's TODO.
- Temporal metadata is stored but is not used to calculate activity or conflicts.
- RST fields are placeholders and do not participate in reasoning.
- Empty and duplicate facts are allowed.
- IDs referenced by justifications are not checked for referential integrity.
- In a multi-conflict resolution, a retracted new fact may still retract later old facts because the loop continues without checking the new fact's state.
- Cascade retraction computes an active-ID snapshot once per recursive invocation; sibling retractions can make an earlier snapshot stale.
- `resolve_conflicts` returns `(retracted, kept)`, but `kept` is never populated.

These constraints describe the current code rather than proposed behavior.
