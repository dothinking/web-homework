# Docker

`Docker` is a platform for developers and sysadmins to **build, run, and share applications with containers**.

## 1. Architecture

![docker architecture](https://docs.docker.com/engine/images/architecture.svg)

*source from [[1]](#1)*

- `Image`：类似于一个root文件系统
- `Container`：镜像运行时的实体
- `Repository`：镜像存储中心

## 2. Installation

- Linux系统以`Ubuntu`为例，参考步骤[[2]](#2)；使用国内镜像加速安装参考[[3]](#3)
- Windows系统下载安装`Docker for Windows`
- WSL同时需要以上两步：使用Linux的Client连接Windows中的`docker deamon`，参考[[4]](#4)

### 启动docker服务

将当前用户加入`docker`组

```bash
sudo usermod -aG docker $USER
```
启动`docker`服务：

```bash
sudo service docker start
```

### 检查版本

```bash
docker version
```

### 设置国内镜像源[[5]](#5)

`docker pull`默认从`Docker Hub`获取镜像，设置国内镜像源进行加速

```json
# vi /etc/docker/daemon.json
{
    "registry-mirrors": ["http://hub-mirror.c.163.com"]
}
```

Docker for Windows设置`Docker Engine`：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://registry.docker-cn.com"
  ],
  "insecure-registries": [
    "hub-mirror.c.163.com"
  ],
  "debug": true,
  "experimental": false
}
```

## 3. Hello World

```bash
$ docker container run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
1b930d010525: Pull complete
Digest: sha256:f9dfddf63636d84ef479d645ab5885156ae030f611a56f3a7ac7f2fdd86d7e4e
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

查看已经安装的镜像

```bash
$ docker image ls
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
hello-world         latest              fce289e99eb9        14 months ago       1.84kB
```

查看已经启动的容器

```bash
$ docker container ls -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS                     PORTS               NAMES
35fa36bd1b78        hello-world         "/hello"            2 hours ago         Exited (0) 5 minutes ago                       romantic_archimedes
```

更多关于镜像和容器的操作参考[[6](#6), [7](#7)]



---

- [[1] Docker overview](https://docs.docker.com/engine/docker-overview/)<span id='1'></span>
- [[2] Get Docker Engine - Community for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)<span id='2'></span>
- [[3] Docker Community Edition 镜像使用帮助](https://mirror.tuna.tsinghua.edu.cn/help/docker-ce/)<span id='3'></span>
- [[4] 在WSL中使用docker](http://zuyunfei.com/2018/07/06/use-docker-in-wsl/)<span id='4'></span>
- [[5] docker 设置国内镜像源](https://blog.csdn.net/whatday/article/details/86770609)<span id='5'></span>
- [[6] docker image](https://docs.docker.com/engine/reference/commandline/image/)<span id='6'></span>
- [[7] docker container](https://docs.docker.com/engine/reference/commandline/container/)<span id='7'></span>