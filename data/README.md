# City dataset

The focus city is **UDA-city**, released at kickoff on 24 June as a public repository:
[UMEP-dev/uda-city-hackathon](https://github.com/UMEP-dev/uda-city-hackathon).

## Load it at kickoff

In plain language, tell your AI agent:

> Add the challenge city from https://github.com/UMEP-dev/uda-city-hackathon into my `data/`
> folder, then load it and confirm it runs.

The agent reads `agent_manifest.yml` first, which loads `uda-city.yml` — the shared
**10-neighbourhood** city everyone analyses, so every submission is directly comparable. The
pack also carries the present and a hotter-future (+2.5 °C) forcing, the per-neighbourhood
socio-economic profile (population and vulnerability proxies), and the reference
heat-to-risk bridge (`risk_bridge.py` + `risk_bridge.md`).

Prefer the command line?

    gh repo clone UMEP-dev/uda-city-hackathon
    # then point your agent at uda-city-hackathon/agent_manifest.yml

Note: anthropogenic heat (QF) is off in this dataset, so per-neighbourhood population is
exposure data for the risk bridge, not a model-heat input.
