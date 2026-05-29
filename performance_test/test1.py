import os
import cv2
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path


SEQUENCE_LENGTH = 63
FEATURE_SIZE = 72

# -----------------------------
# Model setup
# -----------------------------
model = load_model("best_acc_final.keras")

pose = TfPoseEstimator(
    get_graph_path("mobilenet_thin_432x368"),
    target_size=(432, 368)
)

# -----------------------------
# Helpers
# -----------------------------
def centroid(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return sum(xs) / len(xs), sum(ys) / len(ys)

def extract_features(points):
    cx, cy = centroid(points)

    features = []

    for x, y in points:
        r = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
        a = np.arctan2(y - cy, x - cx)
        features.extend([r, a])

    features = np.array(features)

    if len(features) < FEATURE_SIZE:
        features = np.pad(features, (0, FEATURE_SIZE - len(features)))
    else:
        features = features[:FEATURE_SIZE]

    return features

# -----------------------------
# Predict one video
# -----------------------------
def predict_video(video_path):

    cap = cv2.VideoCapture(video_path)
    sequence = deque(maxlen=SEQUENCE_LENGTH)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        humans = pose.inference(frame)

        best_person = None
        max_points = 0

        for human in humans:
            pts = []
            for i in range(18):
                if i in human.body_parts:
                    pts.append(i)

            if len(pts) > max_points:
                max_points = len(pts)
                best_person = human

        if best_person is None:
            continue

        person_points = []
        for i in range(18):
            if i in best_person.body_parts:
                part = best_person.body_parts[i]
                x = int(part.x * frame.shape[1])
                y = int(part.y * frame.shape[0])
                person_points.append((x, y))

        if len(person_points) < 5:
            continue

        features = extract_features(person_points)
        sequence.append(features)

        if len(sequence) == SEQUENCE_LENGTH:

            input_data = np.array(sequence).reshape(1, SEQUENCE_LENGTH, FEATURE_SIZE)
            score = model.predict(input_data, verbose=0)[0][0]

            if score > 0.5:
                cap.release()
                return "VIOLENCE"

    cap.release()
    return "NON_VIOLENCE"


def evaluate_violent_only(test_dir):

    folder_path = os.path.join(test_dir, "violent")

    if not os.path.exists(folder_path):
        print("Missing folder:", folder_path)
        return

    y_pred = []
    detected = 0
    total = 0

    for file in os.listdir(folder_path):

        video_path = os.path.join(folder_path, file)

        print("Testing:", video_path)

        pred = predict_video(video_path)

        y_pred.append(pred)
        total += 1

        if pred == "VIOLENCE":
            detected += 1

        print("Pred:", pred)

    if total == 0:
        print("No videos found!")
        return

    print("\n====================")
    print("TOTAL VIOLENCE_VIDEOS:", total)
    print("DETECTED AS VIOLENCE:", detected)
    print("MISS RATE:", round((total - detected) / total, 3))
    print("====================")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    evaluate_violent_only("performance_test/dataset")