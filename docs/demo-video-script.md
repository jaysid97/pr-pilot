# PR Pilot — Demo Video Script
## Runtime: ~2 minutes

---

### Scene 1: The Problem (0:00–0:15)
**[Screen: GitHub — a list of PRs, several with "3 days ago", "5 days ago" labels]**

> *"Pull requests pile up. Reviewers are busy. Good code waits days for feedback. 
> PR Pilot fixes that — by putting an AI reviewer directly into your Discord."*

---

### Scene 2: The Setup (0:15–0:30)
**[Screen: Switch Console — loading pr-pilot.template.yaml]**

> *"With Switch, I load one template file..."*

**[Screen: Discord — #pr-reviews channel appears, @pr-reviewer and @pr-standards join]**

> *"...and two AI agents appear in #pr-reviews as teammates."*

---

### Scene 3: Opening a PR (0:30–1:00)
**[Screen: Split — GitHub on left, Discord on right]**

> *"I'll open a real PR right now. Watch what happens in Discord."*

**[Action: Create a PR on GitHub titled "feat: add JWT authentication"]**

**[Discord: within 3-5 seconds, @pr-reviewer posts the review message]**

> *"The GitHub webhook fires, Switch routes it to the room, and @pr-reviewer 
> reads the diff and posts a structured review — in under 5 seconds."*

**[Highlight: summary, risk level HIGH, 3 pointed questions to the author]**

---

### Scene 4: Standards Check (1:00–1:15)
**[Discord: @pr-standards posts the checklist]**

> *"@pr-standards automatically checks: conventional commit title, description, 
> tests, no unlinked TODOs, docs updated. One warning — no test file changes detected."*

---

### Scene 5: Human Interaction (1:15–1:35)
**[Screen: Discord]**

**[Type in Discord: "Does this handle token refresh edge cases?"]**

**[@pr-reviewer responds with a detailed answer based on the diff]**

> *"You can ask the agent anything about the code. It knows the diff."*

**[Type: "approve"]**

**[Screen: Discord shows "✅ Approved on GitHub on behalf of @demo-user"]**
**[Screen: GitHub shows the PR is now approved]**

> *"Type 'approve' — and it's done on GitHub. The whole loop, without leaving Discord."*

---

### Scene 6: Wrap-up (1:35–2:00)
**[Screen: Architecture diagram from README]**

> *"PR Pilot is built on Switch — the open source infrastructure that lets AI agents 
> join your team chat as real teammates. Remove Switch, and the agents are gone."*

> *"GitHub webhooks → Switch server → Discord — with Antigravity powering the agents."*

> *"One template file. Five-minute setup. Your team ships faster."*

**[Screen: GitHub repo URL]**

> *"Check it out: github.com/YOUR_USERNAME/pr-pilot"*

---

## Recording Tips
- Use OBS with a vertical split scene (GitHub left, Discord right)
- Record at 1080p, export at 30fps
- Add captions for the "you type → agent responds" moments
- Keep background music low (lofi works well)
- Total runtime: aim for exactly 2:00

