import mysql.connector
import datetime
import os
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="********",
        password="********",
        database="violence_db"
    )
    return conn

def init_violence_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violence_events (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            Camera_ID VARCHAR(20),
            Timestamp DATETIME,
            location VARCHAR(200),
            Severity VARCHAR(20),
            Confidence VARCHAR(20),
            evidence VARCHAR(200)
        )
    """)
    conn.commit()
    conn.close()

def init_camera_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id VARCHAR(20) PRIMARY KEY,
            model VARCHAR(100),
            location VARCHAR(200),
            stream_url VARCHAR(200),
            timezone VARCHAR(50) DEFAULT 'Asia/Riyadh'
        )
    """)

    cameras = [

        ("CAM_002", "Hikvision ColorVu DS-2CD2T83G2-2LI",
         "Riyadh, King Saud University, College of Medicine, Sports Field",
         "rtsp://192.168.1.11:554/Streaming/Channels/101", "Asia/Riyadh"),

        ("CAM_001", "Hikvision ColorVu DS-2CD2T83G2-2LI",
          "Al-Qassim, Mulayda, College of Computer, Main Hall",
          "****************************", "Asia/Riyadh"),

        
    ]

    for cam in cameras:
        cursor.execute("""
            INSERT IGNORE INTO cameras (camera_id, model, location, stream_url, timezone)
            VALUES (%s, %s, %s, %s, %s)
        """, cam)

    conn.commit()
    conn.close()

def get_camera_info_by_stream(stream_url):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT camera_id, location, timezone 
        FROM cameras 
        WHERE CAST(stream_url AS CHAR) = %s
        LIMIT 1
    """, (str(stream_url),))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0], result[1], result[2]
    else:
        return "Unknown", "Unknown", "UTC"

def save_violence_event(frame, camera_id, location, tz_name):

    tz = ZoneInfo(tz_name)
    time_now = datetime.datetime.now(tz)
    time_now_str = time_now.strftime("%Y-%m-%d %H:%M:%S")

    severity = "-"
    confidence = "-"

    if not os.path.exists("violence_images"):
        os.makedirs("violence_images")

    image_name = f"violence_{time_now.strftime('%Y%m%d_%H%M%S')}.jpg"
    image_path = os.path.join("violence_images", image_name)

    import cv2
    cv2.imwrite(image_path, frame)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO violence_events 
        (Camera_ID, Timestamp, location, Severity, Confidence, evidence)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (camera_id, time_now_str, location, severity, confidence, image_path))

    conn.commit()
    conn.close()

    print(f"Violence event saved | Camera: {camera_id} | Location: {location} | Time: {time_now_str}")