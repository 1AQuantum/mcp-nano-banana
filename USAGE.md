# MCP Nano Banana - Usage Guide

## Setup (One Time)

```bash
git clone https://github.com/YOU/mcp-nano-banana.git
cd mcp-nano-banana
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .

cat > ~/.nano_banana_config.json <<'EOF'
{
  "api_key": "YOUR_GEMINI_KEY",
  "output_dir": "~/mcp_generated_images"
}
EOF
```

## Starting the Server

```bash
mcp-nano-banana
```

## Output Directory

By default, images are written to a directory one level above this repo: `../mcp_generated_images` (or your home folder fallback). Override the path via environment variable or config file:

```bash
export NANO_BANANA_OUTPUT_DIR="/absolute/path/you/prefer"
# Or set in ~/.nano_banana_config.json
# { "api_key": "...", "output_dir": "/absolute/path" }
```

## Model Selection

The server defaults to `gemini-2.5-flash-image-preview`. To override:

```bash
export GENAI_IMAGE_MODEL="models/gemini-2.5-flash-image-preview"
# or another available image-capable model from list_models
```

## Claude Code Integration

Portable `.mcp.json` example:

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

You can replace `command` with `/ABS/PATH/TO/.venv/bin/mcp-nano-banana` if the console script is available.

## Available Tools

### Generate Image

```python
@nano-banana.generate_image("A sunset over mountains", style="realistic")
```

### Edit Image

```python
@nano-banana.edit_image("/path/to/image.png", "Add a rainbow")
```

### Blend Images

````python
@nano-banana.blend_images(["/img1.png", "/img2.png"], "Merge seamlessly")

### Programmatic Tool Call Shapes (JSON)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "A futuristic cityscape at sunset",
    "style": "realistic",
    "aspect_ratio": "16:9",
    "quality": "high"
  }
}
````

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/to/image.png",
    "instructions": "Increase contrast and add warm lighting",
    "preserve_style": true
  }
}
```

```json
{
  "name": "blend_images",
  "arguments": {
    "image_paths": ["/path/one.png", "/path/two.png"],
    "instructions": "Combine naturally with consistent shadows",
    "blend_mode": "seamless"
  }
}
```

```

## Troubleshooting

- Ensure the console script is on PATH: `mcp-nano-banana --help`
- Verify credentials: `echo $GEMINI_API_KEY`
- If no images are saved, set a preview model: `export GENAI_IMAGE_MODEL="models/gemini-2.5-flash-image-preview"`
- Check write permissions or override output dir: `export NANO_BANANA_OUTPUT_DIR=...`

## References

- Claude MCP docs: https://docs.claude.com/en/docs/mcp
- MCP specification (2025‑06‑18): https://modelcontextprotocol.io/specification/2025-06-18
```
