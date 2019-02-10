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



def follow_ref(val):
    """Follows a pointer or reference and returns other values
    immediately."""
    try:
        return val.referenced_value()
    except gdb.error:
        return val


def runtime_hint(const_val):
    assert (ConstValSpecial(const_val['special'])
        == ConstValSpecial.ConstValSpecialRuntime)

    type = const_val['type']
    if is_null(type):
        return None

    type_id = ZigTypeId(type['id'])
    if type_id == ZigTypeId.ZigTypeIdPointer:
        variant = 'rh_ptr'
    elif type_id == ZigTypeId.ZigTypeIdErrorUnion:
        variant = 'rh_error_union'
    elif type_id == ZigTypeId.ZigTypeIdOptional:
        variant = 'rh_maybe'
    elif is_slice(type):
        variant = 'rh_slice'
    else:
        return None
    return variant


def const_data(const_val):
    assert (ConstValSpecial(const_val['special']) ==
        ConstValSpecial.ConstValSpecialStatic)

    type = const_val['type']
    if is_null(type):
        return None

    type_id = ZigTypeId(type['id'])
    if type_id in (ZigTypeId.ZigTypeIdInt, ZigTypeId.ZigTypeIdComptimeInt):
        variant = 'x_bigint'
    elif type_id == ZigTypeId.ZigTypeIdComptimeFloat:
        variant = 'x_bigfloat'
    elif type_id == ZigTypeId.ZigTypeIdFloat:
        bit_count = type['data']['floating']['bit_count']
        if bit_count == 16:
            variant = 'x_f16'
        elif bit_count == 32:
            variant = 'x_f32'
        elif bit_count == 64:
            variant = 'x_f64'
        elif bit_count == 128:
            variant = 'x_f128'
        else:
            raise ValueError(f'unexpected float size: {bit_count}')
    elif type_id == ZigTypeId.ZigTypeIdBool:
        variant = 'x_bool'
    elif type_id == ZigTypeId.ZigTypeIdBoundFn:
        variant = 'x_bound_fn'
    elif type_id == ZigTypeId.ZigTypeIdMetaType:
        variant = 'x_type'
    elif type_id == ZigTypeId.ZigTypeIdOptional:
        variant = 'x_optional'
    elif type_id == ZigTypeId.ZigTypeIdErrorUnion:
        variant = 'x_err_union'
    elif type_id == ZigTypeId.ZigTypeIdErrorSet:
        variant = 'x_err_set'
    elif type_id == ZigTypeId.ZigTypeIdEnum:
        variant = 'x_enum_tag'
    elif type_id == ZigTypeId.ZigTypeIdStruct:
        variant = 'x_struct'
    elif type_id == ZigTypeId.ZigTypeIdUnion:
        variant = 'x_union'
    elif type_id == ZigTypeId.ZigTypeIdArray:
        variant = 'x_array'
    elif type_id == ZigTypeId.ZigTypeIdPointer:
        variant = 'x_ptr'
    elif type_id == ZigTypeId.ZigTypeIdNamespace:
        variant = 'x_import'
    elif type_id == ZigTypeId.ZigTypeIdArgTuple:
        variant = 'x_arg_tuple'
    else:
        return None
    return variant
