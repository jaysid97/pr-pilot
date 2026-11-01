#!/usr/bin/env bash
# Send a test GitHub PR payload to the local webhook receiver.
# Useful for testing without needing to open a real PR.

set -euo pipefail

WEBHOOK_URL="${1:-http://localhost:9000/webhook/github}"
SECRET="${GITHUB_WEBHOOK_SECRET:-test-secret}"

PAYLOAD='{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "number": 42,
    "title": "feat: add user authentication with JWT",
    "html_url": "https://github.com/demo-org/demo-repo/pull/42",
    "user": { "login": "alice" },
    "body": "This PR adds JWT-based authentication to the API. Tokens expire after 24h. Refresh tokens are stored in httpOnly cookies.\n\nFixes #38.",
    "base": { "ref": "main" },
    "head": { "ref": "feat/jwt-auth" },
    "additions": 312,
    "deletions": 47,
    "changed_files": 8,
    "draft": false,
    "merged": false
  },
  "repository": { "full_name": "demo-org/demo-repo" },
  "sender": { "login": "alice" }
}'

# Compute HMAC-SHA256 signature
SIG="sha256=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')"

echo "Sending test payload to: $WEBHOOK_URL"
echo "Signature: $SIG"
echo ""

curl -sf -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: $SIG" \
  -d "$PAYLOAD"

echo ""
echo "✅ Payload sent! Check #pr-reviews in Discord."

