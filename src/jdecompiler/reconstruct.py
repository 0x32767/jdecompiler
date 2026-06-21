from pprint import pprint

from jdecompiler.attributes.code import Instruction
from jdecompiler.attributes.code import Opcode
from jdecompiler.constant_pool import ConstantPool

COMPARISON_JUMPS = [
    Opcode.IF_EQ,
    Opcode.IF_GE,
    Opcode.IF_ICMPNE,
    Opcode.IF_ICMPGE,
]


class ControllFlowReconstructor:
    def __init__(self, instructions):
        self._instructions = instructions
        self._index = 0

    def advance(self):
        if self._index + 1 < len(self._instructions):
            self._index += 1
            return True

    def get_jump_point(self, instruction: Instruction):
        assert (instruction.opcode in COMPARISON_JUMPS) or (
            instruction.opcode == Opcode.GOTO
        )
        assert len(instruction.operands) == 1

        if instruction.opcode == Opcode.IF_ICMPGE:
            return instruction.offset + instruction.operands[0] - 1
        else:
            return instruction.offset + instruction.operands[0]

    def take_while(self, f):
        qualified = []

        while self.advance() and f(self._instructions[self._index]):
            qualified.append(self._instructions[self._index])

        return qualified

    def reconstruct(self):
        blocks = []
        while self.advance():
            instruction = self._instructions[self._index]

            if instruction.opcode not in COMPARISON_JUMPS:
                continue

            conditional = self.take_while(
                lambda i: i.offset < self.get_jump_point(instruction)
            )
            goto: Instruction = conditional[-1]
            if goto.opcode != Opcode.GOTO:
                raise TypeError(f"Expectd GOTO after branch end got {goto}")

            jump_point = goto.operands[0]
            if jump_point < 0:
                print("LOOP DETECTED")
            elif jump_point > 0:
                print("IF Statement detected")
            else:
                raise ValueError
