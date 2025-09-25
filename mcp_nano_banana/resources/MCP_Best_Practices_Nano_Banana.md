# Nano Banana (Gemini 2.5 Flash Image) Prompting Guide

## Summary

- Model delivers conversational image, editing, and blending workflows across text-only, image+text, and multi-image prompts. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
- All outputs contain SynthID watermark; ensure downstream workflows account for it.
- Support iterative workflows; refine prompts across turns.

## General Best Practices

1. **Describe the scene** – Provide rich narrative rather than keyword lists. The model leverages language understanding to produce coherent compositions. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
2. **Be hyper-specific** – Include subject details, environment, mood, lighting, camera terminology, and materials. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
3. **State intent** – Clarify usage (e.g., logo, concept art, e-commerce hero) so the model aligns design choices. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
4. **Iterate** – Expect multiple rounds. Request adjustments (“warm the lighting”, “keep composition but change expression”) to refine outputs. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
5. **Structured instructions** – For complex scenes, break into sequential instructions. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
6. **Positive phrasing** – Use semantic negatives (describe what to include vs. “no X”). [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
7. **Camera control** – Specify shot type (“macro”, “low-angle”), lens, and depth-of-field to steer composition. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

## Prompt Patterns by Use Case

### Photorealistic Photography

- Include camera gear, lighting, focal length, and styling cues. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "A photorealistic close-up portrait of an elderly Japanese ceramicist in a dim workshop, 85mm lens, shallow depth of field, dramatic rim lighting highlighting porcelain bowls, cinematic realism",
    "style": "realistic",
    "quality": "high"
  }
}
```

### Stylized Illustrations / Stickers

- Call out medium, texture, outline, background transparency. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Kawaii sticker illustration of a happy red panda sipping bubble tea, chibi proportions, pastel palette, thick white border, transparent background",
    "aspect_ratio": "1:1"
  }
}
```

### Text-Forward Graphics / Logos

- Spell out text exactly; describe typography and layout. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Modern minimalist logo for a coffee shop called 'The Daily Grind', sans-serif lettering, clean negative space, monochrome palette, scalable vector aesthetic",
    "style": "minimalist"
  }
}
```

### Product Mockups / Commercial Photography

- Provide lighting, surface, props, and brand tone. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Studio-lit product photograph of a matte black ceramic coffee mug on a walnut table, soft diffused light, subtle steam, lifestyle brand aesthetic"
  }
}
```

### Minimalist / Negative Space

- Emphasize simplicity, composition, and intended text overlay. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Minimalist composition with a single delicate red maple leaf suspended against a warm beige gradient background, ample negative space, high-resolution backdrop"
  }
}
```

### Sequential Art / Storyboards

- Describe characters, panels, style, and narrative beat. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Single comic panel in gritty noir style: trench-coated detective under neon rain, hard shadows, dramatic perspective, speech bubble reading 'This city hides more than secrets.'"
  }
}
```

## Editing & Blending Workflows

### Add/Remove Elements

- Mention subject, desired edit, maintain style cues. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/to/cat.png",
    "instructions": "Add a small knitted wizard hat matching the cat's fur tones, keep lighting consistent"
  }
}
```

### Semantic Inpainting

- Specify region conceptually; describe replacement attributes. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/to/living_room.png",
    "instructions": "Replace only the blue sofa with a vintage brown leather chesterfield, preserve lighting and perspective"
  }
}
```

### Style Transfer

- Provide target style; describe desired transformation. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/to/city.jpg",
    "instructions": "Reinterpret the scene in a cyberpunk anime style with neon signage and reflective puddles"
  }
}
```

### Multi-Image Composition

- Feed multiple paths and describe composite goal. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "blend_images",
  "arguments": {
    "image_paths": ["/path/dress.png", "/path/model.png"],
    "instructions": "Create a professional e-commerce photo of the model wearing the dress, studio backdrop, natural pose"
  }
}
```

### Detail Preservation

- Reinforce critical traits alongside the edit request. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/path/headshot.png",
    "instructions": "Keep facial features intact; add a subtle 'GA' lapel pin matching brand colors"
  }
}
```

## Iterative Prompting Checklist

- Start with descriptive base prompt.
- Review output; note adjustments needed (lighting, pose, palette, background).
- Issue follow-up instructions referencing previous image (“Keep current composition”).
- Limit edits per iteration for clarity.
- Cache output paths using `image://gallery/recent` resource to avoid re-specifying prompts.

## Limitations & Considerations

