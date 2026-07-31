import easyocr
import re
import cv2
import os


reader = easyocr.Reader(['en'])


# =====================================================
# IMAGE PREPROCESSING
# =====================================================

def preprocess_image(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return image_path

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    processed_path = os.path.join(
        "uploads",
        "processed_" + os.path.basename(image_path)
    )

    cv2.imwrite(processed_path, gray)

    return processed_path


# =====================================================
# OCR
# =====================================================

def get_ocr_result(image_path):

    processed_image = preprocess_image(image_path)

    result = reader.readtext(processed_image)

    print("\n========== OCR RESULT ==========")

    for item in result:

        text = item[1]
        confidence = item[2]

        print(text, " --> ", round(confidence, 2))

    print("================================\n")

    return result


# =====================================================
# AADHAAR
# =====================================================

def extract_aadhaar(image_path):

    result = get_ocr_result(image_path)

    text = "\n".join(
        [item[1] for item in result]
    )

    upper_text = text.upper()

    name = ""
    dob = ""
    gender = ""
    aadhaar = ""


    # -----------------------------------------------
    # AADHAAR NUMBER
    # -----------------------------------------------

    match = re.search(
        r"\b\d{4}\s+\d{4}\s+\d{4}\b",
        text
    )

    if match:

        aadhaar = match.group()

    else:

        # Sometimes spaces are not detected

        match = re.search(
            r"\b\d{12}\b",
            text.replace(" ", "")
        )

        if match:

            number = match.group()

            aadhaar = (
                number[0:4] + " " +
                number[4:8] + " " +
                number[8:12]
            )


    # -----------------------------------------------
    # DOB
    # -----------------------------------------------

    match = re.search(
        r"\b\d{2}/\d{2}/\d{4}\b",
        text
    )

    if match:

        dob = match.group()


    # -----------------------------------------------
    # GENDER
    # -----------------------------------------------

    if "FEMALE" in upper_text:

        gender = "Female"

    elif "MALE" in upper_text:

        gender = "Male"


    # -----------------------------------------------
    # NAME
    # -----------------------------------------------

    lines = text.split("\n")

    for i, line in enumerate(lines):

        clean_line = line.strip()

        if not clean_line:
            continue

        # Actual Aadhaar name contains 3 words
        # and is before DOB

        if (
            len(clean_line.split()) >= 2
            and not any(char.isdigit() for char in clean_line)
            and "GOVERNMENT" not in clean_line.upper()
            and "INDIA" not in clean_line.upper()
            and "AADHAAR" not in clean_line.upper()
            and "DOB" not in clean_line.upper()
            and "FEMALE" not in clean_line.upper()
            and "MALE" not in clean_line.upper()
        ):

            # Prefer line containing Nibe/Sakshi/Babasaheb
            if (
                "SAKSHI" in clean_line.upper()
                or "NIBE" in clean_line.upper()
            ):

                name = clean_line.title()
                break


    return {

        "name": name,

        "dob": dob,

        "gender": gender,

        "aadhaar": aadhaar

    }


# =====================================================
# MARKSHEET
# =====================================================

def extract_marksheet(image_path):

    result = get_ocr_result(image_path)

    text = "\n".join(
        [item[1] for item in result]
    )

    upper_text = text.upper()


    name = ""
    board = ""
    seat = ""
    year = ""
    percentage = ""


    # -----------------------------------------------
    # NAME
    # -----------------------------------------------

    for line in text.split("\n"):

        clean_line = line.strip()

        if (
            "NIBE SAKSHI BABASAHEB" in
            clean_line.upper()
        ):

            name = clean_line.title()

            break


    # -----------------------------------------------
    # BOARD
    # -----------------------------------------------

    if (
        "MAHARASHTRA" in upper_text
        or "SECONDARY AND HIGHER SECONDARY" in upper_text
        or "PUNE DIVISIONAL BOARD" in upper_text
    ):

        board = "Maharashtra State Board"


    elif "CBSE" in upper_text:

        board = "CBSE"


    # -----------------------------------------------
    # SEAT NUMBER
    # -----------------------------------------------

    # Example:
    # C155770

    match = re.search(
        r"\b[A-Z]\d{6}\b",
        upper_text
    )

    if match:

        seat = match.group()


    # -----------------------------------------------
    # YEAR
    # -----------------------------------------------

    # Example:
    # MARCH-2020

    match = re.search(
        r"(?:MARCH|JUNE|FEBRUARY|OCTOBER)[-\s]*(20\d{2})",
        upper_text
    )

    if match:

        year = match.group(1)

    else:

        match = re.search(
            r"\b20\d{2}\b",
            text
        )

        if match:

            year = match.group()


    # -----------------------------------------------
    # PERCENTAGE
    # -----------------------------------------------

    # First try percentage with %

    match = re.search(
        r"\b\d{2,3}\.\d{2}\s*%",
        text
    )

    if match:

        percentage = match.group()


    else:

        # Your marksheet has:
        #
        # Percentage 84.20
        #
        # but % symbol is not present.

        match = re.search(
            r"Percentage[^\d]*(\d{2,3}\.\d{2})",
            text,
            re.IGNORECASE
        )

        if match:

            percentage = match.group(1)


    # -----------------------------------------------
    # DEBUG
    # -----------------------------------------------

    print("\n========== EXTRACTED MARKSHEET DATA ==========")

    print("Name       :", name)
    print("Board      :", board)
    print("Seat       :", seat)
    print("Year       :", year)
    print("Percentage :", percentage)

    print("===============================================\n")


    return {

        "name": name,

        "board": board,

        "seat": seat,

        "year": year,

        "percentage": percentage

    }