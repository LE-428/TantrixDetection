import argparse
import os
import shutil
from pathlib import Path

from image_input import crop_detections
from kmeans_module import analyze_image
from match import preprocess_input, check_variants, get_tile_number


def process_crops(image_dir, base_crop_dir="crops", remove_crop_dir=False):
    # Process only images starting with the original name of the image
    original_basename = Path(image_dir).stem

    # List of all recognised tile numbers
    recognized_tiles = []

    # Number of un(recognised) tiles
    num_recognised = 0
    num_unrecognised = 0


    # Foldernames matching the patterns
    pattern_map = {
        "ccc": "abc",
        "clc": "abcb",
        "clh": "abacbc",
        "cxx": "abcbc"
    }

    for folder_name, pattern in pattern_map.items():
        folder_path = Path(base_crop_dir) / folder_name
        if not folder_path.exists():
            print(f"Directory {folder_path} not found, skipping.")
            continue

        for image_file in folder_path.glob("*.jpg"):
            if not image_file.stem.startswith(original_basename):
                continue  # File does not belong to original image
            print(f"Processing: {image_file}")
            try:
                result, matches = analyze_image(str(image_file))
                variants = preprocess_input(result)
                matched_variant = check_variants(variants, input_pattern=pattern)
                tile_number = get_tile_number(matched_variant)
                print(f"Detected pattern: {matched_variant} → Tile number: {tile_number}")

                 # Extend file name with "_tile_<number>"
                try:
                    new_stem = f"{image_file.stem}_tile_{tile_number}"
                    new_path = image_file.with_name(new_stem + image_file.suffix)
                    image_file.rename(new_path)
                    # If successful, update the file path here for possible further processing
                    image_file = new_path
                except Exception as rename_err:
                    print(f"Warning: Could not rename file: {rename_err}")

                # Append tile number to list
                if tile_number is not None:
                    num_recognised += 1
                    recognized_tiles.append(tile_number)
                else:
                    num_unrecognised += 1

            except Exception as e:
                print(f"Error processing {image_file}: {e}")

    # Print all recognised tile numbers
    print(f"\nUnrecognized tiles: {num_unrecognised}, Recognition ratio: {num_recognised / (num_recognised + num_unrecognised):.2f}")
    print("\nRecognised Tile Numbers:")
    print(recognized_tiles)

    if remove_crop_dir:
        print(f"Removing crop directory: {base_crop_dir}")
        shutil.rmtree(base_crop_dir, ignore_errors=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="Pfad zum Bild, verwende z.B. 'Roboflow/tantrix-extreme.jpg'")
    parser.add_argument("--output_path", "-o", help="Pfad zu den ausgeschnittenen Bildern (default: crops\)", default="crops")
    parser.add_argument("--remove_dir", help="Entferne den Ordner mit den ausgeschnittenen Bildern am Ende", default=False)
    args = parser.parse_args()

    # Step 1: Analyse the image and create the crops
    crop_detections(
        model_path="Roboflow/best.pt",
        input_image_path=args.image_path,
        output_dir=args.output_path
    )

    # Step 2: Process the cropped images
    process_crops(image_dir=args.image_path, base_crop_dir=args.output_path, remove_crop_dir=args.remove_dir)


if __name__ == "__main__":
    main()
