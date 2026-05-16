import av
import cv2
import numpy as np
import threading
from queue import Queue
from tensorflow.keras.models import load_model
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path
from storage_unit import save_violence_event, get_camera_info_by_stream
from weapon_detector import detect_weapon
from severity_classifier import classify_violence
from alerts_manager import alerts_manager

SEQUENCE_LENGTH = 63
FRAME_QUEUE_SIZE = 10

def centroid(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return sum(xs)/len(xs), sum(ys)/len(ys)

def polar(cx, cy, x, y):
    r = np.sqrt((x-cx)**2 + (y-cy)**2)
    a = np.arctan2(y-cy, x-cx)
    return r, a

def read_stream(stream_url, frame_queue):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print(f"Failed to open stream: {stream_url}")
            return
        print(f"Stream opened : {stream_url}")
    except Exception as e:
        print(f"Failed to open stream: {stream_url} | {e}")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(frame)
    cap.release()

def process_frames(frame_queue, camera_id, location, tz_name, stream_url):
    model = load_model("best_acc_final.keras")
    sequence = []
    prev_label = "NON VIOLENCE"
    frame_id = 0

    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame_id += 1

            weapon_detected, weapon_type = detect_weapon(frame)

            label = "NON VIOLENCE"
            color = (0, 255, 0)

            if weapon_detected:
                level = classify_violence(1.0, weapon_type)
                label = f"WEAPON DETECTED ({weapon_type})"
                color = (0, 0, 255)
                print(f"--- [ALERT] Weapon Detected: {weapon_type} ---")

                if prev_label == "NON VIOLENCE":
                    save_violence_event(frame, camera_id, location, tz_name)
                    alerts_manager.send_alert(
                        camera_url=stream_url,
                        severity=level,
                        score=1.0,
                        weapon_type=weapon_type,
                        frame_id=frame_id
                    )

                prev_label = level

            else:
                prev_label = "NON VIOLENCE"

            cv2.putText(frame, label, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            h, w = frame.shape[:2]
            scale = 900 / w
            display = cv2.resize(frame, (900, int(h * scale)))
            cv2.imshow(f"Violence Detection - {camera_id}", display)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

def run_camera(stream_url):
    camera_id, location, tz_name = get_camera_info_by_stream(stream_url)
    frame_queue = Queue(maxsize=FRAME_QUEUE_SIZE)
    t_read = threading.Thread(target=read_stream, args=(stream_url, frame_queue), daemon=True)
    t_process = threading.Thread(target=process_frames, args=(frame_queue, camera_id, location, tz_name, stream_url), daemon=True)
    t_read.start()
    t_process.start()
    t_read.join()
    t_process.join()
