# Decisions

Non-obvious choices and their trade-offs, dated, newest section first. Read the relevant entry before changing a mechanism that looks odd. Choices made autonomously under a delegation are recorded here for the user to review; an entry is a record, not a claim that the capability is complete.

## 2026-10-11

| Decision | Reason and trade-off |
| --- | --- |
| Adopted docket with gates that are red on arrival: the test suite and the format check already failed on `main`, and the fixes are queued in `TODO.md` rather than folded into the adoption change. | Keeps the adoption reviewable as tooling and documentation only, and makes the existing breakage visible instead of hiding it behind a skipped gate. Until `fix-broken-tests` and `ruff-baseline` land, `bash scripts/check.sh` and the CI check job fail on every branch. |
| Until `fix-broken-tests` lands, pushing with `git push --no-verify` is allowed when the PR states it and the change touches no Python. | The pre-push hook runs the suite, which fails on `main` for reasons that predate the hooks, so without this exception no branch could be pushed. Python changes wait for `fix-broken-tests`, which makes the hook pass. Remove this entry in the `fix-broken-tests` PR. |
| Hooks are a tracked `.githooks/` directory wired with `core.hooksPath`, not a hook manager. | No extra tool to install for a two-hook setup. Pre-commit checks the staged content of staged Python files with ruff and never rewrites; pre-push runs the unit suite. Switch to the `pre-commit` framework or lefthook if hooks grow beyond that. |
| Development tools are pinned in `requirements-dev.txt` and Python in `.python-version`; runtime dependencies stay unpinned in `setup.py`. | Enough for reproducible gates without restructuring packaging. A full lock (`pyproject.toml` with `uv.lock`) is queued as `adopt-pyproject-lock`. |
| Ruff's rule set is fixed in `ruff.toml` (`E4`, `E7`, `E9`, `F`, `I`, line length 100). | Without a project config ruff falls back to the user-level config, so local runs and CI would disagree. The selection is ruff's defaults plus import sorting; widen it when a review finds a recurring class of problem. |
| No type checker gate yet. | The code has partial annotations and the daemon depends on untyped rumps; a strict checker would need its own cleanup first. Queued as `add-typecheck-gate`. |
| CI's check job runs on `macos-latest`. | macOS is the only target platform, and the daemon depends on rumps, which is macOS-only, once `setup.py` declares it (`fix-setup-metadata`). The repository is public, so macOS runner minutes are not billed. |
| Scheduled validation of `main` is deferred. | Nothing on `main` is expensive enough to need a run that PR and push CI cannot afford, and a dormant repository has its schedules disabled by GitHub after sixty days anyway. Add `main-validation.yml` when that changes or when codebase reviews start. |
