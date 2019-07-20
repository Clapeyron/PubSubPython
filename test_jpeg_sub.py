import numpy as np
import struct
import time
import test_jpeg as tj
import cv2


if __name__ == "__main__":
    t = tj.get_topic()
    tt = int(time.time()/1000)*1000
    print(f"basis: {tt}")
    try:
        while True:
            b = t.sub()
            image = np.asarray(b[8:], dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            tm = struct.unpack("I", b[4:8])[0]
            print(int((time.time() - tt)*1000000)-tm)
            cv2.imshow(f'delay', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print("Exception:", e)