import argparse
import json
import os
import sys
from typing import Dict, Any, List, Tuple

from PIL import Image, ImageDraw, ImageFont

# --- Fixed Style Values ---
BOX_COLOR: Tuple[int, int, int] = (0, 255, 0)  # Green box/background
TEXT_COLOR: Tuple[int, int, int] = (0, 0, 0)  # Black text (for contrast on green bg)
BOX_THICKNESS: int = 2
FONT_SIZE: int = 15
# Try one common font first, then default
PRIMARY_FONT: str = "arial.ttf"  # Or "DejaVuSans.ttf" if preferred/available
TEXT_BG_PADDING: int = 2  # Pixels padding around text for the background


class ViaJsonExtractorError(Exception):
    """Custom exception for errors during VIA JSON processing."""
    pass


def load_font(font_size: int = FONT_SIZE) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Loads the primary font, falling back to PIL's default."""
    try:
        return ImageFont.truetype(PRIMARY_FONT, font_size)
    except IOError:
        print(f"Warning: Font '{PRIMARY_FONT}' not found. Using default PIL font. "
              "Text quality may be reduced.", file=sys.stderr)
        # Handle potential differences in load_default between Pillow versions
        try:
            # Newer Pillow versions might accept size directly
            return ImageFont.load_default(font_size)
        except TypeError:
            # Older versions might require font_size later or not support it well here
            try:
                return ImageFont.load_default()  # Load default, size applied later if needed
            except AttributeError:  # Even older PIL might have different naming
                print("Error: Could not load any default font.", file=sys.stderr)
                raise  # Re-raise if truly impossible


def load_json_data(json_file: str) -> Dict[str, Any]:
    """Loads JSON data from the given file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ViaJsonExtractorError(f"Error: JSON file not found at {json_file}")
    except json.JSONDecodeError as e:
        raise ViaJsonExtractorError(f"Error: Could not decode JSON file {json_file}. Invalid JSON: {e}")
    except Exception as e:
        raise ViaJsonExtractorError(f"An unexpected error occurred loading {json_file}: {e}")


def extract_score_zones(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extracts bounding box coordinates and labels from all images in the VIA JSON.
    Returns a flat list of score zone dictionaries: [{"label": "name", "bbox": [x1,y1,x2,y2]}, ...]
    """
    score_zones_list: List[Dict[str, Any]] = []
    metadata = data.get('_via_img_metadata')

    if not metadata:
        print("Warning: '_via_img_metadata' key not found in JSON. No zones extracted.", file=sys.stderr)
        return score_zones_list

    print(f"Processing {len(metadata)} image entries in VIA JSON...")

    for image_id, image_data in metadata.items():
        filename = image_data.get('filename', f'unknown_image_{image_id}')  # Use ID if filename missing
        regions = image_data.get('regions', [])

        if not regions:
            # print(f"Info: No regions found for image entry: {filename}", file=sys.stderr)
            continue  # Skip images with no regions defined

        processed_regions = 0
        for region in regions:
            shape_attributes = region.get('shape_attributes')
            region_attributes = region.get('region_attributes', {})

            if shape_attributes and shape_attributes.get('name') == 'rect':
                try:
                    x = int(shape_attributes.get('x', 0))
                    y = int(shape_attributes.get('y', 0))
                    width = int(shape_attributes.get('width', 0))
                    height = int(shape_attributes.get('height', 0))
                    # Use 'region_attributes'.'label' or 'name' if available, otherwise default
                    label = region_attributes.get('label', region_attributes.get('name', 'unknown'))

                    if width <= 0 or height <= 0:
                        print(
                            f"Warning: Skipping region in {filename} (label: {label}) with non-positive width/height.",
                            file=sys.stderr)
                        continue

                    score_zones_list.append({
                        "label": label,
                        "bbox": [x, y, x + width, y + height],  # x_min, y_min, x_max, y_max
                    })
                    processed_regions += 1
                except (TypeError, ValueError) as e:
                    print(f"Warning: Skipping region in {filename} due to invalid coordinate/dimension: {e}",
                          file=sys.stderr)
                    continue

    print(f"Extracted a total of {len(score_zones_list)} score zones from the JSON.")
    return score_zones_list


