import gdb.printing

from . import util
from .types import *


zig_printers = []


class BasicPrinter:
    """Superclass of most printers that provides some default
    attributes and does bookkeeping."""

    enabled = True
    subprinters = []

    def __init_subclass__(cls):
        zig_printers.append(cls)

    def to_string(self):
        return self.__class__.name


class ConstExprValuePrinter(BasicPrinter):
    name = 'ConstExprValue'

    def __init__(self, val):
        self.val = val

    def children(self):
        special = ConstValSpecial(self.val['special'])
        if special == ConstValSpecial.ConstValSpecialRuntime:
            data = '(runtime)'
            hint = util.runtime_hint(self.val)
            if hint:
                data += ' [hint = {hint}]'
        elif special == ConstValSpecial.ConstValSpecialStatic:
            data = util.const_data(self.val)
        else:
            data = '(undefined)'
        data = data or '(invalid)'
        return (
            ('special', self.val['special']),
            ('type', self.val['type']),
            ('parent', self.val['parent']),
            ('global_refs', self.val['global_refs']),
            ('data', data),
        )


class PrinterFactory:
    """Selects a printer by consulting a mapping of type names to
    printers."""

    def __init__(self, name, printers):
        printers = list(printers)
        self.printers = {printer.name: printer for printer in printers}

        self.name = name
        self.subprinters = printers
        self.enabled = True

    def __call__(self, value):
        type_name = util.get_basic_type(value.type)
        try:
            return self.printers[type_name](value)
        except KeyError:
            return None


def register_printers(obj=None):
    factory = PrinterFactory('zig', zig_printers)
    gdb.printing.register_pretty_printer(obj, factory)
