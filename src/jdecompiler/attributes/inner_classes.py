from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool


@dataclass
class InnerClassesAttribute:
    inner_classes: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        from jdecompiler.class_file import JavaClassFile

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
