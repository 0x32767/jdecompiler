import pprint
from dataclasses import dataclass
from enum import IntEnum
from io import BytesIO
from io import StringIO
from pprint import pformat
from typing import Any
from typing import Optional
from typing import Self


class ClassAccessFlags(IntEnum):
    ACC_PUBLIC = 0x0001
    ACC_FINAL = 0x0010
    ACC_SUPER = 0x0020
    ACC_INTERFACE = 0x0200
    ACC_ABSTRACT = 0x0400
    ACC_SYNTHETIC = 0x1000
    ACC_ANNOTATION = 0x2000
    ACC_ENUM = 0x4000

    @classmethod
    def parse_flags(cls, flags):
        return [
            name for name, value in cls._value2member_map_.items() if flags & value != 0
        ]


class MethodAccessFlags(IntEnum):
    ACC_PUBLIC = 0x0001
    ACC_PRIVATE = 0x0002
    ACC_PROTECTED = 0x0004
    ACC_STATIC = 0x0008
    ACC_FINAL = 0x0010
    ACC_SYNCHRONIZED = 0x0020
    ACC_BRIDGE = 0x0040
    ACC_VARARGS = 0x0080
    ACC_NATIVE = 0x0100
    ACC_ABSTRACT = 0x0400
    ACC_STRICT = 0x0800
    ACC_SYNTHETIC = 0x1000

    @classmethod
    def parse_flags(cls, flags):
        return [
            name for value, name in cls._value2member_map_.items() if flags & value != 0
        ]


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
    ICONST_4 = 0x07
    ICONST_5 = 0x08
    DCONST_0 = 0x0E
    DCONST_1 = 0x0F
    LDC = 0x12
    LDC2_W = 0x14
    ILOAD = 0x15
    DLOAD = 0x18
    ALOAD = 0x19
    ILOAD_1 = 0x1B
    ILOAD_2 = 0x1C
    ILOAD_3 = 0x1D
    ALOAD_0 = 0x2A
    ALOAD_1 = 0x2B
    ALOAD_2 = 0x2C
    ALOAD_3 = 0x2D
    ISTORE = 0x36
    DSTORE = 0x39
    ASTORE = 0x3A
    ISTORE_1 = 0x3C
    ISTORE_2 = 0x3D
    ISTORE_3 = 0x3E
    LSTORE_1 = 0x40
    ASTORE_0 = 0x4B
    ASTORE_1 = 0x4C
    ASTORE_2 = 0x4D
    ASTORE_3 = 0x4E
    POP = 0x57
    DUPLICATE = 0x59
    IADD = 0x60
    DADD = 0x63
    DMUL = 0x6B
    LONG_TO_FLOAT = 0x89
    DOUBLE_TO_INT = 0x8E
    DCMPG = 0x98
    IF_EQ = 0x99
    IF_GE = 0x9C
    IF_ICMPNE = 0xA0
    IF_ICMPGE = 0xA2
    GOTO = 0xA7
    IINC = 0x84
    RETURN = 0xB1
    GET_STATIC = 0xB2
    INVOKE_VIRTUAL = 0xB6
    INVOKE_SPECIAL = 0xB7
    INVOKE_STATIC = 0xB8
    INVOKE_INTERFACE = 0xB9
    INVOKE_DYNAMIC = 0xBA
    NEW = 0xBB
    CHECK_CAST = 0xC0

    @classmethod
    def get_name(cls, value):
        return str(cls._value2member_map_[value].name)


def const_pool_get_utf8(constant_pool, index):
    data_type, _, value = constant_pool[index]
    assert data_type == ConstantType.UTF_8
    return value.decode()


def const_pool_get_class_ref(constant_pool, index):
    data_type, _, value = constant_pool[index]
    assert data_type == ConstantType.CLASS
    return const_pool_get_utf8(constant_pool, value)


def const_pool_get_name_and_type(constant_pool, index):
    data_type, name_index, descriptor_index = constant_pool[index]
    assert data_type == ConstantType.NAME_AND_TYPE
    return (
        const_pool_get_utf8(constant_pool, name_index)
        + " type("
        + const_pool_get_utf8(constant_pool, descriptor_index)
        + ")"
    )


