FROM python:3.7-stretch


WORKDIR /home/patrickapp


COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install --upgrade setuptools
RUN venv/bin/pip install pymysql


COPY app app
COPY migrations migrations
COPY patrickapp.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP patrickapp.py


EXPOSE 5000
ENTRYPOINT ["./boot.sh"]