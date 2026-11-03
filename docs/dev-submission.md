_This is a submission for the [MLH x DEV Writing Challenge](https://dev.to/mlh-hackathon)_

<!-- Make sure you're signed in to DEV with the MLH account linked to your hackathon registration! -->

## What I Built

Every developer knows the dread of the **Pull Request bottleneck**: you push a feature, open a PR, and... silence. Days pass. Context is lost. Reviewers get dragged away by meetings, while authors juggle stale branches. Meanwhile, your team chat (Discord/Slack) is buzzing with activity, completely disconnected from what’s happening on GitHub.

To bridge this divide, I built **PR Pilot**: an automated, dual-agent AI code review system that lives directly inside your team's Discord `#pr-reviews` channel.

Instead of a noisy bot that just dumps notifications, PR Pilot acts like two junior-to-senior pair programmers sitting in the room:

1. **`@pr-reviewer` (The Strategic Reviewer)**:
   - Ingests the GitHub diff upon PR creation.
   - Summarizes the "why" and "what" in 2–3 concise sentences.
   - Assesses a risk tier (**LOW / MEDIUM / HIGH**) targeting security, auth, migrations, and breaking changes.
   - Prompts the author with 2–3 pointed questions about edge cases and maintainability.
   - Listens for team instructions: typing `approve` or `request changes` will execute the actual GitHub API review directly from Discord!

2. **`@pr-standards` (The Automated Gatekeeper)**:
   - Triggered automatically by `@pr-reviewer`.
   - Runs an objective 6-point checklist:
     - ✅ Conventional Commit title (`feat:`, `fix:`, etc.)
     - ✅ Non-empty description explaining the intent
     - ⚠️ Test coverage check (flags if source changed without tests)
     - ✅ Unlinked `TODO` / `FIXME` detection (must cite issue numbers)
     - ✅ Documentation updates for public APIs / config
     - ✅ PR diff size check (< 400 lines)

### How It Works

```text
┌──────────────┐   GitHub Webhook   ┌─────────────────┐   SSE / Room Event   ┌──────────────────┐
│   GitHub     │ ─────────────────► │    PR Pilot     │ ───────────────────► │  Switch Server   │
│  (PR event)  │                    │ Webhook Receiver│                      │ (Local / Docker) │
└──────────────┘                    └─────────────────┘                      └────────┬─────────┘
                                                                                      │ Discord Bridge
                                                                             ┌────────▼─────────┐
                                                                             │     Discord      │
                                                                             │   #pr-reviews    │
                                                                             │                  │
                                                                             │  @pr-reviewer    │
                                                                             │  @pr-standards   │
                                                                             │  👤 Team Humans  │
                                                                             └──────────────────┘
                                                                                      │
                                                                             GitHub API Execution
                                                                             (Approve / Block)
```

1. A developer opens a PR on GitHub.
2. A GitHub webhook hits the PR Pilot FastAPI service.
3. The event routes to the Discord room through **Switch**.
4. `@pr-reviewer` reads the diff, writes a review, and tags `@pr-standards`.
5. `@pr-standards` posts its pass/warn/fail scorecard.
6. Teammates can ask questions in the thread, discuss with the AI, and type `approve` to officially approve the PR on GitHub without ever leaving Discord.

---

## Demo

- 📦 **GitHub Repository**: [github.com/jaysid97/pr-pilot](https://github.com/jaysid97/pr-pilot)
- 📹 **Demo Walkthrough Video**: _[Insert your demo video link or walkthrough here]_

### Live Walkthrough in Discord

Here is what the interaction looks like when a developer opens a pull request:

> **PR Opened:** `feat: add JWT authentication logic` (#42)
> 
> **`@pr-reviewer`**:
> > 🔍 **Summary**: Implements JWT verification middleware and token renewal endpoints.
> > ⚠️ **Risk Level**: **HIGH** — modifies core authentication logic and security headers.
> > ❓ **Questions for @author**:
> > 1. Have we accounted for token replay prevention during silent refresh?
> > 2. Is the secret rotation strategy compatible with multi-instance clustering?
> > 
> > `@pr-standards please run your checklist on this PR: https://github.com/demo/repo/pull/42`
>
> **`@pr-standards`**:
> > 📋 **Standards Check for PR #42**:
> > - ✅ Conventional commit title
> > - ✅ Description present
> > - ⚠️ No test files updated (`tests/test_auth.py` missing)
> > - ✅ No unlinked TODOs
> > - ✅ PR size: 142 lines (healthy)
> > 
> > **Overall**: PASS with 1 warning.
>
> **Developer**: *"Does this handle token refresh edge cases?"*  
> **`@pr-reviewer`**: *"Yes, in `auth_service.py:84`, expired tokens return `401 TOKEN_EXPIRED`, but network retry backoff should still be handled by the client."*  
> 
> **Developer**: *"approve"*  
> **`@pr-reviewer`**: *"✅ Approved on GitHub on behalf of @developer."*

---

## Partner Technologies

### 1. Switch
[Switch](https://github.com/sandbox-quantum/switch) served as the foundational infrastructure for PR Pilot. Rather than building custom Discord bot handlers, websocket daemons, and session trackers from scratch:
- **Declarative Room Templates**: With `pr-pilot.template.yaml`, the entire multi-agent environment (agent identities, instruction prompts, communication policies, and channel bindings) is spin-up ready in a single click via Switch Console.
- **Agent Communication Protocol**: `@pr-reviewer` and `@pr-standards` consume room events via Server-Sent Events (SSE) and post through HTTP back to Switch.
- **Discord Bridge**: Switch translates bidirectional messages between Discord's API and the agents seamlessly, allowing agents to react to human input in natural conversational threads.

### 2. Antigravity & Agent Runtimes
I leveraged **Antigravity** to formulate the agent personalities, system prompts, and strict guardrails. The dual-agent separation prevents prompt bloat: `@pr-reviewer` specializes in qualitative reasoning, code comprehension, and API execution, while `@pr-standards` operates as a deterministic, objective checklist engine.

### 3. FastAPI & Docker
The webhook receiver was built with FastAPI, containerized using Docker Compose, and securely exposed via tunnels to handle GitHub payload verification (`HMAC-SHA256`) and dispatch events to the Switch network with sub-second latency.

---

## Hackathon Experience

Building PR Pilot during the hackathon was an absolute blast. 

Hackathons are famous for high adrenaline and tight timelines, but the biggest revelation for me was how natural multi-agent architectures feel when anchored inside a team chat application. Instead of isolating AI into web dashboards or CLI tools that people forget to check, putting them where developers already hang out (Discord) transforms AI from a passive utility into an active pair-programming teammate.

The most memorable moment was testing the full loop for the first time: pushing a mock breaking commit, watching Discord light up 3 seconds later with a targeted warning from `@pr-reviewer`, discussing it in the channel, and seeing the PR status tick green on GitHub just by typing "approve" in chat.

### What's Next for PR Pilot
- Support for GitLab and Bitbucket webhooks.
- Inline PR code comment suggestions directly generated from Discord threads.
- Custom organization rulebooks that let teams define their own `@pr-standards` checklists via simple YAML files.

---

_Check out the repository on [GitHub](https://github.com/jaysid97/pr-pilot) and feel free to try running the Switch template in your own server! Let me know in the comments how your team manages pull request reviews._

