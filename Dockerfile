# pull official base image
FROM python:3.10.6
ENV PYTHONUNBUFFERED 1
RUN apt install git
RUN git clone https://github.com/unlimmitted/MikroTik_WG_WebManager.git
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN python manage.py makemigrations
RUN python manage.py migrate
