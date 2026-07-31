from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

from config import db, cursor
from ai.ocr import extract_aadhaar, extract_marksheet
from ai.agent import verify_student, generate_response


app = Flask(__name__)


# =====================================================
# UPLOAD FOLDER
# =====================================================

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# CHAT
# =====================================================

@app.route("/chat")
def chat():
    return render_template("chat.html")


# =====================================================
# UPLOAD PAGE
# =====================================================

@app.route("/upload")
def upload():
    return render_template("upload.html")


# =====================================================
# OCR + AI AGENT + AUTO FILL
# =====================================================

@app.route("/autofill", methods=["POST"])
def autofill():

    # Check Aadhaar file
    if "aadhaar" not in request.files:
        return "❌ Aadhaar file not found"

    # Check Marksheet file
    if "marksheet" not in request.files:
        return "❌ Marksheet file not found"

    aadhaar_file = request.files["aadhaar"]
    marksheet_file = request.files["marksheet"]

    # Check filenames
    if aadhaar_file.filename == "":
        return "❌ Please select Aadhaar file"

    if marksheet_file.filename == "":
        return "❌ Please select Marksheet file"


    # =================================================
    # SAVE AADHAAR
    # =================================================

    aadhaar_filename = secure_filename(
        aadhaar_file.filename
    )

    aadhaar_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        aadhaar_filename
    )

    aadhaar_file.save(aadhaar_path)


    # =================================================
    # SAVE MARKSHEET
    # =================================================

    marksheet_filename = secure_filename(
        marksheet_file.filename
    )

    marksheet_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        marksheet_filename
    )

    marksheet_file.save(marksheet_path)


    # =================================================
    # AADHAAR OCR
    # =================================================

    print("\n==============================")
    print("Starting Aadhaar OCR...")
    print("==============================")

    aadhaar_data = extract_aadhaar(
        aadhaar_path
    )


    # =================================================
    # MARKSHEET OCR
    # =================================================

    print("\n==============================")
    print("Starting Marksheet OCR...")
    print("==============================")

    marksheet_data = extract_marksheet(
        marksheet_path
    )


    # =================================================
    # COMBINE DATA
    # =================================================

    student_data = {

        "name": aadhaar_data.get("name", ""),

        "dob": aadhaar_data.get("dob", ""),

        "gender": aadhaar_data.get("gender", ""),

        "aadhaar": aadhaar_data.get("aadhaar", ""),

        "board": marksheet_data.get("board", ""),

        "seat": marksheet_data.get("seat", ""),

        "year": marksheet_data.get("year", ""),

        "percentage": marksheet_data.get(
            "percentage",
            ""
        )
    }


    # =================================================
    # PRINT OCR DATA
    # =================================================

    print("\n==============================")
    print("EXTRACTED STUDENT DATA")
    print("==============================")

    print("Name       :", student_data["name"])
    print("DOB        :", student_data["dob"])
    print("Gender     :", student_data["gender"])
    print("Aadhaar    :", student_data["aadhaar"])
    print("Board      :", student_data["board"])
    print("Seat       :", student_data["seat"])
    print("Year       :", student_data["year"])
    print("Percentage :", student_data["percentage"])

    print("==============================\n")


    # =================================================
    # AI AGENT VERIFICATION
    # =================================================

    verification = verify_student(
        student_data
    )

    message = generate_response(
        verification["status"]
    )


    # =================================================
    # AUTO FILL FORM
    # =================================================

    return render_template(
        "autofill.html",

        name=student_data["name"],

        dob=student_data["dob"],

        gender=student_data["gender"],

        aadhaar=student_data["aadhaar"],

        board=student_data["board"],

        seat=student_data["seat"],

        year=student_data["year"],

        percentage=student_data["percentage"],

        message=message
    )


# =====================================================
# FINAL REGISTRATION
# =====================================================

@app.route("/success", methods=["POST"])
def success():

    # -------------------------------------------------
    # GET FORM DATA
    # -------------------------------------------------

    name = request.form.get(
        "name", ""
    ).strip()

    dob = request.form.get(
        "dob", ""
    ).strip()

    gender = request.form.get(
        "gender", ""
    ).strip()

    aadhaar = request.form.get(
        "aadhaar", ""
    ).replace(" ", "").strip()

    board = request.form.get(
        "board", ""
    ).strip()

    seat = request.form.get(
        "seat", ""
    ).strip()

    year = request.form.get(
        "year", ""
    ).strip()

    percentage = request.form.get(
        "percentage", ""
    ).strip()


    # =================================================
    # VALIDATION
    # =================================================

    if not name:

        return """
        <h2 style="color:red;text-align:center;">
        ❌ Name is missing
        </h2>
        """


    if not aadhaar:

        return """
        <h2 style="color:red;text-align:center;">
        ❌ Aadhaar Number is missing
        </h2>
        """


    # =================================================
    # DUPLICATE CHECK
    # =================================================

    print("\nChecking duplicate Aadhaar:", aadhaar)

    cursor.execute(
        "SELECT id FROM students WHERE aadhaar=%s",
        (aadhaar,)
    )

    student = cursor.fetchone()


    if student:

        return render_template(
            "already_registered.html",
            aadhaar=aadhaar
        )


    # =================================================
    # INSERT STUDENT
    # =================================================

    sql = """
    INSERT INTO students
    (
        full_name,
        dob,
        gender,
        aadhaar,
        board,
        seat_no,
        passing_year,
        percentage
    )
    VALUES
    (
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    """


    values = (
        name,
        dob,
        gender,
        aadhaar,
        board,
        seat,
        year,
        percentage
    )


    cursor.execute(
        sql,
        values
    )

    db.commit()


    print("✅ Student registered successfully")


    # =================================================
    # SUCCESS PAGE
    # =================================================

    return render_template(
        "success.html",

        name=name,

        dob=dob,

        gender=gender,

        aadhaar=aadhaar,

        board=board,

        seat=seat,

        year=year,

        percentage=percentage
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )