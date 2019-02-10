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


class BufPrinter(BasicPrinter):
    name = 'Buf'

    def __init__(self, val):
        self.val = val

    def to_string(self):
        ls = self.val['list']
        length = ls['length']
        return ls['items'].string(encoding='utf-8', length=length)

    def display_hint(self):
        return 'string'


class ZigListPrinter(BasicPrinter):
    name = 'ZigList'

    def __init__(self, val):
        self.val = val

    def to_string(self):
        type = util.get_basic_type(self.val.type)
        length = self.val['length']
        capacity = self.val['capacity']
        return f'{type}[len={length}, cap={capacity}]'

    def children(self):
        length = int(self.val['length'])
        elem = self.val['items']
        for i in range(length):
            yield (str(i), util.follow_ref(elem))
            elem = elem + 1

    def display_hint(self):
        return 'array'


class ConstParentPrinter(BasicPrinter):
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
        type = self.val['type']
        if not util.is_null(type):
            type = type['name']
        else:
            type = 'nullptr'

        special = ConstValSpecial(self.val['special'])
        if special == ConstValSpecial.ConstValSpecialRuntime:
            data = '(runtime)'
            variant = util.runtime_hint(self.val)
            hint = self.val['data'][variant]
            if hint:
                data += f' [hint = {hint}]'
        elif special == ConstValSpecial.ConstValSpecialStatic:
            variant = util.const_data(self.val)
            data = self.val['data'][variant]
        else:
            variant = None
            data = '(undefined)'

        # Special case printing
        if variant == 'x_type':
            data = data['name']

        if data is None:
            data = '(invalid)'

        data_name = 'data'
        if variant:
            data_name += '.' + variant

        return (
            ('special', self.val['special']),
            ('type', type),
            ('parent', self.val['parent']),
            ('global_refs', self.val['global_refs']),
            (data_name, data),
        )


class ZigTypePrinter(BasicPrinter):
    name = 'ZigType'

    def __init__(self, val):
        self.val = val

    def children(self):
        variant = util.type_data(self.val)

        if variant:
            data_name = 'data.' + variant
            data = self.val['data'][variant]
        else:
            data_name = 'data'
            data = '(n/a)'

        field = lambda name: (name, self.val[name])
        return (
            field('name'),
            field('id'),
            (data_name, data),
            field('type_ref'),
            field('di_type'),
            field('zero_bits'),
            field('pointer_parent'),
            field('optional_parent'),
            field('promise_parent'),
            field('promise_frame_parent'),
            field('cached_const_name_val'),
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
        full_name = util.get_basic_type(value.type)
        if not full_name:
            return None

        type_name = full_name.split('<')[0]
        try:
            return self.printers[type_name](value)
        except KeyError:
            return None


def register_printers(obj=None):
    factory = PrinterFactory('zig', zig_printers)
    gdb.printing.register_pretty_printer(obj, factory)
