FROM alpine

RUN mkdir -p /app/
WORKDIR /app/
COPY * .

RUN apk add python3 py-pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "wsgi.py" ]
