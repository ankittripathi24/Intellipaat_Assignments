FROM python:3.10-buster
MAINTAINER ankittripathi2402@gmail.com

COPY flaskapp/requirements.txt requirements.txt
COPY flaskapp /opt/

RUN pip3 install --no-cache-dir -r requirements.txt
WORKDIR /opt/

CMD [ "gunicorn", "--bind" , "0.0.0.0:5000", "app:app"]



