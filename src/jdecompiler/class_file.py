import pprint
from dataclasses import dataclass
from enum import IntEnum
from io import BytesIO
from pprint import pformat
from typing import Any
from typing import Optional
from typing import Self


class ConstantType(IntEnum):
    UTF_8 = 1
    INTEGER = 3
    FLOAT = 4
    LONG = 5
    DOUBLE = 6
    CLASS = 7
    STRING = 8
    FIELD_REF = 9
    METHOD_REF = 10
    INTERFACE_METHOD_REF = 11
    NAME_AND_TYPE = 12
    METHOD_HANDLE = 15
    METHOD_TYPE = 16
    INVOKE_DYNAMIC = 18


class Opcode(IntEnum):
    NOP = 0
    ICONST_0 = 0x03
    ICONST_1 = 0x04
    ICONST_5 = 0x08
    LDC = 0x12
    LDC2_W = 0x14
    ILOAD_2 = 0x1C
    ILOAD_3 = 0x1D
    ALOAD_0 = 0x2A
    ASTORE = 0x3A
    ISTORE_1 = 0x3C
    ISTORE_2 = 0x3D
    ISTORE_3 = 0x3E
    LSTORE_1 = 0x40
    ASTORE_0 = 0x4B
    DUPLICATE = 0x59
    IADD = 0x60
    DMUL = 0x6B
    DOUBLE_TO_INT = 0x8E
    RETURN = 0xB1
    GET_STATIC = 0xB2
    INVOKE_VIRTUAL = 0xB6
    INVOKE_SPECIAL = 0xB7
    INVOKE_STATIC = 0xB8
    INVOKE_DYNAMIC = 0xBA
    NEW = 0xBB


@dataclass
class Instruction:
    opeocde: Opcode


@dataclass
class CodeAttribute:
    max_stack: int
    max_locals: int
    code: bytes
    exception_table: list
    attributes: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        max_stack = JavaClassFile.read_u2(buffer)
        max_locals = JavaClassFile.read_u2(buffer)
        code_length = JavaClassFile.read_u4(buffer)
        code = cls.read_code(buffer, code_length)
        exception_table_length = JavaClassFile.read_u2(buffer)

        exceptions = []
        for _ in range(exception_table_length):
            start_pc = JavaClassFile.read_u2(buffer)
            end_pc = JavaClassFile.read_u2(buffer)
            handler_pc = JavaClassFile.read_u2(buffer)
            catch_type = JavaClassFile.read_u2(buffer)
            exceptions.append(
                (
                    start_pc,
                    end_pc,
                    handler_pc,
                    catch_type,
                )
            )

        attribute_count = JavaClassFile.read_u2(buffer)
        attributes = [
            read_attribute(buffer, constant_pool) for _ in range(attribute_count)
        ]

        return cls(max_stack, max_locals, code, exceptions, attributes)

    @staticmethod
    def read_code(buffer, length):
        instructions = []

        current = 0
        while current < length:
            instruction = JavaClassFile.read_u1(buffer)
            current += 1

            if instruction == Opcode.NOP:
                instructions.append(Instruction(Opcode.NOP))
            elif instruction == Opcode.ALOAD_0:
                instructions.append(Instruction(Opcode.ALOAD_0))
            elif instruction == Opcode.RETURN:
                instructions.append(Instruction(Opcode.RETURN))
            elif instruction == Opcode.DMUL:
                instructions.append(Instruction(Opcode.DMUL))
            elif instruction == Opcode.DOUBLE_TO_INT:
                instructions.append(Instruction(Opcode.DOUBLE_TO_INT))
            elif instruction == Opcode.IADD:
                instructions.append(Instruction(Opcode.IADD))
            elif instruction == Opcode.ISTORE_1:
                instructions.append(Instruction(Opcode.ISTORE_1))
            elif instruction == Opcode.ISTORE_2:
                instructions.append(Instruction(Opcode.ISTORE_2))
            elif instruction == Opcode.ICONST_5:
                instructions.append(Instruction(Opcode.ICONST_5))
            elif instruction == Opcode.ILOAD_2:
                instructions.append(Instruction(Opcode.ILOAD_2))
            elif instruction == Opcode.ILOAD_3:
                instructions.append(Instruction(Opcode.ILOAD_3))
            elif instruction == Opcode.INVOKE_DYNAMIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                zero_byte_1 = JavaClassFile.read_u1(buffer)
                current += 1
                zero_byte_2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.INVOKE_DYNAMIC))
            elif instruction == Opcode.INVOKE_SPECIAL:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.INVOKE_SPECIAL))
            elif instruction == Opcode.LDC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.LDC))
            elif instruction == Opcode.ASTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.ASTORE))
            elif instruction == Opcode.LDC2_W:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.LDC2_W))
            elif instruction == Opcode.INVOKE_STATIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.INVOKE_STATIC))
            elif instruction == Opcode.INVOKE_VIRTUAL:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.INVOKE_VIRTUAL))
            elif instruction == Opcode.RETURN:
                instructions.append(Instruction(Opcode.RETURN))
            elif instruction == Opcode.ISTORE_3:
                instructions.append(Instruction(Opcode.ISTORE_3))
            elif instruction == Opcode.DUPLICATE:
                instructions.append(Instruction(Opcode.DUPLICATE))
            elif instruction == Opcode.ICONST_1:
                instructions.append(Instruction(Opcode.ICONST_1))
            elif instruction == Opcode.ICONST_0:
                instructions.append(Instruction(Opcode.ICONST_0))
            elif instruction == Opcode.LSTORE_1:
                instructions.append(Instruction(Opcode.LSTORE_1))
            elif instruction == Opcode.ASTORE_0:
                instructions.append(Instruction(Opcode.ASTORE_0))
            elif instruction == Opcode.NEW:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.NEW))
            elif instruction == Opcode.GET_STATIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                current += 1
                idx_byte2 = JavaClassFile.read_u1(buffer)
                current += 1
                instructions.append(Instruction(Opcode.GET_STATIC))
            else:
                raise NotImplementedError(f"{hex(instruction)} {current} {length}")

        return instructions


