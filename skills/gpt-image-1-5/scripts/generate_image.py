#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.50.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate and edit images using OpenAI's GPT Image 1.5 model.

Usage:
    # Generate new image
    uv run generate_image.py --prompt "description" --filename "output.png" [options]

    # Generate multiple variations
    uv run generate_image.py --prompt "description" --filename "output.png" --n 4 [options]

    # Edit image (no mask, full image edit)
    uv run generate_image.py --prompt "edit instructions" --filename "output.png" --input-image "input.png" [options]

    # Edit image with mask (precise inpainting)
    uv run generate_image.py --prompt "what to add" --filename "output.png" --input-image "input.png" --mask "mask.png" [options]

    # Edit with multiple reference images (compositing/style transfer)
    uv run generate_image.py --prompt "combine these" --filename "output.png" --input-image "a.png" --input-image "b.png" [options]
"""

import argparse
import base64
import os
import sys
from io import BytesIO
from pathlib import Path


def get_api_key(provided_key: str | None) -> str | None:
    """Get API key from argument first, then environment."""
    if provided_key:
        return provided_key
    return os.environ.get("OPENAI_API_KEY")


def create_full_transparent_mask(image_path: str) -> bytes:
    """Create a fully transparent PNG mask matching the input image dimensions."""
    from PIL import Image

    with Image.open(image_path) as img:
        width, height = img.size

    mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    buf = BytesIO()
    mask.save(buf, format="PNG")
    return buf.getvalue()


def generate_image(
    client,
    prompt: str,
    quality: str = "medium",
    size: str = "auto",
    background: str = "auto",
    output_format: str = "png",
    output_compression: int | None = None,
    n: int = 1,
) -> list[bytes]:
    """Generate image(s) using the Images API with gpt-image-1.5."""

    kwargs = {
        "model": "gpt-image-1.5",
        "prompt": prompt,
        "quality": quality,
        "n": n,
        "output_format": output_format,
    }

    if size != "auto":
        kwargs["size"] = size

    if background != "auto":
        kwargs["background"] = background

    if output_compression is not None and output_format in ("webp", "jpeg"):
        kwargs["output_compression"] = output_compression

    response = client.images.generate(**kwargs)

    results = []
    for item in response.data:
        results.append(base64.b64decode(item.b64_json))
    return results


def edit_image(
    client,
    prompt: str,
    image_paths: list[str],
    mask_path: str | None,
    size: str = "auto",
    quality: str = "medium",
    input_fidelity: str | None = None,
    output_format: str = "png",
    output_compression: int | None = None,
    n: int = 1,
) -> list[bytes]:
    """Edit image(s) using the Images API with mask support and multi-image input."""

    # Build the image input list
    image_files = [open(p, "rb") for p in image_paths]

    # If single image, pass directly (API expects file or list)
    image_input = image_files if len(image_files) > 1 else image_files[0]

    # If no mask provided, create a fully transparent one (edit entire image)
    if mask_path:
        mask_file = open(mask_path, "rb")
    else:
        mask_bytes = create_full_transparent_mask(image_paths[0])
        mask_file = BytesIO(mask_bytes)
        mask_file.name = "mask.png"

    try:
        kwargs = {
            "model": "gpt-image-1.5",
            "image": image_input,
            "mask": mask_file,
            "prompt": prompt,
            "size": size if size != "auto" else "1024x1024",
            "quality": quality,
            "n": n,
            "output_format": output_format,
        }

        if input_fidelity:
            kwargs["input_fidelity"] = input_fidelity

        if output_compression is not None and output_format in ("webp", "jpeg"):
            kwargs["output_compression"] = output_compression

        result = client.images.edit(**kwargs)

        results = []
        for item in result.data:
            results.append(base64.b64decode(item.b64_json))
        return results
    finally:
        for f in image_files:
            f.close()
        if mask_path:
            mask_file.close()


def save_image(image_bytes: bytes, output_path: Path, output_format: str, background: str):
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

    if background == "transparent" or output_format == "png":
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        image.save(str(output_path), fmt)
    else:
        if image.mode == "RGBA":
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[3])
            rgb_image.save(str(output_path), fmt)
        elif image.mode == "RGB":
            image.save(str(output_path), fmt)
        else:
            image.convert("RGB").save(str(output_path), fmt)


def main():
    parser = argparse.ArgumentParser(
        description="Generate and edit images using OpenAI GPT Image 1.5"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Image description or editing instructions"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., output.png). For n>1, files are numbered: output-1.png, output-2.png"
    )
    parser.add_argument(
        "--input-image", "-i",
        action="append",
        help="Input image path(s) for editing. Can be specified multiple times for multi-image compositing"
    )
    parser.add_argument(
        "--mask", "-m",
        help="Mask image path for precise inpainting (PNG with transparent areas to edit)"
    )
    parser.add_argument(
        "--quality", "-q",
        choices=["low", "medium", "high"],
        default="medium",
        help="Output quality: low, medium (default), or high"
    )
    parser.add_argument(
        "--size", "-s",
        choices=["1024x1024", "1024x1536", "1536x1024", "auto"],
        default="auto",
        help="Output size (default: auto)"
    )
    parser.add_argument(
        "--background", "-b",
        choices=["transparent", "opaque", "auto"],
        default="auto",
        help="Background type for generation (default: auto)"
    )
    parser.add_argument(
        "--output-format",
        choices=["png", "webp", "jpeg"],
        default="png",
        help="Output image format (default: png)"
    )
    parser.add_argument(
        "--output-compression",
        type=int,
        choices=range(0, 101),
        metavar="0-100",
        help="Compression level for webp/jpeg output (0-100, default: 100)"
    )
    parser.add_argument(
        "--n",
        type=int,
        choices=range(1, 5),
        metavar="1-4",
        default=1,
        help="Number of images to generate (1-4, default: 1)"
    )
    parser.add_argument(
        "--input-fidelity",
        choices=["high", "low"],
        help="Input fidelity for editing (high preserves identity/details, default: model decides)"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="OpenAI API key (overrides OPENAI_API_KEY env var)"
    )

    args = parser.parse_args()

    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Please either:", file=sys.stderr)
        print("  1. Provide --api-key argument", file=sys.stderr)
        print("  2. Set OPENAI_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    # Warn if compression is set but format doesn't support it
    if args.output_compression is not None and args.output_format == "png":
        print("Warning: --output-compression is ignored for PNG format. Use --output-format webp or jpeg.", file=sys.stderr)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine file extension from output_format
    ext_map = {"png": ".png", "webp": ".webp", "jpeg": ".jpg"}
    desired_ext = ext_map[args.output_format]

    # Determine operation mode
    if args.input_image:
        # Validate all input images exist
        for img_path in args.input_image:
            if not Path(img_path).exists():
                print(f"Error: Input image not found: {img_path}", file=sys.stderr)
                sys.exit(1)

        if args.mask and not Path(args.mask).exists():
            print(f"Error: Mask image not found: {args.mask}", file=sys.stderr)
            sys.exit(1)

        mode_desc = "with mask (inpainting)" if args.mask else "full image edit"
        print(f"Editing image ({mode_desc}) using Images API...")
        print(f"  Input(s): {', '.join(args.input_image)}")
        if args.mask:
            print(f"  Mask: {args.mask}")
        print(f"  Quality: {args.quality}")
        print(f"  Size: {args.size}")
        print(f"  Format: {args.output_format}")
        if args.input_fidelity:
            print(f"  Input fidelity: {args.input_fidelity}")
        if args.n > 1:
            print(f"  Variations: {args.n}")

        try:
            image_bytes_list = edit_image(
                client,
                args.prompt,
                args.input_image,
                args.mask,
                args.size,
                args.quality,
                args.input_fidelity,
                args.output_format,
                args.output_compression,
                args.n,
            )
        except Exception as e:
            print(f"Error editing image: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Generation mode
        print(f"Generating image using Images API...")
        print(f"  Quality: {args.quality}")
        print(f"  Size: {args.size}")
        print(f"  Background: {args.background}")
        print(f"  Format: {args.output_format}")
        if args.n > 1:
            print(f"  Variations: {args.n}")

        try:
            image_bytes_list = generate_image(
                client,
                args.prompt,
                args.quality,
                args.size,
                args.background,
                args.output_format,
                args.output_compression,
                args.n,
            )
        except Exception as e:
            print(f"Error generating image: {e}", file=sys.stderr)
            sys.exit(1)

    # Save image(s)
    if len(image_bytes_list) == 1:
        # Single image — use filename as-is, but fix extension
        final_path = output_path.with_suffix(desired_ext)
        save_image(image_bytes_list[0], final_path, args.output_format, args.background)
        print(f"\nImage saved: {final_path.resolve()}")
    else:
        # Multiple images — number them
        stem = output_path.stem
        parent = output_path.parent
        saved = []
        for idx, img_bytes in enumerate(image_bytes_list, 1):
            numbered_path = parent / f"{stem}-{idx}{desired_ext}"
            save_image(img_bytes, numbered_path, args.output_format, args.background)
            saved.append(str(numbered_path.resolve()))
        print(f"\n{len(saved)} images saved:")
        for s in saved:
            print(f"  {s}")


if __name__ == "__main__":
    main()
