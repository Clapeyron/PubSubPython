import test_jpeg as tj
import struct
import traceback
import time
import cv2


if __name__ == "__main__":
    t = tj.get_topic()
    tt = int(time.time()/1000)*1000
    print(f"basis: {tt}")
    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        i = 0
        while True:
            i += 1
            ret, frame = cap.read()
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            bts = cv2.imencode('.jpg', frame)[1].tostring()
            print(len(bts))
            t.write(struct.pack("I", i) + struct.pack("I", int((time.time() - tt) * 1000000)) + bts)
    except Exception as e:
        print("Exception:", e)
        print(traceback.format_exc())