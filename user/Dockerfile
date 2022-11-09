FROM golang:1.16 AS builder
WORKDIR /go/src/vdg/helloworld/
RUN go mod init
COPY app.go ./
RUN CGO_ENABLED=0 go build -a -installsuffix cgo -o app .

FROM alpine:latest  
RUN adduser -S -H monuser -h /
USER monuser
WORKDIR /
COPY --from=builder --chown=monuser:nogroup /go/src/vdg/helloworld/app ./
CMD ["./app"]
