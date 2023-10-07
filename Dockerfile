# FROM amazon/aws-lambda-python:3.9
FROM --platform=linux/amd64 python:3.9

LABEL maintainer="Andrew Knoesen"
# Installs python, removes cache file to make things smaller
RUN apt update -y && \
    apt install -y python3 python3-dev python3-pip gcc cron && \
    rm -Rf /var/cache/apt

# Copies requirements.txt file into the container
COPY requirements.txt ./
# Installs dependencies found in your requirements.txt file
RUN pip install -r requirements.txt

# Be sure to copy over the function itself!
# Goes last to take advantage of Docker caching.
COPY . .

EXPOSE 80

# Points to the handler function of your lambda function
# CMD ["app.handler"]
# ENTRYPOINT [ "executable" ]
# CMD ["python3", "main.py"]
RUN chmod a+x script.sh

CMD ["./script.sh"]