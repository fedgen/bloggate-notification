FROM python:3.9

ENV JWT_SECRET_KEY="QYmXTKt6bnzaFi76H7R88FQ"

ENV DB_HOST="127.0.0.1"

ENV DJANGO_SECRET_KEY='django-insecure-wcqs6m4gqx(k_2%0t#wosgpfc5e575hxs8na^ais(a-^(d*vax'

RUN apt update && apt install -y gcc libmariadb-dev-compat

RUN pip install gunicorn

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app/

CMD python manage.py migrate

EXPOSE 80/tcp

ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:80 notification.wsgi