from topic import TopicSpawnMode, Topic
import ctypes as C


class MyPoint(C.Structure):
    _pack_ = 1
    _fields_=(('x', C.c_float), ('y', C.c_float))


if __name__ == "__main__":
    t = Topic(b"Mycooltopic_struct1", C.sizeof(MyPoint), 10, TopicSpawnMode.CREATE)
    try:
        while True: t.pub_struct(MyPoint(*map(float, input("> ").strip().split(" "))))
    except Exception as e:
        print("Exception:", e)
        t.free()