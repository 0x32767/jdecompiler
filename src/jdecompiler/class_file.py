import pprint
from dataclasses import dataclass
from enum import IntEnum
from io import BytesIO
from io import StringIO
from pprint import pformat
from typing import Any
from typing import Optional
from typing import Self

from jdecompiler.attributes import *
from jdecompiler.constant_pool import ConstantPool


class ClassAccessFlags(IntEnum):
    ACC_PUBLIC = 0x0001
    ACC_FINAL = 0x0010
    ACC_SUPER = 0x0020
    ACC_INTERFACE = 0x0200
    ACC_ABSTRACT = 0x0400
    ACC_SYNTHETIC = 0x1000
    ACC_ANNOTATION = 0x2000
    ACC_ENUM = 0x4000

    @classmethod
    def parse_flags(cls, flags):
        return [
            name for name, value in cls._value2member_map_.items() if flags & value != 0
        ]


class MethodAccessFlags(IntEnum):
    ACC_PUBLIC = 0x0001
    ACC_PRIVATE = 0x0002
    ACC_PROTECTED = 0x0004
    ACC_STATIC = 0x0008
    ACC_FINAL = 0x0010
    ACC_SYNCHRONIZED = 0x0020
    ACC_BRIDGE = 0x0040
    ACC_VARARGS = 0x0080
    ACC_NATIVE = 0x0100
    ACC_ABSTRACT = 0x0400
    ACC_STRICT = 0x0800
    ACC_SYNTHETIC = 0x1000

    @classmethod
    def parse_flags(cls, flags):
        return [
            name for value, name in cls._value2member_map_.items() if flags & value != 0
        ]


class FieldAccessFlags(IntEnum):
    ACC_PUBLIC = 0x0001
    ACC_PRIVATE = 0x0002
    ACC_PROTECTED = 0x0004
    ACC_STATIC = 0x0008
    ACC_FINAL = 0x0010
    ACC_VOLATILE = 0x0040
    ACC_TRANSIENT = 0x0080
    ACC_SYNTHETIC = 0x1000
    ACC_ENUM = 0x4000

    @classmethod
    def parse_flags(cls, flags):
        return [
            name for value, name in cls._value2member_map_.items() if flags & value != 0
        ]


@dataclass
class Method:
    access_flags: list
    name: str
    descriptor: str
    attributes: dict

    @staticmethod
    def read_descriptor(descriptor_string: str):
        if descriptor_string[0] != "(":
            raise ValueError(
                f"Method descriptor must start with opening bracket, got {descriptor_string!r}"
            )

        index = 1  # starts at 1 to skip opening paren
        paramiters = []

        while descriptor_string[index] != ")":
            degree = 0
            while descriptor_string[index] == "[":  # param is array
                index += 1
                degree += 1

            if descriptor_string[index] == "B":
                paramiter_type = "byte"
            elif descriptor_string[index] == "C":
                paramiter_type = "char"
            elif descriptor_string[index] == "D":
                paramiter_type = "double"
            elif descriptor_string[index] == "F":
                paramiter_type = "float"
            elif descriptor_string[index] == "I":
                paramiter_type = "int"
            elif descriptor_string[index] == "J":
                paramiter_type = "long"
            elif descriptor_string[index] == "S":
                paramiter_type = "short"
            elif descriptor_string[index] == "Z":
                paramiter_type = "boolean"
            elif descriptor_string[index] == "L":
                index += 1  # skips the L
                paramiter_type = ""
                while descriptor_string[index] != ";":
                    paramiter_type += descriptor_string[index]
                    index += 1
            else:
                raise NotImplementedError(
                    f"{descriptor_string} {descriptor_string[index]}"
                )

            paramiters.append((paramiter_type, degree))
            index += 1

        return_type = descriptor_string[index + 1 :]

        if return_type == "V":
            return_type = "void"
        else:
            raise NotImplementedError

        return paramiters, return_type

    @staticmethod
    def recreate_signature(
        access_flags: list[MethodAccessFlags], name: str, descriptor
    ):
        access = " ".join(
            [
                {
                    MethodAccessFlags.ACC_PUBLIC: "public",
                    MethodAccessFlags.ACC_PRIVATE: "private",
                    MethodAccessFlags.ACC_PROTECTED: "protcted",
                    MethodAccessFlags.ACC_STATIC: "static",
                    MethodAccessFlags.ACC_FINAL: "final",
                    MethodAccessFlags.ACC_SYNCHRONIZED: "synchronised",
                    MethodAccessFlags.ACC_ABSTRACT: "abstract",
                }[flag]
                for flag in access_flags
            ]
        )

        paramiters, return_type = descriptor
        arguments = ", ".join(
            param_type + "[]" * degree for param_type, degree in paramiters
        )

        return f"{access} {return_type} {name}({arguments})"

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        access_flags = JavaClassFile.read_u2(buffer)

        name = constant_pool.get_utf8(JavaClassFile.read_u2(buffer))
        descriptor = constant_pool.get_utf8(JavaClassFile.read_u2(buffer))

        attribute_count = JavaClassFile.read_u2(buffer)

        attributes = {}
        for _ in range(attribute_count):
            attr_name, attr_data = read_attribute(buffer, constant_pool)
            attributes[attr_name] = attr_data

        return cls(
            access_flags=MethodAccessFlags.parse_flags(access_flags),
            name=name,
            descriptor=cls.read_descriptor(descriptor),
            attributes=attributes,
        )

    def nice_print(self, indent=0):
        print(
            " " * indent
            + self.recreate_signature(self.access_flags, self.name, self.descriptor)
        )
        for attr_name, attribute in self.attributes.items():
            attribute.nice_print(indent=indent + 2)


