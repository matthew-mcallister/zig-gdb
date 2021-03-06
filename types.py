from enum import Enum

import gdb
import gdb.types


def zig_enum(name):
    items = gdb.types.make_enum_dict(gdb.lookup_type(name))
    res = Enum(name, items)

    # Cast constructor argument to int.
    # Note that, confusingly, Enum requires you to override __new__
    # rather than __init__.
    res.__new__ = lambda cls, val: Enum.__new__(cls, int(val))

    return res


ConstParentId = zig_enum('ConstParentId')
ConstValSpecial = zig_enum('ConstValSpecial')
IrInstructionId = zig_enum('IrInstructionId')
NodeType = zig_enum('NodeType')
ZigTypeId = zig_enum('ZigTypeId')
