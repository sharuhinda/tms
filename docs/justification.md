# Justification

## Purpose

`Justification` is a Pydantic record used by the repository's Justification-based Truth Maintenance System (JTMS). It connects one consequence fact to the set of premise facts required to support it:

```text
{premise A, premise B, ...} => consequence
```

Multiple justifications may support the same consequence. This represents alternative derivations: the consequence remains well justified when at least one complete premise set is active.

Entity implementation: [`src/core/justification.py`](../src/core/justification.py). Algorithms and indexes: [`src/core/tms_engine.py`](../src/core/tms_engine.py).

## Properties

| Property | Type | Default | Purpose |
| --- | --- | --- | --- |
| `id` | `str` | UUID4 hexadecimal string | Stable identifier for the justification. Callers may override it. |
| `consequence_id` | `str` | `""` | ID of the fact inferred or supported by this justification. |
| `premise_ids` | `Set[str]` | empty set | IDs of all facts that must be active for this justification to be satisfied. Set semantics remove duplicate IDs. |
| `source` | `str` | `"direct_input"` | Free-form provenance label, such as `user_utterance` or `rule_inference`. |

The entity defines no custom methods. Validation, serialization, copying, and schema behavior come from Pydantic `BaseModel`.

## Creation

The normal path is `TruthMaintenanceSystem.add_justification(consequence_id, premise_ids, source)`. It:

1. constructs a `Justification`;
2. appends it to the consequence's list in the forward index;
3. adds the consequence ID to the reverse-index entry for every premise ID.

`KnowledgeBase.add_fact(...)` calls this method only when its `premises` argument is truthy. Therefore `None` and an empty set both create a fact without a registered justification.

`add_justification(...)` currently returns `None`; it does not return the created record.

## Storage and indexes

`TruthMaintenanceSystem` maintains two in-memory indexes.

### Forward index

```python
justifications: Dict[str, List[Justification]]
```

Maps a consequence fact ID to all alternative justifications registered for it. A list is used, so duplicate records can be stored.

### Reverse index

```python
premise_to_consequences: Dict[str, Set[str]]
```

Maps a premise fact ID to every consequence that mentions it. This supports efficient dependent lookup during cascade retraction.

The two indexes are updated together when a justification is added. There is no removal or update operation, and neither index is persisted.

## Well-justified algorithm

`TruthMaintenanceSystem.is_well_justified(fact_id, active_fact_ids)` evaluates support as follows:

```text
if the fact has no registered justifications:
    return true

for each justification of the fact:
    if every premise ID belongs to active_fact_ids:
        return true

return false
```

Formally, a justification `J` is satisfied when:

```text
J.premise_ids ⊆ active_fact_ids
```

A consequence is well justified when at least one of its justifications is satisfied. This gives AND semantics within one premise set and OR semantics across alternative justifications:

```text
(A AND B) OR (C AND D) => consequence
```

A fact with no registered justification is treated as a base assumption or direct input and is always considered well justified by this method.

## Cascade belief revision

`KnowledgeBase.retract_fact_cascade(fact_id)` uses the reverse index and the well-justified test:

1. Mark the selected fact inactive.
2. Look up consequences that list it as a premise.
3. For each active consequence, evaluate all of its justifications against active fact IDs.
4. Keep the consequence if another premise set is fully active.
5. Otherwise, recursively retract that consequence.

This allows alternative derivations to protect a consequence. For example, if `{A, B}` and `{C}` are separate justifications for `D`, retracting `A` does not retract `D` while `C` remains active.

Retraction does not delete justification records or index entries. This preserves dependency history and permits inspection, but stale records remain in memory.

## Interaction with facts and relations

- `consequence_id` and `premise_ids` are string references to `Fact.id` values.
- The `Justification` object does not contain `Fact` objects.
- The model does not inspect subjects, relations, values, confidence, or validity intervals.
- Relation names do not affect whether a justification is satisfied.
- The TMS trusts the `active_fact_ids` set supplied by its caller.

## Complexity

Let `P` be the number of premises in a newly added justification, `J` the number of alternative justifications for a consequence, and `Pj` the premise count of justification `j`.

- Adding a justification: `O(P)` index updates, excluding dictionary/set amortized constants.
- Checking support: worst-case `O(sum(Pj) for j in J)`; it may return early when one justification succeeds.
- Finding immediate dependents of a premise: approximately `O(1)` dictionary lookup plus iteration over the returned consequence set.
- Cascade cost depends on the reachable dependency subgraph and repeated support checks.

## Validation and edge cases

### Empty premise set

Calling `TruthMaintenanceSystem.add_justification(...)` directly with an empty set creates a justification that is always satisfied, because an empty set is a subset of every active set. By contrast, `KnowledgeBase.add_fact(..., premises=set())` registers no justification because the empty set is falsey.

### Missing fact IDs

Neither the model nor the TMS verifies that premise or consequence IDs exist in `KnowledgeBase.facts`. A justification may therefore contain dangling references.

### Cycles

The current implementation has no explicit cycle detection. A cycle in the dependency graph can exist. Support checks do not recursively prove facts; they only test IDs against an externally supplied active set. Cascade retraction avoids immediately reprocessing a fact once it is inactive, but cyclic semantics are not otherwise defined.

## Current implementation constraints

- `source` is free-form and unvalidated.
- Direct-input source information is not retained when no premises are provided, because no justification record is created.
- There is no rule ID, explanation text, confidence score, timestamp, active flag, or validity interval on a justification.
- Duplicate justifications are allowed.
- Referential integrity is not enforced.
- Index entries are never removed or rebuilt.
- Recursive support is not computed independently; the TMS relies on caller-maintained fact activity.
- Cascade evaluation can use an active-ID snapshot that becomes stale after recursive sibling retractions.
- `datetime` is imported but unused in `src/core/justification.py`.

These limitations are observations about the current implementation, not guarantees about the intended final design.
