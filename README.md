# Image Generation Skills

A collection of Agent Skills for AI-powered image generation and editing. These skills wrap popular image generation APIs for seamless use with AI coding agents.

Skills follow the Agent Skills format.

## Installation

Install this skill pack:

```bash
npx skills add tamtom/image-generation-skills
```

## Updating

Check for updates and pull the latest versions:

```bash
npx skills check          # check for available updates
npx skills update         # update all skills to latest versions
```

## Available Skills

### gpt-image-1-5

Generate and edit images using OpenAI's GPT Image 1.5 model via the Images API.

**Use when:**
- You need to generate images from text descriptions
- You want to edit or modify existing images
- You need multi-image compositing or style transfer
- You want precise inpainting with mask support

**Capabilities:**
- Text-to-image generation (quality: low/medium/high)
- Full image editing (without mask)
- Precise inpainting (with mask)
- Multi-image compositing and style transfer
- Multiple variations in a single call (1-4)
- Transparent background support
- Output formats: PNG, WebP, JPEG

### gemini-imagen *(coming soon)*

Image generation using Google's Gemini Imagen model.

## Skill Structure

Each skill contains:
- `SKILL.md` - Instructions for the agent
- `scripts/` - Helper scripts for automation (optional)

## License

MIT