def const_pool_get_field_ref(constant_pool, index):
    data_type, class_index, name_and_type = constant_pool[index]
    assert data_type == ConstantType.FIELD_REF
    return (
        const_pool_get_class_ref(constant_pool, class_index)
        + "."
        + const_pool_get_name_and_type(constant_pool, name_and_type)
    )


def const_pool_get_method_ref(constant_pool, index):
    data_type, class_index, name_and_type = constant_pool[index]
    assert data_type == ConstantType.METHOD_REF
    return (
        const_pool_get_class_ref(constant_pool, class_index)
        + "."
        + const_pool_get_name_and_type(constant_pool, name_and_type)
    )


@dataclass
class Instruction:
    opcode: Opcode
    offset: int
    operands: list
    line_number: int = 0

    def nice_print(self, indent=0):
        print(
            " " * (indent + 2)
            + f"{self.line_number:<3} ({self.offset:<4}) {Opcode.get_name(self.opcode):<20} {','.join(map(str, self.operands))}"
        )


@dataclass
class CodeAttribute:
    max_stack: int
    max_locals: int
    instructions: list[Instruction]
    exception_table: list
    attributes: dict

    def set_line_numbers(self, line_numbers: LineNumberTableAttribute):
        for instruction in self.instructions:
            instruction.line_number = line_numbers.line_for_instruction_offset(
                instruction.offset
            )

    def set_bootstrap_methods(self, constant_pool, bootstrap_methods):
        for instruction in self.instructions:
            if instruction.opcode != Opcode.INVOKE_DYNAMIC:
                continue

            ((op_type, bootstrap_idx, method_descriptor),) = instruction.operands
            assert op_type == ConstantType.INVOKE_DYNAMIC
            instruction.operands = [
                bootstrap_methods.get(bootstrap_idx),
                const_pool_get_name_and_type(constant_pool, method_descriptor),
            ]

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        max_stack = JavaClassFile.read_u2(buffer)
        max_locals = JavaClassFile.read_u2(buffer)
        code_length = JavaClassFile.read_u4(buffer)
        code = cls.read_code(buffer, code_length, constant_pool)
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
        attributes = {}
        for _ in range(attribute_count):
            attr_name, attr_data = read_attribute(buffer, constant_pool)
            attributes[attr_name] = attr_data

        instance = cls(max_stack, max_locals, code, exceptions, attributes)
        instance.set_line_numbers(attributes["LineNumberTable"])
        return instance

    @staticmethod
    def read_code(buffer, length, constant_pool):
        instructions = []

        current = 0
        while current < length:
            instruction = JavaClassFile.read_u1(buffer)

            if instruction == Opcode.NOP:
                instructions.append(Instruction(Opcode.NOP, current, []))
            elif instruction == Opcode.ALOAD_0:
                instructions.append(Instruction(Opcode.ALOAD_0, current, []))
            elif instruction == Opcode.ALOAD_1:
                instructions.append(Instruction(Opcode.ALOAD_1, current, []))
            elif instruction == Opcode.ALOAD_2:
                instructions.append(Instruction(Opcode.ALOAD_2, current, []))
            elif instruction == Opcode.ALOAD_3:
                instructions.append(Instruction(Opcode.ALOAD_3, current, []))
            elif instruction == Opcode.RETURN:
                instructions.append(Instruction(Opcode.RETURN, current, []))
            elif instruction == Opcode.DMUL:
                instructions.append(Instruction(Opcode.DMUL, current, []))
            elif instruction == Opcode.DOUBLE_TO_INT:
                instructions.append(Instruction(Opcode.DOUBLE_TO_INT, current, []))
            elif instruction == Opcode.LONG_TO_FLOAT:
                instructions.append(Instruction(Opcode.LONG_TO_FLOAT, current, []))
            elif instruction == Opcode.DCMPG:
                instructions.append(Instruction(Opcode.DCMPG, current, []))
            elif instruction == Opcode.IADD:
                instructions.append(Instruction(Opcode.IADD, current, []))
            elif instruction == Opcode.POP:
                instructions.append(Instruction(Opcode.POP, current, []))
            elif instruction == Opcode.DCONST_1:
                instructions.append(Instruction(Opcode.DCONST_1, current, []))
            elif instruction == Opcode.DCONST_0:
                instructions.append(Instruction(Opcode.DCONST_0, current, []))
            elif instruction == Opcode.ISTORE_1:
                instructions.append(Instruction(Opcode.ISTORE_1, current, []))
            elif instruction == Opcode.ISTORE_2:
                instructions.append(Instruction(Opcode.ISTORE_2, current, []))
            elif instruction == Opcode.ICONST_5:
                instructions.append(Instruction(Opcode.ICONST_5, current, []))
            elif instruction == Opcode.ILOAD_1:
                instructions.append(Instruction(Opcode.ILOAD_1, current, []))
            elif instruction == Opcode.ILOAD_2:
                instructions.append(Instruction(Opcode.ILOAD_2, current, []))
            elif instruction == Opcode.ILOAD_3:
                instructions.append(Instruction(Opcode.ILOAD_3, current, []))
            elif instruction == Opcode.DADD:
                instructions.append(Instruction(Opcode.DADD, current, []))
            elif instruction == Opcode.INVOKE_DYNAMIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                assert JavaClassFile.read_u1(buffer) == 0
                assert JavaClassFile.read_u1(buffer) == 0
                instructions.append(
                    Instruction(
                        Opcode.INVOKE_DYNAMIC,
                        current,
                        [constant_pool[idx_byte1 << 8 | idx_byte2]],
                    )
                )
                current += 4
            elif instruction == Opcode.INVOKE_INTERFACE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                count = JavaClassFile.read_u1(buffer)
                assert JavaClassFile.read_u1(buffer) == 0
                instructions.append(
                    Instruction(
                        Opcode.INVOKE_INTERFACE,
                        current,
                        [constant_pool[idx_byte1 << 8 | idx_byte2], count],
                    )
                )
                current += 4
            elif instruction == Opcode.INVOKE_SPECIAL:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.INVOKE_SPECIAL,
                        current,
                        [
                            const_pool_get_method_ref(
                                constant_pool, idx_byte1 << 8 | idx_byte2
                            )
                        ],
                    )
                )
                current += 2
            elif instruction == Opcode.CHECK_CAST:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.CHECK_CAST,
                        current,
                        [constant_pool[idx_byte1 << 8 | idx_byte2]],
                    )
                )
                current += 2
            elif instruction == Opcode.IF_ICMPNE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(Opcode.IF_ICMPNE, current, [idx_byte1 << 8 | idx_byte2])
                )
                current += 2
            elif instruction == Opcode.IF_GE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(Opcode.IF_GE, current, [idx_byte1 << 8 | idx_byte2])
                )
                current += 2
            elif instruction == Opcode.IF_EQ:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(Opcode.IF_EQ, current, [idx_byte1 << 8 | idx_byte2])
                )
                current += 2
            elif instruction == Opcode.GOTO:
                instructions.append(
                    Instruction(Opcode.GOTO, current, [JavaClassFile.read_i2(buffer)])
                )
                current += 2
            elif instruction == Opcode.IINC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(Opcode.IINC, current, [idx_byte1, idx_byte2])
                )
                current += 2
            elif instruction == Opcode.IF_ICMPGE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(Opcode.IF_ICMPGE, current, [idx_byte1 << 8 | idx_byte2])
                )
                current += 2
            elif instruction == Opcode.LDC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.LDC, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.DSTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.DSTORE, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.DLOAD:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.DLOAD, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ALOAD:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ALOAD, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ISTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ISTORE, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ILOAD:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ILOAD, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ASTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ASTORE, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.LDC2_W:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.LDC2_W,
                        current,
                        [constant_pool[idx_byte1 << 8 | idx_byte2]],
                    )
                )
                current += 2
            elif instruction == Opcode.INVOKE_STATIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.INVOKE_STATIC,
                        current,
                        [constant_pool[idx_byte1 << 8 | idx_byte2]],
                    )
                )
                current += 2
            elif instruction == Opcode.INVOKE_VIRTUAL:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.INVOKE_VIRTUAL,
                        current,
                        [
                            const_pool_get_method_ref(
                                constant_pool, idx_byte1 << 8 | idx_byte2
                            )
                        ],
                    )
                )
                current += 2
            elif instruction == Opcode.RETURN:
                instructions.append(Instruction(Opcode.RETURN, current, []))
            elif instruction == Opcode.ISTORE_3:
                instructions.append(Instruction(Opcode.ISTORE_3, current, []))
            elif instruction == Opcode.DUPLICATE:
                instructions.append(Instruction(Opcode.DUPLICATE, current, []))
            elif instruction == Opcode.ICONST_0:
                instructions.append(Instruction(Opcode.ICONST_0, current, []))
            elif instruction == Opcode.ICONST_1:
                instructions.append(Instruction(Opcode.ICONST_1, current, []))
            elif instruction == Opcode.ICONST_4:
                instructions.append(Instruction(Opcode.ICONST_4, current, []))
            elif instruction == Opcode.LSTORE_1:
                instructions.append(Instruction(Opcode.LSTORE_1, current, []))
            elif instruction == Opcode.ASTORE_0:
                instructions.append(Instruction(Opcode.ASTORE_0, current, []))
            elif instruction == Opcode.ASTORE_1:
                instructions.append(Instruction(Opcode.ASTORE_1, current, []))
            elif instruction == Opcode.ASTORE_2:
                instructions.append(Instruction(Opcode.ASTORE_2, current, []))
            elif instruction == Opcode.ASTORE_3:
                instructions.append(Instruction(Opcode.ASTORE_3, current, []))
            elif instruction == Opcode.NEW:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.NEW,
                        current,
                        [
                            const_pool_get_class_ref(
                                constant_pool, idx_byte1 << 8 | idx_byte2
                            )
                        ],
                    )
                )
                current += 2
            elif instruction == Opcode.GET_STATIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.GET_STATIC,
                        current,
                        [
                            const_pool_get_field_ref(
                                constant_pool, idx_byte1 << 8 | idx_byte2
                            )
                        ],
                    )
                )
                current += 2
            else:
                raise NotImplementedError(f"{hex(instruction)} {current} {length}")

            current += 1

        return instructions

    def nice_print(self, indent=0):
        print(" " * indent + f"Code Attribute {self.max_stack=} {self.max_locals=}")

        for instruction in self.instructions:
            instruction.nice_print(indent=indent + 2)

        for _, attr in self.attributes.items():
            attr.nice_print(indent=indent + 2)


