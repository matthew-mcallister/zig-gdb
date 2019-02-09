import gdb

from .types import *


def is_null(ptr):
    """Tests if a pointer is null.

    Reads better than writing `int(ptr) == 0` all the time.
    """
    return int(ptr) == 0


def is_slice(type):
    return (ZigTypeId(type['id']) == ZigTypeId.ZigTypeIdStruct
        and bool(type['data']['structure']['is_slice']))


# From the GNU libstdc++ printer
def get_basic_type(type):
    if type.code == gdb.TYPE_CODE_REF:
        type = type.target()

    type = type.unqualified().strip_typedefs()

    return type.tag


def runtime_hint(const_val):
    assert (ConstValSpecial(const_val['special'])
        == ConstValSpecial.ConstValSpecialRuntime)

    type = const_val['type']
    if is_null(type):
        return None

    type_id = ZigTypeId(type['id'])
    if type_id == ZigTypeId.ZigTypeIdPointer:
        return 'rh_ptr'
    elif type_id == ZigTypeId.ZigTypeIdErrorUnion:
        return 'rh_error_union'
    elif type_id == ZigTypeId.ZigTypeIdOptional:
        return 'rh_maybe'
    elif is_slice(type):
        return 'rh_slice'
    else:
        return None


def const_data(const_val):
    assert (ConstValSpecial(const_val['special']) ==
        ConstValSpecial.ConstValSpecialStatic)

    type = const_val['type']
    if is_null(type):
        return None

    type_id = ZigTypeId(type['id'])
    if type_id in (ZigTypeId.ZigTypeIdInt, ZigTypeId.ZigTypeIdComptimeInt):
        return 'x_bigint'
    elif type_id == ZigTypeId.ZigTypeIdComptimeFloat:
        return 'x_bigfloat'
    elif type_id == ZigTypeId.ZigTypeIdFloat:
        bit_count = type['data']['floating']['bit_count']
        if bit_count == 16:
            return 'x_f16'
        elif bit_count == 32:
            return 'x_f32'
        elif bit_count == 64:
            return 'x_f64'
        elif bit_count == 128:
            return 'x_f128'
        else:
            raise ValueError(f'unexpected float size: {bit_count}')
    elif type_id == ZigTypeId.ZigTypeIdBool:
        return 'x_bool'
    elif type_id == ZigTypeId.ZigTypeIdBoundFn:
        return 'x_bound_fn'
    elif type_id == ZigTypeId.ZigTypeIdMetaType:
        return 'x_type'
    elif type_id == ZigTypeId.ZigTypeIdOptional:
        return 'x_optional'
    elif type_id == ZigTypeId.ZigTypeIdErrorUnion:
        return 'x_err_union'
    elif type_id == ZigTypeId.ZigTypeIdErrorSet:
        return 'x_err_set'
    elif type_id == ZigTypeId.ZigTypeIdEnum:
        return 'x_enum_tag'
    elif type_id == ZigTypeId.ZigTypeIdStruct:
        return 'x_struct'
    elif type_id == ZigTypeId.ZigTypeIdUnion:
        return 'x_struct'
    elif type_id == ZigTypeId.ZigTypeIdArray:
        return 'x_array'
    elif type_id == ZigTypeId.ZigTypeIdPointer:
        return 'x_ptr'
    elif type_id == ZigTypeId.ZigTypeIdNamespace:
        return 'x_import'
    elif type_id == ZigTypeId.ZigTypeIdArgTuple:
        return 'x_arg_tuple'
    else:
        return None
