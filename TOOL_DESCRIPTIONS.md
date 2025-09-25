# Nano Banana MCP – Tool & Best Practices Summary

_Last updated: $(date)_

## Tools

### `generate_image`

- **Purpose**: text → image with Gemini 2.5 Flash Image.
- **Arguments**:
  - `prompt` (required) – richly describe subject, environment, lighting, style.
  - `style`, `aspect_ratio`, `quality` (optional) – see tool docstring.
- **Usage Tips**:
  - Write narrative descriptions (not single words or comma-separated lists).
  - Incorporate photographic vocabulary (shot type, lens, depth-of-field, lighting style).
  - Iterate using follow-up prompts; responses return `metadata` for prompt, style, aspect ratio.
  - Consult `docs://prompting/guide` and `docs://prompting/cheatsheet` for curated fragments.

### `edit_image`

- **Purpose**: semantic edits/inpainting using natural language.
- **Arguments**:
  - `image_path` absolute file path.
  - `instructions` describing the modification.
  - `preserve_style` toggles whether to maintain original look.
- **Tips**:
  - Be explicit about what changes vs. what stays (lighting, color grade, perspective).
  - Mention crucial features to keep (faces, logos, brand colors).
  - Chain multiple small edits rather than one complex instruction.

### `blend_images`

- **Purpose**: multi-image composition / style transfer.
- **Arguments**:
  - `image_paths` (2–3) absolute file paths.
  - `instructions` defining composition and relationships between sources.
  - `blend_mode` optional cue `natural`/`artistic`/`seamless`.
- **Tips**:
  - Describe spatial layout (“model wearing jacket from second image, studio backdrop”).
  - Give lighting/lens cues to harmonize sources.
  - Use `edit_image` for detailed touch-ups after blending.

## Resources

- `image://gallery/recent` – list of latest generated PNGs with metadata.
- `config://api/status` – environment/setup info and documentation pointers.
- `docs://prompting/guide` – Markdown best-practices file (Gemini 2.5 references, use-case patterns).
- `docs://prompting/cheatsheet` – JSON of prompt fragments (shot types, lighting, templates).

## Gemini 2.5 Flash Image Guidelines

_Source: [Google Gemini Image Generation docs](https://ai.google.dev/gemini-api/docs/image-generation)_

- Be hyper-specific; detail subject, environment, lighting, materials, mood.
- Provide intent (logo, product hero, concept art) to influence composition and fidelity.
- Iterate and refine; maintain conversational loop with positive instructions.
- Use structured prompts for complex scenes; call out composition order.
- Employ semantic negatives by describing what should appear, not just what to avoid.
- Control camera & lighting using photography terms (wide angle, macro, low-angle, Rembrandt lighting).
- Editing & blending: specify what to change vs. preserve, especially for style transfer or detail retention.
- Constraints: best performance with ≤3 input images; supports select languages (EN, es-MX, ja-JP, zh-CN, hi-IN); outputs include SynthID watermark; honor policy restrictions.

For detailed examples and cross-model references (DALL·E, Midjourney, Stable Diffusion, Adobe Firefly), review `mcp_nano_banana/resources/MCP_Best_Practices_Nano_Banana.md`.
