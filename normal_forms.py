from itertools import combinations
from normalizer import attribute_closure, split_fds


def analyze_normal_forms(attributes, functional_dependencies, candidate_keys, is_1nf=False):
    attrs = set(attributes)
    keys = [set(key) for key in candidate_keys]
    if not attrs or not keys:
        raise ValueError("Attributes and candidate keys are required.")

    prime = set().union(*keys)
    non_prime = attrs - prime
    fds = split_fds(functional_dependencies)
    violations_2nf = []
    violations_3nf = []
    violations_bcnf = []

    # 2NF: a non-prime attribute must not depend on a proper subset of a key.
    seen_2nf = set()
    for key in keys:
        key_list = sorted(key)
        for size in range(len(key_list)):
            for combo in combinations(key_list, size):
                determinant = set(combo)
                dependent = (attribute_closure(determinant, fds) - determinant) & non_prime
                if dependent:
                    sig = (tuple(sorted(determinant)), tuple(sorted(dependent)))
                    if sig not in seen_2nf:
                        seen_2nf.add(sig)
                        violations_2nf.append({
                            "determinant": sorted(determinant),
                            "attributes": sorted(dependent),
                            "reason": "A non-prime attribute depends on a proper subset of a candidate key."
                        })

    # Find minimal determinants for each implied non-trivial dependency.
    minimal_dependencies = []
    ordered = sorted(attrs)
    for size in range(len(ordered) + 1):
        for combo in combinations(ordered, size):
            determinant = set(combo)
            closure = attribute_closure(determinant, fds)
            for attr in sorted(closure - determinant):
                # Only keep a determinant if no proper subset determines this attribute.
                has_smaller = False
                for smaller_size in range(len(determinant)):
                    for smaller_combo in combinations(sorted(determinant), smaller_size):
                        smaller = set(smaller_combo)
                        if attr in attribute_closure(smaller, fds):
                            has_smaller = True
                            break
                    if has_smaller:
                        break
                if not has_smaller:
                    minimal_dependencies.append((determinant, attr))

    for determinant, attr in minimal_dependencies:
        closure = attribute_closure(determinant, fds)
        is_superkey = closure == attrs
        if not is_superkey:
            violation = {
                "determinant": sorted(determinant),
                "attributes": [attr],
                "reason": "The determinant is not a superkey."
            }
            violations_bcnf.append(violation)
            if attr in non_prime:
                violations_3nf.append({
                    "determinant": sorted(determinant),
                    "attributes": [attr],
                    "reason": "A non-prime attribute depends on a determinant that is not a superkey."
                })

    def unique(items):
        seen, result = set(), []
        for item in items:
            signature = (tuple(item["determinant"]), tuple(item["attributes"]))
            if signature not in seen:
                seen.add(signature)
                result.append(item)
        return result

    v2, v3, vb = unique(violations_2nf), unique(violations_3nf), unique(violations_bcnf)
    return {
        "prime_attributes": sorted(prime),
        "non_prime_attributes": sorted(non_prime),
        "1NF": {
            "satisfied": bool(is_1nf),
            "violations": [] if is_1nf else [{
                "determinant": [],
                "attributes": sorted(attrs),
                "reason": "Confirm that each table cell contains one atomic value."
            }]
        },
        "2NF": {"satisfied": bool(is_1nf) and not v2, "violations": v2},
        "3NF": {"satisfied": bool(is_1nf) and not v3, "violations": v3},
        "BCNF": {"satisfied": bool(is_1nf) and not vb, "violations": vb}
    }
