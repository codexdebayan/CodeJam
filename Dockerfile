FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code folders to the container
COPY codespace /app/codespace
COPY queries /app/queries
COPY src /app/src
COPY static /app/static
COPY templates /app/templates

# Copy the .env and other necessary files to the container
COPY .env /app/.env
COPY app.py /app/app.py
Copy sql_runner.py /app/sql_runner.py

# Expose the Flask default port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]