from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "alumni_secret_key"




def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="TanmAy@1234",       
        database="aldb"
    )


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    # Total alumni
    cursor.execute("SELECT COUNT(*) FROM alureg")
    total_alumni = cursor.fetchone()[0]

    # Total events
    cursor.execute("SELECT COUNT(*) FROM event")
    total_events = cursor.fetchone()[0]

    # Total companies
    cursor.execute(
        "SELECT COUNT(DISTINCT curr_company) FROM alureg "
        "WHERE curr_company IS NOT NULL AND curr_company != ''"
    )
    total_companies = cursor.fetchone()[0]

    # Total branches
    cursor.execute(
        "SELECT COUNT(DISTINCT branch) FROM alureg "
        "WHERE branch IS NOT NULL AND branch != ''"
    )
    total_branches = cursor.fetchone()[0]

    # Recent alumni
    cursor.execute("""
        SELECT alu_id, first_name, last_name,
               curr_company, branch
        FROM alureg
        ORDER BY alu_id DESC
        LIMIT 5
    """)

    recent_alumni = cursor.fetchall()

    # Upcoming events
    cursor.execute("""
        SELECT event_name, event_date, venue, status
        FROM event
        ORDER BY event_date ASC
        LIMIT 4
    """)

    upcoming_events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_alumni=total_alumni,
        total_events=total_events,
        total_companies=total_companies,
        total_branches=total_branches,
        recent_alumni=recent_alumni,
        upcoming_events=upcoming_events
    )


# ---------------------------------------------------
# ALUMNI DIRECTORY
# ---------------------------------------------------

@app.route("/alumni")
def alumni():

    search = request.args.get("search", "")

    conn = get_db_connection()
    cursor = conn.cursor()

    if search:

        query = """
            SELECT *
            FROM alureg
            WHERE first_name LIKE %s
               OR last_name LIKE %s
               OR curr_company LIKE %s
               OR branch LIKE %s
               OR curr_city LIKE %s
        """

        value = "%" + search + "%"

        cursor.execute(
            query,
            (value, value, value, value, value)
        )

    else:

        cursor.execute("SELECT * FROM alureg")

    alumni_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "alumni.html",
        alumni_list=alumni_list,
        search=search
    )
@app.route("/events")


# ---------------------------------------------------
# ADD ALUMNI
# ---------------------------------------------------

@app.route("/add-alumni", methods=["GET", "POST"])
def add_alumni():

    if request.method == "POST":

        fname = request.form["first_name"]
        lname = request.form["last_name"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        address = request.form["address"]
        official_address = request.form["official_address"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        city = request.form["city"]
        company = request.form["company"]
        designation = request.form["designation"]
        session_from = request.form["session_from"]
        session_to = request.form["session_to"]
        branch = request.form["branch"]

        # Generate Alumni ID
        alid = "A1" + fname[:2].upper() + lname[:2].upper() + mobile[:4]

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO alureg
            (
                alu_id,
                first_name,
                last_name,
                dob,
                gender,
                add_corr,
                ad_offc,
                email_add,
                mob_no,
                curr_city,
                curr_company,
                desg,
                session_from,
                session_to,
                branch
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            alid,
            fname,
            lname,
            dob,
            gender,
            address,
            official_address,
            email,
            mobile,
            city,
            company,
            designation,
            session_from,
            session_to,
            branch
        )

        try:

            cursor.execute(sql, values)
            conn.commit()

            flash(
                "Alumni registered successfully! ID: " + alid,
                "success"
            )

        except mysql.connector.Error as err:

            conn.rollback()

            flash(
                "Database Error: " + str(err),
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

        return redirect(url_for("alumni"))

    return render_template("add_alumni.html")


# ---------------------------------------------------
# EDIT ALUMNI
# ---------------------------------------------------

@app.route("/edit-alumni", methods=["GET", "POST"])
def edit_alumni():

    if request.method == "POST":

        alu_id = request.form["alu_id"]
        fname = request.form["first_name"]
        lname = request.form["last_name"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        company = request.form["company"]
        designation = request.form["designation"]
        city = request.form["city"]
        branch = request.form["branch"]

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE alureg
            SET
                first_name=%s,
                last_name=%s,
                email_add=%s,
                mob_no=%s,
                curr_company=%s,
                desg=%s,
                curr_city=%s,
                branch=%s
            WHERE alu_id=%s
        """

        values = (
            fname,
            lname,
            email,
            mobile,
            company,
            designation,
            city,
            branch,
            alu_id
        )

        try:

            cursor.execute(sql, values)
            conn.commit()

            flash(
                "Alumni details updated successfully!",
                "success"
            )

        except mysql.connector.Error as err:

            conn.rollback()

            flash(
                "Database Error: " + str(err),
                "danger"
            )

        finally:

            cursor.close()
            conn.close()

        return redirect(url_for("alumni"))

    return render_template("edits.html")


# ---------------------------------------------------
# DELETE ALUMNI
# ---------------------------------------------------

@app.route("/delete-alumni/<alu_id>")
def delete_alumni(alu_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM alureg WHERE alu_id=%s",
        (alu_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Alumni deleted successfully!", "success")

    return redirect(url_for("alumni"))


# ---------------------------------------------------
# EVENTS
# ---------------------------------------------------

@app.route("/events")
def events():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM event
        ORDER BY event_date ASC
    """)

    event_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "events.html",
        event_list=event_list
    )


# ---------------------------------------------------
# ADD EVENT
# ---------------------------------------------------

@app.route("/add-event", methods=["POST"])
def add_event():

    event_name = request.form["event_name"]
    event_date = request.form["event_date"]
    venue = request.form["venue"]
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO event
        (event_name, event_date, venue, status)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (event_name, event_date, venue, status)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Event added successfully!", "success")

    return redirect(url_for("events"))


# ---------------------------------------------------
# DELETE EVENT
# ---------------------------------------------------

@app.route("/delete-event/<event_name>")
def delete_event(event_name):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM event WHERE event_name=%s",
        (event_name,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Event deleted successfully!", "success")

    return redirect(url_for("events"))


# ---------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)