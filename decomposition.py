from itertools import combinations
import re

from normalizer import (
    attribute_closure,
    find_candidate_keys,
    minimal_cover,
)


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------

def _remove_contained(relations):
    """Remove duplicate relations and proper subsets of other relations."""
    unique = []

    for relation in relations:
        relation = set(relation)

        if relation and relation not in unique:
            unique.append(relation)

    return [
        relation
        for relation in unique
        if not any(relation < other for other in unique)
    ]


def _project_fds(relation_attrs, original_fds):
    """
    Calculate functional dependencies implied on a relation
    by the original functional dependencies.
    """
    relation = set(relation_attrs)
    projected = []
    attrs = sorted(relation)

    for size in range(len(attrs) + 1):
        for combo in combinations(attrs, size):
            left = set(combo)
            closure = attribute_closure(left, original_fds) & relation

            for attr in sorted(closure - left):
                projected.append(
                    (frozenset(left), frozenset({attr}))
                )

    return minimal_cover(projected)


# --------------------------------------------------
# 3NF DECOMPOSITION
# --------------------------------------------------

def decompose_3nf(attributes, functional_dependencies):
    """Decompose a relation using the 3NF synthesis algorithm."""
    attrs = set(attributes)
    fds = list(functional_dependencies)

    if not attrs:
        return []

    cover = minimal_cover(fds)
    grouped = {}

    # FIX: FDs with the same determinant are merged into one relation.
    # (A->B and A->C  =>  {A, B, C})
    for left, right in cover:
        determinant = tuple(sorted(left))
        grouped.setdefault(determinant, set(left)).update(right)

    relations = list(grouped.values())

    keys = find_candidate_keys(attrs, fds)

    # Ensure at least one generated relation contains a candidate key.
    if keys and not any(
        set(key).issubset(relation)
        for key in keys
        for relation in relations
    ):
        relations.append(set(keys[0]))

    # If there are no non-trivial FDs, retain a key relation.
    if not relations and keys:
        relations.append(set(keys[0]))

    # Safety guard: every original attribute must appear somewhere.
    covered = set().union(*relations) if relations else set()
    missing = attrs - covered

    if missing:
        relations.append(missing)

    return [
        sorted(relation)
        for relation in _remove_contained(relations)
    ]


# --------------------------------------------------
# BCNF DECOMPOSITION
# --------------------------------------------------

def decompose_bcnf(attributes, functional_dependencies):
    """Recursively decompose a relation until no BCNF violation remains."""
    attrs = set(attributes)
    original_fds = list(functional_dependencies)

    if not attrs:
        return []

    pending = [attrs]
    final_relations = []

    while pending:
        relation = pending.pop()
        projected = _project_fds(relation, original_fds)
        violation = None
        ordered = sorted(relation)

        # Find X -> A where X is not a superkey.
        for size in range(len(ordered) + 1):
            for combo in combinations(ordered, size):
                left = set(combo)
                closure = attribute_closure(left, projected) & relation

                if closure - left and closure != relation:
                    violation = (left, closure)
                    break

            if violation:
                break

        if not violation:
            final_relations.append(relation)
            continue

        left, x_plus = violation

        r1 = set(x_plus)
        r2 = relation - (set(x_plus) - left)

        if (
            not r1
            or not r2
            or r1 == relation
            or r2 == relation
        ):
            final_relations.append(relation)
        else:
            pending.append(r1)
            pending.append(r2)

    return [
        sorted(relation)
        for relation in _remove_contained(final_relations)
    ]


# --------------------------------------------------
# SQL GENERATION
# --------------------------------------------------

def generate_sql(relation_name, relations, functional_dependencies=None):
    """
    Generate CREATE TABLE statements with primary keys,
    foreign keys, and parent-before-child creation order.
    """
    safe_relation = "".join(
        char for char in relation_name
        if char.isalnum() or char == "_"
    ) or "Relation"

    original_fds = list(functional_dependencies or [])

    relations = [
        sorted(set(relation))
        for relation in relations
        if relation
    ]

    if not relations:
        return ""

    table_names = [
        f"{safe_relation}_N{index}"
        for index in range(1, len(relations) + 1)
    ]

    relation_keys = []

    for relation in relations:
        projected_fds = _project_fds(relation, original_fds)
        keys = find_candidate_keys(relation, projected_fds)
        relation_keys.append([set(key) for key in keys])

    statements = []

    for index, relation in enumerate(relations):
        relation_set = set(relation)
        table_name = table_names[index]
        columns = []

        for attr in relation:
            safe_attr = "".join(
                char for char in attr
                if char.isalnum() or char == "_"
            ) or "attribute"

            columns.append(f"    `{safe_attr}` VARCHAR(255)")

        # Select a deterministic candidate key as the primary key.
        keys = relation_keys[index]

        primary_key = None

        if keys:
            primary_key = min(
                keys,
                key=lambda key: (len(key), sorted(key))
            )

            pk_columns = [
                attr for attr in relation
                if attr in primary_key
            ]

            columns.append(
                "    PRIMARY KEY ("
                + ", ".join(f"`{attr}`" for attr in pk_columns)
                + ")"
            )

        # Add foreign keys referencing another relation's selected PK.
        foreign_keys = []

        for parent_index, parent_keys in enumerate(relation_keys):
            if parent_index == index or not parent_keys:
                continue

            parent_pk = min(
                parent_keys,
                key=lambda key: (len(key), sorted(key))
            )

            # Only create an FK when the child contains the entire parent PK.
            if parent_pk and parent_pk.issubset(relation_set):
                parent_relation = set(relations[parent_index])

                # Do not create a redundant self-reference.
                if parent_pk == relation_set:
                    continue

                fk_columns = [
                    attr for attr in relation
                    if attr in parent_pk
                ]

                parent_columns = [
                    attr for attr in relations[parent_index]
                    if attr in parent_pk
                ]

                foreign_keys.append(
                    "    FOREIGN KEY ("
                    + ", ".join(f"`{attr}`" for attr in fk_columns)
                    + f") REFERENCES `{table_names[parent_index]}` ("
                    + ", ".join(f"`{attr}`" for attr in parent_columns)
                    + ")"
                )

        columns.extend(foreign_keys)

        statements.append(
            f"CREATE TABLE `{table_name}` (\n"
            + ",\n".join(columns)
            + "\n);"
        )

    # Sort creation order so referenced tables come first.
    table_statements = {
        table_names[index].lower(): statements[index]
        for index in range(len(table_names))
    }

    dependencies = {
        name: set()
        for name in table_statements
    }

    for name, statement in table_statements.items():
        referenced_tables = re.findall(
            r"REFERENCES\s+`?([A-Za-z0-9_]+)`?",
            statement,
            flags=re.IGNORECASE,
        )

        for parent in referenced_tables:
            parent = parent.lower()

            if parent in table_statements and parent != name:
                dependencies[name].add(parent)

    ordered_statements = []
    remaining = set(table_statements)

    while remaining:
        ready = sorted(
            name for name in remaining
            if not (dependencies[name] & remaining)
        )

        if not ready:
            raise ValueError(
                "Circular foreign-key dependency detected. "
                "Review the generated relations and their keys."
            )

        for name in ready:
            ordered_statements.append(table_statements[name])
            remaining.remove(name)

    return "\n\n".join(ordered_statements)