@dataclass
class LineNumberTableAttribute:
    line_numbers: list[tuple[int, int]]

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        num_enteries = JavaClassFile.read_u2(buffer)
        line_numbers = []

        for _ in range(num_enteries):
            start_pc = JavaClassFile.read_u2(buffer)
            end_pc = JavaClassFile.read_u2(buffer)
            line_numbers.append((start_pc, end_pc))

        return cls(line_numbers)


@dataclass
class SourceFileAttribute:
    name: str

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        source_file_index = JavaClassFile.read_u2(buffer)
        constant_type, _, data = constant_pool[source_file_index]
        assert constant_type == ConstantType.UTF_8

        return cls(data)


@dataclass
class BootstrapMethodsAttribute:
    bootstrap_methods: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        num_bootstrap_methods = JavaClassFile.read_u2(buffer)

        bootstrap_methods = []
        for _ in range(num_bootstrap_methods):
            bootstrap_method_ref = JavaClassFile.read_u2(buffer)
            num_bootstrap_args = JavaClassFile.read_u2(buffer)
            bootstrap_methods.append(
                [
                    bootstrap_method_ref,
                    [JavaClassFile.read_u2(buffer) for _ in range(num_bootstrap_args)],
                ]
            )

        return cls(bootstrap_methods)


@dataclass
class InnerClassesAttribute:
    inner_classes: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        num_inner_classes = JavaClassFile.read_u2(buffer)

        inner_classes = []
        for _ in range(num_inner_classes):
            inner_class_info_index = JavaClassFile.read_u2(buffer)
            outer_class_info_index = JavaClassFile.read_u2(buffer)
            inner_name_indx = JavaClassFile.read_u2(buffer)
            inner_class_class_access_flags = JavaClassFile.read_u2(buffer)
            inner_classes.append(
                (
                    inner_class_info_index,
                    outer_class_info_index,
                    inner_name_indx,
                    inner_class_class_access_flags,
                )
            )

        return cls(inner_classes)


