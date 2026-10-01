# Entity documentation task

## Result

Created implementation-grounded documentation for the current Fact, relation, and Justification concepts:

- `docs/fact_enfity.md`
- `docs/relation_entity.md`
- `docs/justification.md`

The requested `fact_enfity.md` spelling was preserved exactly.

## Decisions

- Documented current behavior from `src/core/facts.py`, `src/core/justification.py`, `src/core/tms_engine.py`, and `src/core/knowledge_base.py`.
- Clearly identified that no standalone `Relation` entity currently exists instead of inventing an API.
- Included purpose, properties, methods, algorithms, component interactions, complexity where useful, edge cases, and known implementation constraints.
- Described possible relation-model extension points only as future options, not as implemented behavior.

## Rejected alternatives

- Renaming `fact_enfity.md` to `fact_entity.md` was rejected because the requested filename must be preserved.
- Changing source code to address documented limitations was rejected because the task requested documentation only.
- Describing intended behavior as completed functionality was rejected in favor of matching the repository's current implementation.
