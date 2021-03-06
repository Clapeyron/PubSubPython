import enum
import ctypes as C
_Lib = C.pydll.LoadLibrary('./libclap_pubsub.so')


@enum.unique
class TopicSpawnMode(enum.Enum):
    STRICT = 0
    IGNORE_MSGCOUNT = 1
    IGNORE_ALL = 2
    CREATE = 3


class TpcInterruptedException(Exception):
    pass


class PubSub:
    _dst = None
    _interrupted = _Lib.was_interrupted
    _interrupted.restype = C.c_bool

    def read(self):
        raise NotImplementedError()

    def write(self, message: bytes):
        raise NotImplementedError()

    def read_struct(self, s_type):
        return s_type.from_buffer_copy(self.read())

    def write_struct(self, s: C.Structure):
        return self.write(bytes(s))

    def read_dict(self):
        if self._dst is None: raise Exception("no default struct given")
        return get_dict(self.read_struct(self._dst))

    def write_dict(self, dct):
        if self._dst is None: raise Exception("no default struct given")
        return self.write_struct(self._dst(**dct))

    def free(self):
        raise NotImplementedError()

    @staticmethod
    def remove(name):
        raise NotImplementedError()


class Variable(PubSub):
    def __init__(self, name, size, create=True, def_str_type=None):
        assert isinstance(name, bytes), "Name should be ascii bytes"
        self._dst = def_str_type
        self.bname, self.size = name, size
        self._create, self._create.restype = _Lib.varCreate, C.c_bool
        self._open, self._open.restype = _Lib.varOpen, C.c_bool
        self._W, self._W.restype, self._W.argtypes = _Lib.varWrite, C.c_bool, [C.c_void_p, C.c_char_p, C.c_uint32]
        self._R, self._R.restype = _Lib.varRead, C.c_bool #, [C.c_void_p, C.c_char_p, C.c_uint32]
        self.Ptr = C.byref(C.create_string_buffer(b"", size=_Lib.varPtrSize()))
        e = Exception("Can't create Variable: topic.hpp returned nullptr (:")
        if create:
            if not self._create(self.Ptr, self.bname, self.size): raise e
        else:
            if not self._open(self.Ptr, self.bname, self.size): raise e
        self.buf = C.create_string_buffer(b'', size=self.size)
        self.bufRef = C.byref(self.buf)

    def read(self):
        res = self._R(self.Ptr, self.bufRef, 0)
        if not res: raise Exception("zero-length message, abort")
        return bytearray(self.buf)

    def write(self, message:bytes):
        ln = len(message)
        if ln == 0: raise Exception("Message can't be empty")
        if ln > self.size: raise Exception(f"Too big message: got {ln}, needed <= {self.size}")
        try: return self._W(self.Ptr, C.c_char_p(message), ln)
        except KeyboardInterrupt: raise Exception("")

    def free(self):
        pass

    @classmethod
    def remove(cls, name):
        return _Lib.varRemove(C.byref(C.create_string_buffer(name)))


