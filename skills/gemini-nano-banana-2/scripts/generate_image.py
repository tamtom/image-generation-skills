#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate and edit images using Google's Gemini Nano Banana 2 (gemini-3.1-flash-image-preview).

Usage:
    # Generate new image
    uv run generate_image.py --prompt "description" --filename "output.png" [options]

    # Edit image (provide input image + text prompt)
    uv run generate_image.py --prompt "edit instructions" --filename "output.png" --input-image "input.png" [options]

    # Multi-image input (compositing/style transfer, up to 14 reference images)
    uv run generate_image.py --prompt "combine these" --filename "output.png" --input-image "a.png" --input-image "b.png" [options]

    # With Google Search grounding (real-time data)
    uv run generate_image.py --prompt "current weather in Tokyo as infographic" --filename "output.png" --google-search [options]

    # With Google Image Search grounding
    uv run generate_image.py --prompt "a painting of a resplendent quetzal bird" --filename "output.png" --image-search [options]
"""

import argparse
import os
import sys
from io import BytesIO
from pathlib import Path


# ── Cost estimation constants (USD) ──────────────────────────────────────────
# Per-image output charges by resolution
# Source: https://ai.google.dev/gemini-api/docs/pricing#gemini-3.1-flash-image-preview
IMAGE_COST = {"512": 0.045, "1K": 0.067, "2K": 0.101, "4K": 0.151}

# Token pricing per 1M tokens
INPUT_TOKEN_PRICE = 0.50       # text + image input
THINKING_TOKEN_PRICE = 3.00    # output text + thinking tokens

# Approximate token counts for cost estimation
INPUT_TOKENS_PER_IMAGE = 258   # ~258 tokens per input image
THINKING_TOKENS = {"minimal": 2000, "high": 10000}  # estimated thinking tokens
SEARCH_OVERHEAD_TOKENS = 500   # extra input tokens for search grounding

DEFAULT_COST_THRESHOLD = 0.10  # USD — warn above this


def estimate_cost(
    resolution: str,
    thinking_level: str,
    google_search: bool,
    image_search: bool,
    num_input_images: int,
    prompt_length: int,
) -> tuple[float, list[str]]:
    """Estimate request cost. Returns (total_usd, breakdown_lines)."""
    breakdown = []

    # 1) Per-image output charge (the main cost)
    img_cost = IMAGE_COST[resolution]
    breakdown.append(f"  Image output ({resolution}):  ${img_cost:.4f}")

    # 2) Input tokens (prompt text + input images)
    input_tokens = (prompt_length // 4) + (num_input_images * INPUT_TOKENS_PER_IMAGE)
    input_cost = input_tokens * INPUT_TOKEN_PRICE / 1_000_000
    if num_input_images:
        breakdown.append(f"  Input tokens (~{input_tokens} tok, {num_input_images} images): ${input_cost:.4f}")

    # 3) Thinking / output text tokens
    think_tokens = THINKING_TOKENS[thinking_level]
    think_cost = think_tokens * THINKING_TOKEN_PRICE / 1_000_000
    breakdown.append(f"  Thinking ({thinking_level}, ~{think_tokens} tok): ${think_cost:.4f}")

    # 4) Search grounding overhead
    search_cost = 0.0
    if google_search or image_search:
        search_tokens = SEARCH_OVERHEAD_TOKENS
        search_cost = search_tokens * INPUT_TOKEN_PRICE / 1_000_000
        label = "web+image" if (google_search and image_search) else ("image" if image_search else "web")
        breakdown.append(f"  Search grounding ({label}): ${search_cost:.4f}")

    total = img_cost + input_cost + think_cost + search_cost
    return total, breakdown


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def generate_image(
    client,
    prompt: str,
    input_images: list[str] | None = None,
    aspect_ratio: str = "1:1",
    resolution: str = "1K",
    response_modality: str = "text-and-image",
    google_search: bool = False,
    image_search: bool = False,
    thinking_level: str = "minimal",
) -> tuple[list[bytes], list[str]]:
    """Generate or edit image(s) using Gemini Nano Banana 2.

    Returns a tuple of (image_bytes_list, text_parts_list).
    """
    from google.genai import types
    from PIL import Image

    # Build contents — text prompt first, then images (matches API convention)
    contents = [prompt]

    # Add input images if provided (editing/compositing mode)
    if input_images:
        for img_path in input_images:
            contents.append(Image.open(img_path))

    # Build response modalities
    if response_modality == "image-only":
        modalities = ["IMAGE"]
    else:
        modalities = ["TEXT", "IMAGE"]

    # Build image config
    image_config = types.ImageConfig(
        aspect_ratio=aspect_ratio,
        image_size=resolution,
    )

    # Build tools list
    tools = []
    if image_search:
        # Image Search requires the typed search_types form
        search_types_kwargs = {"image_search": types.ImageSearch()}
        if google_search:
            search_types_kwargs["web_search"] = types.WebSearch()
        tools.append(
            types.Tool(
                google_search=types.GoogleSearch(
                    search_types=types.SearchTypes(**search_types_kwargs)
                )
            )
        )
    elif google_search:
        # Web-only search uses the simple dict form (per docs)
        tools.append({"google_search": {}})

    # Build thinking config
    thinking_config = types.ThinkingConfig(
        thinking_level=thinking_level.capitalize(),
        include_thoughts=False,
    )

    # Build config
    config_kwargs = {
        "response_modalities": modalities,
        "image_config": image_config,
        "thinking_config": thinking_config,
    }
    if tools:
        config_kwargs["tools"] = tools

    config = types.GenerateContentConfig(**config_kwargs)

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=config,
    )

    images = []
    texts = []

    for part in response.parts:
        if part.thought:
            # Skip thinking parts (interim reasoning images/text)
            continue
        if part.text is not None:
            texts.append(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            buf = BytesIO()
            image.save(buf, format="PNG")
            images.append(buf.getvalue())

    return images, texts


def save_image(image_bytes: bytes, output_path: Path, output_format: str):
    """Save image bytes to the specified path with correct format handling."""
    from PIL import Image

    image = Image.open(BytesIO(image_bytes))

    fmt = output_format.upper()
    if fmt == "JPEG":
        fmt = "JPEG"
    elif fmt == "WEBP":
        fmt = "WEBP"
    else:
        fmt = "PNG"

    if fmt in ("JPEG",):
        # JPEG doesn't support alpha
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            rgb_image.save(str(output_path), fmt)
        elif image.mode == "RGB":
            image.save(str(output_path), fmt)
        else:
            image.convert("RGB").save(str(output_path), fmt)
    else:
        # PNG and WEBP support alpha
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        image.save(str(output_path), fmt)


def main():
    parser = argparse.ArgumentParser(
        description="Generate and edit images using Gemini Nano Banana 2 (gemini-3.1-flash-image-preview)"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description or editing instructions"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., output.png)"
    )
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        help="Input image path(s) for editing. Can be specified multiple times (up to 14 reference images: 10 objects + 4 characters)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9"],
        default="1:1",
        help="Output aspect ratio (default: 1:1)"
    )
    parser.add_argument(
        "--resolution", "-r",
        choices=["512", "1K", "2K", "4K"],
        default="1K",
        help="Output resolution: 512, 1K (default), 2K, or 4K"
    )
    parser.add_argument(
        "--output-format",
        choices=["png", "webp", "jpeg"],
        default="png",
        help="Output image format (default: png)"
    )
    parser.add_argument(
        "--response-modality",
        choices=["text-and-image", "image-only"],
        default="text-and-image",
        help="Response type: text-and-image (default) or image-only"
    )
    parser.add_argument(
        "--google-search",
        action="store_true",
        help="Enable Google Web Search grounding for real-time data in generated images"
    )
    parser.add_argument(
        "--image-search",
        action="store_true",
        help="Enable Google Image Search grounding for visual reference from web images"
    )
    parser.add_argument(
        "--thinking-level",
        choices=["minimal", "high"],
        default="minimal",
        help="Thinking level: minimal (default, faster) or high (better quality for complex prompts)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="Gemini API key (overrides GEMINI_API_KEY / GOOGLE_API_KEY env var)"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip cost confirmation prompt (auto-approve)"
    )
    parser.add_argument(
        "--cost-threshold",
        type=float,
        default=DEFAULT_COST_THRESHOLD,
        help=f"Cost threshold in USD that triggers confirmation (default: ${DEFAULT_COST_THRESHOLD:.2f})"
    )

    args = parser.parse_args()

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set GEMINI_API_KEY environment variable", file=sys.stderr)
        print("  3. Set GOOGLE_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Validate input images exist
    if args.input_image:
        for img_path in args.input_image:
            if not Path(img_path).exists():
                print(f"Error: Input image not found: {img_path}", file=sys.stderr)
                sys.exit(1)
        if len(args.input_image) > 14:
            print("Error: Maximum 14 reference images supported.", file=sys.stderr)
            sys.exit(1)

    from google import genai

    client = genai.Client(api_key=api_key)

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine file extension from output_format
    ext_map = {"png": ".png", "webp": ".webp", "jpeg": ".jpg"}
    desired_ext = ext_map[args.output_format]

    # Log operation details
    if args.input_image:
        print(f"Editing image using Gemini Nano Banana 2...")
        print(f"  Input(s): {', '.join(args.input_image)}")
    else:
        print(f"Generating image using Gemini Nano Banana 2...")

    print(f"  Aspect ratio: {args.aspect_ratio}")
    print(f"  Resolution: {args.resolution}")
    print(f"  Format: {args.output_format}")
    print(f"  Response modality: {args.response_modality}")
    print(f"  Thinking level: {args.thinking_level}")
    if args.google_search:
        print(f"  Google Web Search grounding: enabled")
    if args.image_search:
        print(f"  Google Image Search grounding: enabled")

    # Cost estimation and confirmation
    num_input = len(args.input_image) if args.input_image else 0
    estimated_cost, cost_breakdown = estimate_cost(
        args.resolution,
        args.thinking_level,
        args.google_search,
        args.image_search,
        num_input,
        len(args.prompt),
    )
    print(f"\n  Estimated cost: ${estimated_cost:.4f}")

    if estimated_cost >= args.cost_threshold:
        print(f"\n⚠ Cost warning: estimated ${estimated_cost:.4f} exceeds ${args.cost_threshold:.2f} threshold")
        for line in cost_breakdown:
            print(line)
        if not args.yes:
            try:
                answer = input(f"\nProceed? [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                answer = ""
            if answer not in ("y", "yes"):
                print("Aborted.")
                sys.exit(0)
        else:
            print("  (auto-approved via --yes)")

    try:
        image_bytes_list, text_parts = generate_image(
            client,
            args.prompt,
            args.input_image,
            args.aspect_ratio,
            args.resolution,
            args.response_modality,
            args.google_search,
            args.image_search,
            args.thinking_level,
        )
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        sys.exit(1)

    if not image_bytes_list:
        print("Error: No images were returned by the model.", file=sys.stderr)
        if text_parts:
            print("Model response text:", file=sys.stderr)
            for text in text_parts:
                print(f"  {text}", file=sys.stderr)
        sys.exit(1)

    # Print any text from the model
    for text in text_parts:
        print(f"\nModel: {text}")

    # Save image(s)
    if len(image_bytes_list) == 1:
        final_path = output_path.with_suffix(desired_ext)
        save_image(image_bytes_list[0], final_path, args.output_format)
        print(f"\nImage saved: {final_path.resolve()}")
    else:
        stem = output_path.stem
        parent = output_path.parent
        saved = []
        for idx, img_bytes in enumerate(image_bytes_list, 1):
            numbered_path = parent / f"{stem}-{idx}{desired_ext}"
            save_image(img_bytes, numbered_path, args.output_format)
            saved.append(str(numbered_path.resolve()))
        print(f"\n{len(saved)} images saved:")
        for s in saved:
            print(f"  {s}")


if __name__ == "__main__":
    main()
