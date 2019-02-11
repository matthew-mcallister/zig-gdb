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


def value_items(val):
    """Returns an iterator over the `key, value` pairs of fields of a
    value."""
    for field in val.type.fields():
        yield (field.name, val[field])


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

    if type_id == ZigTypeId.ZigTypeIdFloat:
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
        return variant

    variants = {
        ZigTypeId.ZigTypeIdInt: 'x_bigint',
        ZigTypeId.ZigTypeIdComptimeInt: 'x_bigint',
        ZigTypeId.ZigTypeIdComptimeFloat: 'x_bigfloat',
        ZigTypeId.ZigTypeIdBool: 'x_bool',
        ZigTypeId.ZigTypeIdBoundFn: 'x_bound_fn',
        ZigTypeId.ZigTypeIdMetaType: 'x_type',
        ZigTypeId.ZigTypeIdOptional: 'x_optional',
        ZigTypeId.ZigTypeIdErrorUnion: 'x_err_union',
        ZigTypeId.ZigTypeIdErrorSet: 'x_err_set',
        ZigTypeId.ZigTypeIdEnum: 'x_enum_tag',
        ZigTypeId.ZigTypeIdStruct: 'x_struct',
        ZigTypeId.ZigTypeIdUnion: 'x_union',
        ZigTypeId.ZigTypeIdArray: 'x_array',
        ZigTypeId.ZigTypeIdPointer: 'x_ptr',
        ZigTypeId.ZigTypeIdNamespace: 'x_import',
        ZigTypeId.ZigTypeIdArgTuple: 'x_arg_tuple',
    }
    return variants.get(type_id)


def type_data(type):
    id = ZigTypeId(type['id'])
    variants = {
        ZigTypeId.ZigTypeIdPointer: 'pointer',
        ZigTypeId.ZigTypeIdInt: 'integral',
        ZigTypeId.ZigTypeIdFloat: 'floating',
        ZigTypeId.ZigTypeIdArray: 'array',
        ZigTypeId.ZigTypeIdStruct: 'structure',
        ZigTypeId.ZigTypeIdOptional: 'maybe',
        ZigTypeId.ZigTypeIdErrorUnion: 'error_union',
        ZigTypeId.ZigTypeIdErrorSet: 'error_set',
        ZigTypeId.ZigTypeIdEnum: 'enumeration',
        ZigTypeId.ZigTypeIdUnion: 'unionation',
        ZigTypeId.ZigTypeIdFn: 'fn',
        ZigTypeId.ZigTypeIdBoundFn: 'bound_fn',
        ZigTypeId.ZigTypeIdPromise: 'promise',
        ZigTypeId.ZigTypeIdVector: 'vector',
    }
    return variants.get(id)


