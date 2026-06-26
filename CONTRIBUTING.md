# Contributing to VibeForge

Thanks for taking the time to contribute! Here's everything you need to know.

---

## Getting Started

```bash
git clone https://github.com/YOUR_USERNAME/vibeforge.git
cd vibeforge
uv sync
cp .env.example .env   # add your GROQ_API_KEY
```

Run the unit tests to confirm your environment is working:

```bash
uv run pytest tests/test_models.py -v
```

---

## Ways to Contribute

- **Bug reports** — open an issue with the error output and your OS/Python version
- **New LLM provider** — add a backend in `playlist_agent.py` and document it in README
- **New context source** — extend `context.py` (e.g. calendar, location)
- **UI improvements** — `display.py` uses Rich; new layouts / export formats welcome
- **Tests** — more coverage in `tests/` is always appreciated

---

## Pull Request Guidelines

1. **One concern per PR** — keep diffs focused and easy to review
2. **Tests** — add or update tests for any changed behaviour
3. **No new dependencies** without discussion in an issue first
4. **Type hints** — all public functions must be fully annotated
5. **No comments** that just restate what the code does — only add comments for non-obvious *why*

### Branch naming

```
feature/add-spotify-export
fix/memory-file-path
docs/update-provider-table
```

---

## Code Style

- Formatter: none enforced, but keep lines under 100 chars
- Imports: stdlib → third-party → local, each group alphabetical
- Pydantic models go in `models.py`; new agents go in their own file

---

## Reporting Issues

Please include:
- OS and Python version (`python --version`)
- Full error traceback
- The `--mood` input that triggered the issue
- Which LLM provider you're using

---

## License

By contributing you agree your code will be released under the [MIT License](LICENSE).
