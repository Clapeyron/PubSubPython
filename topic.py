import enum
import ctypes as C
_TopicLib = C.pydll.LoadLibrary('./libclap_pubsub.so')


@enum.unique
class TopicSpawnMode(enum.Enum):
    STRICT = 0
    IGNORE_MSGCOUNT = 1
    IGNORE_ALL = 2
    CREATE = 3


class Topic:
    def __init__(self, name, msg_size, msg_count, spawn_mode = TopicSpawnMode.CREATE):
        assert isinstance(name, bytes), "Name should be ascii bytes"
        self.name = name
        self.msg_size = msg_size
        self.msg_count = msg_count
        self.__spawn = _TopicLib.spawn_topic
        self.__create = _TopicLib.create_topic
        self.__create.restype = C.c_bool
        self.__spawn.restype = C.c_bool
        self.__ptr_sz = _TopicLib.TopSZ()
        self._pub = _TopicLib.pub
        self._pub.argtypes = [C.c_void_p, C.c_char_p, C.c_uint32]
        self._t = C.byref(C.create_string_buffer(b"", size=self.__ptr_sz))
        self._n = C.byref(C.create_string_buffer(name))
        e = Exception("Error: topic.hpp returned nullptr (:")
        if spawn_mode == TopicSpawnMode.CREATE:
            ok = self.__create(self._t, self._n, self.msg_size, self.msg_count)
            if not ok: raise e
        elif spawn_mode == TopicSpawnMode.IGNORE_ALL:
            ok = self.__spawn(self._t, self._n, 0, 0)
            if not ok: raise e
            self.msg_size = _TopicLib.msg_size(self._t)
            self.msg_count = _TopicLib.msg_count(self._t)
        elif spawn_mode == TopicSpawnMode.IGNORE_MSGCOUNT:
            assert isinstance(msg_size, int), "msg_size should be int"
            assert msg_size > 0, "msg_size should be > 0"
            ok = self.__spawn(self._t, self._n, msg_size, 0)
            if not ok: raise e
            self.msg_count = _TopicLib.msg_count(self._t)
        elif spawn_mode == TopicSpawnMode.STRICT:
            assert isinstance(msg_size, int), "msg_size should be int"
            assert msg_size > 0, "msg_size should be > 0"
            assert isinstance(msg_count, int), "msg_count should be int"
            assert msg_count > 0, "msg_count should be > 0"
            ok = self.__spawn(self._t, self._n, msg_size, msg_count)
            if not ok: raise e
        print(f"Topic created. Size {self.msg_size}, count {self.msg_count}")
        self._b = C.create_string_buffer(b'', size=self.msg_size)
        self._br = C.byref(self._b)

    def pub(self, message:bytes):
        # print("bytes to pub:", message, "type:", type(message))
        ln = len(message)
        if ln == 0: raise Exception("Message can't be empty")
        if ln > self.msg_size: raise Exception(f"Too big message: got {ln}, needed <= {self.msg_size}")
        return self._pub(self._t, C.c_char_p(message), ln)

    def sub(self):
        res = _TopicLib.sub(self._t, self._br)
        # print(f"RES: {res}")
        if res == 0:
            raise Exception("zero-length message, abort")
        b = bytearray(self._b)
        # print("sub _b.value:", self._b.value, "type:", type(self._b.value))
        return b

    def free(self):
        pass

    def pub_struct(self, strct: C.Structure):
        b = bytes(strct)
        return self.pub(b)

    def sub_struct(self, strtype):
        return strtype.from_buffer_copy(self.sub())

    @classmethod
    def remove(cls, name):
        _n = C.byref(C.create_string_buffer(name))
        return _TopicLib.remove_topic(_n)


def getdict(struct):
    result = {}
    for field, _ in struct._fields_:
         value = getattr(struct, field)
         # if the type is not a primitive and it evaluates to False ...
         if (type(value) not in [C.c_int, C.c_long, C.c_float, C.c_bool]) and not bool(value):
             # it's a null pointer
             value = None
         elif hasattr(value, "_length_") and hasattr(value, "_type_"):
             # Probably an array
             value = list(value)
         elif hasattr(value, "_fields_"):
             # Probably another struct
             value = getdict(value)
         result[field] = value
    return result


class TopicFactory:
    def __init__(self, prefix=""):
        self.prefix = prefix
        self._topic_decl = {}
        self._topics = {}

    def register(self, name, struct_clz, msg_count, spawn_mode:TopicSpawnMode):
        if name in self._topic_decl: raise Exception(f"Topic '{name}' already registered to this Factory")
        self._topic_decl[name] = (struct_clz, msg_count, spawn_mode)

    def extract_top(self, name):
        t, strct = self._topics.get(name, (None, None))
        if t is None:
            decl = self._topic_decl.get(name, None)
            if decl is None:
                print(f"Topic '{name}' wasn't declared")
                return None, None
            strct = decl[0]
            t = Topic((self.prefix+name).encode("ascii"), msg_size=C.sizeof(strct), msg_count=decl[1], spawn_mode=decl[2])
            self._topics[name] = (t, strct)
        return t, strct

    def pub(self, name, dct):
        t, struct_clz = self.extract_top(name)
        if t is None: return
        t.pub_struct(struct_clz(**dct))

    def sub(self, name):
        t, struct_clz = self.extract_top(name)
        if t is None: return
        struct = t.sub_struct(struct_clz)
        return getdict(struct)

