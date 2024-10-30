FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6868

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6868"]