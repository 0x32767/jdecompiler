from jdecompiler.attributes.code import Instruction
from jdecompiler.attributes.code import Opcode
from jdecompiler.constant_pool import ConstantPool


def reconstruct(instructions: list[Instruction], constant_pool: ConstantPool): ...
