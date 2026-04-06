from ultralytics import YOLO

yolo_model = YOLO("best.pt")

def detect_weapon(frame):

    results = yolo_model(frame, verbose=False)

    weapon_detected = False
    weapon_type = "none"

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            name = yolo_model.names[cls]

            if name in ["gun", "pistol", "rifle"]:
                weapon_detected = True
                weapon_type = "gun"

            elif name == "knife":
                weapon_detected = True
                weapon_type = "knife"

    return weapon_detected, weapon_type