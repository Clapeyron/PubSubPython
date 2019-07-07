import ctypes as C
from topic import TopicSpawnMode, Topic


class Image1M(C.Structure):
    _pack_ = 1
    _fields_=(('i', C.c_uint32), ('t', C.c_uint32), ('data', C.c_char * 500000))

    def __str__(self):
        return f"Image1M({self.i})"


def rm_topic(name=b"Mycooltopic_jpeg0"):
    Topic.remove(name)


def get_topic(name=b"Mycooltopic_jpeg0"):
    return Topic(name, C.sizeof(Image1M), 10, TopicSpawnMode.CREATE)