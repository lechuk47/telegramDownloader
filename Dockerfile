FROM python:3.7-slim


RUN \
  pip install telethon

WORKDIR /app

CMD python /app/main.py
