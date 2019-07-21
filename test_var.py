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
        t.write_struct(MyPoint(*map(float, sys.argv[1:3])))
    else:
        print(t.read_struct(MyPoint))
