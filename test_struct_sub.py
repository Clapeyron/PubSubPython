from topic import TopicSpawnMode, Topic, get_dict
import ctypes as C


class MyPoint(C.Structure):
    _pack_ = 1
    _fields_=(('x', C.c_float), ('y', C.c_float))

    def __str__(self):
        return f"MyPoint({self.x}, {self.y})"


if __name__ == "__main__":
    t = Topic(b"Mycooltopic_struct1", C.sizeof(MyPoint), 10, TopicSpawnMode.CREATE)
    try:
        while True:
            s = t.read_struct(MyPoint)
            print(s, get_dict(s))
    except Exception as e:
        print("Exception:", e)
        t.free()