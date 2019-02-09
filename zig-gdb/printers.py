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


class ConstParentPrinter(BasicPrinter):
    """Prints a `ConstParent` in a semi-compact form."""

    name = 'ConstParent'

    variants = {
        ConstParentId.ConstParentIdStruct: 'p_struct',
        ConstParentId.ConstParentIdErrUnionCode: 'p_err_union_code',
        ConstParentId.ConstParentIdErrUnionPayload: 'p_err_union_payload',
        ConstParentId.ConstParentIdOptionalPayload: 'p_optional_payload',
        ConstParentId.ConstParentIdArray: 'p_array',
        ConstParentId.ConstParentIdUnion: 'p_union',
        ConstParentId.ConstParentIdScalar: 'p_scalar',
    }

    def __init__(self, val):
        self.val = val

    def to_string(self):
        return str(self.val['id'])

    def children(self):
        variant = self.variants.get(ConstParentId(self.val['id']))
        if variant:
            return self.val['data'][variant].items()
        else:
            return []


class ConstExprValuePrinter(BasicPrinter):
    name = 'ConstExprValue'

    def __init__(self, val):
        self.val = val

    def children(self):
        special = ConstValSpecial(self.val['special'])
        variant = None
        if special == ConstValSpecial.ConstValSpecialRuntime:
            data = '(runtime)'
            variant = util.runtime_hint(self.val)
            if variant:
                hint = self.val['data'][variant]
                data += f' [hint = {hint}]'
        elif special == ConstValSpecial.ConstValSpecialStatic:
            variant = util.const_data(self.val)
            data = self.val['data'][variant]
        else:
            data = '(undefined)'
        data = data or '(invalid)'

        data_name = 'data'
        if variant:
            data_name += '.' + variant

        return (
            ('special', self.val['special']),
            ('type', self.val['type']),
            ('parent', self.val['parent']),
            ('global_refs', self.val['global_refs']),
            (data_name, data),
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
