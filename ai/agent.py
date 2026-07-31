def verify_student(data):

    required_fields = [
        "name",
        "dob",
        "gender",
        "aadhaar",
        "board",
        "seat",
        "year",
        "percentage"
    ]


    missing = []


    for field in required_fields:

        if not data.get(field):
            missing.append(field)


    if len(missing) > 0:

        return {
            "status": "incomplete",
            "message": "Please provide missing details",
            "missing": missing
        }


    return {

        "status": "success",
        "message": "All details verified successfully"

    }



def generate_response(status):

    if status == "success":

        return "🤖 AI Agent: Details verified. You can submit registration."

    else:

        return "🤖 AI Agent: Some details are missing. Please check again."