@dataclass
class StackMapTableAttribute:
    stack_frames: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        # TODO calculate the stack layout given the function descriptor as too
        num_frames = JavaClassFile.read_u2(buffer)

        frames: list = []
        for _ in range(num_frames):
            tag = JavaClassFile.read_u1(buffer)

            if 0 <= tag <= 63:
                frames.append("SAME FRAME")

            elif 64 <= tag <= 127:
                frames.append(
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                )

            elif 128 <= tag <= 246:
                raise NotImplementedError

            elif tag == 247:
                offset_delta = JavaClassFile.read_u2(buffer)
                frames.append(
                    (
                        offset_delta,
                        StackMapTableAttribute._read_verification_type_info(
                            buffer, constant_pool
                        ),
                    )
                )

            elif 248 <= tag <= 250:
                offset_delta = JavaClassFile.read_u2(buffer)
                frames.append(offset_delta)

            elif tag == 251:
                offset_delta = JavaClassFile.read_u2(buffer)

            elif 252 <= tag <= 254:
                offset_delta = JavaClassFile.read_u2(buffer)
                locals = [
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                    for _ in range(tag - 251)
                ]

            elif tag == 255:
                offset_delta = JavaClassFile.read_u2(buffer)
                num_locals = JavaClassFile.read_u2(buffer)
                locals = [
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                    for _ in range(num_locals)
                ]
                num_tack_items = JavaClassFile.read_u2(buffer)
                locals = [
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                    for _ in range(num_tack_items)
                ]

            else:
                raise ValueError

        return cls(frames)

    @staticmethod
    def _read_verification_type_info(buffer, constant_pool):
        tag = JavaClassFile.read_u1(buffer)

        if tag == 0:
            return "ITEM_top"
        elif tag == 1:
            return "ITEM_Integer"
        elif tag == 2:
            return "ITEM_Float"
        elif tag == 4:
            return "ITEM_Long"
        elif tag == 3:
            return "ITEM_Double"
        elif tag == 5:
            return "ITEM_NULL"
        elif tag == 6:
            return "ITEM_UninitialisedThis"
        elif tag == 7:
            return "ITEM_Object", constant_pool[JavaClassFile.read_u2(buffer)]
        elif tag == 8:
            return "ITEM_VeriableInfo", JavaClassFile.read_u2(buffer)
        else:
            raise ValueError(tag)


def read_attribute(buffer: BytesIO, constant_pool: dict[int, tuple]):
    name_index = JavaClassFile.read_u2(buffer)
    name_type, _, name = constant_pool[name_index]
    assert name_type == ConstantType.UTF_8

    JavaClassFile.read_u4(buffer)  # length of attribute, not needed

    if name == b"Code":
        return CodeAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == b"LineNumberTable":
        return LineNumberTableAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == b"StackMapTable":
        return StackMapTableAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == b"SourceFile":
        return SourceFileAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == b"BootstrapMethods":
        return BootstrapMethodsAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == b"InnerClasses":
        return InnerClassesAttribute.from_buffer_and_pool(buffer, constant_pool)

    else:
        raise NotImplementedError(name)


@dataclass
class Method:
    access_flags: int
    name: str
    descriptor: str
    attributes: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        # pprint.pprint(constant_pool)
        access_flags = JavaClassFile.read_u2(buffer)

        name_type, _, name = constant_pool[JavaClassFile.read_u2(buffer)]
        assert name_type == ConstantType.UTF_8, f"{name_type} {name!r}"

        name_type, _, descriptor = constant_pool[JavaClassFile.read_u2(buffer)]
        assert name_type == ConstantType.UTF_8

        attribute_count = JavaClassFile.read_u2(buffer)

        attributes = []
        for _ in range(attribute_count):
            attributes.append(read_attribute(buffer, constant_pool))

        return cls(
            access_flags=access_flags,
            name=name,
            descriptor=descriptor,
            attributes=attributes,
        )


