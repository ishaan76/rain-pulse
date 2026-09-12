# AquaAlert AI — Agent Collaboration Rules & Boundaries

## 1. Directory Ownership & Boundaries
- **Agent 1** $\rightarrow$ `data/weather/`
- **Agent 2** $\rightarrow$ `data/terrain/`
- **Agent 3** $\rightarrow$ `model/`
- **Agent 4** $\rightarrow$ `backend/`
- **Agent 5** $\rightarrow$ `app/`
- **Agent 6** $\rightarrow$ `tests/`

Agents may read other directories. Agents should not unnecessarily modify another agent's core files.
When integration requires a cross-module change:
1. Inspect the existing implementation.
2. Make the smallest necessary change.
3. Document the change.
4. Run relevant tests.

## 2. Shared Project Rules
1. Inspect the repository before editing.
2. Preserve existing working functionality.
3. Avoid unnecessary dependencies.
4. Keep interfaces simple and documented.
5. Use type hints on public Python functions.
6. Use Google-style docstrings.
7. Add tests for important functionality.
8. Run relevant tests before finishing.
9. Never hard-code API keys or secrets.
10. Use environment variables for secrets/configuration.
11. Handle missing and invalid data safely.
12. Document assumptions.
13. Do not claim unsupported scientific accuracy.
14. Do not duplicate another agent's logic.
15. Keep demo mode working.
16. Leave the repository in a state that another teammate/AI worker can continue from.
17. Make the smallest reasonable changes.
18. If changing a shared interface, document the change.
19. Prefer clarity and reliability over cleverness.
20. Never delete another agent's work without explicit justification.

## 3. Definition of Done
A feature is finished when:
1. Code written with type hints & Google-style docstrings.
2. Dependencies installed/verified.
3. Tests written and passing (`pytest`).
4. Code passes formatting and linting.
5. Feature manually verified.
6. Documentation updated.
