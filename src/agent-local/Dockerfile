FROM python:3.9-slim-buster

WORKDIR /app

COPY scale_out_api.py .
COPY promQL.py .
COPY health_check.py .

RUN apt-get update && \
    apt-get install curl -y

RUN apt-get install -y git && \
    git clone --recursive https://github.com/kubernetes-client/python.git && \
    cd python && \
    pip install -r requirements.txt && \
    pip install kubernetes && \
    cd .. && \
    rm -rf python && \
    apt-get remove -y git && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN pip install prometheus-api-client \
    Flask

EXPOSE 80

ENTRYPOINT [ "python3", "scale_out_api.py" ]



