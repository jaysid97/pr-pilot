# PR Pilot — Detailed Setup Guide

## Overview

This guide walks you through setting up PR Pilot end-to-end on your machine.
Estimated time: **15–20 minutes**.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Switch Console | Latest | [Download here](https://github.com/sandbox-quantum/switch/releases) |
| Docker Desktop | 4.x+ | [Download here](https://www.docker.com/products/docker-desktop) |
| ngrok (or Cloudflare Tunnel) | Any | For public webhook URL |
| GitHub account | — | With a repo to test on |
| Antigravity account | — | [Sign up here](https://antigravity.dev) |
| Discord server | — | Where you have admin rights |

---

## Step 1: Clone the repo

```bash
git clone https://github.com/jaysid97/pr-pilot.git
cd pr-pilot
```

---

## Step 2: Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
GITHUB_WEBHOOK_SECRET=some-random-secret-string   # You choose this
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx             # GitHub PAT, repo scope
SWITCH_SERVER_URL=http://host.docker.internal:8080 # Default Switch port
SWITCH_ROOM_NAME=pr-reviews
```

**Creating a GitHub Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Repository permissions: **Pull requests** → Read and write
3. Copy the token into `.env`

---

## Step 3: Set up Switch Console

1. Download and install Switch Console
2. Open it and sign in with your Antigravity account
3. Connect your Discord bridge:
   - Click **Bridges → Add Bridge → Discord**
   - Follow the OAuth flow to authorise Switch in your Discord server
4. Load the PR Pilot template:
   - Click **Rooms → New Room from Template**
   - Select the file: `switch/pr-pilot.template.yaml`
   - Switch creates `#pr-reviews` in Discord and adds both agents

---

## Step 4: Start the webhook receiver

```bash
bash scripts/setup.sh
```

Or manually:
```bash
docker compose up -d --build
docker compose logs -f webhook
```

You should see:
```
INFO: PR Pilot Webhook Receiver started on 0.0.0.0:9000
```

Test it:
```bash
curl http://localhost:9000/health
# {"status":"ok","room":"pr-reviews"}
```

---

## Step 5: Get a public URL

### Option A: ngrok (easiest)

```bash
ngrok http 9000
```

Copy the `https://` URL (e.g. `https://abc123.ngrok.io`).

### Option B: Cloudflare Tunnel (more stable)

1. Create a tunnel in the [Cloudflare dashboard](https://one.dash.cloudflare.com)
2. Copy your tunnel token into `.env` as `CLOUDFLARE_TUNNEL_TOKEN`
3. Uncomment the `cloudflared` service in `docker-compose.yml`
4. `docker compose up -d cloudflared`

---

## Step 6: Configure GitHub webhook

In your GitHub repository:
1. **Settings → Webhooks → Add webhook**
2. **Payload URL**: `https://YOUR_PUBLIC_URL/webhook/github`
3. **Content type**: `application/json`
4. **Secret**: same value as `GITHUB_WEBHOOK_SECRET` in `.env`
5. **Which events?**: Select **Let me select individual events** → check **Pull requests**
6. Click **Add webhook** — GitHub will send a ping event (no Discord message expected)

---

## Step 7: Test it!

```bash
# Send a fake PR payload (no real PR needed)
bash scripts/test-webhook.sh

# OR open a real PR on your GitHub repo
```

Watch `#pr-reviews` in Discord — within a few seconds you'll see `@pr-reviewer` post.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No message in Discord | Check `docker compose logs webhook` for errors |
| "Invalid signature" error | Make sure `GITHUB_WEBHOOK_SECRET` matches in `.env` and GitHub settings |
| Agents not responding | Check Switch Console — agents may need to be restarted |
| ngrok URL expired | Free ngrok URLs change on restart; update the GitHub webhook URL |
| Switch server not reachable | Check `SWITCH_SERVER_URL` in `.env`; use `host.docker.internal` on Mac/Windows |

