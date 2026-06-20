from dataclasses import dataclass
from enum import IntEnum


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


@dataclass
class ConstantPool:
    constants: dict

    def get_utf8(self, index):
        data_type, _, value = self.constants[index]
        assert data_type == ConstantType.UTF_8
        return value.decode()

    def get_class_ref(self, index):
        data_type, _, value = self.constants[index]
        assert data_type == ConstantType.CLASS
        return self.get_utf8(value)

    def get_name_and_type(self, index):
        data_type, name_index, descriptor_index = self.constants[index]
        assert data_type == ConstantType.NAME_AND_TYPE
        return (
            self.get_utf8(name_index) + " type(" + self.get_utf8(descriptor_index) + ")"
        )

    def get_field_ref(self, index):
        data_type, class_index, name_and_type = self.constants[index]
        assert data_type == ConstantType.FIELD_REF
        return (
            self.get_class_ref(class_index)
            + "."
            + self.get_name_and_type(name_and_type)
        )

    def get_method_ref(self, index):
        data_type, class_index, name_and_type = self.constants[index]
        assert data_type == ConstantType.METHOD_REF
        return (
            self.get_class_ref(class_index)
            + "."
            + self.get_name_and_type(name_and_type)
        )

    def get_invoke_dynamic(self, data):
        op_type, bootstrap_idx, method_descriptor_index = data
        assert op_type == ConstantType.INVOKE_DYNAMIC
        return bootstrap_idx, method_descriptor_index

    @classmethod
    def read_constant_pool(cls, buffer, count):
        from jdecompiler.class_file import JavaClassFile

        enteries = {}

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

    def __getitem__(self, value):
        return self.constants[value]
