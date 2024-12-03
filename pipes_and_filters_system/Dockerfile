FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set environment variables for SMTP configuration
ENV SMTP_SERVER=smtp.example.com
ENV SMTP_PORT=587
ENV SMTP_USER=your_email@example.com
ENV SMTP_PASSWORD=your_password
ENV RECIPIENTS=recipient@example.com

CMD ["python", "main.py"]
