FROM python:3.14
MAINTAINER Frédéric Rodrigo <fred.rodrigo@gmail.com>

RUN mkdir -p /data/work/root/results/

RUN apt update && \
    apt install -y --no-install-recommends \
        bzip2 \
        gettext \
        postgresql-client && \
    apt-get clean

WORKDIR /data/project/osmose/frontend
COPY requirements.txt .
RUN pip install uvicorn && \
    pip install -r requirements.txt

COPY web web
COPY web_api web_api
RUN cd web/po && make mo && cd ..

COPY . .

ENV LANG en_US.UTF-8
CMD uvicorn osmose:app --host 0.0.0.0 --port 20009 --reload --reload-delay 10
EXPOSE 20009
