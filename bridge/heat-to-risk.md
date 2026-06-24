# Heat-to-risk bridge

The reference bridge ships in the challenge dataset repository,
[UMEP-dev/uda-city-hackathon](https://github.com/UMEP-dev/uda-city-hackathon):

- `risk_bridge.py` — the runnable function.
- `risk_bridge.md` — how it works, plus the caveats that must travel with any output.
- `socioeconomic.csv` — the per-neighbourhood socio-economic inputs it uses.

It follows the UNDRR framing: risk = hazard × exposure × vulnerability, each scaled to
[0, 1] and combined as a geometric mean. The hazard comes from your SUEWS run; exposure
and vulnerability come from the dataset.

This is a **reference, not the answer you must copy.** The threshold, the weights, and the
combination rule are all exposed as choices, so define and justify your own. Your task
includes saying plainly where this hazard-to-risk link holds and where it breaks — that
honest discussion is itself a judged criterion.
