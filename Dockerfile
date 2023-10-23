# FROM amazon/aws-lambda-python:3.9
FROM --platform=linux/arm64 python:3.11

LABEL maintainer="Andrew Knoesen"
# Installs python, removes cache file to make things smaller
RUN apt update -y && \
    apt install -y cron && \
    rm -Rf /var/cache/apt

# Copies requirements.txt file into the container
COPY . .

# Copy the cron file to the container
COPY cronfile /etc/cron.d/cronfile
RUN touch /var/log/cron.log

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronfile

# Apply the cron job
RUN crontab /etc/cron.d/cronfile

# Installs dependencies found in your requirements.txt file
RUN pip3 install -r requirements.txt

RUN chmod +x /start_service.sh
RUN chmod +x /telegram_main.py
RUN chmod +x /stock_alerter_main.py

# EXPOSE 80

# CMD ["cron", "-f"]
CMD ["bash", "start_service.sh"]