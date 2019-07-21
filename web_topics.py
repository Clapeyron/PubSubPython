import ctypes as C
from topic import PubSubFactory, TopicSpawnMode


tf = PubSubFactory(prefix="clapeyron-v1.")


class WheelSpeed(C.Structure):
    _pack_ = 1
    _fields_=(('left', C.c_float), ('right', C.c_float))

class SomeTextStructure(C.Structure):
    _pack_ = 1
    _fields_ = (("text", C.c_char * 1024), )

class AlgoOn(C.Structure):
    _pack_ = 1
    _fields_ = (("on", C.c_bool), )


tf.register_topic("wheels", WheelSpeed, 10, TopicSpawnMode.CREATE)
tf.register_topic("chat", SomeTextStructure, 10, TopicSpawnMode.CREATE)
tf.register_var("algo_on", AlgoOn, True)
