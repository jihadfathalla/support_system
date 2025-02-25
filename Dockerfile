


# Use an official Python image as the base
FROM python:3.11.4

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



# COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh


# Copy the entire project into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the Django server
# ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]