@dataclass
class LineNumberTableAttribute:
    line_numbers: list[tuple[int, int]]

    def line_for_instruction_offset(self, instruction_offset):
        for starting_offset, line_number in reversed(self.line_numbers):
            if starting_offset <= instruction_offset:
                return line_number

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        num_enteries = JavaClassFile.read_u2(buffer)
        line_numbers = []

        for _ in range(num_enteries):
            start_pc = JavaClassFile.read_u2(buffer)
            end_pc = JavaClassFile.read_u2(buffer)
            line_numbers.append((start_pc, end_pc))

        return cls(line_numbers)

    def nice_print(self, indent=0):
        print(" " * indent + "Line Number Table")
        for offset, line in self.line_numbers:
            print(" " * (indent + 2) + f"{offset} -> {line}")


@dataclass
class SourceFileAttribute:
    name: str

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        source_file_index = JavaClassFile.read_u2(buffer)
        constant_type, _, data = constant_pool[source_file_index]
        assert constant_type == ConstantType.UTF_8

        return cls(data.decode())


@dataclass
class BootstrapMethodsAttribute:
    bootstrap_methods: list

    def get(self, index):
        return self.bootstrap_methods[index]

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

    def nice_print(self, indent=0):
        # TODO once implemented
        ...


def read_attribute(buffer: BytesIO, constant_pool: dict[int, tuple]):
    name_index = JavaClassFile.read_u2(buffer)
    name_type, _, name = constant_pool[name_index]
    assert name_type == ConstantType.UTF_8

    JavaClassFile.read_u4(buffer)  # length of attribute, not needed

    if name == b"Code":
        return name.decode(), CodeAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == b"LineNumberTable":
        return name.decode(), LineNumberTableAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    elif name == b"StackMapTable":
        return name.decode(), StackMapTableAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    elif name == b"SourceFile":
        return name.decode(), SourceFileAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    elif name == b"BootstrapMethods":
        return name.decode(), BootstrapMethodsAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    elif name == b"InnerClasses":
        return name.decode(), InnerClassesAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    else:
        raise NotImplementedError(name)


