import os
import subprocess
import tempfile
from flask import Flask, render_template, jsonify, abort, request
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os
import re
from pypdf import PdfReader
from sql_runner import DatabaseConnection, QueryExecutor


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No GEMINI_API_KEY found in .env file!")

genai.configure(api_key=api_key)
modal = genai.GenerativeModel("gemini-1.5-flash")

# Database connection
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_for_codespace = os.getenv("DB_FOR_CODESPACE")

app = Flask(__name__)
CORS(app)

# Dictionary of projects
python_projects = {
    "anti-html": "Write a program anti_html.py that takes a URL as an argument, downloads the HTML from the web, and prints it after stripping HTML tags.",
    "classes-and-objects": "Define a class Person and its two child classes: Male and Female. All classes have a method get_gender which can print Male for Male class and Female for Female Class.",
    "data-manipulation-problem": "A problem on data manipulation using Python.",
    "map-and-lambda-function": "Write a program that can map() to make a list whose elements are squares of numbers between 1 and 20 (both included).",
    "set-and-its-usage": "With a given list [12,24,35,24,88,120,155,88,120,155], write a program to print this list after removing all duplicate values with original order reserved.",
    "xlsx-to-csv-file-converter": "Converting XLSX files to CSV using Python.",
}

sql_projects = {
    "Leetcode-177": "Write an SQL query to report the nth highest salary from the Employee table. If there is no nth highest salary, the query should report null.",
    "Leetcode-570": "Write an SQL query to report the managers with at least five direct reports. Return the result table in any order.",
    "Leetcode-602": "Write an SQL query to find the people who have the most friends and the most friend number",
    "Leetcode-626": "Write an SQL query to swap the seat id of every two consecutive students. If the number of students is odd, the id of the last student is not swapped.",
    "Leetcode-1045": "Write an SQL query to report the customer ids from the Customer table that bought all the products in the Product table",
    "Leetcode-1158": "Write an SQL query to find for each user, the join date and the number of orders they made as a buyer in 2019",
}


@app.route("/")
def index():
    return render_template("index.html")


# ---- Code Space -----
@app.route("/codespace")
@app.route("/codespace/")
def codespace():
    return render_template("codespace.html")


@app.route("/codespace/python", methods=["GET"])
def codespace_python():
    script_path = os.path.join("codespace", "python", "test.py")
    if os.path.isfile(script_path):
        with open(script_path, "r") as f:
            code_content = f.read()
    else:
        code_content = "Error: Script not found."
    return render_template("codespace_python.html", code_content=code_content)


@app.route("/codespace/python", methods=["POST"])
def run_codespace_python():
    data = request.json
    code_content = data.get("code_content")
    custom_input = data.get("user_input")  # Get the custom input
    script_path = os.path.join("codespace", "python", "test.py")

    try:
        # Write the code content to a Python file
        with open(script_path, "w") as script_file:
            script_file.write(code_content)
    except Exception as e:
        return jsonify({"output": f"Error writing script: {str(e)}"})

    try:
        # Run the script and provide the custom input to it
        result = subprocess.run(
            ["python", script_path],
            input=custom_input,  # Pass custom input to the script via stdin
            capture_output=True,
            text=True,  # To handle input/output as strings (text mode)
            timeout=60,
        )
        # Capture the output or error depending on the return code
        output = result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        output = "Error: Script execution timed out."
    except Exception as e:
        output = f"Error: {str(e)}"

    return jsonify({"output": output})


@app.route("/codespace/sql")
def codespace_render_sql_page():
    script_path = os.path.join("codespace", "sql", "codespace-sql.txt")

    if os.path.isfile(script_path):
        with open(script_path, "r") as f:
            query_content = f.read()
    else:
        query_content = "Error: Query not found."

    return render_template("codespace_sql.html", query_content=query_content)


@app.route("/query_run/codespace-sql", methods=["GET"])
def query_run_codespace_sql():
    script_path = os.path.join("codespace", "sql", "codespace-sql.txt")

    if not os.path.isfile(script_path):
        return jsonify({"output": "Error: Query file not found."}), 404

    try:
        db2 = DatabaseConnection(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_FOR_CODESPACE
        )

        db2.connect()

        if db2.connection is None:
            return jsonify({"output": "Error: Failed to connect to the database."}), 500

        with open(script_path, "r") as file:
            query = file.read()

        cursor = db2.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        cursor.close()
        db2.close()

        return jsonify({"columns": column_names, "rows": rows})

    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"}), 500


@app.route("/query_run/codespace-sql", methods=["POST"])
def query_save_codespace_sql():
    script_path = os.path.join("codespace", "sql", "codespace-sql.txt")
    query_content = request.json.get("query_content")

    try:
        with open(script_path, "w") as file:
            file.write(query_content)
        return jsonify({"message": "Query saved successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error saving the query: {str(e)}"}), 500


# ---- SQL Section ----


@app.route("/sql")
@app.route("/sql/")
def sql_page():
    project_keys = sql_projects.keys()
    return render_template("sql_page.html", sql_tasks=project_keys)


@app.route("/sql/<name>")
def sql_project_page(name):
    if name not in sql_projects:
        abort(404, description="Project not found")

    project_value = sql_projects[name]
    script_path = os.path.join("queries", f"{name}.txt")

    if os.path.isfile(script_path):
        with open(script_path, "r") as f:
            query_content = f.read()
    else:
        query_content = "Error: Query not found"

    return render_template(
        "sql_project_page.html",
        project_name=name,
        project_value=project_value,
        query_content=query_content,
    )


