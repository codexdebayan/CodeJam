# README

## Project Overview

This README provides a comprehensive guide to the Flask application, including route definitions, function names, and short descriptions of their functionalities. The application supports both Python and SQL code execution and integrates with Google Gemini AI for content generation.

## Routes and Function Descriptions

### General Routes

- `GET /`: Renders the main index page of the application.

### Codespace Routes

- `GET /codespace`: Renders the codespace page.
  
- `GET /codespace/python`: Displays the content of a Python script located in the codespace.
  
- `POST /codespace/python`: Executes the provided Python code with custom input and returns the output.
  
- `GET /codespace/sql`: Renders the SQL codespace page with a predefined SQL query.
  
- `GET /query_run/codespace-sql`: Executes a predefined SQL query from the codespace and returns the results.
  
- `POST /query_run/codespace-sql`: Saves a new SQL query to the codespace.

### SQL Routes

- `GET /sql`: Renders a page listing available SQL projects.
  
- `GET /sql/<name>`: Displays details for a specific SQL project based on its name.
  
- `GET /run_query/<project_name>`: Executes a specific SQL query and returns the results.
  
- `POST /query_run/<project_name>`: Saves a new SQL query for a specific project.

### Python Routes

- `GET /python`: Renders a page listing available Python projects.
  
- `GET /python/<name>`: Displays details for a specific Python project based on its name.
  
- `POST /run_code/<name>`: Executes provided Python code and returns the output.

### AI Integration Route

- `GET /genai`: Renders the page for generating content using Google Gemini AI.
  
- `POST /generate`: Processes input text or PDF files to generate questions using AI based on selected templates.
