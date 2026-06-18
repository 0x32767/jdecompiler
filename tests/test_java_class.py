from pprint import pprint

from jdecompiler.class_file import JavaClassFile


def test_creation():
    file = JavaClassFile.from_file("tests/samples/testFile.class")
    # pprint(file)
    file.nice_print()
    assert False
