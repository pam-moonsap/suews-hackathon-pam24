# Prompt history - 2026-06-24

This file records the user prompts from the Codex session for the SUEWS
Community Hackathon practice repository. It is prompt-only evidence of the
collaboration path; detailed setup notes remain in `setup-session-2026-06-24.md`.

## Prompt 01

> You're helping me get set up for the SUEWS Community Hackathon. Do each step,
> check it worked before moving on, and tell me plainly if you need my input:
> 1. Create a public GitHub repo called suews-hackathon-Pam under the
> organization UMEP-dev, from the template UMEP-dev/suews-hackathon-template
> (gh repo create UMEP-dev/suews-hackathon-Pam --template
> UMEP-dev/suews-hackathon-template --public --clone), and open it.
> 2. Read TASK_BRIEF.md and check the newly loaded files in the data/ folder and
> bridge/heat-to-risk.md to understand our focus city and risk formula.

## Prompt 02

> clone UMEP-dev/suews-hackathon-template to UMEP-dev/suews-hackathon-Pam then
> accsess

## Prompt 03

> Show UMEP-dev/suews-hackathon-Pam repo

## Prompt 04

> You're helping me get set up for the SUEWS Community Hackathon. Do each step,
> check it worked before moving on, and tell me plainly if you need my input:
>
> Create a public GitHub repo under my own account called
> suews-hackathon-practice, from the template UMEP-dev/suews-hackathon-template
> (gh repo create pam-moonsap/suews-hackathon-pam24 --template
> UMEP-dev/suews-hackathon-template --public --clone), and open it.
> Read TASK_BRIEF.md in that repo so you understand the task.
> Using the suews-agent, run one small example SUEWS simulation to confirm the
> tool works end to end.
> Publish the docs/ folder as a public GitHub Pages site (main branch, /docs)
> and give me the URL.
> Save a transcript of this session into transcripts/, then commit and push.
> Finish by printing: my repo URL, my Pages URL, and a one-line status per step.

## Prompt 05

> You're helping me get set up for the SUEWS Community Hackathon. Do each step,
> check it worked before moving on, and tell me plainly if you need my input:
>
> Create a public GitHub repo under my own account called
> suews-hackathon-practice, from the template UMEP-dev/suews-hackathon-template
> (gh repo create pam-moonsap/suews-hackathon-pam24 --template
> UMEP-dev/suews-hackathon-template --public --clone), and open it.
> Read TASK_BRIEF.md in that repo so you understand the task.
> Using the suews-agent, run one small example SUEWS simulation to confirm the
> tool works end to end.
> Publish the docs/ folder as a public GitHub Pages site (main branch, /docs)
> and give me the URL.
> Save a transcript of this session into transcripts/, then commit and push.
> Finish by printing: my repo URL, my Pages URL, and a one-line status per step.

## Prompt 06

> I can't find uda data on GitHub pam-moonsap/suews-hackathon-pam24

## Prompt 07

> Show land cover data file

## Prompt 08

> Using the suews-agent, analyze the land cover and meteorological data to
> identify two contrast zones: the most built-up urban core versus the most
> vegetated suburban area. Run baseline simulations for the focus city.
> After that, create a climate change scenario by increasing the forcing air
> temperature by 2.5 C and run it. Extract the hourly sensible heat flux (QH),
> latent heat flux (QE), and air temperature (T2) for all runs.
> Then, please generate two high-quality plots and save them directly into the
> docs/ folder:
> 1. A diurnal cycle plot comparing QH and T2 between the baseline and climate
> change scenario for the high-risk zone.
> 2. A stacked bar chart showing the surface energy balance components (QN, QH,
> QE, QS) across different land-cover zones to highlight the Urban Heat Island
> effect. Correct details to match with full brief below:
> Focus city is UDA-city: a synthetic, lower-income, hot-humid, Colombo-like
> city with 10 neighbourhoods split into refuge/core/hotspot types. The main
> config is uda-city.yml; scenarios are present hot-humid and a +2.5 C future
> pseudo-warming. QF is off, so population is for exposure/risk, not model heat
> input.
> Risk bridge: default hazard is dangerous heat hours where hourly T2 > 35 C
> after spin-up. Exposure is daytime population density. Vulnerability combines
> over-65, under-5, lack of AC, outdoor work, and deprivation. The reference
> index is:
> risk_index = minmax((hazard * exposure * vulnerability)^(1/3))
> with all pillars scaled to [0, 1]. The bridge is explicitly a reference, not
> something we must copy blindly.

## Prompt 09

> Continue the prompt

## Prompt 10

> Why QH is the same for both present and future? Does it make sense?

## Prompt 11

> Ok. Try plotting the difference of QH (and QS, QE, QN) (calculate the change
> point by point first before doing the same methods) instead of QH for diurnal
> plot.

## Prompt 12

> Plot again by keep using T, not T change but keep using difference for heat
> fluxes

## Prompt 13

> Analyze the same thing but separate seasons (include 4 panels--each for one
> season in one figure) but still keep the previous analysis files (maybe we
> have to use it)

## Prompt 14

> Save prompts history
