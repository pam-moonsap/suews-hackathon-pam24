# Setup session transcript - 2026-06-24

## Request

Set up a SUEWS Community Hackathon practice repository, read the task brief,
run a small SUEWS example simulation, publish GitHub Pages from `docs/`, save a
transcript, then commit and push.

## Repository setup

- Checked `pam-moonsap/suews-hackathon-practice`: it already existed and was public.
- Checked `pam-moonsap/suews-hackathon-pam24`: it did not exist.
- Followed the explicit command target from the prompt:

```powershell
gh repo create pam-moonsap/suews-hackathon-pam24 --template UMEP-dev/suews-hackathon-template --public --clone
```

- Result: repository created and cloned successfully.
- Local path:
  `C:\Users\USER\Documents\Codex\2026-06-24\you-re-helping-me-get-set\suews-hackathon-pam24`
- Remote:
  `https://github.com/pam-moonsap/suews-hackathon-pam24.git`

Verification:

```powershell
git status --short
git remote -v
gh api repos/pam-moonsap/suews-hackathon-pam24 --jq '{html_url,private,default_branch,has_pages,visibility}'
```

Confirmed public repo, default branch `main`, clean checkout, and correct origin.

## Task brief

Read `TASK_BRIEF.md`.

Key understanding:

- The hackathon uses SUEWS and suews-agent to model urban heat in a heat-vulnerable city.
- The task is to produce a heat hazard layer and translate it into a socio-economic heat-risk indicator.
- The submission is judged on scientific soundness, honest hazard-to-risk bridging, professional contribution, presentation, and AI collaboration.
- The Pages site is the public judged showcase.
- SUEWS must be cited with the Jarvi et al. (2011) and Ward et al. (2016) papers, plus version-specific software citation guidance.

## SUEWS example simulation

The local `suews` and `suews-run` commands were not on PATH, and the SUEWS MCP
tool bootstrap hung on first use. I used the hackathon dataset's own
suews-agent-oriented route instead:

```powershell
gh repo clone UMEP-dev/uda-city-hackathon data\uda-city-hackathon
```

Then read:

- `data/uda-city-hackathon/agent_manifest.yml`
- `data/uda-city-hackathon/README.md`
- `data/uda-city-hackathon/scripts/smoke_test.py`
- `data/uda-city-hackathon/pyproject.toml`

Ran the provided smoke test:

```powershell
uv run python scripts\smoke_test.py
```

Result:

```text
OK: 10 site(s) x 2,016 steps (7 days) under supy 2026.6.5; NARP+OHM on disk; T2 26.2..38.9 C; config: uda-city.yml.
```

This confirms the UDA-city SUEWS configuration loads, the present forcing is
valid, the simulation completes for all 10 neighbourhoods, and `T2`/`QH`
diagnostics are finite.

Note: the dataset checkout and `.venv` are local working material and were not
staged in this commit.

## GitHub Pages

Enabled Pages from `main` branch and `/docs`:

```powershell
gh api --method POST repos/pam-moonsap/suews-hackathon-pam24/pages -f "source[branch]=main" -f "source[path]=/docs"
```

Build status check:

```text
status: built
error: null
```

Render check:

```text
https://pam-moonsap.github.io/suews-hackathon-pam24/ -> HTTP 200 OK
```

## URLs

- Repo: https://github.com/pam-moonsap/suews-hackathon-pam24
- Pages: https://pam-moonsap.github.io/suews-hackathon-pam24/
