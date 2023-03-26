FROM python:3.7.3

LABEL maintainer="epsiloninfinityservices@gmail.com"

RUN mkdir -p /latherapeutics/
COPY . /latherapeutics/
WORKDIR /latherapeutics/

RUN python3 --version && pip3 install --upgrade pip && pip3 --version

RUN pip3 install -r requirements.txt

EXPOSE 8084

ENTRYPOINT ["python3", "app.py"]
