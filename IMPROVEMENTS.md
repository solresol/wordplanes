# IMPROVEMENTS.md

*Analysis date: 2026-07-11*

wordplanes is a small scientific-programming experiment (solresol/wordplanes) asking whether word embeddings for personality adjectives lie near 2D planes in embedding space. Pipeline: `personalityadjectives.py` (WordNet adjectives classified by Claude 3.5 Haiku into `personality_adjectives.sqlite`) → `createembeddings.py` (OpenAI + Ollama nomic-embed-text embeddings) → `language_plane_finder.py` (fits planes through triples of embeddings via `plane.py`, records distance statistics). Current state: the pipeline is broken by a syntax error introduced by an automated Sweep PR, there are no tests, and dependency management is a stale two-line `requirements.txt`.

## Bugs & Fixes (do these first)

1. **`plane.py` will not even import.** Inside `Plane._calculate_normal_basis`, a Sweep-generated commit left a stray `from typing import List, Tuple` at column 0 in the middle of the method body (around line 47, between the docstring block and the SVD call). That is a `SyntaxError`, which breaks `language_plane_finder.py` (it does `from plane import Plane`). Move the import to the top of the file. Then audit the other files for similar Sweep damage — the merged "add-type-annotations" PRs (#70, #71, #73 in `git log`) are the likely source.
2. **Consider disabling or fixing Sweep.** `sweep.yaml` contains the same rule three times ("Python functions should have type annotations") and its PRs have already broken the code once. Either remove `sweep.yaml` or dedupe the rules and review its PRs before merging.
3. **SQL built by f-string in `language_plane_finder.py`**: `table = f"{args.embedding_provider}_embeddings"` is interpolated into the query. Low risk (local CLI) but validate against a whitelist (`{'openai','ollama'}`) — a typo currently gives a confusing sqlite error.
4. **`Plane` numeric robustness**: the collinearity check (`< 1e-10`) is fine, but callers in `language_plane_finder.py` should catch the `ValueError` and skip that triple rather than crash mid-sweep.

## Housekeeping / Modernization

- **Migrate off `requirements.txt` to uv.** The two-line `requirements.txt` (`nltk`, `numpy`) is both useless and wrong — the code also imports `openai`, `requests`, `tqdm`, `pandas`, `matplotlib`, and `anthropic`. Create a `pyproject.toml` with `uv init` / `uv add nltk numpy openai requests tqdm pandas matplotlib anthropic`, commit `pyproject.toml` + `uv.lock`, delete `requirements.txt`, and run scripts as `uv run personalityadjectives.py` etc. Update the README's virtualenv/pip instructions accordingly.
- Delete editor backup files `createembeddings.py~` and `personalityadjectives.py~`, and the committed `__pycache__/` directory; add both patterns to `.gitignore`.
- `personality_adjectives.sqlite` (data) and `output-distributions/` (results) are committed to git. Fine for a small experiment, but consider whether the sqlite file should be regenerable-only (it costs API credits to rebuild, so keeping it is defensible — document that decision in the README).
- Decide the fate of `archive/` — the commit "I don't have the heart to delete these files yet" suggests it can go now.

## Improvements

- `language_plane_finder.py` is a flat script with module-level side effects (creates tables, runs the sweep at import). Wrap in `main()` so it can be imported and tested.
- The triple-sweep over all combinations is O(n^3); document expected runtime, and consider sampling triples (the `--random-seed` flag suggests this is partly intended) or parallelizing with `multiprocessing`.
- Embeddings are stored as JSON text in sqlite; storing as BLOBs of `np.float32` bytes would shrink the DB and speed up loading substantially.
- `createembeddings.py` uses the module-level `openai` API style; confirm it matches the installed SDK version once pinned via uv.
- `personalityadjectives.py` defines `create_tool_schema()` with an OpenAI-style `{"type": "function", "function": {...}}` wrapper — the Anthropic tools API expects `{name, description, input_schema}` at the top level. Verify this actually worked, or fix it before any re-run.

## Testing

- No tests exist. `plane.py` is pure numpy and trivially testable: unit-test `Plane` construction, collinearity rejection, `distance_to_plane` for known 3D cases, and that the normal basis is orthonormal and orthogonal to the plane directions. A syntax-error-level breakage (bug #1) would have been caught by even one import-level test.
- Add a minimal CI workflow (or fix the existing GitHub Actions referenced by sweep.yaml) that runs `uv run pytest` and a byte-compile/import check of every module.

## Documentation

- README covers the pipeline order well; add: expected runtimes/costs (Anthropic + OpenAI API usage), the schema of `planar_statistics`, what "the fitter" does, and how to interpret `output-distributions/` images.
- State the research question's current findings (are the distributions consistent with planar structure or not?) — the repo's whole point.

## Security

- No committed secrets found — API keys are read from the environment. Keep it that way.
- The f-string SQL noted above is the only injection-adjacent pattern.

## Quick Wins

1. Fix the misplaced import in `plane.py` (one-line move; unbreaks everything).
2. `rm *.py~; git rm -r --cached __pycache__` and update `.gitignore`.
3. Dedupe or delete `sweep.yaml`.
4. `uv init` + `uv add` the real dependency list; delete `requirements.txt`.
