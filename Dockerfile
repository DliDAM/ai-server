FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./routers  /code/routers

COPY ./data /code/data

COPY ./templates /code/templates

COPY ./main.py /code/main.py

CMD [ "uvicorn", "main:app","--proxy-headers", "--host", "0.