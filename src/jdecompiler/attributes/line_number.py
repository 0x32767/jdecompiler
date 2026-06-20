from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool
    from io import BytesIO


@dataclass
class LineNumberTableAttribute:
    line_numbers: list[tuple[int, int]]

    def line_for_instruction_offset(self, instruction_offset):
        for starting_offset, line_number in reversed(self.line_numbers):
            if starting_offset <= instruction_offset:
                return line_number

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        from jdecompiler.class_file import JavaClassFile

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