# --------------------------------------------------
# LOSSLESS JOIN VALIDATION - CHASE TEST
# --------------------------------------------------

def check_lossless_join(attributes, functional_dependencies, relations):
    """
    Test whether a decomposition is lossless using the chase algorithm.
    Returns True if lossless, otherwise False.
    """
    attrs = list(dict.fromkeys(attributes))
    attr_set = set(attrs)

    if not attrs or not relations:
        return False

    normalized_relations = [
        set(relation)
        for relation in relations
    ]

    # Validate that the decomposition covers every original attribute.
    if any(
        not relation or not relation.issubset(attr_set)
        for relation in normalized_relations
    ):
        return False

    covered = set().union(*normalized_relations)

    if covered != attr_set:
        return False

    # A decomposition into the original relation itself is lossless.
    if any(relation == attr_set for relation in normalized_relations):
        return True

    attr_index = {
        attr: index
        for index, attr in enumerate(attrs)
    }

    # Distinguished symbols represent original attributes.
    # Other symbols are unique to each row.
    rows = []

    for row_index, relation in enumerate(normalized_relations):
        row = []

        for attr in attrs:
            if attr in relation:
                row.append(("a", attr))
            else:
                row.append(("b", row_index, attr))

        rows.append(row)

    fds = []

    for left, right in functional_dependencies:
        left = set(left)
        right = set(right)

        if not left.issubset(attr_set) or not right.issubset(attr_set):
            return False

        # Split RHS attributes so each FD has one RHS attribute.
        for attr in right:
            fds.append((left, {attr}))

    changed = True

    while changed:
        changed = False

        for left, right in fds:
            left_indexes = [attr_index[attr] for attr in left]
            right_indexes = [attr_index[attr] for attr in right]

            # Rows agreeing on X must agree on each A in X -> A.
            for i in range(len(rows)):
                for j in range(i + 1, len(rows)):
                    if all(
                        rows[i][col] == rows[j][col]
                        for col in left_indexes
                    ):
                        for col in right_indexes:
                            symbol_i = rows[i][col]
                            symbol_j = rows[j][col]

                            if symbol_i == symbol_j:
                                continue

                            # Prefer the distinguished symbol.
                            if symbol_i[0] == "a":
                                target = symbol_i
                            elif symbol_j[0] == "a":
                                target = symbol_j
                            else:
                                target = symbol_i

                            old_symbols = {symbol_i, symbol_j}

                            # Unify these symbols throughout the tableau.
                            for row in rows:
                                for position, symbol in enumerate(row):
                                    if symbol in old_symbols:
                                        row[position] = target

                            changed = True

    # Lossless if a row contains only distinguished symbols.
    for row in rows:
        if all(
            symbol == ("a", attr)
            for symbol, attr in zip(row, attrs)
        ):
            return True

    return False


# --------------------------------------------------
# DEPENDENCY PRESERVATION VALIDATION
# --------------------------------------------------

def check_dependency_preservation(
    attributes,
    functional_dependencies,
    relations,
):
    """
    Check whether projected dependencies collectively imply
    every original functional dependency.
    """
    attrs = set(attributes)

    if not attrs or not relations:
        return False

    normalized_relations = [
        set(relation)
        for relation in relations
    ]

    if any(
        not relation or not relation.issubset(attrs)
        for relation in normalized_relations
    ):
        return False

    if set().union(*normalized_relations) != attrs:
        return False

    # If the original relation itself is present, all original FDs
    # remain available in that relation.
    if any(relation == attrs for relation in normalized_relations):
        return True

    projected_fds = []

    for relation in normalized_relations:
        projected_fds.extend(
            _project_fds(relation, functional_dependencies)
        )

    projected_fds = list(dict.fromkeys(projected_fds))

    # Every original FD must follow from the union of projected FDs.
    for left, right in functional_dependencies:
        left = set(left)
        right = set(right)

        if not left.issubset(attrs) or not right.issubset(attrs):
            return False

        closure = attribute_closure(left, projected_fds)

        if not right.issubset(closure):
            return False

    return True