@app.route("/run_query/<project_name>", methods=["GET"])
def run_query(project_name):
    script_path = os.path.join("queries", f"{project_name}.txt")

    if not os.path.isfile(script_path):
        return jsonify({"output": "Error: Query file not found."}), 404

    try:
        db = DatabaseConnection(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        db.connect()

        if db.connection is None:
            return jsonify({"output": "Error: Failed to connect to the database."}), 500

        with open(script_path, "r") as file:
            query = file.read()

        cursor = db.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        cursor.close()
        db.close()

        return jsonify({"columns": column_names, "rows": rows})

    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"}), 500


@app.route("/query_run/<project_name>", methods=["POST"])
def query_run(project_name):
    script_path = os.path.join("queries", f"{project_name}.txt")
    query_content = request.json.get("query_content")

    try:
        with open(script_path, "w") as file:
            file.write(query_content)
        return jsonify({"message": "Query saved successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error saving the query: {str(e)}"}), 500


# ---- Python Section ----


@app.route("/python")
@app.route("/python/")
def python_page():
    project_keys = python_projects.keys()
    return render_template("python_page.html", projects=project_keys)


@app.route("/python/<name>")
def python_project_page(name):
    if name not in python_projects:
        abort(404, description="Project not found")

    project_value = python_projects[name]
    script_path = os.path.join("src", name, f"{name}.py")

    if os.path.isfile(script_path):
        with open(script_path, "r") as f:
            code_content = f.read()
    else:
        code_content = "Error: Script not found."

    return render_template(
        "python_project_page.html",
        project_name=name,
        project_value=project_value,
        code_content=code_content,
    )


@app.route("/run_code/<name>", methods=["POST"])
def run_code(name):
    try:
        # Get the posted data
        data = request.json
        code_content = data["code_content"]

        # Create a temporary file to run the code
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(code_content.encode("utf-8"))
            temp_file.flush()
            temp_file_name = temp_file.name

        # Execute the file and capture the output
        result = subprocess.run(
            ["python3", temp_file_name], capture_output=True, text=True
        )

        # Return the result
        if result.returncode == 0:
            return jsonify(output=result.stdout)
        else:
            return jsonify(output=result.stderr), 400
    except Exception as e:
        return jsonify(output=str(e)), 500


# ---- Gen Ai -----


@app.route("/genai")
def genai():
    return render_template("genai.html")


def get_gemini_response(input, prompt):
    response = modal.generate_content([input, prompt])
    return response.text


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    print(file)
    no_of_pages = len(reader.pages)
    text_content = ""
    for i in range(no_of_pages):
        page = reader.pages[i]
        temp_text = page.extract_text()
        if temp_text:
            text_content += "\n" + temp_text  # Corrected concatenation
    return text_content


prompt_templates = {
    "MCQ": """
        You are a question generator. Create 10 multiple-choice questions based on the provided text.
        Format each question as follows:
        - Question number.
        - Four options (A, B, C, D).
        Ensure the questions are clear, concise, and relevant to the input text.
        
        Ensure the questions are different from previosuly generated questions.
    """,
    "MCQ with Answers": """
        You are a question generator. Create 10 multiple-choice questions with answers based on the provided text.
        Format each question as follows:
        - Question number.
        - Four options (A, B, C, D).
        - Provide the correct answer after each question.
        Ensure the questions are clear, concise, and relevant to the input text.
        
        Ensure the questions are different from previosuly generated questions.
    """,
    "Long Questions": """
        You are a question generator. Create 5 long-answer questions based on the provided text.
        Format each question with a question number and ensure it requires detailed responses.
        
        Ensure the questions are different from previosuly generated questions.
    """,
    "Long Questions with Answers": """
        You are a question generator. Create 5 long-answer questions with answers based on the provided text.
        Format each question with a question number followed by the answer.
        Ensure the questions and answers are clear, detailed, and relevant to the input text.
        
        Ensure the questions are different from previosuly generated questions.
    """,
}


@app.route("/generate", methods=["POST"])
def generate():
    try:
        input_text = request.form.get("inputText")
        option = request.form.get("option")
        pdf_file = request.files.get("pdfFile")

        if not input_text and not pdf_file:
            return jsonify({"msg": "Input text or PDF file is required!"}), 400

        if pdf_file:
            input_text = extract_text_from_pdf(pdf_file)

        prompt_template = prompt_templates.get(option)
        if not prompt_template:
            return jsonify({"message": "Invalid option selected"}), 400

        prompt = prompt_template

        response = get_gemini_response(input_text, prompt)

        # Make sentences starting with ** bold
        formatted_response = response.replace("\n", "<br>").replace(". ", ".<br><br>")

        # Find sentences starting with ** and ending with ** and wrap them in <strong> tags
        formatted_response = re.sub(
            r"\*\*(.*?)\*\*", r"<strong>\1</strong>", formatted_response
        )

        # Find sentences starting with * and ending with * and wrap them in <em> tags for semi-bold
        formatted_response = re.sub(r"\*(.*?)\*", r"<em>\1</em>", formatted_response)

        return jsonify({"message": formatted_response}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
