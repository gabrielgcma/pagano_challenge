FROM python:3.11
WORKDIR /opcua
COPY ../opc-ua/ /opcua/
COPY ../requirements.txt /opcua/
RUN pip install --no-cache-dir --upgrade -r /opcua/requirements.txt
WORKDIR /opcua
CMD python3 server.py
