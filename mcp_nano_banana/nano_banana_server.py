#!/usr/bin/env python3
"""
MCP Server for Nano Banana (Google Gemini Image Generation)
Provides image generation, editing, and blending capabilities
"""

import os
import json
import base64
import asyncio
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import logging

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text description of the image to generate")
    style: Optional[str] = Field(None, description="Art style (realistic, cartoon, abstract, etc.)")
    aspect_ratio: Optional[str] = Field("1:1", description="Aspect ratio (1:1, 16:9, 4:3, etc.)")
    quality: Optional[str] = Field("standard", description="Quality level (standard, high)")

class ImageEditRequest(BaseModel):
    """Request model for image editing"""
    image_path: str = Field(..., description="Path to the input image")
    instructions: str = Field(..., description="Natural language editing instructions")
    preserve_style: bool = Field(True, description="Maintain original image style")

class ImageBlendRequest(BaseModel):
    """Request model for image blending"""
    image_paths: List[str] = Field(..., description="List of image paths to blend (2-3 recommended)")
    instructions: str = Field(..., description="Instructions for blending the images")
    blend_mode: Optional[str] = Field("natural", description="Blending mode (natural, artistic, seamless)")

class ImageGenerationResponse(BaseModel):
    """Response model for image operations"""
    success: bool
    image_path: Optional[str] = None
    image_data: Optional[str] = None  # Base64 encoded
    message: str
    metadata: Optional[Dict[str, Any]] = None

# Initialize MCP server
mcp = FastMCP(
    "Nano Banana Image Generation"
)

