Docker is a platform for developers and sysadmins to build, run, and share applications with containers.

## Architecture

![docker architecture](https://docs.docker.com/engine/images/architecture.svg)

*source from [[1]](#1)*

- `Image`：类似于一个root文件系统
- `Container`：镜像运行时的实体
- `Repository`：镜像存储中心

## Installation

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

## 主要命令

- `docker image ...` [[6]](#6)
- `docker container ...` [[7]](#7)



---

- <span id='1'>[1]</span> [Docker overview](https://docs.docker.com/engine/docker-overview/)
- <span id='2'>[2]</span> [Get Docker Engine - Community for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- <span id='3'>[3]</span> [Docker Community Edition 镜像使用帮助](https://mirror.tuna.tsinghua.edu.cn/help/docker-ce/)
- <span id='4'>[4]</span> [在WSL中使用docker](http://zuyunfei.com/2018/07/06/use-docker-in-wsl/)
- <span id='5'>[5]</span> [docker 设置国内镜像源](https://blog.csdn.net/whatday/article/details/86770609)
- <span id='6'>[6]</span> [docker image](https://docs.docker.com/engine/reference/commandline/image/)
- <span id='7'>[7]</span> [docker container](https://docs.docker.com/engine/reference/commandline/container/)
