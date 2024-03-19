FROM python:3.11
WORKDIR /app
COPY ../app/ /app/
COPY ../requirements.txt /app/
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
WORKDIR /home
RUN touch data.txt
RUN chmod ugo+rwx data.txt
RUN apt-get update
RUN apt-get install -y vim
WORKDIR /app
CMD python3 client.py

