---
name: gemini-nano-banana-2
description: Generate and edit images using Google's Gemini Nano Banana 2 (gemini-3.1-flash-image-preview). Use when the user asks to generate, create, edit, modify, change, alter, or update images using Gemini. Also use when user references an existing image file and asks to modify it in any way. Supports text-to-image generation, image editing, multi-image compositing (up to 14 reference images), style transfer, Google Web Search and Image Search grounding for real-time data, high-resolution output up to 4K, controllable thinking levels, 14 aspect ratios, and advanced text rendering. DO NOT read the image file first - use this skill directly with the --input-image parameter.
---

# Gemini Nano Banana 2 - Image Generation & Editing

Generate new images or edit existing ones using Google's Gemini Nano Banana 2 model (`gemini-3.1-flash-image-preview`) via the Gemini API. This is the latest and most capable Gemini image model, featuring advanced reasoning ("Thinking") with controllable levels, high-fidelity text rendering, Google Web + Image Search grounding, output from 512 up to 4K resolution, and 14 aspect ratios.

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "your image description" --filename "output.png" [--aspect-ratio 1:1|1:4|1:8|2:3|3:2|3:4|4:1|4:3|4:5|5:4|8:1|9:16|16:9|21:9] [--resolution 512|1K|2K|4K] [--output-format png|webp|jpeg] [--response-modality text-and-image|image-only] [--thinking-level minimal|high] [--google-search] [--image-search] [--yes] [--cost-threshold 0.10] [--api-key KEY]
```

**Edit existing image:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "editing instructions" --filename "output.png" --input-image "path/to/input.png" [--aspect-ratio 1:1] [--resolution 2K] [--api-key KEY]
```

**Edit with multiple reference images (compositing/style transfer, up to 14 images):**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "combine the subject from first image with the style of second image" --filename "output.png" --input-image "subject.png" --input-image "style-ref.png" [--resolution 2K] [--api-key KEY]
```

**Generate with Google Web Search grounding (real-time data):**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "visualize the current weather forecast for San Francisco" --filename "output.png" --google-search --aspect-ratio 16:9 [--api-key KEY]
```