- Optimal languages: English, es-MX, ja-JP, zh-CN, hi-IN. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
- Max 3 input images recommended. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
- For text-in-image, consider generating text separately first. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
- Outputs include SynthID watermark—retain metadata when distributing. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)
- Avoid disallowed content per Google Prohibited Use Policy. [[Google AI Gemini Image Generation Docs]](https://ai.google.dev/gemini-api/docs/image-generation)

## Embedding into MCP Documentation

- Link this guide from MCP README under “Prompting Tips.”
- Provide quick link to Google Gemini documentation for up-to-date examples.
- Encourage agents to log adjustments made between iterations for auditability.

## Appendix: Example Workflow

1. Call `generate_image` with rich prompt.
2. If adjustments needed, call `edit_image` referencing output path and targeted instructions.
3. For composites, use `blend_images` with previously generated assets.
4. Surface metadata from tool responses (prompt, timestamp, aspect ratio) to agent UI for context.

## Cross‑Model Prompting References (Beyond Google)

- OpenAI Images (DALL·E) Prompting Guide: [[OpenAI Images docs]](https://platform.openai.com/docs/guides/images)
- Midjourney Prompting & Parameters: [[Midjourney Prompts]](https://docs.midjourney.com/docs/prompts), [[Styles & Parameters]](https://docs.midjourney.com/docs/styles-and-parameters)
- Stable Diffusion community prompt guide: [[Stable Diffusion Prompt Guide]](https://stable-diffusion-art.com/prompt-guide/)
- Adobe Firefly prompt tips: [[Adobe Firefly Prompt Tips]](https://helpx.adobe.com/firefly/using/tips-for-writing-prompts.html)

Key themes that generalize across models:

- Be specific about subjects, materials, lighting, style, and composition
- Use photographic/cinematic vocabulary to control framing and mood
- Iterate with small, focused changes; preserve what you like explicitly
- Provide references or exemplars when possible (links, uploaded images)

## Photographic & Cinematographic Techniques (Prompt Fragments)

Use these ready‑to‑paste fragments to steer composition and style. Combine a few per prompt; avoid over‑constraining.

### Framing & Shot Types

- "wide shot, establishing shot, rule of thirds"
- "medium shot, subject waist‑up, centered composition"
- "close‑up portrait, head‑and‑shoulders, eye‑level"
- "extreme close‑up of texture, macro detail"

References: [[StudioBinder – Camera Shots]](https://www.studiobinder.com/blog/types-of-camera-shots/)

### Camera Angles & Movement

- Angles: "low‑angle hero shot", "high‑angle overview", "bird’s‑eye top‑down", "Dutch tilt"
- Movement feel: "handheld, natural shake", "smooth dolly push‑in", "slow pan left"

References: [[StudioBinder – Camera Angles]](https://www.studiobinder.com/blog/camera-angles/), [[StudioBinder – Camera Movements]](https://www.studiobinder.com/blog/types-of-camera-movements/)

### Lenses & Perspective (Focal Length)

- "24mm wide‑angle perspective, strong foreground/background separation"
- "35mm environmental portrait, natural perspective"
- "50mm standard view, minimal distortion"
- "85mm portrait lens, gentle compression, flattering facial proportions"
- "135mm telephoto, strong background compression"

Reference: [[Photography Life – What Is Focal Length]](https://photographylife.com/what-is-focal-length)

### Depth of Field, Aperture, Bokeh

- "shallow depth of field, creamy bokeh, f/1.8"
- "deep focus landscape, f/11, everything sharp"
- "specular bokeh highlights, circular aperture blades"

### Lighting Styles & Setups

- Three‑point: "key light 45° off‑axis, soft fill, subtle hair/back light"
- Portrait patterns: "Rembrandt lighting", "butterfly lighting", "loop lighting", "split lighting"
- Time/mood: "golden hour warm backlight", "blue hour cool ambience", "overcast softbox skies"

References: [[B&H – Portrait Lighting 101]](https://www.bhphotovideo.com/explora/photography/tips-and-solutions/portrait-lighting-101), [[MasterClass – Lighting Styles]](https://www.masterclass.com/articles/lighting-styles)

### Composition & Design

- "rule of thirds, leading lines, strong foreground interest"
- "symmetry and reflections, centered composition"
- "minimalist negative space for text overlay"

### Color, Film, and Grade

- "cinematic teal‑and‑orange grade, soft film halation"
- "pastel palette, low contrast matte blacks"
- "Kodachrome‑inspired colors, subtle grain"

### Production Notes (Context That Helps)

- "hero product centered on seamless backdrop"
- "brand palette: deep indigo and silver"
- "e‑commerce ready, shadow under product, true‑to‑color"

## Cross‑Model Prompt Templates (MCP Tool Shapes)

Photorealistic product (works across models):

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Studio product photo of a brushed steel smartwatch on matte black acrylic, soft 45° key light, subtle rim light, 85mm portrait lens compression, shallow depth of field (f/2.8), rule of thirds, premium editorial aesthetic",
    "style": "realistic",
    "quality": "high",
    "aspect_ratio": "4:3"
  }
}
```

Stylized logo/text accuracy:

```json
{
  "name": "generate_image",
  "arguments": {
    "prompt": "Minimalist logo reading 'CYBER POINT' in geometric sans serif, tight kerning, high legibility, accurate letterforms, monochrome on white, vector‑like simplicity"
  }
}
```

Edit with semantic inpainting:

```json
{
  "name": "edit_image",
  "arguments": {
    "image_path": "/absolute/path/to/input.png",
    "instructions": "Change only the sofa to a vintage brown leather chesterfield; preserve lighting, perspective, and color balance"
  }
}
```

Blend/composite:

```json
{
  "name": "blend_images",
  "arguments": {
    "image_paths": ["/path/model.png", "/path/jacket.png"],
    "instructions": "Create an editorial fashion shot of the model wearing the jacket in a studio set; soft rim light, neutral gray backdrop, 85mm lens compression"
  }
}
```

## Example Outputs from Your Project

You can embed recent results for quick reference:

![Generated example](mcp_generated_images/generated_20250925_122050.png)
![Blended example](mcp_generated_images/blended_20250924_214248.png)

—

Further reading:

- Google Gemini Image Generation: [[ai.google.dev]](https://ai.google.dev/gemini-api/docs/image-generation)
- OpenAI Images: [[platform.openai.com]](https://platform.openai.com/docs/guides/images)
- Midjourney Prompts: [[docs.midjourney.com]](https://docs.midjourney.com/docs/prompts)
- Stable Diffusion Prompting: [[stable-diffusion-art.com]](https://stable-diffusion-art.com/prompt-guide/)
- Adobe Firefly Tips: [[helpx.adobe.com]](https://helpx.adobe.com/firefly/using/tips-for-writing-prompts.html)
