FROM ubuntu
ADD . /code
WORKDIR /code
EXPOSE 7735

ENTRYPOINT "python /code/server.py o.txt 0.2"
