import av
import cv2
import numpy as np

rtsp_url = "************************************"

container = av.open(rtsp_url, options={"rtsp_transport": "tcp"})

print(" stream opened byPyAV TCP")

for frame in container.decode(video=0):
    img = frame.to_ndarray(format='bgr24')

    h, w = img.shape[:2]
    scale = 900 / w
    display = cv2.resize(img, (900, int(h * scale)))

    cv2.imshow("RTSP Stream PyAV", display)

    if cv2.waitKey(1) & 0xFF == 27:  
        break

container.close()
cv2.destroyAllWindows() 