@dataclass
class Method:
    access_flags: list
    name: str
    descriptor: str
    attributes: dict

    @staticmethod
    def read_descriptor(descriptor_string: str):
        if descriptor_string[0] != "(":
            raise ValueError(
                f"Method descriptor must start with opening bracket, got {descriptor_string!r}"
            )

        index = 1  # starts at 1 to skip opening paren
        paramiters = []

        while descriptor_string[index] != ")":
            degree = 0
            while descriptor_string[index] == "[":  # param is array
                index += 1
                degree += 1

            if descriptor_string[index] == "B":
                paramiter_type = "byte"
            elif descriptor_string[index] == "C":
                paramiter_type = "char"
            elif descriptor_string[index] == "D":
                paramiter_type = "double"
            elif descriptor_string[index] == "F":
                paramiter_type = "float"
            elif descriptor_string[index] == "I":
                paramiter_type = "int"
            elif descriptor_string[index] == "J":
                paramiter_type = "long"
            elif descriptor_string[index] == "S":
                paramiter_type = "short"
            elif descriptor_string[index] == "Z":
                paramiter_type = "boolean"
            elif descriptor_string[index] == "L":
                index += 1  # skips the L
                paramiter_type = ""
                while descriptor_string[index] != ";":
                    paramiter_type += descriptor_string[index]
                    index += 1
            else:
                raise NotImplementedError(
                    f"{descriptor_string} {descriptor_string[index]}"
                )

            paramiters.append((paramiter_type, degree))
            index += 1

        return paramiters, descriptor_string[index + 1 :]

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: dict[int, tuple]):
        access_flags = JavaClassFile.read_u2(buffer)

        name_type, _, name = constant_pool[JavaClassFile.read_u2(buffer)]
        assert name_type == ConstantType.UTF_8, f"{name_type} {name!r}"

        name_type, _, descriptor = constant_pool[JavaClassFile.read_u2(buffer)]
        assert name_type == ConstantType.UTF_8

        attribute_count = JavaClassFile.read_u2(buffer)

        attributes = {}
        for _ in range(attribute_count):
            attr_name, attr_data = read_attribute(buffer, constant_pool)
            attributes[attr_name] = attr_data

        return cls(
            access_flags=MethodAccessFlags.parse_flags(access_flags),
            name=name.decode(),
            descriptor=cls.read_descriptor(descriptor.decode()),
            attributes=attributes,
        )

    def nice_print(self, indent=0):
        print(" " * indent + f"{self.access_flags} {self.name} {self.descriptor}")
        for attr_name, attribute in self.attributes.items():
            attribute.nice_print(indent=indent + 2)


