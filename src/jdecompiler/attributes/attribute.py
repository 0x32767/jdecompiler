from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool
    from jdecompiler.attributes import LineNumberTableAttribute
    from io import BytesIO


def read_attribute(buffer: BytesIO, constant_pool: ConstantPool):
    from jdecompiler.class_file import JavaClassFile
    from jdecompiler.attributes import (
        CodeAttribute,
        LineNumberTableAttribute,
        SourceFileAttribute,
        StackMapTableAttribute,
        BootstrapMethodsAttribute,
        InnerClassesAttribute,
    )

    name = constant_pool.get_utf8(JavaClassFile.read_u2(buffer))

    JavaClassFile.read_u4(buffer)  # length of attribute, not needed

    if name == "Code":
        return name, CodeAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == "LineNumberTable":
        return name, LineNumberTableAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    elif name == "StackMapTable":
        return name, StackMapTableAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == "SourceFile":
        return name, SourceFileAttribute.from_buffer_and_pool(buffer, constant_pool)

    elif name == "BootstrapMethods":
        return name, BootstrapMethodsAttribute.from_buffer_and_pool(
            buffer, constant_pool
        )

    elif name == "InnerClasses":
        return name, InnerClassesAttribute.from_buffer_and_pool(buffer, constant_pool)

    else:
        raise NotImplementedError(name)
