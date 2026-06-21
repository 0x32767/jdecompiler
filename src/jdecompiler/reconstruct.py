from pprint import pprint

from jdecompiler.attributes.code import Instruction
from jdecompiler.attributes.code import NET_STACK_CHANGE
from jdecompiler.attributes.code import Opcode
from jdecompiler.constant_pool import ConstantPool

COMPARISON_JUMPS = [
    Opcode.IF_EQ,
    Opcode.IF_GE,
    Opcode.IF_ICMPNE,
    Opcode.IF_ICMPEQ,
    Opcode.IF_ICMPGE,
]


class ControllFlowReconstructor:
    def __init__(self, instructions):
        self._instructions: list[Instruction] = instructions
        self._index = 0

    def get_jump_point(self, instruction: Instruction):
        assert (instruction.opcode in COMPARISON_JUMPS) or (
            instruction.opcode == Opcode.GOTO
        )
        assert len(instruction.operands) == 1

        if instruction.opcode == Opcode.IF_ICMPGE:
            return instruction.offset + instruction.operands[0] - 1
        else:
            return instruction.offset + instruction.operands[0]

    def get_instruction_range_offset(self, start, end):
        instructions = []

        for instruction in self._instructions:
            if start <= instruction.offset <= end:
                instructions.append(instruction)

        return instructions

    def group_conditions(self):
        for index, instruction in enumerate(self._instructions):
            if instruction.opcode in COMPARISON_JUMPS:
                condition_related = [instruction]

                net_stack_size = NET_STACK_CHANGE[instruction.opcode]
                index -= 1
                while net_stack_size != 0:
                    back_instruction = self._instructions[index]
                    net_stack_size += NET_STACK_CHANGE[back_instruction.opcode]
                    condition_related.insert(0, back_instruction)
                    index -= 1

                pprint(condition_related)
