FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

EXPOSE 8989

CMD ["gunicorn", "--bind", "0.0.0.0:8989", "--workers", "3", "store.wsgi:application"]
