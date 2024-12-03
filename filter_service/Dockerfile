FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY filter_service.py ./

CMD ["python", "filter_service.py"]
