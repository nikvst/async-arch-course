FROM python:3.11-slim
RUN pip install poetry

WORKDIR /code

ADD pyproject.toml poetry.lock /code/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

ADD ./alembic.ini /code
ADD ./migrations/ /code/migrations
ADD ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
