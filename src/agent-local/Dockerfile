#FROM python:3.9-slim-buster
FROM python:3.9

# COPY scale_out_api.py .
# COPY promQL.py .
# COPY requirements.txt .
COPY new_requirements.txt .
# COPY entrypoint.sh .
# RUN chmod +x entrypoint.sh

RUN apt-get update && \
    apt-get install curl -y

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

# RUN pip install prometheus-api-client \
#     Flask \
#     torch torchvision torchaudio \
#     gym \
#     stable-baselines3 \
#     tensorboard

RUN pip install -r new_requirements.txt

EXPOSE 6006
EXPOSE 80

# COPY health_check.py .
# CMD ["python3", "health_check.py"]
# CMD ["python3", "agent_learn.py"]
# ENTRYPOINT ["./entrypoint.sh"]



