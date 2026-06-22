from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool
    from io import BytesIO
    from jdecompiler.attributes import LineNumberTableAttribute


class Opcode(IntEnum):
    NOP = 0
    ACONST_NULL = 0x01
    ALOAD_M1 = 0x02
    ICONST_0 = 0x03
    ICONST_1 = 0x04
    ICONST_2 = 0x05
    ICONST_3 = 0x06
    ICONST_4 = 0x07
    ICONST_5 = 0x08
    LCONST_0 = 0x09
    LCONST_1 = 0x0A
    FCONST_0 = 0x0B
    FCONST_1 = 0x0C
    FCONST_2 = 0x0D
    DCONST_0 = 0x0E
    DCONST_1 = 0x0F
    BIPUSH = 0x10
    SIPUSH = 0x11
    LDC = 0x12
    LDC_W = 0x13
    LDC2_W = 0x14
    ILOAD = 0x15
    LLOAD = 0x16
    FLOAD = 0x17
    DLOAD = 0x18
    ALOAD = 0x19
    ILOAD_0 = 0x1A
    ILOAD_1 = 0x1B
    ILOAD_2 = 0x1C
    ILOAD_3 = 0x1D
    LLOAD_0 = 0x1E
    LLOAD_1 = 0x1F
    LLOAD_2 = 0x20
    ALOAD_0 = 0x2A
    ALOAD_1 = 0x2B
    ALOAD_2 = 0x2C
    ALOAD_3 = 0x2D
    IALOAD = 0x2E
    LALOAD = 0x2F
    FALOAD = 0x30
    DALOAD = 0x31
    AALOAD = 0x32
    BALOAD = 0x33
    CALOAD = 0x34
    SALOAD = 0x35
    ISTORE = 0x36
    DSTORE = 0x39
    ASTORE = 0x3A
    ISTORE_0 = 0x3B
    ISTORE_1 = 0x3C
    ISTORE_2 = 0x3D
    ISTORE_3 = 0x3E
    LSTORE_0 = 0x3F
    LSTORE_1 = 0x40
    LSTORE_2 = 0x41
    LSTORE_3 = 0x42
    FSTORE_0 = 0x43
    FSTORE_1 = 0x44
    FSTORE_2 = 0x45
    FSTORE_3 = 0x46
    DSTORE_0 = 0x47
    DSTORE_1 = 0x48
    DSTORE_2 = 0x49
    DSTORE_3 = 0x4A
    ASTORE_0 = 0x4B
    ASTORE_1 = 0x4C
    ASTORE_2 = 0x4D
    ASTORE_3 = 0x4E
    IASTORE = 0x4F
    LASTORE = 0x50
    FASTORE = 0x51
    DASTORE = 0x52
    AASTORE = 0x53
    BASTORE = 0x54
    CASTORE = 0x55
    SASTORE = 0x56
    POP = 0x57
    POP2 = 0x58
    DUPLICATE = 0x59
    DUPLICATE_X1 = 0x5A
    DUPLICATE_X2 = 0x5B
    DUP2 = 0x5C
    DUP2_X1 = 0x5D
    DUP2_X2 = 0x5E
    SWAP = 0x5F
    IADD = 0x60
    LADD = 0x61
    FADD = 0x62
    DADD = 0x63
    ISUB = 0x64
    LSUB = 0x65
    FSUB = 0x66
    DSUB = 0x67
    IMUL = 0x68
    LMUL = 0x69
    FMUL = 0x6A
    DMUL = 0x6B
    IDIV = 0x6C
    LDIV = 0x6D
    FDIV = 0x6E
    DDIV = 0x6F
    IREM = 0x70
    LREM = 0x71
    FREM = 0x72
    DREM = 0x73
    INEG = 0x74
    LNEG = 0x75
    FNEG = 0x76
    DNEG = 0x77
    ISHL = 0x78
    LSHL = 0x79
    ISHR = 0x7A
    LSHR = 0x7B
    IUSHR = 0x7C
    LUSHR = 0x7D
    IAND = 0x7E
    LAND = 0x7F
    IOR = 0x80
    LOR = 0x81
    IXOR = 0x82
    LXOR = 0x83
    IINC = 0x84
    INT_TO_LONG = 0x85
    INT_TO_FLOAT = 0x86
    INT_TO_DOUBLE = 0x87
    LONG_TO_INT = 0x88
    LONG_TO_FLOAT = 0x89
    LONG_TO_DOUBLE = 0x8A
    FLOAT_TO_INT = 0x8B
    FLOAT_TO_LONG = 0x8C
    FLOAT_TO_DOUBLE = 0x8D
    DOUBLE_TO_INT = 0x8E
    DOUBLE_TO_LONG = 0x8F
    DOUBLE_TO_FLOAT = 0x90
    INT_TO_BYTE = 0x91
    INT_TO_CHAR = 0x92
    INT_TO_SHORT = 0x93
    LCMP = 0x94
    FCMPL = 0x95
    FCMPG = 0x96
    DCMPL = 0x97
    DCMPG = 0x98
    IF_EQ = 0x99
    IF_NE = 0x9A
    IF_LT = 0x9B
    IF_GE = 0x9C
    IF_GT = 0x9D
    IF_LE = 0x9E
    IF_ICMPEQ = 0x9F
    IF_ICMPNE = 0xA0
    IF_ICMPLT = 0xA1
    IF_ICMPGE = 0xA2
    IF_ICMPGT = 0xA3
    IF_ICMPLE = 0xA4
    IF_ACMPEQ = 0xA5
    IF_ACMPNE = 0xA6
    GOTO = 0xA7
    TABLE_SWITCH = 0xAA
    LOOKUP_SWITCH = 0xAB
    IRETURN = 0xAC
    LRETURN = 0xAD
    FRETURN = 0xAE
    DRETURN = 0xAF
    ARETURN = 0xB0
    RETURN = 0xB1
    GET_STATIC = 0xB2
    PUTSTATIC = 0xB3
    GETFIELD = 0xB4
    PUTFIELD = 0xB5
    INVOKE_VIRTUAL = 0xB6
    INVOKE_SPECIAL = 0xB7
    INVOKE_STATIC = 0xB8
    INVOKE_INTERFACE = 0xB9
    INVOKE_DYNAMIC = 0xBA
    NEWARRAY = 0xBC
    ANEWARRAY = 0xBD
    ARRAYLENGTH = 0xBE
    ATHROW = 0xBF
    CHECKCAST = 0xC0
    INSTANCEOF = 0xC1
    MONITORENTER = 0xC2
    MONITOREXIT = 0xC3
    WIDE = 0xC4
    MULTIANEWARRAY = 0xC5
    IFNULL = 0xC6
    IFNONNULL = 0xC7
    GOTO_W = 0xC8
    BREAKPOINT = 0xCA

    @classmethod
    def get_name(cls, value):
        return str(cls._value2member_map_[value].name)


