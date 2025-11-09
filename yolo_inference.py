from ultralytics import YOLO

model = YOLO("Roboflow/best.pt")
results = model("Roboflow/tantrix-extreme.jpg", save=True)
