# Real-Time Violence Detection System

## Overview

The Real-Time Violence Detection System is an AI-powered surveillance solution designed to automatically detect violent activities from live camera streams. The system analyzes human body movements using pose estimation, classifies violent behavior using a deep learning model, detects weapons when present, evaluates the severity of incidents, stores all detected events in a MySQL database, and immediately notifies security personnel through a real-time monitoring dashboard.

The system is intended for schools, universities, hospitals, shopping malls, public facilities, industrial sites, and other environments requiring continuous surveillance and rapid emergency response.

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

## Project Structure

```text
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

## System Workflow

1. Receive live RTSP video streams.
2. Capture frames.
3. Estimate body keypoints using TF-Pose.
4. Build temporal feature sequences.
5. Classify with LSTM.
6. Detect weapons.
7. Estimate severity.
8. Generate real-time alerts.
9. Display the incident on the dashboard.
10. Store the incident in MySQL.

## Real-Time Alert System

Each detected incident immediately generates an alert containing:

- Date and time
- Camera ID
- Camera location
- Violence confidence score
- Severity level
- Weapon detection result
- Incident status
- Incident description

## Frontend Dashboard

The frontend dashboard includes:

- Secure Login
- Dashboard overview
- Live Monitoring
- Incidents
- Reports
- User Management

The dashboard allows operators to monitor cameras, receive alerts, review incidents, and manage users.

## Technologies Used

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

## Database

Database name:

```text
violence_system_db
```

Stores:

- Users
- Cameras
- Violence incidents
- Detection history
- Alert records

## Installation

```bash
git clone <repository-url>
cd Realtime-Violence-Detection-System
pip install -r requirements.txt
python run.py
```

## Performance Evaluation

Evaluation files are located in:

```text
performance_test/
```

## Machine Learning Model

The project uses a trained LSTM model stored in:

```text
best_acc_final.keras
```

## Applications

- Schools
- Universities
- Hospitals
- Shopping malls
- Public buildings
- Smart cities
- Industrial facilities

## Future Improvements

- Email notifications
- SMS notifications
- Mobile application
- Cloud deployment
- Face recognition
- Improved pose estimation

## License

This project was developed for educational and research purposes.
