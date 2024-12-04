FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

# Expose port 5000 for the Flask app
EXPOSE 5000


CMD ["python", "main.py"]
