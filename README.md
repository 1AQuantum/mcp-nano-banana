# MCP Nano Banana - Image Generation Server

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

Nano Banana reads `~/.nano_banana_config.json`. Create it with your Gemini API key:

```bash
cat > ~/.nano_banana_config.json <<'EOF'
{
  "api_key": "YOUR_GEMINI_KEY",
  "output_dir": "~/mcp_generated_images"
}
EOF
```

### 3. (Optional) override per session

- `GENAI_IMAGE_MODEL` env var to pick a different Gemini model.
- `NANO_BANANA_OUTPUT_DIR` env var to change output folder.

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
      "args": ["python3", "-m", "src"],
      "cwd": "/ABS/PATH/TO/mcp-nano-banana",
      "env": {
        "PYTHONPATH": "/ABS/PATH/TO/mcp-nano-banana",
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

or equivalently the `/usr/bin/env python3 -m src` variant with `cwd` as above.

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

## Resources

- image://gallery/recent
- config://api/status

## MCP Overview and Security

This server implements the Model Context Protocol (MCP) to expose tools, resources, and prompts over a standardized JSON-RPC transport (stdio). MCP allows hosts like IDEs or assistants to connect to external capabilities in a consistent way. See the official docs for details: [Claude MCP docs](https://docs.claude.com/en/docs/mcp), [MCP Specification (2025‑06‑18)](https://modelcontextprotocol.io/specification/2025-06-18).

Key considerations adapted from the spec:

- Users should explicitly consent to tool usage and understand what each tool does.
- Be mindful of data privacy when exposing resources; do not share sensitive paths or data without consent.
- Provide clear configuration (API keys, output directory) and visibility into side effects (where files are written).

Transport: stdio (recommended for portability). The console script `mcp-nano-banana` launches the server using stdio by default.

## Configuration Reference

Environment variables:

- GEMINI_API_KEY: API key for Google GenAI (required)
- GENAI_IMAGE_MODEL: model id (default: gemini-2.5-flash-image-preview; you may use fully qualified name e.g. models/gemini-2.5-flash-image-preview)
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

### Resource access

```text
@image://gallery/recent
@config://api/status
```

## Troubleshooting

- Tool response too large: If your client enforces strict size limits, keep base64 disabled (default). You can always fetch images from disk via the returned path or the recent gallery resource.

- Command not found: ensure your Python environment's bin is on PATH, then re‑install: `pip install -e .`
- No images saved: set a preview model `export GENAI_IMAGE_MODEL="models/gemini-2.5-flash-image-preview"` or check access.
- Permission errors writing files: set `NANO_BANANA_OUTPUT_DIR` to a writable location.

## License

MIT
