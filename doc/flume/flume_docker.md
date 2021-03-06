# Flume多节点连接实践

在[Flume入门](quickstart.md)的基础上，利用`docker`练习分布式`Flume`。

- flume-1监控文件`/tmp/test.log`
- flume-2监听指定端口的数据流
- flume-3接收flume-1、flume-2数据并打印到控制台


## 1. 创建镜像

利用[`dockfile`](quickstart.md)构建镜像`flume:1.9.0`：

```bash
$ docker build . -t flume:1.9.0
```

## 2. 准备配置文件 [[1]](#1)

在宿主机器上分别准备三个节点的配置文件。

### 2.1 监控文件

- 以`avro`方式输出，需要提供主机名和端口号
- 主机名采用`flume-3` -> 启动容器时关联`--link flume-3`

```bash
# flume-1/flume.conf
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# source
a1.sources.r1.type = exec
a1.sources.r1.command = tail -F /tmp/test.log
a1.sources.r1.shell = /bin/bash -c
a1.sources.r1.channels = c1

# sink
a1.sinks.k1.type = avro
a1.sinks.k1.hostname = flume-3
a1.sinks.k1.port = 55555
a1.sinks.k1.channel = c1

# channel
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100
```

### 2.2 监听端口

- 以`avro`方式输出，需要提供主机名和端口号
- 主机名采用`flume-3` -> 启动容器时关联`--link flume-3`

```bash
# flume-2/flume.conf
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# source
a1.sources.r1.type = netcat
a1.sources.r1.bind = 0.0.0.0
a1.sources.r1.port = 44444
a1.sources.r1.channels = c1

# sink
a1.sinks.k1.type = avro
a1.sinks.k1.hostname = flume-3
a1.sinks.k1.port = 55555
a1.sinks.k1.channel = c1

# channel
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100
```

### 2.3 接收节点数据

`flume-1`及`flume-2`输出端口都为`55555`，故此处`source`监听端口相应为`55555`。

```bash
# flume-3/flume.conf
a1.sources = r1
a1.sinks = k1
a1.channels = c1

# source
a1.sources.r1.type = avro
a1.sources.r1.bind = 0.0.0.0
a1.sources.r1.port = 55555
a1.sources.r1.channels = c1

# sink
a1.sinks.k1.type = logger
a1.sinks.k1.channel = c1

# channel
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100
```

## 3. 启动容器

首先启动`flume-3`：为便于直接观察结果，不以后台模式启动

```bash
$ docker run -v /path/to/workspace/flume-3:/opt/flume/conf/usr \
           --name flume-3 \
           flume:1.9.0 \
           -Dflume.root.logger=INFO,console # 控制台打印输出便于观察
```

然后新建控制台，依次启动`flume-1`和`flume-2`

```bash
# flume-1
$ docker run -d \
           -v /path/to/workspace/flume-1:/opt/flume/conf/usr \
           -p 44441:44444 -p 55551:55555 \   # 映射暴露的端口，以免冲突
           -v /path/to/workspace/tmp:/tmp \  # 关联被监控的文件到宿主机位置
           --name flume-1 \
           --link flume-3 \                  # 关联容器flume-3
           flume:1.9.0
# flume-2
$ docker run -d \
           -v /path/to/workspace/flume-2:/opt/flume/conf/usr \
           -p 44442:44444 -p 55552:55555 \   # 映射暴露的端口，以免冲突
           --name flume-2 \
           --link flume-3 \                  # 关联容器flume-3
           flume:1.9.0
```

## 4. 测试结果

测试监控文件：在宿主机器上写入数据到被监控的文件`/path/to/workspace/tmp/test.log`

```bash
$ echo hello world >> /path/to/workspace/tmp/test.log
```

在宿主机上向测试端口发送数据：

```bash
$ telnet localhost 44442
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
hello flume
OK
```

在启动`flume-3`容器的控制台上即可输出相应的信息：

```bash
Event: { headers:{} body: 68 65 6C 6C 6F 20 77 6F 72 6C 64                hello world }
Event: { headers:{} body: 68 65 6C 6C 6F 20 66 6C 75 6D 65 0D             hello flume. }
```

## 5. docker-compose

将以上手动启动过程写为`docker-compose`文件：

- `docker run`使用`--link`参数来关联容器`flume-1`、`flume-2`与`flume-3`之间的通信，同理可以使用`docker-compose`的`links`关键字实现相同的效果
- 新版`docker-compose`推荐使用`networks`来管理容器间通信，同一`yml`配置文件中的容器默认共享网络，所以可以直接相互访问 [[2]](#2)

> 更多关于`docker-compose`网络设置的案例，例如链接定义在不同`docker-compose.yml`中的容器，参考[[3](#3), [4](#4)]


```yml
version: '3'

services:
  flume3:
    image: flume:1.9.0
    container_name: flume-3
    volumes:
      - ./flume-3:/opt/flume/conf/usr
    command: -Dflume.root.logger=INFO,console

  flume2:
    image: flume:1.9.0
    container_name: flume-2
    ports:
      - "44442:44444"
      - "55552:55555"
    depends_on:
      - flume3
    volumes:
      - ./flume-2:/opt/flume/conf/usr

  flume1:
    image: flume:1.9.0
    container_name: flume-1
    ports:
      - "44441:44444"
      - "55551:55555"
    depends_on:
      - flume3
    volumes:
      - ./flume-1:/opt/flume/conf/usr
      - ./tmp:/tmp
```

---

- [[1] Flume-日志聚合](https://www.cnblogs.com/jhxxb/p/11582470.html)<span id='1'></span>
- [[2] Networking in Compose](https://docs.docker.com/compose/networking/)<span id='2'></span>
- [[3] Docker Compose 网络设置](https://juejin.im/post/5db01cf751882564763e6407)<span id='3'></span>
- [[4] Docker Compose：链接外部容器的几种方式](https://notes.doublemine.me/2017-06-12-Docker-Compose-%E9%93%BE%E6%8E%A5%E5%A4%96%E9%83%A8%E5%AE%B9%E5%99%A8%E7%9A%84%E5%87%A0%E7%A7%8D%E6%96%B9%E5%BC%8F.html)<span id='4'></span>