@dataclass
class JavaClassFile:
    magic: bytes  # magic number at start of java class file must be 0xCAFEBABE
    minor_version: int
    major_version: int
    constant_pool: list
    access_flags: int
    this_class: int
    super_class: int
    interfaces: list
    field_info: list
    methods: list
    attributes: list

    @staticmethod
    def read_u4(buffer: BytesIO):
        return int.from_bytes(buffer.read(4), byteorder="big", signed=False)

    @staticmethod
    def read_u2(buffer: BytesIO):
        return int.from_bytes(buffer.read(2), byteorder="big", signed=False)

    @staticmethod
    def read_u1(buffer: BytesIO):
        return int.from_bytes(buffer.read(1), byteorder="big", signed=False)

    @classmethod
    def from_file(cls, fp):
        with open(fp, "rb") as f:
            return cls.from_buffer(f)

    @staticmethod
    def read_constant_pool(buffer, count):
        enteries: dict[int, tuple[ConstantType, Any, Any]] = {}

        key = 0
        while key < count:
            key += 1
            tag = JavaClassFile.read_u1(buffer)

            if tag == ConstantType.UTF_8:
                # Reads a UTF-8 String
                length = JavaClassFile.read_u2(buffer)
                enteries[key] = (ConstantType.UTF_8, 0, buffer.read(length))

            elif tag == ConstantType.DOUBLE:
                # Reads a number of type double
                enteries[key] = (
                    ConstantType.DOUBLE,
                    JavaClassFile.read_u4(buffer),
                    JavaClassFile.read_u4(buffer),
                )
                # This entery taks up two constant pool enteries
                # so the key is incremented here
                key += 1

            elif tag == ConstantType.CLASS:
                # Class info contains a string with the name of the class
                enteries[key] = (
                    ConstantType.CLASS,
                    None,
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.STRING:
                # String points to a UTF-8 string
                enteries[key] = (
                    ConstantType.STRING,
                    None,
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.FIELD_REF:
                # Points to a class and field belonging to that class
                enteries[key] = (
                    ConstantType.FIELD_REF,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.METHOD_REF:
                # Points to a class and method belonging to that class
                enteries[key] = (
                    ConstantType.METHOD_REF,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.INTERFACE_METHOD_REF:
                # Points to a class and interface used in that class
                enteries[key] = (
                    ConstantType.INTERFACE_METHOD_REF,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.NAME_AND_TYPE:
                # Points to a string and type
                enteries[key] = (
                    ConstantType.NAME_AND_TYPE,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.METHOD_HANDLE:
                enteries[key] = (
                    ConstantType.METHOD_HANDLE,
                    JavaClassFile.read_u1(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.INVOKE_DYNAMIC:
                enteries[key] = (
                    ConstantType.INVOKE_DYNAMIC,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            else:
                raise NotImplementedError(tag)

        return enteries

    @classmethod
    def from_buffer(cls, buffer) -> Self:
        magic = buffer.read(4)

        minor_version = cls.read_u2(buffer)
        major_version = cls.read_u2(buffer)

        constant_pool_count = cls.read_u2(buffer)
        constant_pool = cls.read_constant_pool(buffer, constant_pool_count - 1)

        access_flags = cls.read_u2(buffer)

        data_type, _, this_class = constant_pool.get(cls.read_u2(buffer))
        assert data_type == ConstantType.CLASS

        data_type, _, super_class = constant_pool.get(cls.read_u2(buffer))
        assert data_type == ConstantType.CLASS

        interface_count = cls.read_u2(buffer)
        interfaces: list = []
        for _ in range(interface_count):
            raise NotImplementedError

        fields_count = cls.read_u2(buffer)
        fields: list = []
        for _ in range(fields_count):
            raise NotImplementedError

        methods_count = cls.read_u2(buffer)
        methods = []
        for _ in range(methods_count):
            methods.append(Method.from_buffer_and_pool(buffer, constant_pool))

        attributes_count = cls.read_u2(buffer)
        attributes = []
        for _ in range(attributes_count):
            attributes.append(read_attribute(buffer, constant_pool))

        return cls(
            magic=magic,
            minor_version=minor_version,
            major_version=major_version,
            constant_pool=constant_pool,
            access_flags=access_flags,
            this_class=this_class,
            super_class=super_class,
            interfaces=interfaces,
            field_info=fields,
            methods=methods,
            attributes=attributes,
        )