**Generate with Google Image Search grounding (visual reference from the web):**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "a detailed painting of a resplendent quetzal bird resting on a flower" --filename "output.png" --image-search [--api-key KEY]
```

**Generate with high thinking level (complex prompts):**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "A futuristic city built inside a giant glass bottle floating in space" --filename "output.png" --thinking-level high --resolution 2K [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Parameters

### Aspect Ratio Options (14 ratios)
- **1:1** (default) - Square format
- **1:4** - Extreme vertical (banners)
- **1:8** - Ultra-extreme vertical
- **2:3** - Portrait
- **3:2** - Landscape
- **3:4** - Portrait (closer to square)
- **4:1** - Extreme horizontal (banners)
- **4:3** - Landscape (closer to square)
- **4:5** - Portrait (social media)
- **5:4** - Landscape (social media)
- **8:1** - Ultra-extreme horizontal
- **9:16** - Tall portrait (stories/reels)
- **16:9** - Wide landscape (presentations/video)
- **21:9** - Ultra-wide (cinematic)

Map user requests:
- No mention of size/ratio -> `1:1`
- "square" -> `1:1`
- "portrait", "vertical", "tall" -> `2:3` or `9:16`
- "landscape", "horizontal", "wide" -> `3:2` or `16:9`
- "stories", "reels", "mobile" -> `9:16`
- "presentation", "video", "widescreen" -> `16:9`
- "cinematic", "ultra-wide" -> `21:9`
- "social media post" -> `4:5` (portrait) or `5:4` (landscape)
- "banner", "header" -> `4:1` or `1:4` depending on orientation
- "panoramic" -> `8:1`

### Resolution Options
- **512** - Small/thumbnail (~512px, fastest, lowest cost)
- **1K** (default) - Standard quality (~1024px, fast)
- **2K** - High quality (~2048px, good balance)
- **4K** - Maximum quality (~4096px, slowest, highest cost)

Map user requests:
- No mention of resolution -> `1K`
- "thumbnail", "icon", "small" -> `512`
- "high quality", "detailed", "high-res" -> `2K`
- "maximum quality", "4K", "ultra", "print quality" -> `4K`
- "quick", "fast", "draft" -> `512` or `1K`

### Output Format Options
- **png** (default) - Lossless, supports transparency
- **webp** - Smaller file size, supports transparency
- **jpeg** - Smallest file size, no transparency

Map user requests:
- No mention of format -> `png`
- "small file", "compressed", "web" -> `webp`
- "jpg", "jpeg", "photo" -> `jpeg`

### Response Modality
- **text-and-image** (default) - Returns both text description and image
- **image-only** - Returns only the generated image, no text

Map user requests:
- Default -> `text-and-image`
- "just the image", "no text", "image only" -> `image-only`

### Thinking Level
- **minimal** (default) - Faster generation, good for simple prompts
- **high** - Better quality for complex prompts with many elements, text rendering, or spatial relationships

Map user requests:
- Default / simple prompts -> `minimal`
- Complex scenes, precise text, many elements -> `high`
- "think harder", "best quality", "complex" -> `high`

### Google Web Search Grounding
- **--google-search** flag enables Google Web Search grounding
- Allows the model to use real-time web data when generating images
- Useful for: current weather, recent events, factual infographics, stock charts, data visualizations

Map user requests:
- "current", "today", "latest", "real-time", "up to date" -> add `--google-search`
- Factual data requests (weather, news, sports scores) -> add `--google-search`
- Creative/fictional prompts -> omit (not needed)

### Google Image Search Grounding (Nano Banana 2 exclusive)
- **--image-search** flag enables Google Image Search grounding
- Allows the model to find and use web images as visual reference for generation
- Useful for: accurate depictions of real species, landmarks, products, or people
- Can be combined with `--google-search` for both web and image grounding

Map user requests:
- "accurate", "realistic depiction of [real thing]" -> add `--image-search`
- Requests for specific real-world subjects (animals, landmarks, products) -> add `--image-search`
- Abstract/creative prompts -> omit (not needed)

### Cost Warning & Auto-Approve
- The script estimates request cost before calling the API
- If estimated cost **≥ $0.10** (default threshold), it shows a breakdown and asks for confirmation
- **--yes** / **-y** — Skip confirmation, auto-approve (always pass this flag so the user sees the prompt in their terminal)
- **--cost-threshold** — Custom threshold in USD (default: 0.10)

Approximate per-image costs by resolution:
| Resolution | Per Image |
|---|---|
| 512 | $0.045 |
| 1K | $0.067 |
| 2K | $0.101 |
| 4K | $0.151 |

Additional costs: thinking tokens (~$0.006–$0.030), search grounding (~$0.001), input images (~$0.0001 each). Requests at **2K or above** will typically trigger the cost warning.

**Important:** Always pass `--yes` when calling from Claude so the user is not blocked by an interactive prompt they cannot see. Instead, inform the user of the estimated cost in your message before running the command. If the estimated cost would be high (2K+, 4K, high thinking), mention the approximate cost to the user first and ask if they want to proceed.

### Input Images (editing, up to 14)
- Use `--input-image` for each reference image (can repeat up to 14 times)
- Up to 10 images of objects with high-fidelity detail preservation
- Up to 4 images of characters for character consistency
- Reference images by position in the prompt (e.g., "the person from the first image")

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `GEMINI_API_KEY` environment variable
3. `GOOGLE_API_KEY` environment variable

If none is available, the script exits with an error message.

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.{ext}`

**Format:** `{timestamp}-{descriptive-name}.{ext}`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Extension: Match the `--output-format` (`.png`, `.webp`, `.jpg`)
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation

Examples:
- Prompt "A serene Japanese garden" -> `2025-12-17-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" (webp) -> `2025-12-17-15-30-12-sunset-mountains.webp`
- Prompt "current weather in NYC" (jpeg) -> `2025-12-17-16-45-33-nyc-weather.jpg`

## Image Editing

All editing uses the same `generate_content` API by passing input images alongside the text prompt. The model natively understands editing context.

### Single Image Edit
When the user wants to modify an existing image:
1. Use `--input-image` parameter with the path to the image
2. The prompt should contain editing instructions (e.g., "make the sky more dramatic", "change to cartoon style")

### Multi-Image Input (Compositing, Style Transfer & Character Consistency)
When the user wants to combine elements from multiple images:
1. Use `--input-image` multiple times (up to 14 images)
2. Reference images by order in the prompt (e.g., "apply the style of the second image to the first image")
3. For character consistency, provide multiple angles/poses of the same character

Common editing tasks: add/remove elements, change style, adjust colors, replace backgrounds, composite images, style transfer, character consistency across scenes, text overlay.

## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient. The model excels at understanding natural language descriptions.

**For editing:** Pass editing instructions in `--prompt` (e.g., "add a rainbow in the sky", "make it look like a watercolor painting")

**For multi-image:** Reference images by position (e.g., "combine the person from the first image with the background of the second image")

**For search-grounded:** Include what real-time data is needed (e.g., "visualize the current weather forecast for the next 5 days in San Francisco")

**Advanced text rendering:** This model excels at generating legible text in images. When text is needed, first describe the text content clearly in the prompt (e.g., "a magazine cover with the title 'GEMINI' in bold serif font").

Preserve user's creative intent in all cases.

## Thinking Mode

The model uses a built-in "Thinking" process that reasons through complex prompts. It generates interim "thought images" to refine composition before producing the final output.

- **minimal** (default): Fast, sufficient for most prompts
- **high**: Better quality for complex scenes, precise text, many elements

The thinking process:
- Improves complex multi-element compositions
- Helps with accurate text rendering
- Refines layout and spatial relationships
- Thinking tokens are billed regardless of output

## Output

- Saves image to current directory (or specified path if filename includes directory)
- File extension is automatically matched to `--output-format`
- If the model returns multiple images, files are numbered: `name-1.ext`, `name-2.ext`, etc.
- Script outputs the full path(s) to the generated image(s)
- Any text from the model (descriptions, explanations) is printed to stdout
- **Do not read the image back** - just inform the user of the saved path(s)

## Examples

**Generate new image:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "A photorealistic close-up portrait of an elderly Japanese ceramicist with deep wrinkles and a warm smile, inspecting a freshly glazed tea bowl in his rustic workshop. Soft golden hour light, 85mm portrait lens, bokeh background." --filename "2025-12-17-14-23-05-japanese-ceramicist.png" --resolution 2K --aspect-ratio 2:3
```

**Generate with text rendering (high thinking):**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "A glossy magazine cover with the large bold title 'NANO BANANA' in serif font. A person in a sleek minimal dress playfully holds the number 2. Issue number and 'Feb 2026' in the corner with a barcode. The magazine is on a shelf against an orange plastered wall." --filename "2025-12-17-14-25-30-magazine-cover.png" --resolution 4K --aspect-ratio 3:4 --thinking-level high
```

**Generate with Google Web Search grounding:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "Visualize the current weather forecast for the next 5 days in San Francisco as a clean, modern weather chart with outfit suggestions for each day" --filename "2025-12-17-14-26-00-sf-weather.png" --google-search --aspect-ratio 16:9 --resolution 2K
```

**Generate with Google Image Search grounding:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "A detailed painting of a resplendent quetzal bird resting on a flower, with a natural gradient background" --filename "2025-12-17-14-26-30-quetzal-painting.png" --image-search --aspect-ratio 3:2 --resolution 2K
```

**Edit existing image (style transfer):**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "Transform this photograph into the artistic style of Vincent van Gogh's Starry Night, with swirling impasto brushstrokes and a palette of deep blues and bright yellows" --filename "2025-12-17-14-27-00-starry-night-style.png" --input-image "city-photo.jpg" --resolution 2K
```

**Composite from multiple images:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "Place the person from the first image into the beach scene from the second image, maintaining their appearance and clothing" --filename "2025-12-17-14-29-00-beach-composite.png" --input-image "person.png" --input-image "beach.png" --resolution 2K
```

**Product mockup with logo:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "Put this logo on a high-end advertisement for a premium perfume. The logo is perfectly integrated into the bottle design." --filename "2025-12-17-14-30-00-perfume-ad.png" --input-image "logo.png" --resolution 4K --aspect-ratio 3:4
```

**Character consistency across scenes:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "An office group photo of these people, they are making funny faces" --filename "2025-12-17-14-31-00-office-group.png" --input-image "person1.png" --input-image "person2.png" --input-image "person3.png" --aspect-ratio 5:4 --resolution 2K
```

**Small thumbnail / icon:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "A kawaii-style sticker of a happy red panda wearing a tiny bamboo hat, munching on a green bamboo leaf. Bold clean outlines, cel-shading, vibrant colors. White background." --filename "2025-12-17-14-32-00-red-panda-sticker.png" --resolution 512 --response-modality image-only
```

**Ultra-wide cinematic banner:**
```bash
uv run ~/.claude/skills/gemini-nano-banana-2/scripts/generate_image.py --prompt "A cinematic sci-fi landscape with a massive ring-shaped space station orbiting a gas giant, dramatic volumetric lighting" --filename "2025-12-17-14-33-00-space-banner.png" --aspect-ratio 21:9 --resolution 4K --thinking-level high
```