NET_STACK_CHANGE = {
    Opcode.ICONST_1: 1,
    Opcode.ICONST_2: 1,
    Opcode.ICONST_3: 1,
    Opcode.ICONST_4: 1,
    Opcode.ICONST_5: 1,
    Opcode.ALOAD_M1: 1,
    Opcode.ISTORE: -1,
    Opcode.ISTORE_1: -1,
    Opcode.ISTORE_2: -1,
    Opcode.ISTORE_3: -1,
    Opcode.ILOAD_1: 1,
    Opcode.RETURN: 0,
    Opcode.IF_EQ: -2,
    Opcode.IF_GE: -2,
    Opcode.IF_ICMPNE: -2,
    Opcode.IF_ICMPEQ: -2,
    Opcode.IF_ICMPGE: -2,
}


@dataclass(unsafe_hash=True)
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

    def set_bootstrap_methods(self, constant_pool: ConstantPool, bootstrap_methods):
        for instruction in self.instructions:
            if instruction.opcode != Opcode.INVOKE_DYNAMIC:
                continue

            bootstrap_idx, method_descriptor = constant_pool.get_invoke_dynamic(
                instruction.operands[0]
            )
            instruction.operands = [
                bootstrap_methods.get(bootstrap_idx),
                constant_pool.get_name_and_type(method_descriptor),
            ]

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        from jdecompiler.class_file import JavaClassFile
        from jdecompiler.attributes.attribute import read_attribute

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
        from jdecompiler.class_file import JavaClassFile

        instructions = []

        current = 0
        while current < length:
            instruction = JavaClassFile.read_u1(buffer)

            if instruction == Opcode.NOP:
                instructions.append(Instruction(Opcode.NOP, current, []))
            elif instruction == Opcode.ACONST_NULL:
                instructions.append(Instruction(Opcode.ACONST_NULL, current, []))
            elif instruction == Opcode.ALOAD_M1:
                instructions.append(Instruction(Opcode.ALOAD_M1, current, []))
            elif instruction == Opcode.ICONST_0:
                instructions.append(Instruction(Opcode.ICONST_0, current, []))
            elif instruction == Opcode.ICONST_1:
                instructions.append(Instruction(Opcode.ICONST_1, current, []))
            elif instruction == Opcode.ICONST_2:
                instructions.append(Instruction(Opcode.ICONST_2, current, []))
            elif instruction == Opcode.ICONST_3:
                instructions.append(Instruction(Opcode.ICONST_3, current, []))
            elif instruction == Opcode.ICONST_4:
                instructions.append(Instruction(Opcode.ICONST_4, current, []))
            elif instruction == Opcode.ICONST_5:
                instructions.append(Instruction(Opcode.ICONST_5, current, []))
            elif instruction == Opcode.ICONST_5:
                instructions.append(Instruction(Opcode.ICONST_5, current, []))
            elif instruction == Opcode.DCONST_0:
                instructions.append(Instruction(Opcode.DCONST_0, current, []))
            elif instruction == Opcode.DCONST_1:
                instructions.append(Instruction(Opcode.DCONST_1, current, []))
            elif instruction == Opcode.BIPUSH:
                byte = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.BIPUSH,
                        current,
                        [byte],
                    )
                )
                current += 1
            elif instruction == Opcode.LDC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.LDC, current, [idx_byte1]))
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
            elif instruction == Opcode.ILOAD:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ILOAD, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.DLOAD:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.DLOAD, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ALOAD:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ALOAD, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ILOAD_1:
                instructions.append(Instruction(Opcode.ILOAD_1, current, []))
            elif instruction == Opcode.ILOAD_2:
                instructions.append(Instruction(Opcode.ILOAD_2, current, []))
            elif instruction == Opcode.ILOAD_3:
                instructions.append(Instruction(Opcode.ILOAD_3, current, []))
            elif instruction == Opcode.ALOAD_0:
                instructions.append(Instruction(Opcode.ALOAD_0, current, []))
            elif instruction == Opcode.ALOAD_1:
                instructions.append(Instruction(Opcode.ALOAD_1, current, []))
            elif instruction == Opcode.ALOAD_2:
                instructions.append(Instruction(Opcode.ALOAD_2, current, []))
            elif instruction == Opcode.ALOAD_3:
                instructions.append(Instruction(Opcode.ALOAD_3, current, []))
            elif instruction == Opcode.ISTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ISTORE, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.DSTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.DSTORE, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ASTORE:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                instructions.append(Instruction(Opcode.ASTORE, current, [idx_byte1]))
                current += 1
            elif instruction == Opcode.ISTORE_1:
                instructions.append(Instruction(Opcode.ISTORE_1, current, []))
            elif instruction == Opcode.ISTORE_2:
                instructions.append(Instruction(Opcode.ISTORE_2, current, []))
            elif instruction == Opcode.ISTORE_3:
                instructions.append(Instruction(Opcode.ISTORE_3, current, []))
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
            elif instruction == Opcode.POP:
                instructions.append(Instruction(Opcode.POP, current, []))
            elif instruction == Opcode.DUPLICATE:
                instructions.append(Instruction(Opcode.DUPLICATE, current, []))
            elif instruction == Opcode.IADD:
                instructions.append(Instruction(Opcode.IADD, current, []))
            elif instruction == Opcode.DADD:
                instructions.append(Instruction(Opcode.DADD, current, []))
            elif instruction == Opcode.DMUL:
                instructions.append(Instruction(Opcode.DMUL, current, []))
            elif instruction == Opcode.LONG_TO_FLOAT:
                instructions.append(Instruction(Opcode.LONG_TO_FLOAT, current, []))
            elif instruction == Opcode.DOUBLE_TO_INT:
                instructions.append(Instruction(Opcode.DOUBLE_TO_INT, current, []))
            elif instruction == Opcode.DCMPG:
                instructions.append(Instruction(Opcode.DCMPG, current, []))
            elif instruction == Opcode.IF_EQ:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(Opcode.IF_EQ, current, [JavaClassFile.read_i2(buffer)])
                )
                current += 2
            elif instruction == Opcode.IF_GE:
                instructions.append(
                    Instruction(Opcode.IF_GE, current, [JavaClassFile.read_i2(buffer)])
                )
                current += 2
            elif instruction == Opcode.IF_ICMPEQ:
                instructions.append(
                    Instruction(
                        Opcode.IF_ICMPEQ, current, [JavaClassFile.read_i2(buffer)]
                    )
                )
                current += 2
            elif instruction == Opcode.IF_ICMPNE:
                instructions.append(
                    Instruction(
                        Opcode.IF_ICMPNE, current, [JavaClassFile.read_i2(buffer)]
                    )
                )
                current += 2
            elif instruction == Opcode.IF_ICMPGE:
                instructions.append(
                    Instruction(
                        Opcode.IF_ICMPGE, current, [JavaClassFile.read_i2(buffer)]
                    )
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
            elif instruction == Opcode.RETURN:
                instructions.append(Instruction(Opcode.RETURN, current, []))
            elif instruction == Opcode.GET_STATIC:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.GET_STATIC,
                        current,
                        [constant_pool.get_field_ref(idx_byte1 << 8 | idx_byte2)],
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
                        [constant_pool.get_method_ref(idx_byte1 << 8 | idx_byte2)],
                    )
                )
                current += 2
            elif instruction == Opcode.INVOKE_SPECIAL:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.INVOKE_SPECIAL,
                        current,
                        [constant_pool.get_method_ref(idx_byte1 << 8 | idx_byte2)],
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
            elif instruction == Opcode.NEW:
                idx_byte1 = JavaClassFile.read_u1(buffer)
                idx_byte2 = JavaClassFile.read_u1(buffer)
                instructions.append(
                    Instruction(
                        Opcode.NEW,
                        current,
                        [constant_pool.get_class_ref(idx_byte1 << 8 | idx_byte2)],
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
            elif 0xCB <= instruction <= 0xFD:
                raise ValueError(f"instruction {instruction} not defined in JVM spec")
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
