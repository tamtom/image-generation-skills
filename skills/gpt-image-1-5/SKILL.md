---
name: gpt-image-1-5
description: Generate and edit images using OpenAI's GPT Image 1.5 model. Use when the user asks to generate, create, edit, modify, change, alter, or update images. Also use when user references an existing image file and asks to modify it in any way (e.g., "modify this image", "change the background", "replace X with Y"). Supports text-to-image generation, multi-image compositing, style transfer, and image editing with optional mask. DO NOT read the image file first - use this skill directly with the --input-image parameter.
---

# GPT Image 1.5 - Image Generation & Editing

Generate new images or edit existing ones using OpenAI's GPT Image 1.5 model via the Images API.

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "your image description" --filename "output.png" [--quality low|medium|high] [--size 1024x1024|1024x1536|1536x1024|auto] [--background transparent|opaque|auto] [--output-format png|webp|jpeg] [--output-compression 0-100] [--n 1-4] [--api-key KEY]
```

**Generate multiple variations:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "your image description" --filename "output.png" --n 4 --quality high
```

**Edit existing image (without mask - full image edit):**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "editing instructions" --filename "output.png" --input-image "path/to/input.png" [--quality low|medium|high] [--input-fidelity high|low] [--output-format png|webp|jpeg] [--api-key KEY]
```

**Edit with multiple reference images (compositing/style transfer):**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "combine the subject from first image with the style of second image" --filename "output.png" --input-image "subject.png" --input-image "style-ref.png" [--input-fidelity high] [--api-key KEY]
```

**Edit existing image (with mask - precise inpainting):**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "what to put in masked area" --filename "output.png" --input-image "path/to/input.png" --mask "path/to/mask.png" [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Parameters

### Quality Options
- **low** - Fastest generation, lower quality
- **medium** (default) - Balanced quality and speed
- **high** - Best quality, slower generation. Use for dense text, detailed layouts, and high-fidelity output

Map user requests:
- No mention of quality -> `medium`
- "quick", "fast", "draft" -> `low`
- "high quality", "best", "detailed", "high-res" -> `high`

### Size Options
- **auto** (default) - Model decides best dimensions based on prompt
- **1024x1024** - Square format
- **1024x1536** - Portrait format
- **1536x1024** - Landscape format

Map user requests:
- No mention of size -> `auto`
- "square" -> `1024x1024`
- "portrait", "vertical", "tall" -> `1024x1536`
- "landscape", "horizontal", "wide" -> `1536x1024`

### Background Options (generation only)
- **auto** (default) - Model decides
- **transparent** - Transparent background (requires png or webp output format)
- **opaque** - Solid background

### Output Format Options
- **png** (default) - Lossless, supports transparency
- **webp** - Smaller file size, supports transparency, good for web
- **jpeg** - Smallest file size, no transparency

Map user requests:
- No mention of format -> `png`
- "small file", "compressed", "web" -> `webp`
- "jpg", "jpeg", "photo" -> `jpeg`
- "transparent" -> `png` (or `webp`)

### Output Compression (webp/jpeg only)
- Range: **0-100** (default: 100 = no compression)
- Lower values = smaller file size, lower quality
- Only applies to `webp` and `jpeg` output formats
- Ignored for `png`

### Number of Images (n)
- Range: **1-4** (default: 1)
- Generates multiple variations in a single API call
- When n > 1, files are numbered: `output-1.png`, `output-2.png`, etc.

Map user requests:
- "variations", "options", "alternatives" -> `--n 4`
- "a couple" -> `--n 2`
- No mention -> `1`

### Input Fidelity (editing only)
- **high** - Preserves fine details, facial identity, textures from input image(s)
- **low** - More creative freedom, less strict preservation

Map user requests:
- Face/portrait editing, identity preservation -> `--input-fidelity high`
- "keep the face", "preserve likeness", "maintain details" -> `--input-fidelity high`
- Style transfer with loose reference -> omit (let model decide)

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `OPENAI_API_KEY` environment variable

If neither is available, the script exits with an error message.

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.{ext}`

**Format:** `{timestamp}-{descriptive-name}.{ext}`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Extension: Match the `--output-format` (`.png`, `.webp`, `.jpg`)
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" -> `2025-12-17-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" (webp) -> `2025-12-17-15-30-12-sunset-mountains.webp`
- Prompt "create a photo of a robot" (jpeg) -> `2025-12-17-16-45-33-robot.jpg`

## Image Editing

All editing uses the Images API (`images.edit` endpoint) with `gpt-image-1.5`.

### Without Mask (Full Image Edit)
When the user wants to modify an existing image without specifying exact regions:
1. Use `--input-image` parameter with the path to the image
2. The prompt should contain editing instructions (e.g., "make the sky more dramatic", "change to cartoon style")
3. A fully transparent mask is auto-generated, allowing the model to edit the entire image

### With Mask (Precise Inpainting)
When the user wants to edit specific regions:
1. Use `--input-image` parameter with the path to the image
2. Use `--mask` parameter with a PNG mask file
3. The mask should have transparent areas (alpha=0) where edits should occur
4. The prompt describes what should appear in the masked region

### Multi-Image Input (Compositing & Style Transfer)
When the user wants to combine elements from multiple images or apply a style from one image to another:
1. Use `--input-image` multiple times (e.g., `--input-image "subject.png" --input-image "style.png"`)
2. Reference images by order in the prompt (e.g., "apply the style of the second image to the subject in the first image")
3. Use `--input-fidelity high` when identity/detail preservation matters

Common editing tasks: add/remove elements, change style, adjust colors, replace backgrounds, composite images, style transfer, virtual try-on, text translation in images.

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

**For multi-image:** Reference images by position (e.g., "combine the person from the first image with the background of the second image")

Preserve user's creative intent in all cases.

## Output

- Saves image to current directory (or specified path if filename includes directory)
- File extension is automatically matched to `--output-format`
- For n > 1, files are numbered: `name-1.ext`, `name-2.ext`, etc.
- Script outputs the full path(s) to the generated image(s)
- **Do not read the image back** - just inform the user of the saved path(s)

## Examples

**Generate new image:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2025-12-17-14-23-05-japanese-garden.png" --quality high --size 1536x1024
```

**Generate with transparent background:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "A cute cartoon cat mascot" --filename "2025-12-17-14-25-30-cat-mascot.png" --background transparent --quality high
```

**Generate multiple variations as compressed webp:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "Minimalist logo for a coffee shop" --filename "2025-12-17-14-26-00-coffee-logo.webp" --n 4 --output-format webp --output-compression 80 --quality high
```

**Edit existing image (full image):**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "make the sky more dramatic with storm clouds" --filename "2025-12-17-14-27-00-dramatic-sky.png" --input-image "original-photo.jpg" --quality high
```

**Edit with identity preservation:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "change the outfit to a red dress" --filename "2025-12-17-14-28-00-red-dress.png" --input-image "portrait.png" --input-fidelity high --quality high
```

**Composite from multiple images:**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "place the person from the first image into the beach scene from the second image" --filename "2025-12-17-14-29-00-beach-composite.png" --input-image "person.png" --input-image "beach.png" --input-fidelity high
```

**Edit with mask (inpainting):**
```bash
uv run ~/.claude/skills/gpt-image-1-5/scripts/generate_image.py --prompt "a flamingo swimming" --filename "2025-12-17-14-30-00-lounge-flamingo.png" --input-image "lounge.png" --mask "mask.png"
```
