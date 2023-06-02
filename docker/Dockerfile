FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -yq install python3 python3-dev
RUN apt-get -yq install python3-pip postgresql-client
RUN apt-get -yq install curl libpq-dev

ENV FLASK_APP scip.wsgi:app

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN export PATH="/root/.local/bin:$PATH"
RUN /root/.local/bin/poetry install



EXPOSE 5000
CMD /root/.local/bin/poetry run flask run --host=0.0.0.0