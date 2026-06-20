from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jdecompiler.constant_pool import ConstantPool
    from io import BytesIO
    from jdecompiler.attributes import LineNumberTableAttribute


@dataclass
class StackMapTableAttribute:
    stack_frames: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        from jdecompiler.class_file import JavaClassFile

        # TODO calculate the stack layout given the function descriptor as too
        num_frames = JavaClassFile.read_u2(buffer)

        frames: list = []
        for _ in range(num_frames):
            tag = JavaClassFile.read_u1(buffer)

            if 0 <= tag <= 63:
                frames.append("SAME FRAME")

            elif 64 <= tag <= 127:
                frames.append(
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                )

            elif 128 <= tag <= 246:
                raise NotImplementedError

            elif tag == 247:
                offset_delta = JavaClassFile.read_u2(buffer)
                frames.append(
                    (
                        offset_delta,
                        StackMapTableAttribute._read_verification_type_info(
                            buffer, constant_pool
                        ),
                    )
                )

            elif 248 <= tag <= 250:
                offset_delta = JavaClassFile.read_u2(buffer)
                frames.append(offset_delta)

            elif tag == 251:
                offset_delta = JavaClassFile.read_u2(buffer)

            elif 252 <= tag <= 254:
                offset_delta = JavaClassFile.read_u2(buffer)
                locals = [
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                    for _ in range(tag - 251)
                ]

            elif tag == 255:
                offset_delta = JavaClassFile.read_u2(buffer)
                num_locals = JavaClassFile.read_u2(buffer)
                locals = [
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                    for _ in range(num_locals)
                ]
                num_tack_items = JavaClassFile.read_u2(buffer)
                locals = [
                    StackMapTableAttribute._read_verification_type_info(
                        buffer, constant_pool
                    )
                    for _ in range(num_tack_items)
                ]

            else:
                raise ValueError

        return cls(frames)

    @staticmethod
    def _read_verification_type_info(buffer, constant_pool):
        from jdecompiler.class_file import JavaClassFile

        tag = JavaClassFile.read_u1(buffer)

        if tag == 0:
            return "ITEM_top"
        elif tag == 1:
            return "ITEM_Integer"
        elif tag == 2:
            return "ITEM_Float"
        elif tag == 4:
            return "ITEM_Long"
        elif tag == 3:
            return "ITEM_Double"
        elif tag == 5:
            return "ITEM_NULL"
        elif tag == 6:
            return "ITEM_UninitialisedThis"
        elif tag == 7:
            return "ITEM_Object", constant_pool[JavaClassFile.read_u2(buffer)]
        elif tag == 8:
            return "ITEM_VeriableInfo", JavaClassFile.read_u2(buffer)
        else:
            raise ValueError(tag)

    def nice_print(self, indent=0):
        # TODO once implemented
        ...
