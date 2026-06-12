from jdecompiler.class_file import JavaClassFile
from pprint import pprint

def test_creation():
    file = JavaClassFile.from_file("tests/samples/BasicClass.class")
    pprint(file)
    assert False

