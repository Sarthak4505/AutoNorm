
from normalizer import (
    attribute_closure,
    find_candidate_keys,
    parse_fd,
)


def test_attribute_closure():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A -> B", attributes),
        parse_fd("B -> C", attributes),
    ]

    closure = attribute_closure({"A"}, fds)

    assert closure == {"A", "B", "C"}


def test_single_candidate_key():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A -> B", attributes),
        parse_fd("B -> C", attributes),
    ]

    keys = find_candidate_keys(attributes, fds)

    assert keys == [["A"]]


def test_multiple_candidate_keys():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A, B -> C", attributes),
        parse_fd("C -> B", attributes),
    ]

    keys = find_candidate_keys(attributes, fds)

    assert {tuple(key) for key in keys} == {
        ("A", "B"),
        ("A", "C"),
    }


def test_invalid_functional_dependency():
    attributes = ["A", "B"]

    try:
        parse_fd("A -> C", attributes)
    except ValueError as error:
        assert "Unknown attribute" in str(error)
    else:
        assert False, "Expected ValueError for unknown attribute"



def test_no_functional_dependencies():
    attributes = ["A", "B", "C"]
    fds = []

    keys = find_candidate_keys(attributes, fds)

    assert keys == [["A", "B", "C"]]


def test_invalid_fd_format():
    attributes = ["A", "B"]

    try:
        parse_fd("A B", attributes)
    except ValueError as error:
        assert "Invalid functional dependency" in str(error)
    else:
        assert False, "Expected ValueError for invalid FD format"


def test_duplicate_functional_dependencies():
    attributes = ["A", "B", "C"]
    fds = [
        parse_fd("A -> B", attributes),
        parse_fd("A -> B", attributes),
        parse_fd("B -> C", attributes),
    ]

    keys = find_candidate_keys(attributes, fds)

    assert keys == [["A"]]




