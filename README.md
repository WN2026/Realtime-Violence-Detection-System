# Real-Time Violence Detection System

## Overview

The Real-Time Violence Detection System is an AI-powered surveillance solution designed to automatically detect violent activities from live camera streams. The system analyzes human body movements using pose estimation, classifies violent behavior using a deep learning model, detects weapons when present, evaluates the severity of incidents, and stores detected events in a MySQL database.

The project is intended for environments such as schools, universities, hospitals, shopping centers, public facilities, and other locations where continuous monitoring is required.

---

## Features

- Real-time video stream processing.
- Human pose estimation using TF-Pose.
- Violence detection using a trained LSTM model.
- Weapon detection support.
- Violence severity classification.
- Multi-camera monitoring using multithreading.
- Automatic event logging.
- MySQL database integration.
- Modular system architecture.

---

## Project Structure

```
Realtime-Violence-Detection-System/

├── run.py
├── processing_unit.py
├── storage_unit.py
├── alerts_manager.py
├── severity_classifier.py
├── weapon_detector.py
├── best_acc_final.keras
├── frontend/
├── tf_pose/
├── datasets/
├── performance_test/
└── models/
```

---

## System Workflow

1. Read live video streams from IP cameras (RTSP).
2. Extract frames from the video.
3. Estimate human body keypoints using TF-Pose.
4. Convert pose information into temporal sequences.
5. Feed the sequence into the trained LSTM model.
6. Predict whether violence is occurring.
7. Detect weapons if present.
8. Classify the violence severity.
9. Save the incident information into the database.

---

## Technologies Used

- Python
- TensorFlow
- Keras
- OpenCV
- TF-Pose Estimation
- NumPy
- PyAV
- MySQL
- Multithreading

---

## Database

The system stores information in a MySQL database named:

```
violence_system_db
```

The database maintains camera information, users, and detected violence events.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd Realtime-Violence-Detection-System
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the MySQL connection inside:

```
storage_unit.py
```

Add the camera stream URLs into the cameras table.

Run the project:

```bash
python run.py
```

---

## Performance Evaluation

The project includes a dedicated performance testing module inside:

```
performance_test/
```

This module is used to evaluate the trained model using saved testing datasets and generate performance metrics.

---

## Machine Learning Model

The violence detection component uses a trained Long Short-Term Memory (LSTM) neural network.

The model is stored as:

```
best_acc_final.keras
```

The model receives sequences of extracted body pose features and predicts whether the observed activity represents violent behavior.

---

## Applications

- Schools
- Universities
- Hospitals
- Shopping malls
- Public buildings
- Smart cities
- Industrial facilities

---

## Future Improvements

- Real-time email and SMS notifications.
- Web dashboard for monitoring incidents.
- Mobile application support.
- Cloud database integration.
- Person identification.
- Higher accuracy using newer pose estimation models.

---

## License

This project was developed for educational and research purposes.
