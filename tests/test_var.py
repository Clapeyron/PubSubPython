import sys
from topic import Variable, C


class MyPoint(C.Structure):
    _pack_ = 1
    _fields_=(('x', C.c_float), ('y', C.c_float))

    def __str__(self):
        return f"MyPoint({self.x}, {self.y})"


if __name__ == "__main__":
    t = Variable(b"MyVariable", C.sizeof(MyPoint), create=True)
    if len(sys.argv) > 2:
        p = MyPoint(*map(float, sys.argv[1:3]))
        print(p)
        t.write_struct(p)
    else:
        print(t.read_struct(MyPoint))
