import av
import cv2
import numpy as np
import threading
from queue import Queue
from tensorflow.keras.models import load_model
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path
from storage_unit import save_violence_event, get_camera_info_by_stream

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
        container = av.open(stream_url, options={"rtsp_transport": "tcp"})
        print(f"Stream opened : {stream_url}")
    except av.AVError as e:
        print(f"Failed to open stream: {stream_url} | {e}")
        return

    for frame in container.decode(video=0):
        img = frame.to_ndarray(format='bgr24')
        if frame_queue.full():
            frame_queue.get()
        frame_queue.put(img)
    container.close()

def process_frames(frame_queue, camera_id, location, tz_name):
    model = load_model("best_acc_final.keras")
    pose_estimator = TfPoseEstimator(get_graph_path("mobilenet_thin_432x368"), target_size=(432, 368))
    sequence = []
    prev_label = "NON VIOLENCE"

    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            humans = pose_estimator.inference(frame)
            individuals = []

            for human in humans:
                person_points = []
                xs, ys = [], []
                for i in range(18):
                    if i in human.body_parts:
                        part = human.body_parts[i]
                        x = int(part.x * frame.shape[1])
                        y = int(part.y * frame.shape[0])
                        person_points.append((x, y))
                        xs.append(x)
                        ys.append(y)
                        cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

                if len(person_points) > 5:
                    individuals.append(person_points)
                    x1, y1 = min(xs), min(ys)
                    x2, y2 = max(xs), max(ys)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            for person_points in individuals:
                features = []
                cx, cy = centroid(person_points)
                for x, y in person_points:
                    r, a = polar(cx, cy, x, y)
                    features.extend([r, a, abs(x-cx)/(frame.shape[1]/2), abs(y-cy)/(frame.shape[0]/2)])

                features = np.array(features)
                if len(features) < 72:
                    features = np.pad(features, (0, 72-len(features)))

                sequence.append(features)
                if len(sequence) > SEQUENCE_LENGTH:
                    sequence.pop(0)

                label = "NON VIOLENCE"
                color = (0, 255, 0)

                if len(sequence) == SEQUENCE_LENGTH:
                    input_data = np.array(sequence).reshape(1, 63, 72)
                    prediction = model.predict(input_data, verbose=0, batch_size=1)
                    score = prediction[0][0]
                    if score > 0.5:
                        label = "VIOLENCE"
                        color = (0, 0, 255)
                        if prev_label == "NON VIOLENCE":
                            save_violence_event(frame, camera_id, location, tz_name)
                prev_label = label
                cv2.putText(frame, label, (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

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
    t_process = threading.Thread(target=process_frames, args=(frame_queue, camera_id, location, tz_name), daemon=True)
    t_read.start()
    t_process.start()
    t_read.join()
    t_process.join()