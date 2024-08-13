FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./router  /code/router

CMD [ "uvicorn", "main:app","--proxy-headers", "--host", "0.0.0.0", "--port","80" ]
