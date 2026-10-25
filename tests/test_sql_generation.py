
from normalizer import parse_fd
from decomposition import decompose_3nf, generate_sql


def test_sql_contains_create_table_statements():
    attributes = ["StudentID", "CourseID", "StudentName", "CourseName"]
    fds = [
        parse_fd("StudentID -> StudentName", attributes),
        parse_fd("CourseID -> CourseName", attributes),
    ]

    relations = decompose_3nf(attributes, fds)
    sql = generate_sql("ENROLLMENT", relations, fds)

    assert "CREATE TABLE `ENROLLMENT_N1`" in sql
    assert "CREATE TABLE `ENROLLMENT_N2`" in sql
    assert "CREATE TABLE `ENROLLMENT_N3`" in sql


def test_sql_contains_primary_and_foreign_keys():
    attributes = ["StudentID", "CourseID", "StudentName", "CourseName"]
    fds = [
        parse_fd("StudentID -> StudentName", attributes),
        parse_fd("CourseID -> CourseName", attributes),
    ]

    relations = decompose_3nf(attributes, fds)
    sql = generate_sql("ENROLLMENT", relations, fds)

    assert sql.count("PRIMARY KEY") == 3
    assert "FOREIGN KEY (`StudentID`)" in sql
    assert "FOREIGN KEY (`CourseID`)" in sql


def test_sql_uses_safe_relation_name():
    attributes = ["A", "B"]
    fds = [parse_fd("A -> B", attributes)]
    relations = decompose_3nf(attributes, fds)

    sql = generate_sql("TEST-R", relations, fds)

    assert "CREATE TABLE `TESTR_N1`" in sql
    assert "TEST-R" not in sql
