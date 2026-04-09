from storage_unit import create_database, init_camera_table, get_db_connection, init_users_table, init_violence_table
from processing_unit import run_camera
import threading

create_database()
init_camera_table()
init_users_table()
init_violence_table()


conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT stream_url FROM cameras")
stream_urls = [row[0] for row in cursor.fetchall()]
conn.close()

threads = []
for url in stream_urls:
    t = threading.Thread(target=run_camera, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join() 