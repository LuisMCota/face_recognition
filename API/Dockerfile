FROM python:3.12.0-rc-slim-buster

WORKDIR /app-face

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", 'server.py' ]
