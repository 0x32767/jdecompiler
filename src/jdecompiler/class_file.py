from dataclasses import dataclass
from enum import IntEnum
from io import BytesIO
from pprint import pformat
from typing import Any
from typing import Optional
from typing import Self


class ConstantType(IntEnum):
    UTF_8 = 1
    INTEGER = 3
    FLOAT = 4
    LONG = 5
    DOUBLE = 6
    CLASS = 7
    STRING = 8
    FIELD_REF = 9
    METHOD_REF = 10
    INTERFACE_METHOD_REF = 11
    NAME_AND_TYPE = 12
    METHOD_HANDLE = 15
    METHOD_TYPE = 16
    INVOKE_DYNAMIC = 18


class ConstantPool:
    def __init__(self, enteries: dict[int, tuple[ConstantType, Any, Any]]):
        self._enteries = enteries

    def __str__(self):
        return f"{type(self).__name__}({pformat(self.enteries)})"

    def __repr__(self):
        return str(self)

    def get(self, index):
        return self._enteries[index]

    @property
    def enteries(self):
        return self._enteries.copy()

    @classmethod
    def from_buffer(cls, buffer: BytesIO, count: int):
        enteries: dict[int, tuple[ConstantType, Any, Any]] = {}

        key = 0
        while key < count:
            key += 1
            tag = JavaClassFile.read_u1(buffer)

            if tag == ConstantType.UTF_8:
                # Reads a UTF-8 String
                length = JavaClassFile.read_u2(buffer)
                enteries[key] = (ConstantType.UTF_8, 0, buffer.read(length))

            elif tag == ConstantType.DOUBLE:
                # Reads a number of type double
                enteries[key] = (
                    ConstantType.DOUBLE,
                    JavaClassFile.read_u4(buffer),
                    JavaClassFile.read_u4(buffer),
                )
                # This entery taks up two constant pool enteries
                # so the key is incremented here
                key += 1

            elif tag == ConstantType.CLASS:
                # Class info contains a string with the name of the class
                enteries[key] = (
                    ConstantType.CLASS,
                    None,
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.STRING:
                # String points to a UTF-8 string
                enteries[key] = (
                    ConstantType.STRING,
                    None,
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.FIELD_REF:
                # Points to a class and field belonging to that class
                enteries[key] = (
                    ConstantType.FIELD_REF,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.METHOD_REF:
                # Points to a class and method belonging to that class
                enteries[key] = (
                    ConstantType.METHOD_REF,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.INTERFACE_METHOD_REF:
                # Points to a class and interface used in that class
                enteries[key] = (
                    ConstantType.INTERFACE_METHOD_REF,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.NAME_AND_TYPE:
                # Points to a string and type
                enteries[key] = (
                    ConstantType.NAME_AND_TYPE,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.METHOD_HANDLE:
                enteries[key] = (
                    ConstantType.METHOD_HANDLE,
                    JavaClassFile.read_u1(buffer),
                    JavaClassFile.read_u2(buffer),
                )

            elif tag == ConstantType.INVOKE_DYNAMIC:
                enteries[key] = (
                    ConstantType.INVOKE_DYNAMIC,
                    JavaClassFile.read_u2(buffer),
                    JavaClassFile.read_u2(buffer),
                )

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
        name_type, _, name = constant_pool.get(name_index)
        assert name_type == ConstantType.UTF_8

        length = JavaClassFile.read_u4(buffer)
        data = buffer.read(length)

        return cls(name=name, info=data)


@dataclass
class Method:
    access_flags: int
    name: str
    descriptor: str
    attributes: list

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        access_flags = JavaClassFile.read_u2(buffer)

        name_type, _, name = constant_pool.get(JavaClassFile.read_u2(buffer))
        assert name_type == ConstantType.UTF_8

        name_type, _, descriptor = constant_pool.get(JavaClassFile.read_u2(buffer))
        assert name_type == ConstantType.UTF_8

        attribute_count = JavaClassFile.read_u2(buffer)

        attributes = []
        for _ in range(attribute_count):
            attributes.append(Attribute.from_buffer_and_pool(buffer, constant_pool))

        return cls(
            access_flags=access_flags,
            name=name,
            descriptor=descriptor,
            attributes=attributes,
        )


@dataclass
class JavaClassFile:
    magic: bytes  # magic number at start of java class file must be 0xCAFEBABE
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
    def from_buffer(cls, buffer) -> Self:
        magic = buffer.read(4)

        minor_version = cls.read_u2(buffer)
        major_version = cls.read_u2(buffer)

        constant_pool_count = cls.read_u2(buffer)
        constant_pool = ConstantPool.from_buffer(buffer, count=constant_pool_count - 1)

        access_flags = cls.read_u2(buffer)

        data_type, _, this_class = constant_pool.get(cls.read_u2(buffer))
        assert data_type == ConstantType.CLASS

        data_type, _, super_class = constant_pool.get(cls.read_u2(buffer))
        assert data_type == ConstantType.CLASS

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
            attributes=attributes,
        )
