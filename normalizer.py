from itertools import combinations


def parse_fd(fd_text, attributes):
    if "->" not in fd_text:
        raise ValueError(f"Invalid functional dependency: {fd_text}")
    left_text, right_text = fd_text.split("->", 1)
    left = frozenset(x.strip() for x in left_text.split(",") if x.strip())
    right = frozenset(x.strip() for x in right_text.split(",") if x.strip())
    if not left or not right:
        raise ValueError(f"Both sides are required in: {fd_text}")
    unknown = (set(left) | set(right)) - set(attributes)
    if unknown:
        raise ValueError("Unknown attribute(s): " + ", ".join(sorted(unknown)))
    return left, right


def attribute_closure(attribute_set, functional_dependencies):
    closure = set(attribute_set)
    changed = True
    while changed:
        changed = False
        for left, right in functional_dependencies:
            if set(left).issubset(closure) and not set(right).issubset(closure):
                closure.update(right)
                changed = True
    return closure


def attribute_closure_with_steps(attribute_set, functional_dependencies):
    """
    Calculate attribute closure and record every step
    for step-by-step dependency analysis.
    """
    closure = set(attribute_set)
    steps = []

    steps.append({
        "step": 1,
        "title": "Initialize Closure",
        "before": sorted(closure),
        "fd": "Start",
        "added": [],
        "after": sorted(closure),
        "reason": (
            "The initial closure contains the attributes "
            "provided by the user."
        )
    })

    step_number = 2

    while True:
        changed = False

        for left, right in functional_dependencies:
            before = set(closure)

            if set(left).issubset(closure):
                new_attributes = set(right) - closure

                if new_attributes:
                    closure.update(new_attributes)
                    changed = True

                    steps.append({
                        "step": step_number,
                        "title": "Apply Functional Dependency",
                        "before": sorted(before),
                        "fd": (
                            ", ".join(sorted(left))
                            + " -> "
                            + ", ".join(sorted(right))
                        ),
                        "added": sorted(new_attributes),
                        "after": sorted(closure),
                        "reason": (
                            "The determinant is contained in the "
                            "current closure, so the dependent "
                            "attributes can be added."
                        )
                    })

                    step_number += 1

        if not changed:
            break

    steps.append({
        "step": step_number,
        "title": "Final Closure",
        "before": sorted(closure),
        "fd": "No further applicable dependency",
        "added": [],
        "after": sorted(closure),
        "reason": (
            "No new attributes can be derived. "
            "The attribute closure is complete."
        )
    })

    return sorted(closure), steps



def find_candidate_keys(attributes, functional_dependencies):
    attrs = set(attributes)
    if not attrs:
        return []
    rhs = set()
    for _, right in functional_dependencies:
        rhs.update(right)
    required = attrs - rhs
    optional = sorted(attrs - required)
    keys = []
    for size in range(len(optional) + 1):
        for combo in combinations(optional, size):
            candidate = required | set(combo)
            if attribute_closure(candidate, functional_dependencies) != attrs:
                continue
            if any(key.issubset(candidate) for key in keys):
                continue
            keys.append(candidate)
    return [sorted(key) for key in keys]


def split_fds(functional_dependencies):
    result = []
    for left, right in functional_dependencies:
        for attr in sorted(right):
            fd = (frozenset(left), frozenset({attr}))
            if fd not in result:
                result.append(fd)
    return result


def minimal_cover(functional_dependencies):
    """Return a minimal cover with single-attribute right sides."""
    fds = split_fds(functional_dependencies)

    # Remove extraneous attributes from determinants.
    changed = True
    while changed:
        changed = False
        for i, (left, right) in enumerate(list(fds)):
            for attr in sorted(left):
                reduced_left = frozenset(set(left) - {attr})
                others = fds[:i] + fds[i + 1:]
                if set(right).issubset(attribute_closure(set(reduced_left), others)):
                    fds[i] = (reduced_left, right)
                    changed = True
                    break
            if changed:
                break

    # Remove dependencies implied by all the other dependencies.
    i = 0
    while i < len(fds):
        left, right = fds[i]
        others = fds[:i] + fds[i + 1:]
        if set(right).issubset(attribute_closure(set(left), others)):
            fds.pop(i)
        else:
            i += 1

    unique = []
    for fd in fds:
        if fd not in unique:
            unique.append(fd)
    return unique
