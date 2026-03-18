from storage_unit import init_violence_database, init_camera_database, get_db_connection
from processing_unit import process_camera
import threading

init_violence_database()
init_camera_database()

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT stream_url FROM cameras")
stream_urls = [row[0] for row in cursor.fetchall()]
conn.close()

threads = []
for url in stream_urls:
    t = threading.Thread(target=process_camera, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()