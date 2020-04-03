# install python modules only, e.g. flask, gunicorn
# app data and configuration files will be mounted with volumes
# - working path: /app
# - flask app path: /app/app/
# - flask app main file: /app/app/app.py
# - gunicorn config file: /app/conf/gunicorn.conf.py

# 
FROM python:3.6-alpine

# create project path
WORKDIR /app

# copy and install packages
COPY requirements.txt .
RUN pip install -r requirements.txt  --no-cache-dir \
                -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 5000

WORKDIR /app/app

CMD gunicorn app:app -c /app/conf/gunicorn.conf.py