# Flask

`Flask`是典型的微框架，仅保留了核心功能：

- 请求响应处理，由`Werkzeug`（`WSGI`工具库）完成
- 模板渲染，由`Jinja`模板渲染库完成

具体使用参考官方文档或在线书籍 [[1](#1), [2](#2)]。


## 1. Installation

直接`pip`安装`flask`，如果出现网络连接问题，可以加上`-i`参数改用国内`pypi`源，或者`--proxy`使用代理：

```
$ pip install flask

$ pip install flask \
        -i https://pypi.tuna.tsinghua.edu.cn/simple/
        --proxy xx.xx.xx.xx:yyyy
```

查看当前版本

```bash
$ flask --version

Python 3.6.10
Flask 1.1.1
Werkzeug 1.0.1
```

## 2. Hello World

新建文件`app.py`

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

`flask run`命令默认启动当前路径下的`app.py`：

```bash
$ flask run

 * Serving Flask app "app.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

在浏览器中访问：
- `http://localhost:5000`得到`Hello Flask!`
- `http://localhost:5000/admin`得到`Hello Flask Admin!`

如果启动脚本文件不是默认的`app.py`，例如`hello.py`，则可以通过指定环境变量`FLASK_APP`后再执行：

```bash
$ export FLASK_APP=hello.py
$ flask run
```

注意：

- 定义环境变量`export FLASK_DEBUG=1`来开启调试模式

- 执行`flask run`使用内置的开发服务器（默认监听本地`5000 `端口），部署上线时必须换用性能更好的服务器。

- `flask run`默认只允许当前机器访问，如果允许其他机器公开访问，例如从宿主机访问`docker`中的`flask`应用，需要加上`--host=0.0.0.0`参数：

```bash
$ flask run --host=0.0.0.0
```


## 3. Blueprints

上面`Hello World`示例中，所有路由（尽管目前只有两个）都定义在一个文件`app.py`中；随着项目的复杂化，这个文件将变得越来越臃肿，不利于理解和维护。因此，非常有必要进行模块化，例如分为前台、后台功能。

`Blueprint`即是`flask`提供的用于模块化的方式。顾名思义，它是一个用于构建和扩展应用（即`flask`实例）的“蓝图”。

> 关于蓝图的官方文档参考[[3]](#3)。

上面练习中的`hello`和`admin_hello`分别属于前、后台功能，接下来采用蓝图将它们分离开来。分离后的目录结构：

```bash
$ tree
.
├── admin
│   ├── __init__.py
│   └── views.py
├── home
│   ├── __init__.py
│   └── views.py
└── app.py
```

整个过程分为两步：

### 3.1 定义蓝图

`home`和`admin`文件夹下的`views.py`分别是各自的蓝图，其中定义了相应模块下的路由：

```python
# home/views.py
from flask import Blueprint
 
home = Blueprint('home', __name__)
 
@home.route('/')
def hello():
    return 'Hello Flask!'
```

```python
# admin/views.py
from flask import Blueprint
 
admin = Blueprint('admin', __name__)
 
@admin.route('/')
def hello():
    return 'Hello Flask Admin!'
```

可见，和之前`app.py`中定义路由的**形式**非常相像，并且达到了按模块拆分的目的。


### 3.2 注册蓝图

导入上一步定义好的蓝图，注册到`app`即可

```python
# app.py
from flask import Flask

from admin.views import admin
from home.views import home

# app instance
app = Flask(__name__)

# register blueprints
app.register_blueprint(home)
app.register_blueprint(admin, url_prefix='/admin')
```

其中注册`admin`蓝图时的参数`url_prefix='/admin'`表明，`admin`蓝图下的所有路由都在`http://localhost:5000/admin`路径下。

启动`flask`后测试，得到相同的结果。

本例使用蓝图的文件夹结构是按照模块分的，每个模块文件夹下五脏俱全（视图、静态资源、模板等）；另外也可以按照功能布局，顶层分为视图、模板、静态资源，然后分别在各个功能文件夹下实现蓝图。具体参考文档[[4]](#4)。


## 4. Dockerize Hello-World

根据以上步骤创建`DOckerfile`

```dockerfile
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
```

创建镜像

```bash
$ docker build -t flask-hello-world .
```

创建容器

```bash
$ docker run --rm -d -p 8080:5000 flask-hello-world
```

---

- [[1] Flask’s documentation 1.1.x](https://flask.palletsprojects.com/en/1.1.x/)<span id='1'></span>
- [[2] Flask入门教程](https://read.helloflask.com/)<span id='2'></span>
- [[3] Modular Applications with Blueprints](https://flask.palletsprojects.com/en/1.1.x/blueprints/)<span id='3'></span>
- [[4] 蓝图-Flask之旅](https://spacewander.github.io/explore-flask-zh/7-blueprints.html)<span id='4'></span>