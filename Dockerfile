FROM python:slim

COPY requirements.txt .

COPY src/ .

RUN pip install -r requirements.txt

CMD python server.py ${CHECKBOX_WS_HOST} ${CHECKBOX_WS_PORT}
