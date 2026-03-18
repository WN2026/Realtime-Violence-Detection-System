import cv2
import numpy as np
from tensorflow.keras.models import load_model

from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path

# تحميل موديل العنف
model = load_model("best_acc_final.keras")

# تشغيل pose estimation
pose_estimator = TfPoseEstimator(
    get_graph_path("mobilenet_thin_432x368"),
    target_size=(432,368)
)

cap = cv2.VideoCapture(0)

SEQUENCE_LENGTH = 63
sequence = []

def centroid(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return sum(xs)/len(xs), sum(ys)/len(ys)

def polar(cx,cy,x,y):
    r = np.sqrt((x-cx)**2 + (y-cy)**2)
    a = np.arctan2(y-cy, x-cx)
    return r,a

while True:

    ret, frame = cap.read()
    if not ret:
        break

    humans = pose_estimator.inference(frame)

    individuals = []

    for human in humans:

        person_points = []
        xs = []
        ys = []

        for i in range(18):

            if i in human.body_parts:

                part = human.body_parts[i]

                x = int(part.x * frame.shape[1])
                y = int(part.y * frame.shape[0])

                person_points.append((x,y))
                xs.append(x)
                ys.append(y)

                # رسم نقاط الجسم
                cv2.circle(frame,(x,y),4,(0,255,0),-1)

        if len(person_points) > 5:

            individuals.append(person_points)

            # رسم Bounding Box
            x1 = min(xs)
            y1 = min(ys)
            x2 = max(xs)
            y2 = max(ys)

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)

    for person_points in individuals:

        features = []

        cx,cy = centroid(person_points)

        for x,y in person_points:

            r,a = polar(cx,cy,x,y)

            features.extend([
                r,
                a,
                abs(x-cx)/(frame.shape[1]/2),
                abs(y-cy)/(frame.shape[0]/2)
            ])

        features = np.array(features)

        if len(features) < 72:
            features = np.pad(features,(0,72-len(features)))

        sequence.append(features)

        if len(sequence) > SEQUENCE_LENGTH:
            sequence.pop(0)

        # الافتراضي
        label = "NON VIOLENCE"
        color = (0,255,0)

        if len(sequence) == SEQUENCE_LENGTH:

            input_data = np.array(sequence).reshape(1,63,72)

            prediction = model.predict(input_data, verbose=0)

            score = prediction[0][0]

            if score > 0.5:
                label = "VIOLENCE"
                color = (0,0,255)

        cv2.putText(frame,
                    label,
                    (int(cx),int(cy)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    color,
                    2)

    cv2.imshow("Violence Detection",frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()