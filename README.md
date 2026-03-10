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

### gemini-nano-banana-2

Generate and edit images using Google's Gemini Nano Banana 2 model (`gemini-3.1-flash-image-preview`) — the latest and most capable Gemini image model.

**Use when:**
- You need to generate images from text descriptions using Gemini
- You want to edit or modify existing images
- You need multi-image compositing, style transfer, or character consistency
- You want real-time data in images (weather, news) via Google Search grounding
- You need accurate depictions of real-world subjects via Google Image Search grounding
- You want high-resolution output up to 4K

**Capabilities:**
- Text-to-image generation with advanced text rendering
- Image editing (single or multi-image input, up to 14 reference images)
- Google Web Search grounding (real-time data)
- Google Image Search grounding (visual reference from the web)
- Controllable thinking levels (minimal/high)
- 14 aspect ratios (1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9)
- 4 resolutions (512, 1K, 2K, 4K)
- Output formats: PNG, WebP, JPEG
- Built-in cost estimation with confirmation for requests ≥ $0.10

## Skill Structure

Each skill contains:
- `SKILL.md` - Instructions for the agent
- `scripts/` - Helper scripts for automation (optional)

## License

MIT
