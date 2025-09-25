# MCP Nano Banana - Image Generation Server

## What is the Model Context Protocol?

Nano Banana exposes Gemini 2.5 Flash Image capabilities through the Model Context Protocol (MCP)—an open-source standard that connects AI applications to external tools, data, or workflows in a consistent way. MCP acts like a USB-C port for AI assistants: hosts such as Claude Code or Cursor can attach this server to generate, edit, and blend images without bespoke integrations. Each instance runs the Nano Banana presets by default for image-focused workflows. For a deeper understanding of MCP’s architecture and ecosystem benefits, see: [Model Context Protocol – Getting Started](https://modelcontextprotocol.io/docs/getting-started/intro).

## Quick Start

### 1. Install (recommended: isolated virtual environment)

```bash
git clone https://github.com/YOU/mcp-nano-banana.git
cd mcp-nano-banana
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .
```

### 2. Configure credentials & output path

Nano Banana uses a simple configuration hierarchy:

- **Environment variable (fastest):**
  ```bash
  export GEMINI_API_KEY="YOUR_GEMINI_KEY"
  export NANO_BANANA_OUTPUT_DIR="/absolute/path/for/images"  # optional
  ```
- **Config file (portable default):** create `~/.nano_banana_config.json` so the server works across shells:
  ```bash
  cat > ~/.nano_banana_config.json <<'EOF'
  {
    "api_key": "YOUR_GEMINI_KEY",
    "output_dir": "~/mcp_generated_images"
  }
  EOF
  ```

### 3. (Optional) override per session

- `GENAI_IMAGE_MODEL` env var to pick a different Gemini image model (defaults to `models/gemini-2.5-flash-image-preview`).
- `NANO_BANANA_OUTPUT_DIR` env var to change output folder (overrides config file).

### 4. Smoke test

```bash
mcp-nano-banana  # should start and wait on stdio; Ctrl+C to exit
```

## Claude Code Configuration

### Cursor / Claude Desktop (project `.mcp.json`)

```json
{
  "mcpServers": {
    "nano-banana": {
      "type": "stdio",
      "command": "/usr/bin/env",
      "args": ["python3", "-m", "mcp_nano_banana"],
      "cwd": "/ABS/PATH/TO/mcp-nano-banana",
      "env": {
        "NANO_BANANA_OUTPUT_DIR": "/ABS/PATH/TO/mcp_generated_images"
      }
    }
  }
}
```

You can swap `command` for `mcp-nano-banana` if the console script is on PATH (e.g. from the venv).

### VS Code MCP extensions

Point the MCP entry at whichever interpreter/shell you use. Example:

```json
{
  "type": "stdio",
  "command": "/ABS/PATH/TO/.venv/bin/mcp-nano-banana",
  "args": []
}
```

or equivalently the `/usr/bin/env python3 -m mcp_nano_banana` variant with `cwd` as above.

## Tools (API)

### generate_image

- Args: prompt (required), style?, aspect_ratio?, quality?
- Returns: { success, image_path, message, metadata } (base64 omitted by default)

Example:

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "A banana wearing a superhero costume, studio lighting, 1:1",
    "style": "cartoon",
    "aspect_ratio": "1:1",
    "quality": "high"
  }
}
```

### edit_image

- Args: image_path (required), instructions (required), preserve_style?
- Returns: { success, image_path, message, metadata }

Example:

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/to/input.png",
    "instructions": "Increase contrast and add warm studio lighting",
    "preserve_style": true
  }
}
```

### blend_images

- Args: image_paths (2–3 recommended), instructions, blend_mode?
- Returns: { success, image_path, message, metadata }

Example:

```json
{
  "name": "blend_images",
  "arguments": {
    "image_paths": ["/img1.png", "/img2.png"],
    "instructions": "Merge seamlessly with natural lighting",
    "blend_mode": "natural"
  }
}
```

### generate_text

- Args: prompt (required), system_instruction?, temperature?, max_output_tokens?
- Returns: { success, text, message, metadata }

Example:

```json
{
  "name": "generate_text",
  "arguments": {
    "prompt": "Draft three taglines for a space-themed banana brand.",
    "system_instruction": "Keep each tagline under 12 words.",
    "temperature": 0.8
  }
}
```

## Resources

- image://gallery/recent
- config://api/status (now includes active image and text models)

## MCP Overview and Security

This server implements the Model Context Protocol (MCP) to expose tools, resources, and prompts over a standardized JSON-RPC transport (stdio). MCP allows hosts like IDEs or assistants to connect to external capabilities in a consistent way. See the official docs for details: [Claude MCP docs](https://docs.claude.com/en/docs/mcp), [MCP Specification (2025‑06‑18)](https://modelcontextprotocol.io/specification/2025-06-18).

Key considerations adapted from the spec:

- Users should explicitly consent to tool usage and understand what each tool does.
- Be mindful of data privacy when exposing resources; do not share sensitive paths or data without consent.
- Provide clear configuration (API keys, output directory) and visibility into side effects (where files are written).

Transport: stdio (recommended for portability). The console script `mcp-nano-banana` launches the server using stdio by default.

## Configuration Reference

Environment variables:

- GEMINI_API_KEY: API key for Google GenAI (required if config file absent)
- GENAI_IMAGE_MODEL: image model id (default: `models/gemini-2.5-flash-image-preview`; other Gemini IDs will work as long as they support image generation)
- GENAI_TEXT_MODEL: text model id (default: `models/gemini-2.5-flash`; the server automatically falls back to other Gemini 2.x IDs if the first choice is unavailable)
- NANO_BANANA_OUTPUT_DIR: absolute output directory (default: ../mcp_generated_images or ~/mcp_generated_images fallback)

Optional file: `~/.nano_banana_config.json`

```json
{ "api_key": "...", "output_dir": "/absolute/path" }
```

## Example Workflows

### Generate an image (tool call shape)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "A banana wearing a superhero costume",
    "style": "realistic",
    "aspect_ratio": "1:1",
    "quality": "high"
  }
}
```

### Edit an image (tool call shape)

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/to/input.png",
    "instructions": "Add a rainbow over the scene",
    "preserve_style": true
  }
}
```

### Blend images (tool call shape)

```json
{
  "name": "blend_images",
  "arguments": {
    "image_paths": ["/path/one.png", "/path/two.png"],
    "instructions": "Merge seamlessly with consistent lighting",
    "blend_mode": "natural"
  }
}
```

### Generate text (tool call shape)

```json
{
  "name": "generate_text",
  "arguments": {
    "prompt": "Summarise the mission of Nano Banana in two sentences",
    "system_instruction": "Adopt a friendly marketing tone",
    "max_output_tokens": 200
  }
}
```

### Resource access

```text
@image://gallery/recent
@config://api/status
```

## Troubleshooting

- Tool response too large: If your client enforces strict size limits, keep base64 disabled (default). You can always fetch images from disk via the returned path or the recent gallery resource.

- Command not found: ensure your Python environment's bin is on PATH, then re‑install: `pip install -e .`
- No images saved: set an explicit model `export GENAI_IMAGE_MODEL="models/gemini-2.5-flash-image-preview"` or check access.
- Permission errors writing files: set `NANO_BANANA_OUTPUT_DIR` to a writable location.
- Text output seems short: increase `max_output_tokens` or set `GENAI_TEXT_MODEL` to another accessible ID.

## License

MIT