@dataclass
class JavaClassFile:
    magic: bytes  # magic number at start of java class file must be 0xCAFEBABE
    minor_version: int
    major_version: int
    constant_pool: list
    access_flags: list
    this_class: int
    super_class: int
    interfaces: list
    field_info: list
    methods: list
    attributes: dict

    @staticmethod
    def read_u4(buffer: BytesIO):
        return int.from_bytes(buffer.read(4), byteorder="big", signed=False)

    @staticmethod
    def read_u2(buffer: BytesIO):
        return int.from_bytes(buffer.read(2), byteorder="big", signed=False)

    @staticmethod
    def read_u1(buffer: BytesIO):
        return int.from_bytes(buffer.read(1), byteorder="big", signed=False)

    @staticmethod
    def read_i2(buffer: BytesIO):
        return int.from_bytes(buffer.read(2), byteorder="big", signed=True)

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

        access_flags = ClassAccessFlags.parse_flags(cls.read_u2(buffer))

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
        attributes = {}
        for _ in range(attributes_count):
            attr_name, attr_data = read_attribute(buffer, constant_pool)
            attributes[attr_name] = attr_data

        # set bootstrap
        if "BootstrapMethods" in attributes:
            for method in methods:
                method.attributes["Code"].set_bootstrap_methods(
                    constant_pool, attributes["BootstrapMethods"]
                )

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

    def nice_print(self):
        print("Class File: " + self.attributes["SourceFile"].name)
        for method in self.methods:
            method.nice_print(indent=2)
