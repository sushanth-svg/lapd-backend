FROM python:3.11

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

RUN apt-get update -o Acquire::Retries=3 && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

CMD uvicorn --host=0.0.0.0 main:app
# CMD ["python", "main.py"]


