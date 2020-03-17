在[Flume入门](flume.md)的基础上，利用`docker`练习分布式`Flume`。

- flume-1监控文件`/tmp/test.log`
- flume-2监听指定端口的数据流
- flume-3接收flume-1、flume-2数据并打印到控制台


## 创建镜像

利用[前文](flume.md)的`dockfile`构建镜像`flume:1.9.0`：

```bash
docker build . -t flume:1.9.0
```

## 准备配置文件

在宿主机器上分别准备三个节点的配置文件。

### 1. 监控文件

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

### 2. 监听端口

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

### 3. 接收节点数据

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

## 启动容器

首先启动`flume-3`：为便于直接观察结果，不以后台模式启动

```bash
docker run -v /path/to/workspace/flume-3:/opt/flume/conf/usr \
           --name flume-3 \
           flume:1.9.0 \
           -Dflume.root.logger=INFO,console # 控制台打印输出便于观察
```

然后新建控制台，依次启动`flume-1`和`flume-2`

```bash
# flume-1
docker run -d \
           -v /path/to/workspace/flume-1:/opt/flume/conf/usr \
           -p 44441:44444 -p 55551:55555 \   # 映射暴露的端口，以免冲突
           -v /path/to/workspace/tmp:/tmp \  # 关联被监控的文件到宿主机位置
           --name flume-1 \
           --link flume-3 \                  # 关联容器flume-3
           flume:1.9.0
# flume-2
docker run -d \
           -v /path/to/workspace/flume-2:/opt/flume/conf/usr \
           -p 44442:44444 -p 55552:55555 \   # 映射暴露的端口，以免冲突
           --name flume-2 \
           --link flume-3 \                  # 关联容器flume-3
           flume:1.9.0
```

## 测试结果

测试监控文件：在宿主机器上写入数据到被监控的文件`/path/to/workspace/tmp/test.log`

```bash
echo hello world >> /path/to/workspace/tmp/test.log
```

在宿主机上向测试端口发送数据：

```bash
telnet localhost 44442
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



---

[Flume-日志聚合](https://www.cnblogs.com/jhxxb/p/11582470.html)