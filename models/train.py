from ultralytics import YOLO

model = YOLO('yolov8n.pt')

model.train(
    data='data.yaml',
    epochs=50,
    imgsz=416,
    batch=8,
    project='weights',
    name='weapon_v1'
)

print('Training done. Weights saved to weights/weapon_v1/best.pt')
