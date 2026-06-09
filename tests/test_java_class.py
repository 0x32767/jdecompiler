from jdecompiler.class_file import JavaClassFile
from pprint import pprint

def test_creation():
    file = JavaClassFile.from_file("tests/samples/EmptyClass.class")
    assert file.magic == b"\xCA\xFE\xBA\xBE", "Magic is wrong"
