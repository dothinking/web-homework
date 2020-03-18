
分布式、高可用数据采集中间件。


## 1. Architecture

![flume architecture](http://flume.apache.org/_images/DevGuide_image00.png)

*source from [[1]](#1)*


## 2. Installation

```bash
# install jdk
apt install -y default-jdk

# download and unzip Flume
wget -qO apache-flume-1.9.0-bin.tar.gz https://mirrors.tuna.tsinghua.edu.cn/apache/flume/1.9.0/apache-flume-1.9.0-bin.tar.gz

tar -xzf apache-flume-1.9.0-bin.tar.gz -C /opt
rm -f apache-flume-1.9.0-bin.tar.gz
mv /opt/apache-flume-1.9.0-bin /opt/flume

# set up env. var
JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
PATH=$PATH:$JAVA_HOME/bin:/opt/flume/bin
export JAVA_HOME
```

## 3. Launch

```bash
# run a Flume agent
flume-ng agent  --conf path/to/conf-folder \
                --conf-file path/to/conf-file.conf \
                --name agent-name-defined in conf-file.conf
```

## 4. Hello World [[2]](#2)

### 4.1 准备配置文件

```bash
# example.conf: A single-node Flume configuration

# Name the components on this agent
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# Describe/configure the source
a1.sources.r1.type = netcat
a1.sources.r1.bind = localhost
a1.sources.r1.port = 44444
a1.sources.r1.channels = c1

# Use a channel which buffers events in memory
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100

# Describe the sink
a1.sinks.k1.type = logger
a1.sinks.k1.channel = c1
```

### 4.2 启动`Flume`

```bash
/opt/flume/conf# flume-ng agent --conf . --conf-file example.conf --name a1 -Dflume.root.logger=INFO,console
```

### 4.3 测试

启动新的控制台进行测试：输入Hello Flume，回车后得到OK

```bash
# telnet localhost 44444
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Hello Flume
OK
```

之前启动`Flume`的控制台显示接收到的`event`：

```bash
Event: { headers:{} body: 48 65 6C 6C 6F 20 46 6C 75 6D 65 0D             Hello Flume. }
```



## 5. Dockerfile [[3](#3), [4](#4)]


将以上过程写成`dockfile`，以便后续以容器的方式进行多节点`Flume`测试。配置参数：

- source监听端口：44444
- sink监听端口：55555
- 配置文件挂载目录：`/opt/flume/conf/usr`，其中配置文件名`flume.conf`

> *使用[docker章节](../docker/dockerfile.md)创建的`ubuntu-base`作为基础镜像*

```bash
FROM ubuntu-base

# install java
RUN apt install -qy --no-install-recommends default-jdk

# download and unzip Flume
RUN wget https://mirrors.tuna.tsinghua.edu.cn/apache/flume/1.9.0/apache-flume-1.9.0-bin.tar.gz && \
  tar -xzf apache-flume-1.9.0-bin.tar.gz -C /opt && \
  mv /opt/apache-flume-1.9.0-bin /opt/flume

# set environment variables
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
ENV PATH /opt/flume/bin:$PATH

EXPOSE 44444
EXPOSE 55555

ENTRYPOINT ["/opt/flume/bin/flume-ng", "agent", "--conf", "/opt/flume/conf", "-conf-file", "/opt/flume/conf/usr/flume.conf", "--name", "a1"]
```



---

-  [[1] Apache Flume](http://flume.apache.org/)<span id='1'></span>
- [[2] Flume 1.9.0 User Guide](http://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html)<span id='2'></span>
- [[3] Docker容器中运行flume](https://blog.csdn.net/redstarofsleep/article/details/79756740)<span id='3'></span>
- [[4] 基于 Docker 构建 Flume](https://segmentfault.com/a/1190000000504942)<span id='4'></span>