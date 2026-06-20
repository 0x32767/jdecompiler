from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool


@dataclass
class BootstrapMethodsAttribute:
    bootstrap_methods: list

    def get(self, index):
        return self.bootstrap_methods[index]

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        from jdecompiler.class_file import JavaClassFile

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
