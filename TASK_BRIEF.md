# SUEWS Community Hackathon — Task Brief

> Canonical version: the Task Brief post in the SUEWS hackathon forum. This in-repo copy is a synced snapshot so your AI agent can read it locally.

*A guide for everyone taking part: what to expect and how to prepare. 24 June 2026, [UCL East](https://www.ucl.ac.uk/ucl-east/).*


## Overview

At this hackathon you use SUEWS, driven through the [suews-agent](https://github.com/UMEP-dev/suews-agent), to model urban heat in a heat-vulnerable city, then translate that hazard into a socio-economic heat-risk indicator. Alongside the result, you say plainly where the science holds and where the current model set-up breaks, and what should come next. Together these steps help shape what AI-assisted urban climate and disaster risk reduction can become.

## Key people involved

- About 20 attendees: researchers, students and practitioners.
- SUEWS-expert table leads: Vitor Lavor (Reading), Megan Stretton (Met Office / Reading), Matthew Paskin (Reading), Yiqing Liu (Reading).
- suews-agent and AI tools: Jiapei Liu (Tsinghua / UCL).
- Lead (logistics and planning): Ting Sun (UCL). Co-lead (science): Sue Grimmond (Reading).

## SUEWS and the suews-agent

[SUEWS](https://docs.suews.io/) (Surface Urban Energy and Water Balance Scheme) is an established urban climate model. Given an area's land-cover types and their relative fractions, building and tree heights, anthropogenic heat emissions and meteorology, it returns local outdoor air temperature, the surface energy balance, and water fluxes from neighbourhood to regional scale. At the hackathon you work with the model through a two-tool AI stack: a **general AI coding agent** ([Codex](https://chatgpt.com/codex/), [Claude Code](https://claude.com/claude-code), or your tool of choice) for coding, document and web tasks; and **[suews-agent](https://github.com/UMEP-dev/suews-agent)**, which wraps SUEWS to turn plain-language questions into model runs, help you pick the parameters to change, and return results with caveats on what the model can and cannot represent. You do not write code yourself: you instruct your AI agent in plain language, and it writes and runs the code for you.

## The focus city

You all analyse the same synthetic city: a rapidly urbanising, heat-vulnerable place in a lower-income, hot-humid setting. It has many neighbourhoods (archetypes) with different characteristics; the city's identity and supporting data are revealed on the day. The suews-agent comes preconfigured with this shared dataset, so every submission is directly comparable.

## The hackathon task

Your task is to use the suews-agent to produce a heat hazard layer for the focus city (for example, dangerous-heat hours by sub-district) and translate it into a socio-economic heat-risk indicator, drawn from a metrics framework being developed by the [UN Office for Disaster Risk Reduction (UNDRR)](https://www.undrr.org/) with established global partners. The specific indicators, calculation approach, and supporting reference material are revealed on the day; everything you need to apply them will be in front of you at the start of the session, with table leads on hand for both SUEWS configuration questions and AI-tool support.

## What we will provide

**Before the day:**

- **suews-agent** (which you install after the pre-session), preconfigured for the challenge so you never assemble inputs by hand.
- **£100 of AI-tool support per attendee** to put toward the agent of your choice (we recommend [**OpenAI Codex**](https://chatgpt.com/codex/) by default; [**Claude Code**](https://claude.com/claude-code) for heavier-tech users); how you receive it is covered at the pre-session, and you do not need to sign up or pay for anything before then.
- **A submission template** for your GitHub repository, so you can run the test submission ahead of time.
- **The [hackathon channel of the SUEWS community Discourse](https://community.suews.io/t/welcome-to-the-suews-community-hackathon-24-june/69)**, monitored daily between now and 24 June, for setup, troubleshooting, progress questions, and team formation.

**On the day:**

- **A template GitHub repository**, released to your team at kickoff, pre-loaded with:
  - **The complete city dataset**: land cover, building form, population, anthropogenic heat, a hot-season forcing, and a hotter-future variant (+2–3 °C / amplified heatwave).
  - **The heat-to-risk bridge function**, documented in a markdown file.
- **Four SUEWS-expert table leads** (model, configuration, science) and an **AI-tool expert** (suews-agent prompting, workflow, unsticking the agent when it behaves unexpectedly).
- **Coffee and refreshments**; WiFi via [**eduroam**](https://eduroam.org/) (any institutional login works) or **UCL Guest** otherwise.

You will not be hacking alone: the Discourse channel before the day, and the table leads and AI-tool expert on it, are there to help you do your best work. Asking for help is never marked against you; bring half-formed questions early, since the answers tend to be better than the answers to polished ones. Contributing back to the channel, with best practice and constructive suggestions, is separate, and it is what the *Professional contribution* criterion rewards.

## Taking part

### Before the day

There is nothing to install before the 9 June pre-session; the setup and test-submission instructions are released there, so you cannot be behind in the meantime.

- **Pack a laptop and charger.** You will be hands-on all afternoon, and it is the one thing we cannot provide.
- **Attend the online pre-session** on Tuesday 9 June, 14:00–15:00 BST (strongly recommended; the only live setup help before the day). We walk you through the format, help you set up your AI tool and the suews-agent, and you run your first end-to-end query. [Join via Microsoft Teams](https://teams.microsoft.com/l/meetup-join/19%3ameeting_ZDdjODMzYWMtZDczYy00NDVmLWExMWYtZjgyYzU0MThmMGFk%40thread.v2/0?context=%7b%22Tid%22%3a%221faf88fe-a998-4c5b-93c9-210a11d9a5c2%22%2c%22Oid%22%3a%2236a5367e-6fdf-403b-90a3-c5c4724a3e85%22%7d). If you cannot make it, the transcript and written guidance (including setup, test-submission, and AI-tool support details) will be posted to the SUEWS Discourse hackathon channel, so you can still get set up.
- **Get familiar with GitHub basics:** creating a repository, committing, and publishing a [Pages site](https://docs.github.com/pages). A GitHub Pages site is simply a public web page built from the files in your repository. A quick skim of the basics is plenty; these are clicks and short text entries, not coding.
- **Install the suews-agent and run a test submission** using the instructions we share at the pre-session, any time before 24 June. It runs from the submission template and is separate from the repository you create on the day; it is just a quick check that your pipeline works, not a test of expertise and not a barrier to taking part.
- **Read up on heat risk (lightly):** heat-related risk to people, places and systems, in broad terms. No set reading is required; we will share some guidance on the day to anchor everyone, but you are also welcome to bring your own framing of the problem, as long as you can justify the choice in your submission.
- **Optional: form a team** of up to three by posting on the SUEWS Discourse hackathon channel. Post one entry per team (or solo) with a **team name** (preferably a project name), the members, and each member's **GitHub handle** (so we can add you to the hackathon team under UMEP-dev). We monitor the thread and post the final team list. Solo is fine; you still submit your own repository, and you sit at a table for support on the day (the tables are for facilitation, not submission units). Solo and team entries are judged on the same criteria and scale. *Team formation closes 23:59 BST on Monday 22 June 2026.*

### On the day

The afternoon runs 14:00–17:00:

- **10-minute kickoff** with the challenge reveal.
- **~2.5 hours hands-on** modelling/prompting at challenge tables, with a facilitator at each.
- **~20-minute wrap-up**, with a short in-room showcase if time allows.

Either way, submissions go up the following week in the public online showcase.

### After the day

A one-week refinement window lets you polish your submission for publication, drawing on richer UNDRR reference material. During this window the organising team will give you scientific and technical feedback to help you strengthen the work; this feedback is independent of the judging, which is based on your repository as it stood at 17:00 on 24 June. The refined version becomes the public-facing artefact: published on the [**SUEWS community Discourse**](https://community.suews.io/) and the **UCL RDR Annual Conference website**, and used in our **social media promotion** of the hackathon outcomes (under your name or anonymously, as you chose at submission). Submissions are kept as part of the SUEWS-Next community record and the UCL RDR 16th annual conference legacy.

## Judging and awards

### What you submit

- **One GitHub repository per individual or team**, created **only after the hackathon starts** on 24 June.
- Create it **under the [UMEP-dev organisation](https://github.com/UMEP-dev)** from the **template hackathon repository** we provide (released on the day). We will add you to the hackathon team there, so **share your GitHub handle in advance** (in your team-formation post); this sets up your access, and you create the repository itself on the day. You do not need to be a GitHub expert: your AI agent can walk you through creating the repository, committing, and publishing the Pages site, and we cover the basics in the pre-session.
- Your **GitHub Pages site must be public**: it is the showcase and is judged, so everything you put on that page will be publicly visible, and by submitting you consent to that. The rest of the repository (files, prompts, and your AI transcripts) can be public or private, your choice, but it must stay accessible to the organisers for judging. When you submit, you also choose whether your public page is shown under your name or anonymously.
- The repository carries the raw material we judge against: files, suews-agent and your AI-tool transcripts, prompts, and the feedback you give the SUEWS team. We cover how to prepare and export these in the pre-session, so plan to save your AI sessions as you go.
- **Submit during the event**: send us the repository link by 17:00 BST on 24 June. **Judging is on the state of your repository at that moment**; changes made after 17:00 do not affect the judged version.

### Judging criteria

Five criteria, each scored out of 20 for a 100-point total, equally weighted:

- **Scientific soundness** of the SUEWS configuration and result. *Evidence: GitHub Pages output and the repository files; the workflow must be reproducible and the SUEWS model correctly cited (see Citing SUEWS).*
- **Policy relevance and honest bridging**: does the result say plainly where the hazard-to-indicator link holds, and where it breaks? *Evidence: GitHub Pages presentation.*
- **Professional contribution** to urban climate science and to the SUEWS community. *Evidence: your posts to the SUEWS Discourse hackathon channel in the run-up to the event (up to 24 June): thoughts, best practice, critical suggestions.*
- **Presentation quality**: does the GitHub Pages site tell a clear story? *Evidence: your public GitHub Pages site.*
- **Innovation and AI collaboration**: creative, effective use of suews-agent and your AI tool (novel prompts, workflow, cross-checking). *Evidence: your exported AI session transcripts.*

### How scoring works

Each criterion is scored by the panel that can see its evidence, and the two panel totals add to 100:

- **Invited external panel** (practitioners and stakeholders from outside the SUEWS team) score the two public-facing criteria from your GitHub Pages site: **Policy relevance & honest bridging** and **Presentation quality** (40 points).
- **Expert panel** (the SUEWS team) score the three technical criteria from your repository, exported AI transcripts, and Discourse contributions: **Scientific soundness**, **Professional contribution**, and **Innovation & AI collaboration** (60 points).
- Your final score is the sum of both panels (out of 100).

**Results**: the panels score over the week following submission; results and prizes are announced about one week after the event (around 1 July 2026).

### Awards

- **Top overall winner**: an additional **£200 AI-tool support** (on top of the baseline £100), awarded to the highest total across the five criteria.
- **Three aspect winners**: an additional **£100 AI-tool support each** (again on top of the baseline £100), one per featured aspect:
  - **Climate / risk science and socioeconomic impact**: strongest combined SUEWS configuration, result, and hazard-to-indicator bridging.
  - **Presentation**: strongest GitHub Pages site narrative.
  - **AI use**: most creative and effective use of suews-agent and your AI tool.

The three aspect themes draw on the five judged criteria; they are not a one-to-one split.

*For anything this brief does not cover, the organisers' decision is final.*

## Useful links

- **SUEWS docs**: https://docs.suews.io/
- **suews-agent (GitHub)**: https://github.com/UMEP-dev/suews-agent
- **SUEWS Discourse — Hackathon channel (start here)**: https://community.suews.io/t/welcome-to-the-suews-community-hackathon-24-june/69
- **OpenAI Codex**: https://chatgpt.com/codex/
- **Claude Code**: https://claude.com/claude-code
- **GitHub Pages docs**: https://docs.github.com/pages

## Citing SUEWS

Your submission must cite the SUEWS model correctly; this is part of **Scientific soundness**, so a missing or improper citation will cost marks. Cite both papers:

- Järvi, L., Grimmond, C.S.B. and Christen, A. (2011). The Surface Urban Energy and Water Balance Scheme (SUEWS): Evaluation in Los Angeles and Vancouver. *Journal of Hydrology*, 411(3–4), 219–237. DOI: [10.1016/j.jhydrol.2011.10.001](https://doi.org/10.1016/j.jhydrol.2011.10.001)
- Ward, H.C., Kotthaus, S., Järvi, L. and Grimmond, C.S.B. (2016). Surface Urban Energy and Water Balance Scheme (SUEWS): Development and evaluation at two UK sites. *Urban Climate*, 18, 1–32. DOI: [10.1016/j.uclim.2016.05.001](https://doi.org/10.1016/j.uclim.2016.05.001)

For the specific software version you run, follow the up-to-date [**How to cite SUEWS**](https://docs.suews.io/stable/#how-to-cite-suews) guidance in the documentation; it points to the current archived release, so you cite the version you actually used rather than an outdated one.

## Acknowledgements

This hackathon is part of **SUEWS-Next**, and is supported by the ERC Synergy Grant **urbisphere** (855505).
