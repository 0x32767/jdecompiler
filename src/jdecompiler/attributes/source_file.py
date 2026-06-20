from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool


@dataclass
class SourceFileAttribute:
    name: str

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        from jdecompiler.class_file import JavaClassFile

        file_name = constant_pool.get_utf8(JavaClassFile.read_u2(buffer))
        return cls(file_name)
