# Nginx+Gunicorn部署Flask应用

`Flask`内建服务器不适用于生产（稳定性差、并发支持差），常用的部署方案是`Flask`+`Gunicorn`+`Nginx`。

- `Flask` 开发框架
- `Gunicorn` 生产服务器
- `Nginx` 前端反向代理服务器

![flask deployment](https://files.realpython.com/media/flask-nginx-gunicorn-architecture.012eb1c10f5e.jpg)

> source from [[1]](#1)

## 1. Flask应用

从之前基础版本的`hello-world`开始：

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello Flask!'

@app.route('/admin/')
def admin_hello():
    return 'Hello Flask Admin!'
```

`flask run`可以启动内建服务器运行`flask`应用，但这里不这么做，继续往下走。

## 2. Gunicorn

`pip`安装

```bash
$ pip install gunicorn
```

`Gunicorn`（`Green Unicorn`）是一个UNIX下的WSGI HTTP服务器，可以运行`Flask`应用:

```bash
$ gunicorn -w 4 \            # 4个进程
        -b 0.0.0.0:5000 \  # IP和端口
        app:app              # 启动文件及应用实例名称
```

`app:app`中的量个`app`：

- 前一个指文件名`app.py`
- 后一个指应用实例名`app = Flask(__name__)`

`Gunicorn`默认使用同步阻塞的网络模型，对于大并发的访问可能表现不够好，因此可以引入`gevent`来增加并发量 [[2]](#2)。

```bash
$ pip install gevent
```

参考配置文件`gunicorn.conf.py`

```python
# 同时开启处理请求的进程数量
workers = 5

# gevent库支持异步处理请求，提高吞吐量 
worker_class = "gevent"

# 监听端口
bind = "0.0.0.0:5000"
```

根据配置文件启动：

```bash
$ gunicorn myproject:app -c gunicorn.conf.py
```

此时可在浏览器中访问`127.0.0.1:5000`


## 3. Nginx代理设置

接下来`Nginx`作为`Gunicorn`服务器的反向代理，同时自身也作为托管静态文件的服务器。关于作为`Gunicorn`服务器的代理设置参考官方文档 [[3]](#3)。

```
server {
    listen 80;

    server_name _;

    access_log  /var/log/nginx/access.log;
    error_log  /var/log/nginx/error.log;

    location / {
        proxy_pass         http://127.0.0.1:5000/;
        proxy_redirect     off;

        proxy_set_header   Host                 $http_host;
        proxy_set_header   X-Real-IP            $remote_addr;
        proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto    $scheme;
    }
}
```

此时可在浏览器中访问`127.0.0.1:80`，即通过`nginx`反向代理到`127.0.0.1:5000`。

**注意**

`nginx`中路径模式必须与`flask`路由匹配，例如上例中`location /`如果改为`location /api`表示所有以`api`开头的URL，则`flask`路由相应改为`@app.route('/api/')`及`@app.route('/api/admin/')`。



## 4. Dockerize

接下来使用`docker-compose`编排容器来组合以上过程，文档[[4]](#4)供参考。

```yml
version: '3'

services:
  flask-hello-world:
    image: flask-hello-world:latest
    container_name: flask-hello-world
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - "./app/:/app/app/"
      - "./conf/gunicorn.conf.py:/app/conf/gunicorn.conf.py"
    expose: 
        - "5000"
    networks:
      - web-net

  nginx-proxy:
    image: nginx:latest
    container_name: nginx-proxy
    ports:
      - "8080:80"
    volumes:
      - "./conf/nginx.conf:/etc/nginx/nginx.conf"
      - "./app/html/:/usr/share/nginx/html/static"
    depends_on:
        - flask-hello-world
    networks:
      - web-net

networks:
  web-net:
```

其中：

- `nginx`服务`nginx-proxy`依赖于`flask-hello-world`，故`nginx`反向代理配置的地址为`http://flask-hello-world:5000`。关键配置信息：

```
# static page
location /static {
    root   /usr/share/nginx/html;
    index  index.html index.htm;
}

# flask proxy
location / {
    proxy_pass         http://flask-hello-world:5000;
    proxy_redirect     off;

    proxy_set_header   Host                 $http_host;
    proxy_set_header   X-Real-IP            $remote_addr;
    proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto    $scheme;
}
```

- `flask-hello-world`服务的模板镜像是从`Dockerfile`创建而来的，考虑到部署后的更新主要来自`flask`应用的逻辑代码层面，故创建镜像时只安装基本的Python模块，不包含具体的代码和数据。后期通过`docker-compose`启动时，再挂载代码数据。这样的好处是，当仅仅更新代码时，无需重新构建镜像。

构建`flask-hello-world`镜像的文件：

```dockerfile
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
```

## 5. 测试

启动容器：

```bash
$ docker-compose up -d
```

在宿主机访问测试链接，得到预期结果：

- `http://localhost:8080/static/` -> `nginx`托管的静态文件，显示`Static file hosted by Nginx...`
- `http://localhost:8080/` -> 代理到`gunicorn`服务器的`5000`端口 -> 匹配`flask`的`/`路由，显示`Hello Flask!`
- `http://localhost:8080/admin` -> 代理到`gunicorn`服务器的`5000`端口 -> 匹配`flask`的`/admin/`路由，显示`Hello Flask Admin!`

关闭容器，结束本篇练习

```bash
$ docker-compose down
```


---

- [[1] Kickstarting Flask on Ubuntu – Setup and Deployment](https://realpython.com/kickstarting-flask-on-ubuntu-setup-and-deployment/)<span id='1'></span>
- [[2] Flask + Docker 无脑部署新手教程](https://zhuanlan.zhihu.com/p/78432719)<span id='2'></span>
- [[3] Standalone WSGI Containers: Proxy Setups](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/#proxy-setups)<span id='3'></span>
- [[4] Flask 应用如何部署](https://juejin.im/entry/5b3ebfadf265da0fa8671f08)<span id='4'></span>

