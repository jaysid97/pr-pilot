#!/usr/bin/env bash
# PR Pilot — setup helper
# Run: bash scripts/setup.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[PR Pilot]${NC} $*"; }
warn()  { echo -e "${YELLOW}[PR Pilot]${NC} $*"; }
error() { echo -e "${RED}[PR Pilot]${NC} $*" >&2; }

echo ""
echo "  ✈️  PR Pilot — Setup"
echo "  ─────────────────────────────────────"
echo ""

# 1. Check Docker
if ! command -v docker &>/dev/null; then
  error "Docker not found. Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
  exit 1
fi
info "Docker found: $(docker --version)"

# 2. Check .env
if [[ ! -f .env ]]; then
  warn ".env not found — copying from .env.example"
  cp .env.example .env
  warn "Please edit .env with your secrets, then re-run this script."
  exit 0
fi
info ".env found"

# 3. Check required vars
source .env
missing=()
[[ -z "${GITHUB_WEBHOOK_SECRET:-}" ]] && missing+=("GITHUB_WEBHOOK_SECRET")
[[ -z "${GITHUB_TOKEN:-}" ]] && missing+=("GITHUB_TOKEN")

if [[ ${#missing[@]} -gt 0 ]]; then
  error "Missing required .env variables: ${missing[*]}"
  error "Edit .env and fill them in."
  exit 1
fi
info "Environment variables OK"

# 4. Build and start containers
info "Building and starting webhook receiver..."
docker compose up -d --build

# 5. Health check
sleep 3
if curl -sf http://localhost:9000/health > /dev/null; then
  info "Webhook receiver is healthy at http://localhost:9000"
else
  error "Webhook receiver failed to start. Check logs: docker compose logs webhook"
  exit 1
fi

echo ""
info "✅  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Load switch/pr-pilot.template.yaml in Switch Console"
echo "  2. Run: ngrok http 9000"
echo "  3. Set GitHub webhook URL to: https://<ngrok-url>/webhook/github"
echo "  4. Open a PR and watch the magic in #pr-reviews 🎉"
echo ""

