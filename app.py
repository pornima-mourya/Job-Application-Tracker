from flask import Flask, render_template, request, redirect
from database import get_connection, create_table

app = Flask(__name__)

# Create database table when application starts
create_table()

@app.route("/")
def home():
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")

    connection = get_connection()

    query = "SELECT * FROM applications WHERE 1=1"
    parameters = []

    if search:
        query += " AND (company LIKE ? OR role LIKE ?)"
        parameters.extend([f"%{search}%", f"%{search}%"])

    if status_filter:
        query += " AND status = ?"
        parameters.append(status_filter)

    query += " ORDER BY id DESC"

    applications = connection.execute(
        query, parameters
    ).fetchall()

    total = connection.execute(
        "SELECT COUNT(*) FROM applications"
    ).fetchone()[0]

    applied = connection.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Applied'"
    ).fetchone()[0]

    interview = connection.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Interview'"
    ).fetchone()[0]

    selected = connection.execute(
        "SELECT COUNT(*) FROM applications WHERE status = 'Selected'"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        applications=applications,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
        search=search,
        status_filter=status_filter
    )



@app.route("/add", methods=["POST"])
def add_application():
    company = request.form["company"]
    role = request.form["role"]
    application_date = request.form["application_date"]
    status = request.form["status"]
    interview_date = request.form["interview_date"]
    notes = request.form["notes"]

    connection = get_connection()

    connection.execute("""
        INSERT INTO applications
        (company, role, application_date, status, interview_date, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        company,
        role,
        application_date,
        status,
        interview_date,
        notes
    ))

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/delete/<int:application_id>")
def delete_application(application_id):
    connection = get_connection()

    connection.execute(
        "DELETE FROM applications WHERE id = ?",
        (application_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    connection = get_connection()

    application = connection.execute(
        "SELECT * FROM applications WHERE id = ?",
        (application_id,)
    ).fetchone()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        application_date = request.form["application_date"]
        status = request.form["status"]
        interview_date = request.form["interview_date"]
        notes = request.form["notes"]

        connection.execute("""
            UPDATE applications
            SET company = ?,
                role = ?,
                application_date = ?,
                status = ?,
                interview_date = ?,
                notes = ?
            WHERE id = ?
        """, (
            company,
            role,
            application_date,
            status,
            interview_date,
            notes,
            application_id
        ))

        connection.commit()
        connection.close()

        return redirect("/")

    connection.close()

    return render_template(
        "edit.html",
        application=application
    )


if __name__ == "__main__":
    app.run(debug=True)
