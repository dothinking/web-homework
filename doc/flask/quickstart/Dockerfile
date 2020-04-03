FROM python:3.6-alpine

ENV FLASK_APP "app.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True

# create project path
WORKDIR /app

# copy and install packages
COPY requirements.txt .
RUN pip install -r requirements.txt  --no-cache-dir \
                -i https://pypi.tuna.tsinghua.edu.cn/simple

# copy app
COPY app .

EXPOSE 5000

CMD flask run --host=0.0.0.0