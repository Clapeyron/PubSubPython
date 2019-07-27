import ctypes as C
import faulthandler


if __name__=="__main__":
    faulthandler.enable()
    Topic = C.pydll.LoadLibrary('/home/aynur/Repos/PubSubCPP/release/libclap_pubsub.so')
    print(dir(Topic))
    # print(f"TopSZ: {}")
    sz = Topic.TopSZ()
    name = C.byref(C.create_string_buffer(b'CLAP_PYTHON_topic2'))
    print(bool(Topic.remove_topic(name)))
    create = Topic.create_topic
    create.restype = C.c_bool
    msg_size = Topic.msg_size
    msg_size.restype = C.c_uint32
    t = C.byref(C.create_string_buffer(b"", size=sz))
    print("CREATE:", create(t, name, 8, 8))
    # t = C.c_void_p(t)
    # t = C.byref(t)
    print(Topic.is_null(t))
    print(Topic.msg_size(t))
    str_msg = b'HelloAAAAAAWorld'
    lmsg = len(str_msg)
    msg = C.byref(C.create_string_buffer(str_msg, size=64))
    print(Topic.write(t, str_msg, 0))
    print(Topic.read(t, msg))
    # Topic.free_mem(tref)
    faulthandler.disable()