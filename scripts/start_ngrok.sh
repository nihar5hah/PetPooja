#!/usr/bin/env bash

set -euo pipefail

PORT="${1:-8000}"

exec ngrok http "$PORT"