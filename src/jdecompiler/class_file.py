from pprint import pformat
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Self, Optional


class ConstantPool:
    def __init__(self, enteries: list[tuple[str, Any, Any]]):
        self._enteries = enteries

    def __str__(self):
        return f"{type(self).__name__}({pformat(self.enteries)})"

    def __repr__(self):
        return str(self)

    def get(self, index):
        return self._enteries[index-1]

    def resolve_class_info(self, index):
        t, junk, idx = self.get(index)
        assert t == "CLASS_INFO"
        return self.get(idx)

    @property
    def enteries(self):
        return self._enteries.copy()

    @classmethod
    def from_buffer(cls, buffer: BytesIO, count: int):
        enteries: list[tuple[str, Any, Any]] = []

        for _ in range(count):
            tag = JavaClassFile.read_u1(buffer)

            if tag == 7: # class info
                enteries.append(("CLASS_INFO", 0, JavaClassFile.read_u2(buffer)))

            elif tag == 8: # String
                enteries.append(("STRING", 0, JavaClassFile.read_u2(buffer)))

            elif tag == 9: # field ref
                enteries.append(("FIELD_REF", JavaClassFile.read_u2(buffer), JavaClassFile.read_u2(buffer)))

            elif tag == 10: # method ref
                enteries.append(("METHOD_REF", JavaClassFile.read_u2(buffer), JavaClassFile.read_u2(buffer)))

            elif tag == 11: # Interfacemethod ref
                enteries.append(("INTERFACE_REF", JavaClassFile.read_u2(buffer), JavaClassFile.read_u2(buffer)))

            elif tag == 12: # name and type ref
                enteries.append(("NAMEANDTYPE_REF", JavaClassFile.read_u2(buffer), JavaClassFile.read_u2(buffer)))

            elif tag == 1: # UTF-8
                length = JavaClassFile.read_u2(buffer)
                enteries.append(("UTF-8", 0, buffer.read(length)))

            else:
                raise NotImplementedError(tag)

        return cls(enteries)


@dataclass
class Attribute:
    name: str
    info: bytes

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        name_index = JavaClassFile.read_u2(buffer)
        length = JavaClassFile.read_u4(buffer)
        data = buffer.read(length)
        return cls(name=constant_pool.get(name_index), info=data)


@dataclass
class Method:
    access_flags: int
    name: str
    descriptor: str
    attributes: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        access_flags = JavaClassFile.read_u2(buffer)
        name = constant_pool.get(JavaClassFile.read_u2(buffer))
        descriptor = constant_pool.get(JavaClassFile.read_u2(buffer))
        attribute_count = JavaClassFile.read_u2(buffer)

        attributes = []
        for _ in range(attribute_count):
            attributes.append(Attribute.from_buffer_and_pool(buffer, constant_pool))

        return cls(
            access_flags=access_flags,
            name=name,
            descriptor=descriptor,
            attributes=attributes
        )

@dataclass
class JavaClassFile:
    magic: bytes # magic number at start of java class file must be 0xCAFEBABE
    minor_version: int
    major_version: int
    constant_pool: list
    access_flags: int
    this_class: int
    super_class: int
    interfaces: list
    field_info: list
    methods: list
    attributes: list

    @staticmethod
    def read_u4(buffer: BytesIO):
        return int.from_bytes(buffer.read(4), byteorder="big", signed=False)

    @staticmethod
    def read_u2(buffer: BytesIO):
        return int.from_bytes(buffer.read(2), byteorder="big", signed=False)

    @staticmethod
    def read_u1(buffer: BytesIO):
        return int.from_bytes(buffer.read(1), byteorder="big", signed=False)

    @classmethod
    def from_file(cls, fp):
        with open(fp, "rb") as f:
            return cls.from_buffer(f)

    @classmethod
    def from_buffer(cls, buffer: BytesIO) -> Self:
        magic = buffer.read(4)

        minor_version = cls.read_u2(buffer)
        major_version = cls.read_u2(buffer)

        constant_pool_count = cls.read_u2(buffer)
        constant_pool = ConstantPool.from_buffer(buffer, count=constant_pool_count-1)
        
        access_flags = cls.read_u2(buffer)
        this_class = constant_pool.resolve_class_info(cls.read_u2(buffer))
        super_class = constant_pool.resolve_class_info(cls.read_u2(buffer))

        interface_count = cls.read_u2(buffer)
        interfaces: list = []
        for _ in range(interface_count):
            raise NotImplementedError

        fields_count = cls.read_u2(buffer)
        fields: list = []
        for _ in range(fields_count):
            raise NotImplementedError

        methods_count = cls.read_u2(buffer)
        methods = []
        for _ in range(methods_count):
            methods.append(Method.from_buffer_and_pool(buffer, constant_pool))

        
        attributes_count = cls.read_u2(buffer)
        attributes = []
        for _ in range(attributes_count):
            attributes.append(Attribute.from_buffer_and_pool(buffer, constant_pool))

        return cls(
            magic=magic,
            minor_version=minor_version,
            major_version=major_version,
            constant_pool=constant_pool,
            access_flags=access_flags,
            this_class=this_class,
            super_class=super_class,
            interfaces=interfaces,
            field_info=fields,
            methods=methods,
            attributes=attributes
        )

