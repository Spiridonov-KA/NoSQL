FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install 'pydantic[email]'

EXPOSE 8085

COPY ./app /code/app
COPY ./test /code/test
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
