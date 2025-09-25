#!/usr/bin/env python3
"""
Bridge module for integrating Nano Banana with various AI assistants
Provides optimized interfaces for Claude Code and GPT-5/Codex
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64

from nano_banana_server import nano_banana, ImageGenerationRequest, ImageEditRequest, ImageBlendRequest

class NanoBananaBridge:
    """Bridge for AI assistant integration"""

    def __init__(self):
        self.nano_banana = nano_banana
        self.context_cache = {}

    async def claude_generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimized image generation for Claude Code
        Follows MCP best practices for Claude integration
        """
        # Apply Claude-specific prompt optimizations
        optimized_prompt = self._optimize_for_claude(prompt, context)

        request = ImageGenerationRequest(
            prompt=optimized_prompt,
            style=context.get("style") if context else None,
            aspect_ratio=context.get("aspect_ratio", "1:1") if context else "1:1",
            quality="high" if context and context.get("high_quality") else "standard"
        )

        response = await self.nano_banana.generate_image(request)

        # Format response for Claude's expected structure
        return self._format_claude_response(response.model_dump())

    async def gpt5_generate(self, prompt: str, reasoning_effort: str = "medium") -> Dict[str, Any]:
        """
        Optimized image generation for GPT-5/Codex
        Implements minimal prompting strategy per GPT-5 best practices
        """
        # Apply GPT-5 specific optimizations (minimal approach)
        optimized_prompt = self._optimize_for_gpt5(prompt, reasoning_effort)

        request = ImageGenerationRequest(
            prompt=optimized_prompt,
            quality="high"  # GPT-5 defaults to high quality
        )

        response = await self.nano_banana.generate_image(request)

        # Format for GPT-5's expected structure
        return self._format_gpt5_response(response.model_dump())

    async def batch_generate(self, prompts: List[str], parallel: bool = True) -> List[Dict[str, Any]]:
        """
        Batch generation optimized for parallel execution
        Follows GPT-5 best practice of parallelizing independent operations
        """
        if parallel:
            # Parallel execution for independent operations
            tasks = [self.nano_banana.generate_image(ImageGenerationRequest(prompt=p)) for p in prompts]
            responses = await asyncio.gather(*tasks)
        else:
            # Sequential execution
            responses = []
            for prompt in prompts:
                response = await self.nano_banana.generate_image(ImageGenerationRequest(prompt=prompt))
                responses.append(response)

        return [r.model_dump() for r in responses]

    async def programmatic_generate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate images based on programmatic configuration
        Supports dynamic generation from code contexts
        """
        # Extract generation parameters from config
        prompt = config.get("prompt", "")

        # Apply programmatic enhancements
        if "variables" in config:
            for key, value in config["variables"].items():
                prompt = prompt.replace(f"{{{key}}}", str(value))

        if "components" in config:
            # Build prompt from components
            components = config["components"]
            prompt = self._build_from_components(prompt, components)

        # Handle conditional generation
        if "conditions" in config:
            prompt = self._apply_conditions(prompt, config["conditions"])

        request = ImageGenerationRequest(
            prompt=prompt,
            style=config.get("style"),
            aspect_ratio=config.get("aspect_ratio", "1:1"),
            quality=config.get("quality", "standard")
        )

        response = await self.nano_banana.generate_image(request)
        return response.model_dump()

    def _optimize_for_claude(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Apply Claude-specific optimizations"""
        # Claude benefits from structured, detailed prompts
        optimized = prompt

        if context:
            if "project_style" in context:
                optimized += f", matching the project's {context['project_style']} style"

            if "requirements" in context:
                reqs = context["requirements"]
                if isinstance(reqs, list):
                    optimized += ". Requirements: " + ", ".join(reqs)

        return optimized

    def _optimize_for_gpt5(self, prompt: str, reasoning_effort: str) -> str:
        """Apply GPT-5 specific optimizations (minimal approach)"""
        # GPT-5 Codex works best with minimal, direct prompts
        # Remove unnecessary descriptors based on reasoning effort
        if reasoning_effort in ["minimal", "low"]:
            # Strip excessive adjectives for routine generation
            return prompt.split(".")[0] if "." in prompt else prompt
        else:
            return prompt

    def _format_claude_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for Claude's expected structure"""
        return {
            "type": "image_generation",
            "success": response["success"],
            "data": {
                "path": response.get("image_path"),
                "base64": response.get("image_data"),
                "metadata": response.get("metadata", {})
            },
            "message": response["message"]
        }

    def _format_gpt5_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for GPT-5's expected structure"""
        # GPT-5 prefers concise responses
        return {
            "success": response["success"],
            "path": response.get("image_path"),
            "data": response.get("image_data"),
            "error": None if response["success"] else response["message"]
        }

    def _build_from_components(self, base_prompt: str, components: Dict[str, Any]) -> str:
        """Build prompt from component specifications"""
        parts = [base_prompt]

        if "subject" in components:
            parts.append(f"Subject: {components['subject']}")

        if "style" in components:
            parts.append(f"Style: {components['style']}")

        if "mood" in components:
            parts.append(f"Mood: {components['mood']}")

        if "details" in components:
            details = components["details"]
            if isinstance(details, list):
                parts.extend(details)
            else:
                parts.append(details)

        return ", ".join(parts)

    def _apply_conditions(self, prompt: str, conditions: Dict[str, Any]) -> str:
        """Apply conditional logic to prompt generation"""
        for condition, modification in conditions.items():
            if self._evaluate_condition(condition):
                if isinstance(modification, str):
                    prompt += f", {modification}"
                elif isinstance(modification, dict):
                    if "append" in modification:
                        prompt += f", {modification['append']}"
                    if "prepend" in modification:
                        prompt = f"{modification['prepend']}, {prompt}"

        return prompt

    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate condition for conditional generation"""
        # Simple condition evaluation - extend as needed
        if condition == "high_detail":
            return True
        elif condition == "production":
            return True
        elif condition.startswith("has_"):
            # Check context cache for conditions
            return condition[4:] in self.context_cache

        return False

# Global bridge instance
bridge = NanoBananaBridge()

# Convenience functions for direct use

async def generate_for_claude(prompt: str, **kwargs) -> Dict[str, Any]:
    """Generate image optimized for Claude Code"""
    return await bridge.claude_generate(prompt, kwargs)

async def generate_for_gpt5(prompt: str, reasoning: str = "medium") -> Dict[str, Any]:
    """Generate image optimized for GPT-5/Codex"""
    return await bridge.gpt5_generate(prompt, reasoning)

async def generate_from_code(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate image from programmatic configuration"""
    return await bridge.programmatic_generate(config)