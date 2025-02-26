FROM python:3.13-slim


WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 5005

CMD ["python", "app.py"]