class Topic(PubSub):
    def __init__(self, name, msg_size, msg_count, spawn_mode = TopicSpawnMode.CREATE, def_str_type=None):
        assert isinstance(name, bytes), "Name should be ascii bytes"
        self._dst = def_str_type
        self.name, self.msg_size, self.msg_count = name, msg_size, msg_count
        self.bname = C.byref(C.create_string_buffer(name))
        self._spawn, self._spawn.restype = _Lib.topicSpawn, C.c_bool
        self._create, self._create.restype = _Lib.topicCreate, C.c_bool
        self._pub, self._pub.restype, self._pub.argtypes = _Lib.topicPub, C.c_bool, [C.c_void_p, C.c_char_p, C.c_uint32]
        self._sub, self._sub.restype = _Lib.topicSub, C.c_bool #, self._sub.argtypes = , [C.c_void_p, C.c_char_p]
        self.Ptr = C.byref(C.create_string_buffer(b"", size=_Lib.topPtrSize()))
        e = Exception("Error: topic.hpp returned nullptr (:")
        if spawn_mode == TopicSpawnMode.CREATE:
            if not self._create(self.Ptr, self.bname, self.msg_size, self.msg_count): raise e
        elif spawn_mode == TopicSpawnMode.IGNORE_ALL:
            if not self._spawn(self.Ptr, self.bname, 0, 0): raise e
            self.msg_size, self.msg_count = _Lib.topicMsgSize(self.Ptr), _Lib.topicMsgCount(self.Ptr)
        elif spawn_mode == TopicSpawnMode.IGNORE_MSGCOUNT:
            assert isinstance(msg_size, int), "msg_size should be int"
            assert msg_size > 0, "msg_size should be > 0"
            if not self._spawn(self.Ptr, self.bname, msg_size, 0): raise e
            self.msg_count = _Lib.topicMsgCount(self.Ptr)
        elif spawn_mode == TopicSpawnMode.STRICT:
            assert isinstance(msg_size, int), "msg_size should be int"
            assert msg_size > 0, "msg_size should be > 0"
            assert isinstance(msg_count, int), "msg_count should be int"
            assert msg_count > 0, "msg_count should be > 0"
            if not self._spawn(self.Ptr, self.bname, msg_size, msg_count): raise e
        print(f"Topic created. Size {self.msg_size}, count {self.msg_count}")
        self.buf = C.create_string_buffer(b'', size=self.msg_size)
        self.bufRef = C.byref(self.buf)

    def write(self, message:bytes):
        ln = len(message)
        if ln == 0: raise Exception("Message can't be empty")
        if ln > self.msg_size: raise Exception(f"Too big message: got {ln}, needed <= {self.msg_size}")
        return self._pub(self.Ptr, C.c_char_p(message), ln)

    def read(self):
        res = self._sub(self.Ptr, self.bufRef)
        if not res: raise Exception("zero-length message, abort")
        return bytearray(self.buf)

    def free(self):
        pass

    @classmethod
    def remove(cls, name):
        return _Lib.topicRemove(C.byref(C.create_string_buffer(name)))


def get_dict(struct):
    result = {}
    for field, _ in struct._fields_:
         value = getattr(struct, field)
         if (type(value) not in [C.c_int, C.c_long, C.c_float, C.c_bool]) and not bool(value):
             value = None
         elif hasattr(value, "_length_") and hasattr(value, "_type_"):
             value = list(value)
         elif hasattr(value, "_fields_"):
             value = get_dict(value)
         result[field] = value
    return result


class PubSubFactory:
    def __init__(self, prefix):
        self.prefix = prefix
        self._declared = {}
        self._created = {}

    def register_topic(self, name, struct_class, msg_count, spawn_mode: TopicSpawnMode):
        if name in self._declared: raise Exception(f"Name '{name}' already registered in Factory")
        self._declared[name] = (self._gen_topic, struct_class, msg_count, spawn_mode)

    def register_var(self, name, struct_class, create=True):
        self._declared[name] = (self._gen_var, struct_class, create)

    def rm_topic(self, name):
        return Topic.remove(self._bname(name))

    def rm_var(self, name):
        return Variable.remove(self._bname(name))

    def _bname(self, name):
        return (self.prefix + name).encode("ascii")

    def _gen_topic(self, name, clz, cnt, mode):
        return Topic(self._bname(name), msg_size=C.sizeof(clz), msg_count=cnt, spawn_mode=mode, def_str_type=clz)

    def _gen_var(self, name, clz, create):
        return Variable(self._bname(name), size=clz, create=create, def_str_type=clz)

    def _extract(self, name) -> PubSub:
        p = self._created.get(name, None)
        if p is None:
            p = self._declared.get(name, None)
            if p is None: raise Exception(f"No '{name}' registered")
            p = p[0](name, *p[1:])
            self._created[name] = p
        return p

    def write(self, name, dct):
        p = self._extract(name)
        try: return p.write_dict(dct)
        except TpcInterruptedException:
            p.free()
            self._created.pop(name, None)

    def read(self, name):
        p = self._extract(name)
        try: return p.read_dict()
        except TpcInterruptedException:
            p.free()
            self._created.pop(name, None)

