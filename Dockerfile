FROM python:3.11

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /app

# COPY poetry.lock pyproject.toml ./
# RUN pip3 install poetry==1.0.* && \
#     poetry config virtualenvs.create false && \
#     poetry install --no-dev


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . ./

CMD uvicorn --host=0.0.0.0 app.main:app



