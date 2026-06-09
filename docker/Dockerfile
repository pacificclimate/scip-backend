FROM ubuntu:22.04

RUN apt-get update
RUN apt-get -yq install python3 python3-dev
RUN apt-get -yq install python3-pip postgresql-client
RUN apt-get -yq install curl libpq-dev

ENV FLASK_APP scip.wsgi:app

RUN mkdir /app
WORKDIR /app
ADD . /app/

RUN export PATH="/root/.local/bin:$PATH"
RUN pip install poetry==1.8.5
RUN poetry install



EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/readyz || exit 1

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=5000"]