@dataclass
class Field:
    access_flags: list
    name: str
    descriptor: str
    attributes: dict

    @classmethod
    def from_buffer_and_pool(cls, buffer: BytesIO, constant_pool: ConstantPool):
        access_flags = JavaClassFile.read_u2(buffer)
        name_indx = JavaClassFile.read_u2(buffer)
        descriptor_index = JavaClassFile.read_u2(buffer)
        attribute_count = JavaClassFile.read_u2(buffer)

        attributes = {}
        for _ in range(attribute_count):
            attr_name, attr_data = read_attribute(buffer, constant_pool)
            attributes[attr_name] = attr_data

        return cls(
            access_flags=FieldAccessFlags.parse_flags(access_flags),
            descriptor=cls.read_descriptor(constant_pool.get_utf8(descriptor_index)),
            name=constant_pool.get_utf8(name_indx),
            attributes=attributes,
        )

    @staticmethod
    def read_descriptor(descriptor: str):
        if descriptor[0] == "B":
            return "byte"
        elif descriptor[0] == "C":
            return "char"
        elif descriptor[0] == "D":
            return "double"
        elif descriptor[0] == "F":
            return "float"
        elif descriptor[0] == "I":
            return "int"
        elif descriptor[0] == "J":
            return "long"
        elif descriptor[0] == "S":
            return "short"
        elif descriptor[0] == "Z":
            return "boolean"
        else:
            raise NotImplementedError

    def recreate_signature(self):
        access_flags = " ".join(
            {
                MethodAccessFlags.ACC_PUBLIC: "public",
                MethodAccessFlags.ACC_PRIVATE: "private",
                MethodAccessFlags.ACC_PROTECTED: "protcted",
                MethodAccessFlags.ACC_STATIC: "static",
                MethodAccessFlags.ACC_FINAL: "final",
                MethodAccessFlags.ACC_SYNCHRONIZED: "synchronised",
                MethodAccessFlags.ACC_ABSTRACT: "abstract",
            }[flag]
            for flag in self.access_flags
        )
        return f"{access_flags} {self.descriptor} {self.name}"

    def nice_print(self, indent=2):
        print(" " * indent + self.recreate_signature())


@dataclass
class JavaClassFile:
    magic: bytes  # magic number at start of java class file must be 0xCAFEBABE
    minor_version: int
    major_version: int
    constant_pool: list
    access_flags: list
    this_class: int
    super_class: int
    interfaces: list
    fields: list
    methods: list
    attributes: dict

    @staticmethod
    def read_u4(buffer: BytesIO):
        return int.from_bytes(buffer.read(4), byteorder="big", signed=False)

    @staticmethod
    def read_u2(buffer: BytesIO):
        return int.from_bytes(buffer.read(2), byteorder="big", signed=False)

    @staticmethod
    def read_u1(buffer: BytesIO):
        return int.from_bytes(buffer.read(1), byteorder="big", signed=False)

    @staticmethod
    def read_i2(buffer: BytesIO):
        return int.from_bytes(buffer.read(2), byteorder="big", signed=True)

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
        constant_pool = ConstantPool.read_constant_pool(buffer, constant_pool_count - 1)

        access_flags = ClassAccessFlags.parse_flags(cls.read_u2(buffer))

        this_class = constant_pool.get_class_ref(cls.read_u2(buffer))
        super_class = constant_pool.get_class_ref(cls.read_u2(buffer))

        interface_count = cls.read_u2(buffer)
        interfaces: list = []
        for _ in range(interface_count):
            raise NotImplementedError

        fields_count = cls.read_u2(buffer)
        fields: list = []
        for _ in range(fields_count):
            fields.append(Field.from_buffer_and_pool(buffer, constant_pool))

        methods_count = cls.read_u2(buffer)
        methods = []
        for _ in range(methods_count):
            methods.append(Method.from_buffer_and_pool(buffer, constant_pool))

        attributes_count = cls.read_u2(buffer)
        attributes = {}
        for _ in range(attributes_count):
            attr_name, attr_data = read_attribute(buffer, constant_pool)
            attributes[attr_name] = attr_data

        # set bootstrap
        if "BootstrapMethods" in attributes:
            for method in methods:
                method.attributes["Code"].set_bootstrap_methods(
                    constant_pool, attributes["BootstrapMethods"]
                )

        return cls(
            magic=magic,
            minor_version=minor_version,
            major_version=major_version,
            constant_pool=constant_pool,
            access_flags=access_flags,
            this_class=this_class,
            super_class=super_class,
            interfaces=interfaces,
            fields=fields,
            methods=methods,
            attributes=attributes,
        )

    def nice_print(self):
        print("Class File: " + self.attributes["SourceFile"].name)

        for field in self.fields:
            field.nice_print(indent=2)

        for method in self.methods:
            method.nice_print(indent=2)
