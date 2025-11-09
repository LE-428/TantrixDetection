import cv2
import numpy as np
from sklearn.cluster import KMeans

# Reference colors in RGB-format
REFERENCE_COLORS = {
    1: np.array([12, 108, 217]),   # Blue (#0c6cd9)
    2: np.array([255, 232, 0]),    # Yellow (#ffe800)
    3: np.array([215, 31, 43]),    # Red (#d71f2b)
    4: np.array([0, 161, 69]),     # Green (#00a145)
}

COLOR_NAMES = {
    1: "Blau",
    2: "Gelb",
    3: "Rot",
    4: "Grün",
}

def is_dark(color, threshold=60):
    """Check if the color is classified as black"""
    return np.all(color < threshold)

def cluster_colors(pixels, k=4):
    """Split the pixel values into k clusters"""
    kmeans = KMeans(n_clusters=k, n_init='auto', random_state=0).fit(pixels)
    centers = np.round(kmeans.cluster_centers_).astype(int)
    return centers, kmeans.labels_

def get_middle_region(image, percent=0.6):
    """Extract the middle region of the image to eliminate the background color"""
    h, w = image.shape[:2]
    dh = int(h * percent / 2)
    dw = int(w * percent / 2)
    return image[h//2 - dh:h//2 + dh, w//2 - dw:w//2 + dw]

def split_into_grid(image, rows=3, cols=3):
    """Split the image into a 3x3 grid to analyze the regions further"""
    h, w = image.shape[:2]
    grid = []
    for i in range(rows):
        for j in range(cols):
            y0, y1 = i * h // rows, (i + 1) * h // rows
            x0, x1 = j * w // cols, (j + 1) * w // cols
            grid.append(image[y0:y1, x0:x1])
    return grid

def find_best_reference_matches(candidate_colors, reference_colors, top_n=3):
    """Find the 3 colors in the image that match best with the 4 pre-defined Tantrix tile colors"""
    matches = []
    for c in candidate_colors:
        min_dist = float('inf')
        best_code = None
        for code, ref in reference_colors.items():
            dist = np.linalg.norm(c - ref)
            if dist < min_dist:
                min_dist = dist
                best_code = code
        matches.append((tuple(c), best_code, min_dist))

    sorted_matches = []
    used_codes = set()
    for color, code, dist in sorted(matches, key=lambda x: x[2]):
        if code not in used_codes:
            sorted_matches.append((np.array(color), code))
            used_codes.add(code)
        if len(sorted_matches) == top_n:
            break
    return sorted_matches

def compare_colors(base_colors, target_colors, threshold=30):
    matches = []
    for tc in target_colors:
        if is_dark(tc):
            continue
        for bc in base_colors:
            dist = np.linalg.norm(bc - tc)
            if dist < threshold:
                matches.append(bc)
                break
    return matches

def analyze_image(image_path):
    """Consider the center of the cropped image and extract dominant colors. 
    Compute distances of these colors in RGB space to the four predefined Tantrix colors.
    Select the three image colors that are closest to the reference set and use them further.
    Define a color map that links the occurring image color tones to the Tantrix colors.
    Then examine the outer 8 image segments and compare their colors with the three prominent center colors.
    From that comparison generate a sequence of colors."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Bild konnte nicht geladen werden: {image_path}")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Analyze the center and compare the dominant colors with the 4 Tantrix colors
    middle = get_middle_region(image_rgb, 0.65)
    mid_pixels = middle.reshape(-1, 3)
    mid_centers, _ = cluster_colors(mid_pixels, k=6)
    # Filter out black (background on the tiles)
    candidate_colors = [c for c in mid_centers if not is_dark(c)]

    # Compare the found colors
    best_matches = find_best_reference_matches(candidate_colors, REFERENCE_COLORS, top_n=3)
    allowed_reference_codes = [code for _, code in best_matches]
    color_map = {tuple(c.tolist()): code for c, code in best_matches}

    segments = split_into_grid(image_rgb, 3, 3)
    # positions = [0, 1, 2, 5, 8, 7, 6, 3]  # clockwise
    positions = [0, 3, 6, 7, 8, 5, 2, 1]  # counter-clockwise

    result = []
    for idx in positions:
        segment = segments[idx]
        seg_pixels = segment.reshape(-1, 3)
        # Up to 4 colors per segment: background, black, two Tantrix colors
        seg_centers, _ = cluster_colors(seg_pixels, k=4)
        # Compare the colors found in the segment with the center colors and link them
        matched_colors = compare_colors([c for c, _ in best_matches], seg_centers, threshold=35)

        labels = []
        for c in matched_colors:
            c_tuple = tuple(np.round(c).astype(int).tolist())
            # Append the linked color to the color sequence
            if c_tuple in color_map:
                labels.append(color_map[c_tuple])
            else:
                min_dist = float('inf')
                best_code = None
                for ref_c, code in best_matches:
                    dist = np.linalg.norm(c - ref_c)
                    if dist < min_dist:
                        min_dist = dist
                        best_code = code
                if best_code:
                    labels.append(best_code)

        if len(labels) == 1:
            result.append(labels[0])
        elif len(labels) > 1:
            result.append(labels)
        else:
            result.append(0)

    return result, best_matches

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="Pfad zum Bild")
    args = parser.parse_args()

    result, matches = analyze_image(args.image_path)

    print("Verwendete Referenzfarben (Innenbereich):")
    for _, code in matches:
        print(f"- {COLOR_NAMES[code]}")

    print("\nCodiertes Farbmuster in festgelegter Reihenfolge:")
    print(result)

if __name__ == "__main__":
    main()
