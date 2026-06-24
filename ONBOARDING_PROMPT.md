# Onboarding prompt

Get set up for the SUEWS Community Hackathon in one paste.

**Before you start:** do the one-time AI-agent setup first (the Codex app, GitHub, and the suews-agent) — see the setup guide. Your practice repo goes under your own GitHub account, so you need nothing from us first; the UMEP-dev team is only for the repo you create on the day.

In the Codex app, start a new task (or in Claude Code, your session), and paste the prompt below.

---

You're helping me get set up for the SUEWS Community Hackathon. Do each step, check it worked before moving on, and tell me plainly if you need my input:

1. Create a public GitHub repo under my own account called `suews-hackathon-practice`, from the template `UMEP-dev/suews-hackathon-template` (`gh repo create <my-username>/suews-hackathon-practice --template UMEP-dev/suews-hackathon-template --public --clone`), and open it.
2. Read `TASK_BRIEF.md` in that repo so you understand the task.
3. Using the suews-agent, run one small example SUEWS simulation to confirm the tool works end to end.
4. Publish the `docs/` folder as a public GitHub Pages site (main branch, `/docs`) and give me the URL.
5. Save a transcript of this session into `transcripts/`, then commit and push.

Finish by printing: my repo URL, my Pages URL, and a one-line status per step.

---

**If the agent pauses to ask:** repository visibility = public; GitHub Pages source = main branch, `/docs`. **You are done when** your Pages URL renders (not a 404). If the agent gets stuck, post in the hackathon channel and a table lead will help.
