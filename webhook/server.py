"""
PR Pilot — GitHub Webhook Receiver
Receives GitHub PR events and forwards them to the Switch server,
which bridges them into the Discord #pr-reviews channel.
"""

import hashlib
import hmac
import json
import logging
import os

import httpx
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pr-pilot-webhook")

app = FastAPI(title="PR Pilot Webhook Receiver", version="1.0.0")

# ---------------------------------------------------------------------------
# Config (set via environment variables in docker-compose.yml)
# ---------------------------------------------------------------------------
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
SWITCH_SERVER_URL = os.getenv("SWITCH_SERVER_URL", "http://switch:8080")
SWITCH_ROOM_NAME = os.getenv("SWITCH_ROOM_NAME", "pr-reviews")
SWITCH_API_KEY = os.getenv("SWITCH_API_KEY", "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def verify_github_signature(payload: bytes, sig_header: str | None) -> bool:
    """Verify the X-Hub-Signature-256 from GitHub."""
    if not GITHUB_WEBHOOK_SECRET:
        log.warning("No GITHUB_WEBHOOK_SECRET set — skipping signature check")
        return True
    if not sig_header or not sig_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, sig_header)


def build_pr_message(event: str, payload: dict) -> str:
    """Turn a GitHub PR payload into a human-readable Switch room message."""
    pr = payload.get("pull_request", {})
    repo = payload.get("repository", {})
    sender = payload.get("sender", {})

    title = pr.get("title", "Untitled PR")
    number = pr.get("number", "?")
    url = pr.get("html_url", "")
    author = pr.get("user", {}).get("login", sender.get("login", "unknown"))
    base = pr.get("base", {}).get("ref", "main")
    head = pr.get("head", {}).get("ref", "feature")
    body = (pr.get("body") or "*(no description)*").strip()[:400]
    additions = pr.get("additions", 0)
    deletions = pr.get("deletions", 0)
    changed_files = pr.get("changed_files", 0)
    draft = pr.get("draft", False)
    repo_name = repo.get("full_name", "unknown/repo")

    draft_tag = " **[DRAFT]**" if draft else ""
    action_map = {
        "opened": "🟢 **New PR opened**",
        "synchronize": "🔄 **PR updated** (new commits pushed)",
        "reopened": "🔁 **PR reopened**",
        "ready_for_review": "✅ **PR marked ready for review**",
        "closed": "🔴 **PR closed**" + (" (merged)" if pr.get("merged") else " (without merging)"),
    }
    action_label = action_map.get(event, f"📌 PR event: `{event}`")

    msg = (
        f"{action_label}{draft_tag}\n\n"
        f"**[#{number}: {title}]({url})**\n"
        f"`{repo_name}` · `{head}` → `{base}`\n"
        f"👤 Author: @{author}\n"
        f"📊 `+{additions} / -{deletions}` across {changed_files} file(s)\n\n"
        f"**Description:**\n{body}\n\n"
        f"---\n"
        f"@pr-reviewer please review this PR."
    )
    return msg


async def post_to_switch(message: str) -> bool:
    """Send a message to the Switch room."""
    url = f"{SWITCH_SERVER_URL}/api/rooms/{SWITCH_ROOM_NAME}/messages"
    headers = {"Content-Type": "application/json"}
    if SWITCH_API_KEY:
        headers["Authorization"] = f"Bearer {SWITCH_API_KEY}"

    payload = {"content": message, "sender": "github-webhook"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            log.info("Message posted to Switch room '%s' (HTTP %s)", SWITCH_ROOM_NAME, resp.status_code)
            return True
    except httpx.HTTPError as exc:
        log.error("Failed to post to Switch: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "room": SWITCH_ROOM_NAME}


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    body = await request.body()

    # Verify signature
    if not verify_github_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = x_github_event or "unknown"
    log.info("Received GitHub event: %s", event)

    # Only handle PR events
    if event != "pull_request":
        return JSONResponse({"ignored": True, "event": event})

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    action = payload.get("action", "")

    # Only process relevant PR actions
    relevant_actions = {"opened", "synchronize", "reopened", "ready_for_review", "closed"}
    if action not in relevant_actions:
        log.info("Skipping action: %s", action)
        return JSONResponse({"ignored": True, "action": action})

    # Skip draft PRs unless they're transitioning to ready
    pr = payload.get("pull_request", {})
    if pr.get("draft") and action not in {"ready_for_review"}:
        log.info("Skipping draft PR (action=%s)", action)
        return JSONResponse({"ignored": True, "reason": "draft"})

    message = build_pr_message(action, payload)
    success = await post_to_switch(message)

    if not success:
        raise HTTPException(status_code=502, detail="Failed to forward to Switch")

    return JSONResponse({"ok": True, "event": event, "action": action})

