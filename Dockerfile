FROM python:3
RUN apt-get update && apt-get -y install cron vim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --target="packages"
ENV PYTHON_ENV=production
COPY run-python.sh ./
COPY crontab /etc/cron.d/crontab
COPY /src /app/src
COPY entrypoint.sh ./entrypoint.sh
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

ENTRYPOINT ["sh", "/app/entrypoint.sh"]

