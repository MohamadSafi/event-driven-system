FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY publish_service.py ./

CMD ["python", "publish_service.py"]
