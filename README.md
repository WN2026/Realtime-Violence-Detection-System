<p align="center">
  <img src="assets/img.png" alt="YAQIDH Banner" width="100%">
</p>

## Overview

The Real-Time Violence Detection System is an AI-powered surveillance solution designed to automatically detect violent activities from live camera streams. The system analyzes human body movements using pose estimation, classifies violent behavior using a deep learning model, detects weapons when present, evaluates the severity of incidents, stores all detected events in a MySQL database, and immediately notifies security personnel through a real-time monitoring dashboard.

The system is intended for schools, universities, hospitals, shopping malls, public facilities, industrial sites, and other environments requiring continuous surveillance and rapid emergency response.

---

## Features

- Real-time video stream processing.
- Human pose estimation using TF-Pose.
- Violence detection using a trained LSTM model.
- Weapon detection support.
- Violence severity classification.
- Multi-camera monitoring using multithreading.
- Real-time alert generation.
- Automatic incident logging.
- MySQL database integration.
- Interactive web dashboard.
- User management.
- Reports and statistics.
- Modular system architecture.

---

## Project Structure

```text
Realtime-Violence-Detection-System/

run.py
processing_unit.py
storage_unit.py
alerts_manager.py
severity_classifier.py
weapon_detector.py
best_acc_final.keras
frontend/
tf_pose/
datasets/
performance_test/
models/
```

---

# System Workflow

1. Receive live RTSP video streams from surveillance cameras.
2. Capture video frames continuously.
3. Estimate human body keypoints using TF-Pose.
4. Convert extracted poses into temporal feature sequences.
5. Classify the sequence using the trained LSTM model.
6. Detect the presence of weapons if applicable.
7. Estimate the violence severity level.
8. Generate an immediate alert for security operators.
9. Display the incident on the monitoring dashboard.
10. Store all event information inside the MySQL database.

---

# Real-Time Alert System

Whenever the system detects a violent event, it immediately generates a real-time alert without requiring user intervention.

Each alert includes comprehensive incident information, including:

- Detection time and date.
- Camera ID.
- Camera location.
- Violence confidence score.
- Severity level (Low, Medium, High).
- Weapon detection result.
- Incident status.
- Event description.

These alerts enable security personnel to respond quickly and monitor ongoing incidents as they occur.

---

# Frontend Dashboard

The project includes a web-based monitoring dashboard located inside the **frontend/** directory.

The dashboard provides an intuitive interface for security operators to monitor cameras, review incidents, and manage the overall system.

## Dashboard Components

### Login Page

- Secure authentication screen.
- Username/email login.
- Password protection.
- Restricted access for authorized personnel.

### Dashboard

Provides a real-time overview of the monitoring system, including:

- Total cameras
- Active cameras
- Active alerts
- Recent incidents
- Current date and time
- Overall monitoring status

### Live Monitoring

Displays all surveillance cameras simultaneously.

For each camera, the interface shows:

- Camera name
- Camera location
- Live status
- Detection confidence
- Current alerts

### Incidents Page

Displays all detected violence events.

Each incident includes:

- Incident ID
- Date and time
- Camera information
- Violence confidence
- Severity level
- Detection status
- Event description

### Reports

Provides statistical summaries of detected incidents, allowing operators to review historical system performance and monitor security trends.

### User Management

Allows administrators to:

- View users
- Manage user roles
- Monitor account status
- Review login activity

---

# Technologies Used

- Python
- TensorFlow
- Keras
- OpenCV
- TF-Pose Estimation
- NumPy
- PyAV
- MySQL
- HTML
- CSS
- JavaScript
- Multithreading

---

# Database

The system stores all information inside a MySQL database named:

```text
violence_system_db
```

The database maintains:

- User accounts
- Camera information
- Violence incidents
- Detection history
- Alert records

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd Realtime-Violence-Detection-System
```


Configure the MySQL connection inside:

```text
storage_unit.py
```

Insert camera RTSP URLs into the cameras table.

Run the application:

```bash
python run.py
```

---

# Performance Evaluation

The project contains a dedicated evaluation module inside:

```text
performance_test/
```

This module measures the performance of the trained model using testing datasets and reports detection accuracy and evaluation metrics.

---

# Machine Learning Model

The violence detection module uses a trained Long Short-Term Memory (LSTM) neural network.

Model file:

```text
best_acc_final.keras
```

The model receives temporal sequences of body pose features extracted by TF-Pose and predicts whether the observed activity represents violent behavior.

---

# Applications

- Schools
- Universities
- Hospitals
- Shopping malls
- Public buildings
- Smart cities
- Industrial facilities
- Transportation hubs

---


# License

This project was developed for educational and research purposes.
