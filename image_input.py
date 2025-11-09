import os
import cv2
from ultralytics import YOLO
from pathlib import Path
from PIL import Image

def crop_detections(model_path, input_image_path, output_dir="crops"):
    # Load model
    model = YOLO(model_path)

    # Run inference
    results = model(input_image_path)[0]  # First image only (there is only one)

    # Load original image for cropping
    img = cv2.imread(input_image_path)

    # Alle Detections durchgehen
    for i, box in enumerate(results.boxes):
        cls_id = int(box.cls[0].item())           # Klassennummer
        class_name = results.names[cls_id]        # Klassenname (z. B. "blue", "yellow", ...)
        conf = float(box.conf[0].item())          # Konfidenz (optional)
        xyxy = box.xyxy[0].cpu().numpy().astype(int)  # Bounding Box (x1, y1, x2, y2)

        x1, y1, x2, y2 = xyxy
        crop = img[y1:y2, x1:x2]

        # Prepare output directory
        class_dir = Path(output_dir) / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{Path(input_image_path).stem}_{i}_{class_name}.jpg"
        crop_path = class_dir / filename

        # Crop and save
        cv2.imwrite(str(crop_path), crop)

        print(f"Gespeichert: {crop_path}")

# # Beispielaufruf
# crop_detections(
#     model_path="Roboflow/best.pt",
#     input_image_path="Roboflow/tantrix-extreme.jpg",
#     output_dir="crops"
# )
