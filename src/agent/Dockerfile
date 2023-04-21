FROM python:3.9-slim-buster

ENV PROJECT_ID=master-thesis-hpa
ENV ZONE=europe-west1-b 
ENV CLUSTER_NAME=master-thesis-hpa-agent
ENV GOOGLE_APPLICATION_CREDENTIALS=kube_api_keys.json

COPY entrypoint.sh .
COPY requirements.txt .
RUN chmod +x entrypoint.sh

RUN apt-get update && \
    apt-get install curl -y

# Download and install Google Cloud SDK
RUN curl https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-367.0.0-linux-x86_64.tar.gz -o /tmp/google-cloud-sdk.tar.gz && \
    tar -xzf /tmp/google-cloud-sdk.tar.gz -C /usr/local && \
    rm -rf /tmp/google-cloud-sdk.tar.gz && \
    ln -s /usr/local/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud && \
    ln -s /usr/local/google-cloud-sdk/bin/gsutil /usr/local/bin/gsutil && \
    ln -s /usr/local/google-cloud-sdk/bin/kubectl /usr/local/bin/kubectl && \
    gcloud config set core/disable_usage_reporting true && \
    gcloud config set component_manager/disable_update_check true && \
    gcloud config set metrics/environment github_docker_image

# install Kubernetes API client for Python
# RUN apt-get install -y git && \
#     git clone --recursive https://github.com/kubernetes-client/python.git && \
#     cd python && \
#     pip install -r requirements.txt && \
#     pip install kubernetes && \
#     cd .. && \
#     rm -rf python && \
#     apt-get remove -y git && \
#     apt-get autoremove -y && \
#     rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt
# RUN pip install google-auth \
#     google-auth-oauthlib \
#     google-auth-httplib2 \
#     prometheus-api-client \
#     Flask \
#     gym \
#     stable-baselines3 \
#     tensorboard

# Authenticate to the GKE cluster
WORKDIR /secrets
COPY /keys/kube_api_keys.json .
RUN gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS} \
    && gcloud config set project ${PROJECT_ID} \
    && gcloud config set compute/zone ${ZONE} \
    && gcloud container clusters get-credentials ${CLUSTER_NAME}

# health check HTTP
EXPOSE 80
# tensorboard
EXPOSE 6006 

# ENTRYPOINT [ "python3", "health_check.py" ]
WORKDIR /
ENTRYPOINT ["entrypoint.sh"]
# CMD ["python3", "agent_learn.py"]



