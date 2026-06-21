from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool
    from io import BytesIO
    from jdecompiler.attributes import LineNumberTableAttribute


class Opcode(IntEnum):
    NOP = 0
    ICONST_0 = 0x03
    ICONST_1 = 0x04
    ICONST_2 = 0x05
    ICONST_4 = 0x07
    ICONST_5 = 0x08
    DCONST_0 = 0x0E
    DCONST_1 = 0x0F
    BIPUSH = 0x10
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
                        [constant_pool.get_method_ref(idx_byte1 << 8 | idx_byte2)],
                    )
                )
                current += 2
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
                        [constant_pool.get_method_ref(idx_byte1 << 8 | idx_byte2)],
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
            elif instruction == Opcode.ICONST_2:
                instructions.append(Instruction(Opcode.ICONST_2, current, []))
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
                        [constant_pool.get_class_ref(idx_byte1 << 8 | idx_byte2)],
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
                        [constant_pool.get_field_ref(idx_byte1 << 8 | idx_byte2)],
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
