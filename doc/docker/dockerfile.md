# Dockerfile

我们可以从`dockerfile`创建自己的镜像，参考[[1](#1), [2](#2)]。

本节创建一个`ubuntu`镜像，作为后续练习的虚拟环境。

- 基础镜像`ubuntu:latest`
- 更新`apt`源为阿里云
- 安装软件列表
    - `wget`
    - `vim`


## 1. Dockerfile

```dockerfile
FROM ubuntu

# update apt source
COPY sources.list /etc/apt/sources.list

# install wget, vim
RUN apt update && apt install -qy --no-install-recommends \
  wget  vim \
  # clean to reduce the image size
  && apt-get clean \
  && apt-get autoclean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 
```

其中，`sources.list`内容如下：

```
# ubuntu Ali sources
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
```


## 2. Build Image

基本的`build`命令：

```bash
$ docker build \
    -f /path/to/a/Dockerfile \
    -t image-tag \  # e.g. library/image-name:version
    /context/path   # e.g. current path: .
```

新建上述`dockerfile`，在该目录下执行如下指令创建镜像`ubuntu-base:latest`：

```bash
docker build -t ubuntu-base .
```

---

- [[1] Dockerfile reference](https://docs.docker.com/engine/reference/builder/)<span id='1'></span>
- [[2] 使用 Dockerfile 定制镜像](https://yeasy.gitbooks.io/docker_practice/image/build.html)<span id='2'></span>



