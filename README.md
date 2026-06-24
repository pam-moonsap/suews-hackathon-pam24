# SUEWS Community Hackathon — Submission Template

Template repository for the **SUEWS Community Hackathon** (24 June 2026, UCL East), part of the UCL RDR Annual Conference.

> **Skeleton / work in progress.** The structure is in place; the city dataset and the heat-to-risk bridge function are added at kickoff on 24 June. See the participant Task Brief for the full guide.

## What this is

Each participant or team creates their own repository **from this template** (the green **"Use this template"** button, or `gh repo create`).

- **Before the day (practice):** create it under **your own GitHub account**, e.g. `gh repo create <your-username>/suews-hackathon-practice --template UMEP-dev/suews-hackathon-template --public --clone`. No special access needed.
- **On the day (judged entry):** you create it under the **UMEP-dev** organisation, once we have added you to the hackathon team.

Your on-the-day repository is what we judge.

## The task in one line

Use the **suews-agent** to produce a heat-hazard layer for the focus city, translate it into a socio-economic heat-risk indicator, and say plainly where the science holds and where it breaks.

## Repository layout

- `data/` — the challenge city, loaded at kickoff from [UMEP-dev/uda-city-hackathon](https://github.com/UMEP-dev/uda-city-hackathon) (land cover, building form, population, present and hotter-future forcing). See [`data/README.md`](data/README.md) for the one-line load step.
- `bridge/heat-to-risk.md` — points to the reference heat-to-risk bridge shipped with the dataset (`risk_bridge.py` + `risk_bridge.md`).
- `analysis/` — your suews-agent runs, configuration, and outputs.
- `transcripts/` — your exported AI session transcripts (judged evidence — save as you go).
- `docs/` — your public **GitHub Pages** showcase site (judged; must be public).

## Get started

The whole setup is one paste. See [`ONBOARDING_PROMPT.md`](ONBOARDING_PROMPT.md): open Codex or Claude Code, point it at an empty folder, and paste the prompt. It creates your repo from this template, installs the suews-agent, runs a first end-to-end query, publishes your Pages site, and saves your transcript.

## Links

- suews-agent: https://github.com/UMEP-dev/suews-agent
- SUEWS docs: https://docs.suews.io/
- GitHub Pages docs: https://docs.github.com/pages

## Citing SUEWS

Your submission must cite SUEWS (part of the Scientific soundness criterion):

- Järvi, L., Grimmond, C.S.B. & Christen, A. (2011). The Surface Urban Energy and Water Balance Scheme (SUEWS): Evaluation in Los Angeles and Vancouver. *Journal of Hydrology*, 411(3–4), 219–237. https://doi.org/10.1016/j.jhydrol.2011.10.001
- Ward, H.C., Kotthaus, S., Järvi, L. & Grimmond, C.S.B. (2016). Surface Urban Energy and Water Balance Scheme (SUEWS): Development and evaluation at two UK sites. *Urban Climate*, 18, 1–32. https://doi.org/10.1016/j.uclim.2016.05.001

For the version you run, follow the up-to-date [How to cite SUEWS](https://docs.suews.io/stable/#how-to-cite-suews).

## Acknowledgements

Part of **SUEWS-Next**, supported by the ERC Synergy Grant **urbisphere** (855505).
