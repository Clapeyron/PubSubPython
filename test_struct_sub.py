from topic import TopicSpawnMode, Topic
import ctypes as C


class MyPoint(C.Structure):
    _pack_ = 1
    _fields_=(('x', C.c_float), ('y', C.c_float))

    def __str__(self):
        return f"MyPoint({self.x}, {self.y})"


if __name__ == "__main__":
    t = Topic(b"Mycooltopic_struct1", C.sizeof(MyPoint), 10, TopicSpawnMode.CREATE)
    try:
        while True: print(t.sub_struct(MyPoint))
    except Exception as e:
        print("Exception:", e)
        t.free()