def cast_instruction(inst):
    id = IrInstructionId(inst['id'])
    variants = {
        IrInstructionId.IrInstructionIdDeclVarSrc: 'IrInstructionDeclVarSrc',
        IrInstructionId.IrInstructionIdDeclVarGen: 'IrInstructionDeclVarGen',
        IrInstructionId.IrInstructionIdBr: 'IrInstructionBr',
        IrInstructionId.IrInstructionIdCondBr: 'IrInstructionCondBr',
        IrInstructionId.IrInstructionIdSwitchBr: 'IrInstructionSwitchBr',
        IrInstructionId.IrInstructionIdSwitchVar: 'IrInstructionSwitchVar',
        IrInstructionId.IrInstructionIdSwitchTarget: 'IrInstructionSwitchTarget',
        IrInstructionId.IrInstructionIdPhi: 'IrInstructionPhi',
        IrInstructionId.IrInstructionIdUnOp: 'IrInstructionUnOp',
        IrInstructionId.IrInstructionIdBinOp: 'IrInstructionBinOp',
        IrInstructionId.IrInstructionIdLoadPtr: 'IrInstructionLoadPtr',
        IrInstructionId.IrInstructionIdStorePtr: 'IrInstructionStorePtr',
        IrInstructionId.IrInstructionIdFieldPtr: 'IrInstructionFieldPtr',
        IrInstructionId.IrInstructionIdStructFieldPtr: 'IrInstructionStructFieldPtr',
        IrInstructionId.IrInstructionIdUnionFieldPtr: 'IrInstructionUnionFieldPtr',
        IrInstructionId.IrInstructionIdElemPtr: 'IrInstructionElemPtr',
        IrInstructionId.IrInstructionIdVarPtr: 'IrInstructionVarPtr',
        IrInstructionId.IrInstructionIdCall: 'IrInstructionCall',
        IrInstructionId.IrInstructionIdConst: 'IrInstructionConst',
        IrInstructionId.IrInstructionIdReturn: 'IrInstructionReturn',
        IrInstructionId.IrInstructionIdCast: 'IrInstructionCast',
        IrInstructionId.IrInstructionIdContainerInitList: 'IrInstructionContainerInitList',
        IrInstructionId.IrInstructionIdContainerInitFields: 'IrInstructionContainerInitFields',
        IrInstructionId.IrInstructionIdStructInit: 'IrInstructionStructInit',
        IrInstructionId.IrInstructionIdUnionInit: 'IrInstructionUnionInit',
        IrInstructionId.IrInstructionIdUnreachable: 'IrInstructionUnreachable',
        IrInstructionId.IrInstructionIdTypeOf: 'IrInstructionTypeOf',
        IrInstructionId.IrInstructionIdToPtrType: 'IrInstructionToPtrType',
        IrInstructionId.IrInstructionIdPtrTypeChild: 'IrInstructionPtrTypeChild',
        IrInstructionId.IrInstructionIdSetCold: 'IrInstructionSetCold',
        IrInstructionId.IrInstructionIdSetRuntimeSafety: 'IrInstructionSetRuntimeSafety',
        IrInstructionId.IrInstructionIdSetFloatMode: 'IrInstructionSetFloatMode',
        IrInstructionId.IrInstructionIdArrayType: 'IrInstructionArrayType',
        IrInstructionId.IrInstructionIdPromiseType: 'IrInstructionPromiseType',
        IrInstructionId.IrInstructionIdSliceType: 'IrInstructionSliceType',
        IrInstructionId.IrInstructionIdAsm: 'IrInstructionAsm',
        IrInstructionId.IrInstructionIdSizeOf: 'IrInstructionSizeOf',
        IrInstructionId.IrInstructionIdTestNonNull: 'IrInstructionTestNonNull',
        IrInstructionId.IrInstructionIdOptionalUnwrapPtr: 'IrInstructionOptionalUnwrapPtr',
        IrInstructionId.IrInstructionIdOptionalWrap: 'IrInstructionOptionalWrap',
        IrInstructionId.IrInstructionIdUnionTag: 'IrInstructionUnionTag',
        IrInstructionId.IrInstructionIdClz: 'IrInstructionClz',
        IrInstructionId.IrInstructionIdCtz: 'IrInstructionCtz',
        IrInstructionId.IrInstructionIdPopCount: 'IrInstructionPopCount',
        IrInstructionId.IrInstructionIdImport: 'IrInstructionImport',
        IrInstructionId.IrInstructionIdCImport: 'IrInstructionCImport',
        IrInstructionId.IrInstructionIdCInclude: 'IrInstructionCInclude',
        IrInstructionId.IrInstructionIdCDefine: 'IrInstructionCDefine',
        IrInstructionId.IrInstructionIdCUndef: 'IrInstructionCUndef',
        IrInstructionId.IrInstructionIdRef: 'IrInstructionRef',
        IrInstructionId.IrInstructionIdCompileErr: 'IrInstructionCompileErr',
        IrInstructionId.IrInstructionIdCompileLog: 'IrInstructionCompileLog',
        IrInstructionId.IrInstructionIdErrName: 'IrInstructionErrName',
        IrInstructionId.IrInstructionIdEmbedFile: 'IrInstructionEmbedFile',
        IrInstructionId.IrInstructionIdCmpxchgSrc: 'IrInstructionCmpxchgSrc',
        IrInstructionId.IrInstructionIdCmpxchgGen: 'IrInstructionCmpxchgGen',
        IrInstructionId.IrInstructionIdFence: 'IrInstructionFence',
        IrInstructionId.IrInstructionIdTruncate: 'IrInstructionTruncate',
        IrInstructionId.IrInstructionIdIntCast: 'IrInstructionIntCast',
        IrInstructionId.IrInstructionIdFloatCast: 'IrInstructionFloatCast',
        IrInstructionId.IrInstructionIdIntToFloat: 'IrInstructionIntToFloat',
        IrInstructionId.IrInstructionIdFloatToInt: 'IrInstructionFloatToInt',
        IrInstructionId.IrInstructionIdBoolToInt: 'IrInstructionBoolToInt',
        IrInstructionId.IrInstructionIdIntType: 'IrInstructionIntType',
        IrInstructionId.IrInstructionIdVectorType: 'IrInstructionVectorType',
        IrInstructionId.IrInstructionIdBoolNot: 'IrInstructionBoolNot',
        IrInstructionId.IrInstructionIdMemset: 'IrInstructionMemset',
        IrInstructionId.IrInstructionIdMemcpy: 'IrInstructionMemcpy',
        IrInstructionId.IrInstructionIdSlice: 'IrInstructionSlice',
        IrInstructionId.IrInstructionIdMemberCount: 'IrInstructionMemberCount',
        IrInstructionId.IrInstructionIdMemberType: 'IrInstructionMemberType',
        IrInstructionId.IrInstructionIdMemberName: 'IrInstructionMemberName',
        IrInstructionId.IrInstructionIdBreakpoint: 'IrInstructionBreakpoint',
        IrInstructionId.IrInstructionIdReturnAddress: 'IrInstructionReturnAddress',
        IrInstructionId.IrInstructionIdFrameAddress: 'IrInstructionFrameAddress',
        IrInstructionId.IrInstructionIdHandle: 'IrInstructionHandle',
        IrInstructionId.IrInstructionIdAlignOf: 'IrInstructionAlignOf',
        IrInstructionId.IrInstructionIdOverflowOp: 'IrInstructionOverflowOp',
        IrInstructionId.IrInstructionIdTestErr: 'IrInstructionTestErr',
        IrInstructionId.IrInstructionIdUnwrapErrCode: 'IrInstructionUnwrapErrCode',
        IrInstructionId.IrInstructionIdUnwrapErrPayload: 'IrInstructionUnwrapErrPayload',
        IrInstructionId.IrInstructionIdErrWrapCode: 'IrInstructionErrWrapCode',
        IrInstructionId.IrInstructionIdErrWrapPayload: 'IrInstructionErrWrapPayload',
        IrInstructionId.IrInstructionIdFnProto: 'IrInstructionFnProto',
        IrInstructionId.IrInstructionIdTestComptime: 'IrInstructionTestComptime',
        IrInstructionId.IrInstructionIdPtrCastSrc: 'IrInstructionPtrCastSrc',
        IrInstructionId.IrInstructionIdPtrCastGen: 'IrInstructionPtrCastGen',
        IrInstructionId.IrInstructionIdBitCast: 'IrInstructionBitCast',
        IrInstructionId.IrInstructionIdWidenOrShorten: 'IrInstructionWidenOrShorten',
        IrInstructionId.IrInstructionIdIntToPtr: 'IrInstructionIntToPtr',
        IrInstructionId.IrInstructionIdPtrToInt: 'IrInstructionPtrToInt',
        IrInstructionId.IrInstructionIdIntToEnum: 'IrInstructionIntToEnum',
        IrInstructionId.IrInstructionIdEnumToInt: 'IrInstructionEnumToInt',
        IrInstructionId.IrInstructionIdIntToErr: 'IrInstructionIntToErr',
        IrInstructionId.IrInstructionIdErrToInt: 'IrInstructionErrToInt',
        IrInstructionId.IrInstructionIdCheckSwitchProngs: 'IrInstructionCheckSwitchProngs',
        IrInstructionId.IrInstructionIdCheckStatementIsVoid: 'IrInstructionCheckStatementIsVoid',
        IrInstructionId.IrInstructionIdTypeName: 'IrInstructionTypeName',
        IrInstructionId.IrInstructionIdDeclRef: 'IrInstructionDeclRef',
        IrInstructionId.IrInstructionIdPanic: 'IrInstructionPanic',
        IrInstructionId.IrInstructionIdTagName: 'IrInstructionTagName',
        IrInstructionId.IrInstructionIdTagType: 'IrInstructionTagType',
        IrInstructionId.IrInstructionIdFieldParentPtr: 'IrInstructionFieldParentPtr',
        IrInstructionId.IrInstructionIdByteOffsetOf: 'IrInstructionByteOffsetOf',
        IrInstructionId.IrInstructionIdBitOffsetOf: 'IrInstructionBitOffsetOf',
        IrInstructionId.IrInstructionIdTypeInfo: 'IrInstructionTypeInfo',
        IrInstructionId.IrInstructionIdTypeId: 'IrInstructionTypeId',
        IrInstructionId.IrInstructionIdSetEvalBranchQuota: 'IrInstructionSetEvalBranchQuota',
        IrInstructionId.IrInstructionIdPtrType: 'IrInstructionPtrType',
        IrInstructionId.IrInstructionIdAlignCast: 'IrInstructionAlignCast',
        IrInstructionId.IrInstructionIdOpaqueType: 'IrInstructionOpaqueType',
        IrInstructionId.IrInstructionIdSetAlignStack: 'IrInstructionSetAlignStack',
        IrInstructionId.IrInstructionIdArgType: 'IrInstructionArgType',
        IrInstructionId.IrInstructionIdExport: 'IrInstructionExport',
        IrInstructionId.IrInstructionIdErrorReturnTrace: 'IrInstructionErrorReturnTrace',
        IrInstructionId.IrInstructionIdErrorUnion: 'IrInstructionErrorUnion',
        IrInstructionId.IrInstructionIdCancel: 'IrInstructionCancel',
        IrInstructionId.IrInstructionIdGetImplicitAllocator: 'IrInstructionGetImplicitAllocator',
        IrInstructionId.IrInstructionIdCoroId: 'IrInstructionCoroId',
        IrInstructionId.IrInstructionIdCoroAlloc: 'IrInstructionCoroAlloc',
        IrInstructionId.IrInstructionIdCoroSize: 'IrInstructionCoroSize',
        IrInstructionId.IrInstructionIdCoroBegin: 'IrInstructionCoroBegin',
        IrInstructionId.IrInstructionIdCoroAllocFail: 'IrInstructionCoroAllocFail',
        IrInstructionId.IrInstructionIdCoroSuspend: 'IrInstructionCoroSuspend',
        IrInstructionId.IrInstructionIdCoroEnd: 'IrInstructionCoroEnd',
        IrInstructionId.IrInstructionIdCoroFree: 'IrInstructionCoroFree',
        IrInstructionId.IrInstructionIdCoroResume: 'IrInstructionCoroResume',
        IrInstructionId.IrInstructionIdCoroSave: 'IrInstructionCoroSave',
        IrInstructionId.IrInstructionIdCoroPromise: 'IrInstructionCoroPromise',
        IrInstructionId.IrInstructionIdCoroAllocHelper: 'IrInstructionCoroAllocHelper',
        IrInstructionId.IrInstructionIdAtomicRmw: 'IrInstructionAtomicRmw',
        IrInstructionId.IrInstructionIdAtomicLoad: 'IrInstructionAtomicLoad',
        IrInstructionId.IrInstructionIdPromiseResultType: 'IrInstructionPromiseResultType',
        IrInstructionId.IrInstructionIdAwaitBookkeeping: 'IrInstructionAwaitBookkeeping',
        IrInstructionId.IrInstructionIdSaveErrRetAddr: 'IrInstructionSaveErrRetAddr',
        IrInstructionId.IrInstructionIdAddImplicitReturnType: 'IrInstructionAddImplicitReturnType',
        IrInstructionId.IrInstructionIdMergeErrRetTraces: 'IrInstructionMergeErrRetTraces',
        IrInstructionId.IrInstructionIdMarkErrRetTracePtr: 'IrInstructionMarkErrRetTracePtr',
        IrInstructionId.IrInstructionIdSqrt: 'IrInstructionSqrt',
        IrInstructionId.IrInstructionIdBswap: 'IrInstructionBswap',
        IrInstructionId.IrInstructionIdBitReverse: 'IrInstructionBitReverse',
        IrInstructionId.IrInstructionIdErrSetCast: 'IrInstructionErrSetCast',
        IrInstructionId.IrInstructionIdToBytes: 'IrInstructionToBytes',
        IrInstructionId.IrInstructionIdFromBytes: 'IrInstructionFromBytes',
        IrInstructionId.IrInstructionIdCheckRuntimeScope: 'IrInstructionCheckRuntimeScope',
        IrInstructionId.IrInstructionIdVectorToArray: 'IrInstructionVectorToArray',
        IrInstructionId.IrInstructionIdArrayToVector: 'IrInstructionArrayToVector',
    }
    type_name = variants.get(id)
    if not type_name:
        return None

    casted_type = gdb.lookup_type(type_name)
    return inst.address.reinterpret_cast(casted_type.pointer())