class NanoBananaMCP:
    """MCP wrapper for Nano Banana functionality"""

    def __init__(self):
        self.client = None
        self.config: Dict[str, Any] = {}
        # Control whether to include base64 image data in responses (default: False)
        self.include_base64 = os.getenv('NANO_BANANA_INCLUDE_BASE64', 'false').lower() in {'1', 'true', 'yes', 'on'}
        # Default to Gemini 2.5 Flash Image (preview) if available
        # Allow override via environment variable GENAI_IMAGE_MODEL
        self.model = os.getenv("GENAI_IMAGE_MODEL", "models/gemini-2.5-flash-image-preview")
        self.image_models = [
            "models/gemini-2.5-flash",
            "models/gemini-2.5-flash-image-preview",
            "models/gemini-2.0-flash-exp-image-generation",
        ]
        self._initialize_client()
        # Resolve output directory: env > config file > default (one level above MCP dir)
        self.output_dir = self._resolve_output_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_client(self):
        """Initialize Google GenAI client with API key"""
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            config_path = Path.home() / '.nano_banana_config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.config = config if isinstance(config, dict) else {}
                    api_key = self.config.get('api_key')

        if api_key:
            # Prefer explicit API key for client; falls back to env if not provided
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                # Fallback to environment variable method
                os.environ['GEMINI_API_KEY'] = api_key
                self.client = genai.Client()
            logger.info("Gemini client initialized successfully")
        else:
            logger.warning("No API key found. Image generation will fail.")

    def _resolve_output_dir(self) -> Path:
        """Determine the output directory.

        Priority:
        1) NANO_BANANA_OUTPUT_DIR env var
        2) output_dir in ~/.nano_banana_config.json
        3) Project root (detected via .mcp.json near CWD): <project_root>/mcp_generated_images
        4) Folder one level above the MCP directory: <repo_parent>/mcp_generated_images (when not installed in site-packages)
        5) Fallback to home: ~/mcp_generated_images
        """
        # 1) Env override
        env_dir = os.getenv('NANO_BANANA_OUTPUT_DIR')
        if env_dir:
            return Path(env_dir).expanduser()

        # 2) Config file
        if isinstance(self.config, dict) and self.config.get('output_dir'):
            return Path(self.config['output_dir']).expanduser()

        # 3) Try to detect project root by searching upwards for .mcp.json
        # Start from this file's directory to be robust when CWD is different
        try:
            start_dir = Path(__file__).resolve().parent
            for ancestor in [start_dir] + list(start_dir.parents):
                marker = ancestor / '.mcp.json'
                if marker.exists():
                    if os.access(ancestor, os.W_OK):
                        return ancestor / 'mcp_generated_images'
                    break
        except Exception:
            pass

        # 4) Default one level above MCP repo directory if not in site-packages
        try:
            parent_of_mcp = Path(__file__).resolve().parent.parent.parent
            parent_str = str(parent_of_mcp).lower()
            unsafe = ("site-packages" in parent_str) or ("dist-packages" in parent_str)
            if not unsafe and os.access(parent_of_mcp, os.W_OK):
                return parent_of_mcp / "mcp_generated_images"
        except Exception:
            pass

        # 5) Fallback to home if unexpected path
        return Path.home() / "mcp_generated_images"

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate an image from text prompt"""
        if not self.client:
            return ImageGenerationResponse(
                success=False,
                message="API key not configured. See README 'Configure credentials' section."
            )

        try:
            enhanced_prompt = self._enhance_prompt(request)

            logger.info(f"Generating image: {request.prompt[:50]}...")

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=enhanced_prompt)],
                )
            ]
            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            if response:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.png"
                output_path = self.output_dir / filename

                image_data_b64, mime_type = self._extract_first_image_base64_and_mime(response)
                if image_data_b64:
                    ext = 'png'
                    if mime_type:
                        guessed_ext = mimetypes.guess_extension(mime_type) or '.png'
                        ext = guessed_ext.lstrip('.')
                        if not ext:
                            ext = 'png'
                    filename = f"generated_{timestamp}.{ext}"
                    output_path = self.output_dir / filename
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(image_data_b64))

                return ImageGenerationResponse(
                    success=True,
                    image_path=str(output_path),
                    image_data=image_data_b64 if self.include_base64 else None,
                    message=f"Image generated successfully: {filename}",
                    metadata={
                        "prompt": request.prompt,
                        "style": request.style,
                        "aspect_ratio": request.aspect_ratio,
                        "timestamp": timestamp
                    }
                )
            else:
                return ImageGenerationResponse(
                    success=False,
                    message="Failed to generate image"
                )

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return ImageGenerationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )

    async def edit_image(self, request: ImageEditRequest) -> ImageGenerationResponse:
        """Edit an existing image using natural language"""
        if not self.client:
            return ImageGenerationResponse(
                success=False,
                message="API key not configured"
            )

        try:
            if not Path(request.image_path).exists():
                return ImageGenerationResponse(
                    success=False,
                    message=f"Image not found: {request.image_path}"
                )

            logger.info(f"Editing image: {request.image_path}")

            with open(request.image_path, 'rb') as infile:
                image_bytes = infile.read()
            mime_type, _ = mimetypes.guess_type(request.image_path)
            if not mime_type:
                mime_type = 'image/png'

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        types.Part.from_text(text=f"Edit this image: {request.instructions}"),
                    ],
                )
            ]

            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            if response:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_data_b64, mime_type = self._extract_first_image_base64_and_mime(response)
                if image_data_b64:
                    ext = 'png'
                    if mime_type:
                        guessed_ext = mimetypes.guess_extension(mime_type) or '.png'
                        ext = guessed_ext.lstrip('.')
                        if not ext:
                            ext = 'png'
                    filename = f"edited_{timestamp}.{ext}"
                    output_path = self.output_dir / filename
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(image_data_b64))

                return ImageGenerationResponse(
                    success=True,
                    image_path=str(output_path),
                    image_data=image_data_b64 if self.include_base64 else None,
                    message=f"Image edited successfully: {filename}",
                    metadata={
                        "original": request.image_path,
                        "instructions": request.instructions,
                        "timestamp": timestamp
                    }
                )

        except Exception as e:
            logger.error(f"Error editing image: {e}")
            return ImageGenerationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )

    async def blend_images(self, request: ImageBlendRequest) -> ImageGenerationResponse:
        """Blend multiple images into one"""
        if not self.client:
            return ImageGenerationResponse(
                success=False,
                message="API key not configured"
            )

        try:
            for path in request.image_paths:
                if not Path(path).exists():
                    return ImageGenerationResponse(
                        success=False,
                        message=f"Image not found: {path}"
                    )

            logger.info(f"Blending {len(request.image_paths)} images")

            parts: List[types.Part] = []
            for path in request.image_paths:
                with open(path, 'rb') as infile:
                    image_bytes = infile.read()
                mime_type, _ = mimetypes.guess_type(path)
                if not mime_type:
                    mime_type = 'image/png'
                parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

            blend_prompt = self._create_blend_prompt(request)
            parts.append(types.Part.from_text(text=blend_prompt))

            contents = [
                types.Content(
                    role="user",
                    parts=parts,
                )
            ]

            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )

            if response:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_data_b64, mime_type = self._extract_first_image_base64_and_mime(response)
                if image_data_b64:
                    ext = 'png'
                    if mime_type:
                        guessed_ext = mimetypes.guess_extension(mime_type) or '.png'
                        ext = guessed_ext.lstrip('.')
                        if not ext:
                            ext = 'png'
                    filename = f"blended_{timestamp}.{ext}"
                    output_path = self.output_dir / filename
                    with open(output_path, 'wb') as f:
                        f.write(base64.b64decode(image_data_b64))

                return ImageGenerationResponse(
                    success=True,
                    image_path=str(output_path),
                    image_data=image_data_b64 if self.include_base64 else None,
                    message=f"Images blended successfully: {filename}",
                    metadata={
                        "source_images": request.image_paths,
                        "instructions": request.instructions,
                        "blend_mode": request.blend_mode,
                        "timestamp": timestamp
                    }
                )

        except Exception as e:
            logger.error(f"Error blending images: {e}")
            return ImageGenerationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )

    def _enhance_prompt(self, request: ImageGenerationRequest) -> str:
        """Enhance prompt with style and quality modifiers"""
        prompt = request.prompt

        if request.style:
            style_modifiers = {
                "realistic": "photorealistic, high detail, professional photography",
                "cartoon": "cartoon style, animated, colorful, playful",
                "abstract": "abstract art, creative, artistic interpretation",
                "minimalist": "minimalist design, simple, clean lines",
                "vintage": "vintage style, retro, nostalgic aesthetics"
            }
            if request.style in style_modifiers:
                prompt += f", {style_modifiers[request.style]}"

        if request.aspect_ratio != "1:1":
            prompt += f", aspect ratio {request.aspect_ratio}"

        if request.quality == "high":
            prompt += ", ultra high quality, 8K resolution, masterpiece"

        return prompt

    def _create_blend_prompt(self, request: ImageBlendRequest) -> str:
        """Create optimized blending instructions"""
        base_prompt = request.instructions

        blend_modes = {
            "natural": "Blend these images naturally, maintaining realistic proportions and lighting",
            "artistic": "Create an artistic composition combining elements from all images creatively",
            "seamless": "Merge these images seamlessly as if they were always one cohesive scene"
        }

        mode_instruction = blend_modes.get(request.blend_mode, blend_modes["natural"])
        return f"{mode_instruction}. {base_prompt}"

    def _extract_first_image_base64_and_mime(self, response) -> Tuple[Optional[str], Optional[str]]:
        """Extract the first image as base64 string and its mime type from a google-genai response"""
        try:
            images = getattr(response, 'images', None)
            if images:
                first = images[0]
                data = getattr(first, 'data', None)
                if data:
                    b64 = base64.b64encode(data).decode('utf-8')
                    mime = getattr(first, 'mime_type', None)
                    return b64, mime
        except Exception:
            pass

        try:
            if getattr(response, 'candidates', None):
                candidate0 = response.candidates[0]
                content = getattr(candidate0, 'content', None)
                if content and getattr(content, 'parts', None):
                    for part in content.parts:
                        inline_data = getattr(part, 'inline_data', None)
                        if inline_data and getattr(inline_data, 'data', None):
                            data_bytes = inline_data.data
                            b64 = base64.b64encode(data_bytes).decode('utf-8')
                            mime = getattr(inline_data, 'mime_type', None)
                            return b64, mime
        except Exception:
            pass

        return None, None

# Create singleton instance
nano_banana = NanoBananaMCP()

# MCP Tool Definitions

@mcp.tool()
async def generate_image(
    prompt: str,
    style: Optional[str] = None,
    aspect_ratio: Optional[str] = "1:1",
    quality: Optional[str] = "standard"
) -> Dict[str, Any]:
    """
    Generate an image from a text description using Google's Gemini model.

    Args:
        prompt: Detailed description of the desired image.
        style: Optional style hint (realistic, cartoon, abstract, minimalist, vintage).
        aspect_ratio: Target aspect ratio (1:1, 16:9, 4:3, 9:16).
        quality: Quality level (standard, high).

    Returns:
        Dict with success, image path, optional base64, and metadata.

    Tips:
    - Describe the scene, not just keywords: subject, environment, mood.
    - Use photographic language: shot type (close‑up, wide), lens (35mm/85mm),
      depth of field (shallow f/2.0), lighting (Rembrandt, golden hour), composition
      (rule of thirds, leading lines).
    - Be explicit for logos/text: exact wording, layout, legibility.
    - Iterate: keep what you like, specify small changes between runs.

    See also:
      docs://prompting/guide  and  docs://prompting/cheatsheet
    """
    request = ImageGenerationRequest(
        prompt=prompt,
        style=style,
        aspect_ratio=aspect_ratio,
        quality=quality
    )

    response = await nano_banana.generate_image(request)
    return response.model_dump()

@mcp.tool()
async def edit_image(
    image_path: str,
    instructions: str,
    preserve_style: bool = True
) -> Dict[str, Any]:
    """
    Edit an existing image using natural language instructions.

    Args:
        image_path: Absolute path to the source image.
        instructions: Clear edit request (e.g. "replace blue sofa with brown leather chesterfield,
            preserve lighting/perspective").
        preserve_style: Maintain original style/lighting by default.

    Returns:
        Dict with success, edited path, optional base64, and metadata.

    Tips:
    - Semantic inpainting works best with targeted requests (what to change vs. what to keep).
    - Mention critical details to preserve (faces, logos, colors) alongside the edit.
    - Provide photographic context if needed (angle, lens feel, lighting continuity).

    See also:
      docs://prompting/guide  and  docs://prompting/cheatsheet
    """
    request = ImageEditRequest(
        image_path=image_path,
        instructions=instructions,
        preserve_style=preserve_style
    )

    response = await nano_banana.edit_image(request)
    return response.model_dump()

@mcp.tool()
async def blend_images(
    image_paths: List[str],
    instructions: str,
    blend_mode: Optional[str] = "natural"
) -> Dict[str, Any]:
    """
    Blend multiple images into a single composition.

    Args:
        image_paths: Absolute paths to 2–3 source images.
        instructions: Composition goal and relationships (e.g. "model wearing jacket from second image,
            studio backdrop, neutral pose").
        blend_mode: natural | artistic | seamless.

    Returns:
        Dict with success, blended path, optional base64, and metadata.

    Tips:
    - Describe spatial layout and scale between elements.
    - Add lighting and lens cues to harmonize sources (e.g. 85mm portrait compression, soft rim light).
    - Use iterative edits after blending for fine adjustments.

    See also:
      docs://prompting/guide  and  docs://prompting/cheatsheet
    """
    request = ImageBlendRequest(
        image_paths=image_paths,
        instructions=instructions,
        blend_mode=blend_mode
    )

    response = await nano_banana.blend_images(request)
    return response.model_dump()

# MCP Resource Definitions

@mcp.resource("image://gallery/recent")
async def get_recent_images() -> str:
    """Get list of recently generated images"""
    output_dir = nano_banana.output_dir
    images = sorted(output_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]

    image_list = []
    for img in images:
        image_list.append({
            "filename": img.name,
            "path": str(img),
            "size": img.stat().st_size,
            "created": datetime.fromtimestamp(img.stat().st_mtime).isoformat()
        })

    return json.dumps(image_list, indent=2)

@mcp.resource("config://api/status")
async def get_api_status() -> str:
    """Check Nano Banana API configuration status"""
    status = {
        "configured": nano_banana.client is not None,
        "model": nano_banana.model,
        "output_directory": str(nano_banana.output_dir),
        "daily_limit": 500,
        "price_per_image": "$0.039",
        "documentation": {
            "prompting_guide": "docs://prompting/guide",
            "cheatsheet": "docs://prompting/cheatsheet",
            "gallery": "image://gallery/recent"
        }
    }

    if not status["configured"]:
        status["setup_instructions"] = "Create ~/.nano_banana_config.json or set GEMINI_API_KEY"

    return json.dumps(status, indent=2)

# MCP Prompt Definitions

@mcp.prompt()
def create_app_mockup(
    app_type: str = "mobile",
    features: str = "login, dashboard, profile",
    style: str = "modern"
) -> str:
    """Generate a prompt for creating app mockup images"""
    return f"""Generate a {style} {app_type} app mockup showing these features: {features}.

    Requirements:
    - High-fidelity UI design
    - Clean, professional layout
    - Consistent color scheme
    - Modern design patterns
    - Show multiple screens if needed

    Make it look production-ready and visually appealing."""

@mcp.prompt()
def create_logo(
    company_name: str,
    industry: str,
    style: str = "minimalist"
) -> str:
    """Generate a prompt for creating a company logo"""
    return f"""Design a {style} logo for '{company_name}' in the {industry} industry.

    Requirements:
    - Clean, scalable design
    - Memorable and unique
    - Appropriate for the industry
    - Works in both color and monochrome
    - Professional appearance

    The logo should convey trust, innovation, and professionalism."""

@mcp.prompt()
def enhance_product_photo(
    product_type: str,
    background: str = "white studio",
    lighting: str = "professional"
) -> str:
    """Generate a prompt for product photography enhancement"""
    return f"""Create a {lighting} product photograph of a {product_type} with a {background} background.

    Requirements:
    - High-quality product rendering
    - Professional lighting setup
    - Clean composition
    - E-commerce ready
    - Highlight product features

    Make it suitable for marketing and e-commerce use."""

# Additional preset prompts for common workflows

@mcp.prompt()
def preset_product_shot() -> str:
    """Preset: photorealistic product shot with classic studio cues."""
    return (
        "Studio product photo of a brushed steel smartwatch on matte black acrylic, "
        "soft 45° key light with subtle rim light, 85mm portrait lens compression, "
        "shallow depth of field (f/2.8), rule of thirds, premium editorial aesthetic"
    )

@mcp.prompt()
def preset_logo_text_accuracy() -> str:
    """Preset: text-forward logo with high legibility."""
    return (
        "Minimalist logo reading 'CYBER POINT' in geometric sans serif, tight kerning, high legibility, "
        "monochrome on white, vector-like simplicity"
    )

# Documentation resources

@mcp.resource("docs://prompting/guide")
async def get_prompting_guide() -> str:
    """Return the local Nano Banana prompting guide Markdown for agent consumption."""
    try:
        guide_path = Path(__file__).resolve().parent / "resources" / "MCP_Best_Practices_Nano_Banana.md"
        if guide_path.exists():
            return guide_path.read_text(encoding="utf-8")
        return "Prompting guide not found."
    except Exception as e:
        return f"Error reading prompting guide: {e}"

@mcp.resource("docs://prompting/cheatsheet")
async def get_prompting_cheatsheet() -> str:
    """Return a JSON cheatsheet of photo/cinema prompt fragments and templates."""
    cheatsheet: Dict[str, Any] = {
        "framing_shots": [
            "wide shot, establishing shot, rule of thirds",
            "medium shot, waist-up, centered composition",
            "close-up portrait, head-and-shoulders, eye-level",
            "extreme close-up, macro texture detail"
        ],
        "angles_movement": [
            "low-angle hero shot", "high-angle overview", "top-down bird's-eye", "Dutch tilt",
            "handheld natural shake", "smooth dolly push-in", "slow pan left"
        ],
        "focal_lengths": {
            "24mm": "wide-angle perspective, strong foreground emphasis",
            "35mm": "environmental portrait, natural perspective",
            "50mm": "standard view, minimal distortion",
            "85mm": "portrait lens, gentle compression",
            "135mm": "telephoto, strong background compression"
        },
        "depth_of_field": [
            "shallow DoF, creamy bokeh, f/1.8",
            "deep focus landscape, f/11",
            "specular bokeh highlights"
        ],
        "lighting_styles": [
            "three-point: key 45°, soft fill, subtle hair/back light",
            "Rembrandt lighting", "butterfly lighting", "loop lighting", "split lighting",
            "golden hour warm backlight", "blue hour cool ambience", "overcast softbox skies"
        ],
        "composition": [
            "rule of thirds, leading lines, strong foreground interest",
            "symmetry and reflections, centered composition",
            "minimalist negative space for text overlay"
        ],
        "color_grade": [
            "cinematic teal-and-orange grade, soft film halation",
            "pastel palette, low contrast matte blacks",
            "Kodachrome-inspired colors, subtle grain"
        ],
        "templates": {
            "product_photography": "Studio product photo of a brushed steel smartwatch on matte black acrylic, soft 45° key light, 85mm lens, shallow DoF (f/2.8), premium editorial aesthetic",
            "logo_text_accuracy": "Minimalist logo reading 'CYBER POINT' in geometric sans serif, tight kerning, high legibility, monochrome on white, vector-like simplicity"
        }
    }
    return json.dumps(cheatsheet, indent=2)

if __name__ == "__main__":
    # Run the MCP server
    import sys
    mcp.run("stdio")
