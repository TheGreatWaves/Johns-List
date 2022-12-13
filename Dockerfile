# syntax=docker/dockerfile:1
FROM python:3.10
WORKDIR /code
ENV FLASK_APP=johns_list.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get install python3
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["flask", "run"]