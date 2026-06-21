from pprint import pprint

from jdecompiler.class_file import JavaClassFile
from jdecompiler.reconstruct import ControllFlowReconstructor


def test_creation():
    file = JavaClassFile.from_file("tests/samples/BasicClass.class")
    # file.nice_print()

    pprint(
        ControllFlowReconstructor(
            file.methods[1].attributes["Code"].instructions
        ).reconstruct()
    )
    # pprint(file.methods[1].attributes["Code"].instructions)
    # e = Emulator()
    # e.run(file.methods[1].attributes["Code"].instructions, file.constant_pool)
    assert False
