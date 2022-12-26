FROM python:3.8-slim-buster
MAINTAINER ankittripathi2402@gmail.com

COPY flaskapp/requirements.txt requirements.txt
COPY flaskapp /opt/

RUN pip3 install -r requirements.txt
WORKDIR /opt/

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]



