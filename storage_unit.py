import mysql.connector
import datetime
import os

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


def create_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="###################",
        password="###########################"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS violence_system_db")
    conn.close()


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="######################",
        password="###############",
        database="violence_system_db"
    )


def init_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) UNIQUE,
            password VARCHAR(100)
        )
    """)

    users = [
        (1, 'user1@test.com', '123456'),
        (2, 'user2@test.com', '123456')
    ]

    for user in users:
        cursor.execute("""
            INSERT IGNORE INTO users (user_id, email, password)
            VALUES (%s, %s, %s)
        """, user)

    conn.commit()
    conn.close()


def init_camera_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id VARCHAR(20) PRIMARY KEY,
            model VARCHAR(100),
            location VARCHAR(200),
            stream_url VARCHAR(200),
            timezone VARCHAR(50) DEFAULT 'Asia/Riyadh',
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cameras = [

        ("CAM_002", "Hikvision ColorVu DS-2CD2T83G2-2LI",
         "Riyadh, King Saud University, College of Medicine, Sports Field",
         "rtsp://192.168.1.11:554/Streaming/Channels/101", "Asia/Riyadh", 2),

        ("CAM_001", "Hikvision ColorVu DS-2CD2T83G2-2LI",
         "Al-Qassim, Mulayda, College of Computer, Main Hall",
         "##########################", "Asia/Riyadh", 1),

        ("CAM_003", "Hikvision ColorVu DS-2CD2T83G2-2LI",
         "Riyadh, King Saud University, Library",
         "rtsp://192.168.1.12:554/Streaming/Channels/101", "Asia/Riyadh", 2),

        ("CAM_004", "Hikvision ColorVu DS-2CD2T83G2-2LI",
         "Riyadh, King Saud University, Cafeteria",
         "rtsp://192.168.1.13:554/Streaming/Channels/101", "Asia/Riyadh", 2),

       ("CAM_005", "Hikvision ColorVu DS-2CD2T83G2-2LI",
         "Riyadh, King Saud University, Parking Lot",
         "rtsp://192.168.1.14:554/Streaming/Channels/101", "Asia/Riyadh", 2),
    ]

    for cam in cameras:
        cursor.execute("""
            INSERT IGNORE INTO cameras 
            (camera_id, model, location, stream_url, timezone, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, cam)

    conn.commit()
    conn.close()


def init_violence_table():
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


def save_violence_event(frame, camera_id, location, tz_name,score,level):

    tz = ZoneInfo(tz_name)
    time_now = datetime.datetime.now(tz)
    time_now_str = time_now.strftime("%Y-%m-%d %H:%M:%S")

    

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
    """, (camera_id, time_now_str, location, level, score, image_path))

    conn.commit()
    conn.close()

    print(f"Violence event saved | Camera: {camera_id} | Location: {location} | Time: {time_now_str}")


def get_user_events_for_dashboard(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        v.ID AS event_id,
        v.Camera_ID,
        c.location AS camera_location,
        v.Timestamp,
        v.Severity,
        v.Confidence,
        v.evidence
    FROM violence_events v
    JOIN cameras c ON v.Camera_ID = c.camera_id
    WHERE c.user_id = %s
    ORDER BY v.Timestamp DESC
    """
    
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results


