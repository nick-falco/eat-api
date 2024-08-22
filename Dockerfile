FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", ":8080", "src.api:app", "--timeout", "120"]
