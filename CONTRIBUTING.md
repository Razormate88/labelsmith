# Contributing to LabelSmith

Thanks for your interest in LabelSmith! This is a small, focused
package that turns messy human labels into clean, code-safe field
names. Contributions that keep it small, predictable, and well-tested
are very welcome.

## Setting up a local development environment

LabelSmith uses a src-layout package, `hatchling` for builds, and
`pytest` for tests. The `dev` optional dependency group pulls in only
what's needed for testing and building.

```bash
git clone https://github.com/Razormate88/labelsmith.git
cd labelsmith

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

After that, `python -c "import labelsmith; print(labelsmith.__version__)"`
should print the current version from your working tree.

## Running the test suite

```bash
python -m pytest
```

The default config lives in `pyproject.toml` (`[tool.pytest.ini_options]`).
It uses `pythonpath=["src"]` so tests run directly against the working
tree without reinstalling.

Please make sure the full test suite passes before opening a pull
request. New behavior should come with new tests; bug fixes should come
with a regression test that fails before the fix.

## Building and checking the package

```bash
python -m build
python -m twine check dist/*
```

The wheel must install cleanly with no transitive dependencies, and
`twine check` must pass before any release.

## Contribution expectations

* **Keep the scope small.** LabelSmith intentionally avoids Excel/PDF
  parsing, LLM calls, database integration, and schema generation.
  Features in those areas belong in companion packages, not here.
* **No runtime dependencies.** LabelSmith uses only the Python
  standard library at runtime. New runtime imports (anything not in
  the stdlib) should be discussed in an issue before being added.
* **Deterministic behavior.** Same input, same output, every time. No
  hidden state. No randomness in the public API.
* **Maintain the public API surface.** `field_name`,
  `field_names`, and `field_map` are the only public entry points.
  Breaking changes to their signatures or documented behavior require
  a deliberate version bump and a clear CHANGELOG entry.
* **Type everything.** New code should carry annotations; the
  `py.typed` marker depends on it.
* **Update the docs.** If your change is user-facing, please update
  `README.md` and add a `CHANGELOG.md` entry under the
  next-release heading.

## Reporting issues

Please use the GitHub issue templates at
<https://github.com/Razormate88/labelsmith/issues/new/choose>. A small,
self-contained reproduction is the fastest path to a fix.

## License

By contributing, you agree that your contributions will be licensed
under the [MIT License](LICENSE), the same license as the project.