def write_json_output(score_zones_list: List[Dict[str, Any]], output_file: str) -> None:
    """Writes the list of score zones directly to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            output_dict = {
                "score_zones": score_zones_list
            }
            json.dump(output_dict, f, indent=2, ensure_ascii=False)
        print(f"Score Zones list successfully saved to {output_file}")
    except IOError as e:
        print(f"Error: Could not write JSON to {output_file}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred writing JSON output: {e}", file=sys.stderr)


# --- MODIFIED FUNCTION ---
def draw_bounding_boxes(
        image_path: str,
        score_zones: List[Dict[str, Any]],  # Takes the flat list directly
        output_path: str = "annotated_image.jpg"
) -> None:
    """Draws bounding boxes from the list onto the specified image using fixed styles."""
    if not score_zones:
        print("No score zones provided to draw. Skipping annotation.")
        return

    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            draw = ImageDraw.Draw(img)
            font = load_font(FONT_SIZE)  # Load font once

            print(f"Drawing {len(score_zones)} bounding boxes on {os.path.basename(image_path)}...")
            for zone in score_zones:
                label = zone.get("label", "unknown")
                bbox = zone.get("bbox")

                if not bbox or len(bbox) != 4:
                    print(f"Warning: Skipping invalid bbox data for label '{label}'.", file=sys.stderr)
                    continue

                try:
                    x_min, y_min, x_max, y_max = map(int, bbox)
                except (ValueError, TypeError):
                    print(f"Warning: Skipping bbox with non-integer coords for label '{label}'.", file=sys.stderr)
                    continue

                # Draw rectangle outline
                draw.rectangle([(x_min, y_min), (x_max, y_max)], outline=BOX_COLOR, width=BOX_THICKNESS)

                # --- Add label text with background ---
                text = str(label)
                # Position text slightly inside the top-left corner
                text_x = x_min + BOX_THICKNESS + 1
                text_y = y_min + BOX_THICKNESS + 1

                try:
                    # Calculate text bounding box using draw.textbbox for better accuracy
                    # Note: textbbox might require Pillow 8.0.0+
                    text_bbox = draw.textbbox((text_x, text_y), text, font=font)
                    # Define background rectangle with padding
                    bg_rect = [
                        (text_bbox[0] - TEXT_BG_PADDING, text_bbox[1] - TEXT_BG_PADDING),
                        (text_bbox[2] + TEXT_BG_PADDING, text_bbox[3] + TEXT_BG_PADDING)
                    ]
                    # Draw background rectangle (green)
                    draw.rectangle(bg_rect, fill=BOX_COLOR)
                except AttributeError:
                    # Fallback if textbbox is not available (older Pillow versions)
                    # This won't draw a background, just the text.
                    print("Warning: Cannot draw text background (draw.textbbox not available). "
                          "Consider upgrading Pillow.", file=sys.stderr)
                    pass  # Continue to draw text without background
                except Exception as e:
                    print(f"Warning: Error calculating text background for '{label}': {e}. Drawing text only.",
                          file=sys.stderr)
                    pass  # Try drawing text anyway

                # Draw text (black) on top of the background (or directly on image if bg failed)
                try:
                    draw.text((text_x, text_y), text, fill=TEXT_COLOR, font=font)
                except Exception as e:
                    print(f"Error drawing text for label '{label}': {e}", file=sys.stderr)
                # --- End text drawing ---

            img.save(output_path)
            print(f"Annotated image saved successfully as {output_path}")

    except FileNotFoundError:
        print(f"Error: Input image file not found at {image_path}", file=sys.stderr)
    except ImportError:
        # This check is primarily done in main, but good to have fallback here too
        print("Error: Pillow library not found. Please install it: pip install Pillow", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while drawing bounding boxes: {e}", file=sys.stderr)


def main():
    """Main function to parse arguments and coordinate actions."""
    parser = argparse.ArgumentParser(
        description="Extract all score zones (bounding boxes + labels) from a VIA JSON into a flat list, "
                    "save them, and optionally draw them ALL on a single specified image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("json_file", help="Path to the input VIA JSON file.")
    parser.add_argument("-i", "--image_path", default="captured_frame.jpg",
                        help="Optional: Path to a single image file to draw ALL extracted bounding boxes on.")
    parser.add_argument("-o", "--output_json", default="score_zones.json",
                        help="Path to save the extracted score zones list JSON data.")
    parser.add_argument("-od", "--output_draw", default="annotated_image.jpg",
                        help="Path to save the annotated image (used only if -i is specified).")
    args = parser.parse_args()

    pillow_available = False
    if args.image_path:  # Only check for Pillow if drawing is requested
        try:
            from PIL import Image, ImageDraw, ImageFont
            pillow_available = True
        except ImportError:
            print("Error: Pillow library is required for drawing annotations (-i specified), but it's not installed. "
                  "Please install it: pip install Pillow", file=sys.stderr)
            # Exit if drawing was explicitly requested but Pillow is missing
            sys.exit(1)

    try:
        # 1. Load VIA Data
        via_data = load_json_data(args.json_file)

        # 2. Extract ALL Score Zones into a flat list
        score_zones_list = extract_score_zones(via_data)

        if not score_zones_list:
            print(
                "No valid score zones (rectangular regions with labels) extracted from the JSON. Only saving empty list.")
            # Still write the empty list as requested by the output format
            write_json_output(score_zones_list, args.output_json)
            # If no zones, no point in trying to draw even if requested
            if args.image_path:
                print(f"Skipping drawing on {args.image_path} as no zones were extracted.")
            return  # Exit after saving empty list

        # 3. Write Extracted Score Zones List to JSON
        write_json_output(score_zones_list, args.output_json)

        # 4. Draw on Image (if specified an image path AND Pillow is available)
        if args.image_path and pillow_available:
            # Pass the flat list of all extracted zones to the drawing function
            draw_bounding_boxes(
                args.image_path,
                score_zones_list,  # Pass the list directly
                args.output_draw
            )
        elif args.image_path and not pillow_available:
            # This case should theoretically be caught earlier, but added for robustness
            print("Skipping annotation drawing because Pillow library is not installed.")
        elif not args.image_path:
            print("No image path provided via -i. Skipping drawing annotations.")

    except ViaJsonExtractorError as e:
        print(f"Processing Error: {e}", file=sys.stderr)
        sys.exit(1)  # Exit with error code on processing errors
    except Exception as e:
        print(f"An unexpected critical error occurred: {e}", file=sys.stderr)
        sys.exit(1)  # Exit with error code on critical errors


if __name__ == "__main__":
    main()
