FROM ubuntu:22.04

RUN apt-get update
RUN apt-get -yq install python3 python3-dev
RUN apt-get -yq install python3-pip postgresql-client
RUN apt-get -yq install curl libpq-dev python3-poetry

ENV FLASK_APP scip.wsgi:app

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN export PATH="/root/.local/bin:$PATH"
RUN poetry install



EXPOSE 5000
CMD /root/.local/bin/poetry run flask run --host=0.0.0.0