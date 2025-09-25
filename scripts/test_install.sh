#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/.test-venv"

rm -rf "${VENV_DIR}"
python3 -m venv "${VENV_DIR}"
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip
pip install "${PROJECT_ROOT}"

which mcp-nano-banana
mcp-nano-banana --help || true

python - <<'PY'
import asyncio
from mcp_nano_banana.nano_banana_server import generate_image

async def main():
    result = await generate_image(
        prompt="Nano Banana smoke test portrait, cinematic lighting",
        style="realistic",
        aspect_ratio="1:1",
        quality="standard",
    )
    print("Smoke test:", result.get("success"), result.get("message"))

asyncio.run(main())
PY

deactivate
rm -rf "${VENV_DIR}"
