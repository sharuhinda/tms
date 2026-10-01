# Relation Entity

## Current status

There is currently **no `Relation` class or standalone relation entity** in the repository. A relation is represented by the unconstrained `Fact.relation: str` field in [`src/core/facts.py`](../src/core/facts.py).

This document therefore describes the implemented relation semantics rather than an entity API that does not yet exist.

## Purpose

A relation is the predicate in a fact's directed triple:

```text
subject --relation--> value
```

It gives meaning to the connection between the subject and value. For example:

```text
Alice --works_at--> Acme
Alice --lives_in--> Berlin
```

The relation name also determines whether the knowledge base applies its current single-value conflict rule.

## Representation and properties

The only stored relation property is its name:

| Property | Type | Location | Behavior |
| --- | --- | --- | --- |
| `relation` | `str` | `Fact.relation` | Defaults to an empty string. `KnowledgeBase.add_fact` strips outer whitespace but performs no other normalization or validation. |

There is no relation ID, description, schema object, domain, range, inverse, cardinality field, version, or provenance record.

Relation names are matched exactly and case-sensitively. Consequently, `works_at`, `Works_At`, and `works-at` are three different predicates.

## Functional relations

`KnowledgeBase` initializes a mutable `functional_relations: Set[str]` containing:

- `works_at`
- `lives_in`
- `has_gout_diagnosis`

The set acts as a minimal in-memory ontology or TBox. A functional relation is treated as single-valued for a given subject among active facts. If two active facts have the same subject and functional relation but different values, they conflict.

The implementation does not expose dedicated registration methods. Callers can mutate the public set directly, for example:

```python
knowledge_base.functional_relations.add("has_primary_email")
```

That mutation is runtime-only; there is no persistence mechanism.

## Methods

No relation-specific methods exist. Relation behavior is distributed across other components:

- `KnowledgeBase.add_fact(...)` trims and stores the relation string.
- `KnowledgeBase.detect_conflicts(candidate)` applies functional-relation semantics.
- `KnowledgeBase.resolve_conflicts(new_fact, conflicts)` resolves the resulting fact conflicts by confidence.
- `Fact.__repr__()` includes the relation in debug output.

## Conflict-detection algorithm

The algorithm in [`src/core/knowledge_base.py`](../src/core/knowledge_base.py) is:

```text
function detect_conflicts(candidate):
    if candidate.relation is not in functional_relations:
        return []

    conflicts = []
    for fact in active facts:
        if fact.subject == candidate.subject
           and fact.relation == candidate.relation
           and lower(fact.value) != lower(candidate.value):
            conflicts.append(fact)

    return conflicts
```

Important comparison rules:

- relation names: case-sensitive;
- subjects: case-sensitive;
- values: case-insensitive;
- only active facts are considered;
- validity timestamps are ignored.

A non-functional relation can have any number of values for the same subject without triggering this algorithm.

## Conflict-resolution interaction

Relations identify conflicts but do not decide the winner. `KnowledgeBase.resolve_conflicts(...)` compares the facts' confidence scores. The new fact wins when its confidence is greater than or equal to the old fact's confidence; the losing fact is cascade-retracted.

Adding a fact does not automatically run conflict detection or resolution. The caller is responsible for this sequence:

```python
new_fact = knowledge_base.add_fact(...)
conflicts = knowledge_base.detect_conflicts(new_fact)
knowledge_base.resolve_conflicts(new_fact, conflicts)
```

## Relationship to justifications

Relations do not participate directly in JTMS dependency indexing. A `Justification` connects premise and consequence **fact IDs**, regardless of those facts' relation names. Causal and assumption links are therefore represented as support edges between facts, not as `Relation` entities.

## Missing entity capabilities

A future first-class relation model may need some or all of the following, but none is implemented now:

- a stable relation ID and canonical name;
- aliases or normalization rules;
- human-readable description;
- domain and range constraints;
- cardinality, including functional or inverse-functional flags;
- inverse, symmetric, transitive, or reflexive semantics;
- relation hierarchy or subproperty links;
- temporal applicability;
- provenance and versioning;
- persistence and a schema-registration API.

These are possible extension points, not current requirements or behavior.

## Current implementation constraints

- Functional semantics are hard-coded globally by relation name.
- No validation prevents empty, misspelled, or unknown relation names.
- Equivalent spellings or letter cases are not normalized.
- Conflict semantics cannot vary by subject type or context.
- Validity periods are ignored, so temporally distinct values can conflict.
- No persistence layer stores relation definitions.
- The README's causal links and assumptions are handled through justifications, not relation metadata.

Until a dedicated model is introduced, documentation and calling code should refer to a **relation string** or **predicate**, not imply that a `Relation` object exists.
