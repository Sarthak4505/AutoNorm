
from normalizer import parse_fd
from decomposition import (
    decompose_3nf,
    decompose_bcnf,
    check_lossless_join,
    check_dependency_preservation,
)


def relation_set(relations):
    """Convert relations to sets for order-independent comparison."""
    return {frozenset(relation) for relation in relations}


def test_3nf_decomposition():
    attributes = ["EmpID", "DeptID", "DeptName"]
    fds = [
        parse_fd("EmpID -> DeptID", attributes),
        parse_fd("DeptID -> DeptName", attributes),
    ]

    relations = decompose_3nf(attributes, fds)

    expected = {
        frozenset(["EmpID", "DeptID"]),
        frozenset(["DeptID", "DeptName"]),
    }

    assert relation_set(relations) == expected


def test_bcnf_decomposition():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A, B -> C", attributes),
        parse_fd("C -> B", attributes),
    ]

    relations = decompose_bcnf(attributes, fds)

    expected = {
        frozenset(["A", "C"]),
        frozenset(["B", "C"]),
    }

    assert relation_set(relations) == expected


def test_lossless_join():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A -> B", attributes),
        parse_fd("B -> C", attributes),
    ]
    relations = [
        ["A", "B"],
        ["B", "C"],
    ]

    assert check_lossless_join(attributes, fds, relations) is True


def test_bcnf_decomposition_dependency_preservation():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A, B -> C", attributes),
        parse_fd("C -> B", attributes),
    ]
    relations = decompose_bcnf(attributes, fds)

    assert check_lossless_join(attributes, fds, relations) is True
    assert check_dependency_preservation(
        attributes, fds, relations
    ) is False


def test_3nf_decomposition_dependency_preservation():
    attributes = ["EmpID", "DeptID", "DeptName"]
    fds = [
        parse_fd("EmpID -> DeptID", attributes),
        parse_fd("DeptID -> DeptName", attributes),
    ]
    relations = decompose_3nf(attributes, fds)

    assert check_lossless_join(attributes, fds, relations) is True
    assert check_dependency_preservation(
        attributes, fds, relations
    ) is True
def test_lossy_join():
    attributes = ["A", "B", "C"]
    fds = []

    relations = [["A", "B"], ["B", "C"]]

    assert check_lossless_join(attributes, fds, relations) is False

def test_lossy_join():
    attributes = ["A", "B", "C"]
    fds = []

    relations = [["A", "B"], ["B", "C"]]

    assert check_lossless_join(attributes, fds, relations) is False