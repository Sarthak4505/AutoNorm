
import re

from flask import Flask, render_template, request, redirect, url_for, flash

from normalizer import (
    parse_fd,
    find_candidate_keys,
    attribute_closure_with_steps,
    minimal_cover,
)
from normal_forms import analyze_normal_forms
from decomposition import (
    decompose_3nf,
    decompose_bcnf,
    generate_sql,
    check_lossless_join,
    check_dependency_preservation,
)
from database.connection import test_connection, get_connection

app = Flask(__name__)
app.secret_key = "change-this-to-a-long-random-secret"


def analyze_input(relation_name, attributes_text, fds_text, is_1nf, target_form):
    """Validate inputs and generate all normalization analysis results."""

    relation_name = relation_name.strip()
    attributes_text = attributes_text.strip()
    fds_text = fds_text.strip()

    if not relation_name or not attributes_text or not fds_text:
        raise ValueError("Please fill in all required fields.")

    if not relation_name.replace("_", "").isalnum():
        raise ValueError(
            "Use letters, numbers, and underscores in the relation name."
        )

    attributes = [
        item.strip()
        for item in attributes_text.split(",")
        if item.strip()
    ]

    if not attributes:
        raise ValueError("Enter at least one attribute.")

    if len(attributes) != len(set(attributes)):
        raise ValueError("Duplicate attributes are not allowed.")

    if any(not item.replace("_", "").isalnum() for item in attributes):
        raise ValueError(
            "Use letters, numbers, and underscores in attribute names."
        )

    fd_lines = [
        line.strip()
        for line in fds_text.splitlines()
        if line.strip()
    ]

    parsed_fds = [parse_fd(fd, attributes) for fd in fd_lines]

    keys = find_candidate_keys(attributes, parsed_fds)

    if not keys:
        raise ValueError(
            "No candidate key could be identified. Check your dependencies."
        )

    # Step-by-step attribute closure for each candidate key.
    closure_analysis = []

    for key in keys:
        final_closure, closure_steps = attribute_closure_with_steps(
            set(key),
            parsed_fds,
        )

        closure_analysis.append({
            "attributes": sorted(key),
            "steps": closure_steps,
            "final_closure": sorted(final_closure),
            "is_superkey": set(final_closure) == set(attributes),
        })

    # Minimal cover result.
    minimal_cover_fds = minimal_cover(parsed_fds)

    minimal_cover_display = [
        {
            "left": sorted(left),
            "right": sorted(right),
        }
        for left, right in minimal_cover_fds
    ]

    forms = analyze_normal_forms(
        attributes,
        parsed_fds,
        keys,
        is_1nf=is_1nf,
    )

    if target_form == "BCNF":
        relations = decompose_bcnf(attributes, parsed_fds)
    else:
        target_form = "3NF"
        relations = decompose_3nf(attributes, parsed_fds)

    sql = generate_sql(relation_name, relations, parsed_fds)

    lossless = check_lossless_join(
        attributes, parsed_fds, relations
    )

    dependency_preserved = check_dependency_preservation(
        attributes, parsed_fds, relations
    )

    return {
        "relation_name": relation_name,
        "attributes": attributes,
        "functional_dependencies": fd_lines,
        "candidate_keys": keys,
        "normal_form_results": forms,
        "target_form": target_form,
        "decomposed_relations": relations,
        "generated_sql": sql,
        "lossless_join": lossless,
        "dependency_preserved": dependency_preserved,
        "closure_analysis": closure_analysis,
        "minimal_cover_display": minimal_cover_display,
    }


@app.route("/")
def home():
    return render_template(
        "index.html",
        db_status=test_connection(),
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    relation_name = request.form.get("relation_name", "").strip()
    attributes_text = request.form.get("attributes", "").strip()
    fds_text = request.form.get("fds", "").strip()
    is_1nf = request.form.get("is_1nf") == "yes"
    target_form = request.form.get("target_form", "3NF")

    try:
        result = analyze_input(
            relation_name,
            attributes_text,
            fds_text,
            is_1nf,
            target_form,
        )
    except ValueError as exc:
        return render_template(
            "index.html",
            error=str(exc),
            db_status=test_connection(),
        )

    result.update({
        "attributes_text": attributes_text,
        "fds_text": fds_text,
        "is_1nf": is_1nf,
        "db_status": test_connection(),
    })

    return render_template("results.html", **result)


@app.route("/create-tables", methods=["POST"])
def create_tables():
    """Create generated tables after checking for existing table names."""

    relation_name = request.form.get("relation_name", "").strip()
    attributes_text = request.form.get("attributes", "").strip()
    fds_text = request.form.get("fds", "").strip()
    is_1nf = request.form.get("is_1nf") == "yes"
    target_form = request.form.get("target_form", "3NF")

    conn = None

    try:
        result = analyze_input(
            relation_name,
            attributes_text,
            fds_text,
            is_1nf,
            target_form,
        )

        statements = [
            statement.strip()
            for statement in result["generated_sql"].split(";")
            if statement.strip()
        ]

        if not statements:
            raise ValueError("No SQL statements were generated.")

        table_names = []

        for statement in statements:
            match = re.match(
                r"CREATE\s+TABLE\s+`?([A-Za-z0-9_]+)`?",
                statement,
                flags=re.IGNORECASE,
            )

            if not match:
                raise ValueError(
                    "Generated SQL contains an unsupported statement."
                )

            table_names.append(match.group(1))

        if len(table_names) != len(set(table_names)):
            raise ValueError("Generated SQL contains duplicate table names.")

        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE() AS db_name")
            row = cursor.fetchone()
            current_database = row["db_name"]

            if not current_database:
                raise ValueError("No MySQL database is selected.")

            for table_name in table_names:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS table_count
                    FROM information_schema.tables
                    WHERE table_schema = %s
                      AND table_name = %s
                    """,
                    (current_database, table_name),
                )

                if cursor.fetchone()["table_count"] > 0:
                    raise ValueError(
                        f"Table '{table_name}' already exists. "
                        "No new tables were created. Use a new relation name."
                    )

            for statement in statements:
                cursor.execute(statement)

        flash(
            "All generated tables were created successfully in MySQL.",
            "success",
        )

    except Exception as exc:
        flash(f"Table creation failed: {exc}", "error")

    finally:
        if conn is not None:
            conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
