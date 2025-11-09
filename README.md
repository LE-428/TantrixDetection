# Tantrix Tile Detection

This project detects Tantrix tiles from an image using YOLOv5, crops the tiles, and classifies their types using clustering and pattern matching. The indices corresponding to the image below are returned

## Tantrix Tiles

**The 56 Tantrix tiles, grouped into 4 sets of 3 colors, with their corresponding numbers:**

![Tantrix tiles enumeration](images/tiles.png)

## Folder Structure

```
.
├── .venv/              # Your Python virtual environment
├── crops/              # Output directory for cropped tile images
├── Roboflow/           # Folder containing the YOLOv5 model weights (best.pt)
├── runs/               # YOLO output (optional)
├── image2tiles.py      # Main script
├── image_input.py      # Contains YOLO inference and cropping code
├── kmeans_module.py    # KMeans color clustering and analysis with OpenCV
├── match.py            # Matching detected color patterns to known variants
├── yolo_inference.py   # Try out YOLO model inference in this file
├── requirements.txt    # Required packages
└── README.md           # This file
```

## Installation

1. **Clone the repository** (if not already done)

2. **Set up a virtual environment** (optional but recommended)

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/macOS
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

## Usage

```bash
python image2tiles.py <image_path> <output_path>
```

Example:

```bash
python image2tiles.py Roboflow/tantrix-extreme.jpg crops
```

This will:

1. Use YOLOv5 to detect and crop individual tiles from the input image.
2. Save the cropped tiles in the `crops/` directory (or the directory you specify).
3. Analyze each cropped tile and print its recognized variant and tile number.

Access the help menu:

```bash
python image2tiles.py -h
```

## Requirements

See `requirements.txt` for Python dependencies. Key packages include:

* `ultralytics`
* `opencv-python`
* `numpy`
* `scikit-learn`

## Notes

* The YOLO model weights are placed at: `Roboflow/best.pt`, the dataset is found under `Roboflow/Tantrix.v5i.yolov8.zip`
* Tile classification is based on KMeans color clustering and a fixed mapping of expected color sequences.

## License

MIT License
