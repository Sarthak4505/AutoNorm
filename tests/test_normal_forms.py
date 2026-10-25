
from normalizer import parse_fd, find_candidate_keys
from normal_forms import analyze_normal_forms


def analyze(attributes, fd_texts, is_1nf=True):
    fds = [parse_fd(fd, attributes) for fd in fd_texts]
    keys = find_candidate_keys(attributes, fds)
    return analyze_normal_forms(attributes, fds, keys, is_1nf=is_1nf)


def test_1nf_confirmation():
    result = analyze(["A", "B"], ["A -> B"], is_1nf=True)

    assert result["1NF"]["satisfied"] is True
    assert result["2NF"]["satisfied"] is True


def test_1nf_not_confirmed():
    result = analyze(["A", "B"], ["A -> B"], is_1nf=False)

    assert result["1NF"]["satisfied"] is False
    assert result["2NF"]["satisfied"] is False
    assert result["3NF"]["satisfied"] is False
    assert result["BCNF"]["satisfied"] is False


def test_2nf_violation():
    result = analyze(
        ["StudentID", "CourseID", "StudentName"],
        ["StudentID, CourseID -> StudentName", "StudentID -> StudentName"],
    )

    assert result["2NF"]["satisfied"] is False
    assert result["2NF"]["violations"]


def test_3nf_violation_but_2nf_satisfied():
    result = analyze(
        ["A", "B", "C"],
        ["A -> B", "B -> C"],
    )

    assert result["2NF"]["satisfied"] is True
    assert result["3NF"]["satisfied"] is False
    assert result["BCNF"]["satisfied"] is False


def test_3nf_satisfied_but_bcnf_violated():
    result = analyze(
        ["A", "B", "C"],
        ["A, B -> C", "C -> B"],
    )

    assert result["2NF"]["satisfied"] is True
    assert result["3NF"]["satisfied"] is True
    assert result["BCNF"]["satisfied"] is False


def test_bcnf_satisfied():
    result = analyze(
        ["A", "B", "C"],
        ["A -> B", "B -> C"],
    )

    # This relation is not BCNF because B -> C violates BCNF.
    assert result["BCNF"]["satisfied"] is False


def test_empty_attributes_raise_error():
    try:
        analyze_normal_forms([], [], [])
    except ValueError as error:
        assert "required" in str(error)
    else:
        assert False, "Expected ValueError for empty attributes and keys"
