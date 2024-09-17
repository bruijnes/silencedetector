# Use the Alpine Linux base image
FROM alpine:latest

# Set the working directory in the container
WORKDIR /app

# Copy the necessary scripts into the container
COPY monitor.sh /app/

# Make scripts executable
RUN chmod +x /app/monitor.sh
RUN apk update
RUN apk add curl ffmpeg grep

CMD [ "/bin/sh", "-c", "/app/monitor.sh" ]