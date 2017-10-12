FROM python:3.6.3-alpine3.4

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pytest

COPY . /app

EXPOSE 8008
CMD ["honcho", "start", "-c", "taskdl=4"]
