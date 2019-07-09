import ctypes as C
from topic import TopicFactory, TopicSpawnMode


tf = TopicFactory(prefix="clapeyron-v1.")


class WheelSpeed(C.Structure):
    _pack_ = 1
    _fields_=(('left', C.c_float), ('right', C.c_float))


tf.register("wheels", WheelSpeed, 10, TopicSpawnMode.CREATE)


class SomeTextStructure(C.Structure):
    _pack_ = 1
    _fields_ = (("text", C.c_char * 1024), )


tf.register("chat", SomeTextStructure, 10, TopicSpawnMode.CREATE)