# CRITICAL RULES

* Don't assume. Don't hide confusion. Surface tradeoffs. If not sure — ASK, not guess
* One task at a time, DO NOT do several changes simultaneously. Minimum that solves the problem, nothing speculative. Touch only what you must. No code refactoring until asked explicitly
* ALWAYS use `beads-issue-tracker` skill for issue management and issue tracking instead of Markdown TODOs or other external tools
* DO NOT change existing tests without asking user
* ALWAYS run tests after any code change
* ALWAYS do `git checkpoint` before serious refactoring
* ALWAYS write down to `docs/agent\_descr` a summary about tasks you have done: what was done, what options were considered and rejected, what was the final decision and why


# Working Style

* PLAN first, then code or act
* use subagents for codebase exploration
* ALWAYS create separate git branch for each issue taken into work
* small diffs: one file → tests → next file
* always make sure the virtual environment is activated before performing any action using command line or terminal. All actions should be performed in the virtual environment ONLY. If the virtual environment is not active, activate it by calling `source ./.venv/bin/activate` command.
* if needed to install new packages, always use `uv add` command in the virtual environment.


# Using subagents

* Use `tester` subagent after any code changes. ALWAYS ask user explicitly for changing tests
* Use `code-reviewer` agent before committing changes



# Development Guidelines

## Before Committing

1. **Activate virtual environment**: `source .venv/bin/activate`
2. **Run tests**: `python3 -m pytest`
3. **Export issues**: `bd export -o .beads/issues.jsonl`
4. **Update docs**: If you changed code's behavior, update README.md and other relevant docs



# Current Project Status

Run `bd stats` to see overall progress.



# Questions?

* Check existing issues: `bd list`
* Look at recent commits: `git log --oneline -20`
* Read the docs: README.md, AGENTS.md, files in 'docs' folder
* Create an issue if unsure: `bd create "Question: ..." -t task -p 2`



# Important Files

* **README.md** - Main documentation (keep this updated!)
* **AGENTS.md** - Agent guidelines and instructions
* search for place where documentation is stored in project folder structure



# Pro Tips for Agents

* Check `bd ready` before asking "what next?"
* Use `bd dep tree` to understand complex dependencies
* Priority 0-1 issues are usually more important than 2-4



# Landing the Plane (Session Completion)

When ending a work session use `land-the-plane` skill.

