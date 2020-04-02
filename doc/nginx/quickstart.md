# Nginx

`nginx` is an HTTP and reverse proxy server, a mail proxy server, and a generic TCP/UDP proxy server. [[1]](#1)

![reverse proxy and load balance](https://www.runoob.com/wp-content/uploads/2018/08/1535725078-1224-20160201162405944-676557632.jpg)

> source from [[2]](#2)

`nginx`有一个主进程`master process`和多个子进程`worker process`：

- 主进程加载和执行配置文件，并且维护子进程
- 子进程处理实际请求。

`nginx`采取基于事件模型`event-based model`和`OS`依赖的机制，在多个子进程之间高效地分配请求。子进程的个数在配置文件中指定，或者根据`CPU`核数自动调整。

## 1. Installation

文档[[1]](#1)中有常规的安装方式，这里直接使用docker方式：

```bash
$ docker pull nginx
```

查看镜像

```bash
$ docker image ls nginx
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
nginx               latest              ed21b7a8aee9        25 hours ago        127MB
```

启动并进入容器后查看当前`nginx`版本

```bash
$ nginx -v
nginx version: nginx/1.17.9
```


## 2. Start / Stop Nginx

`nginx`及其子模块的工作方式定义在默认配置文件`/etc/nginx/nginx.conf`中，因此指定配置文件进行启动：

```bash
$ nginx -c /path/to/nginx.conf
```

或者测试配置文件的合法性（不启动）

```bash
$ nginx -t -c /path/to/nginx.conf
```

其中`-c`参数指定配置文件路径，不指定则采用默认文件`/etc/nginx/nginx.conf`

启动`nginx`后，采用如下命令与主进程交互[[3]](#3)：

```bash
$ nginx -s <SIGNAL>
```

其中 `<SIGNAL>` 可以是:

- `quit`   – 从容关闭服务(`gracefully`)，等待工作进程结束已有请求
- `stop`   – 快速关闭服务
- `reload` – 重载配置文件，即不间断服务地重启`nginx`
- `reopen` – 重新打开日志

## 3. 配置文件

配置文件`/etc/nginx/nginx.conf`定义了`nginx`运行的一些默认参数，例如

- `80` 默认端口
- `/var/log/nginx/` 日志目录
- `/usr/share/nginx/html` 网站目录

当然，这些都可以通过自定义配置文件进行修改，更多配置参数参考[[4](#4), [5](#5), [6](#6)]。


## 4. Hello World

大致了解`nginx`及其配置文件后，下面从容器内部回到宿主环境下练习：

映射`8080`端口后启动容器

```bash
$ docker run --name nginx_test -d -p 8080:80 --rm nginx
```

访问`http://localhost:8080/`，即可得到`Welcome to nginx!`的欢迎页面。

以上采用的都是默认参数，更实际的应用是挂载宿主机上的工作目录，例如：

- 替换默认的配置文件`/etc/nginx/nginx.conf`
- 替换网站根目录`/usr/share/nginx/html`
- 替换日志目录`/var/log/nginx/`

```bash
$ docker run --name nginx_test -d \
    -p 8080:80 \
    -v $PWD/conf/nginx-quickstart.conf:/etc/nginx/nginx.conf \
    -v $PWD/www:/usr/share/nginx/html \
    -v $PWD/logs:/var/log/nginx \
    --rm nginx
```

此时访问`http://localhost:8080/`得到的是替换后的页面`Hello Nginx!!`。


---

- [[1] nginx](https://nginx.org/en/)<span id='1'></span>
- [[2] Nginx 配置详解](https://www.runoob.com/w3cnote/nginx-setup-intro.html)<span id='2'></span>
- [[3] Controlling NGINX Processes at Runtime](https://docs.nginx.com/nginx/admin-guide/basic-functionality/runtime-control/)<span id='3'></span>
- [[4] Beginner’s Guide](http://nginx.org/en/docs/beginners_guide.html)<span id='4'></span>
- [[5] Creating NGINX Plus and NGINX Configuration Files](https://docs.nginx.com/nginx/admin-guide/basic-functionality/managing-configuration-files/)<span id='5'></span>
- [[6] Nginx 常用配置](https://learnku.com/laravel/t/2583/nginx-common-configuration)<span id='6'></span>

