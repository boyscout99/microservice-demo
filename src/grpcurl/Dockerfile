FROM golang:latest 

RUN go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

COPY demo.proto .
COPY script.sh .

CMD ["sh", "-c", "while true; do sleep 1; done"]