FROM python:2.7

MAINTAINER Eugene-Yuan Kow

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app/
RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["/usr/src/app/run.sh"]
