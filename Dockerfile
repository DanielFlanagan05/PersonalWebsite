# Authors  : Prof. MM Ghassemi <ghassem3@msu.edu>, Daniel Flanagan
# Access instance using `docker exec -it hw3-container_flask-app bash`

# Base OS
FROM ubuntu:20.04
LABEL maintainer="Daniel Flanagan"

# Update
RUN apt update && apt-get update -qq

# Install Python and dependencies
RUN apt -y install python3-pip
RUN apt -y install vim

# Set timezone
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy your app
RUN mkdir /app
COPY . /app
WORKDIR /app

# Install Python requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run must listen on $PORT
EXPOSE 8080
ENV PORT 8080
ENV FLASK_ENV=production

# Run only your app
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class eventlet --threads 8 --timeout 0 app:app
