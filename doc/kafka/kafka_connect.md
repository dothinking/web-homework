# Kafka Connect

`Kafka`不仅是一个分布式的消息队列，更是一个流处理平台——源于它于`0.9.0.0`和`0.10.0.0`引入的两个全新的组件`Kafka Connect`与`Kafka Streaming`。

`Kafka Connect`是一款可扩展并且可靠地在`Kafka`和其他系统之间进行数据传输的工具。消息队列需要上下游来生产和消费数据，例如`Flume`采集日志写入`Kafka`；而借助`Kafka Connect`即可替代Flume，让数据传输这部分工作由`Kafka Connect`来完成[[1](#1), [2](#2)]。


![kafka connect](https://images2017.cnblogs.com/blog/314515/201708/314515-20170821220746418-613069141.png)

> source from [[3]](#3)

[Flume多节点连接实践](../flume/flume_docker.md)练习了以`Flume`为数据采集中间件监控文本文件内容，结合[Flume-Kafka连接实例](../flume/flume_kafka.md)可将采集内容写入`Kafka`主题。本文以`kafka Connect`替代`Flume`，直接监控源文件作为生产者写入`Kafka`，最终模拟消费者写入到新的文件中。

实践过程参考[[4]](#4)：

- 使用`Kafka Connect`读取源文件`test.txt`
- 存入`Kafka`主题`test-topics`
- 从`Kafka`主题`test-topics`消费数据写入`test.sink.txt`


## 1. 启动命令

`Kafka Connect`有两种工作模式：

- `standalone` ：所有worker都在一个独立的进程中完成
- `distributed`：高扩展性及提供自动容错机制

本文尝试单机模式，启动命令为：

```bash
$ bin/connect-standalone.sh \
        config/connect-standalone.properties \
        connector1.properties [connector2.properties ...]
```

其中，

- 第一个参数`connect-standalone.properties`是当前worker的配置文件，例如`Kafka`集群地址`bootstrap.servers`

- 后面参数为`connector`（`source`和`sink`）的配置文件，其中`connector.class`指明了该`connector`的类型。可以根据需要配置`source connect`或`sink connect`或同时包含二者。


更多关于分布式`Kafka Connect`及自定义`Connector`，以后有需要再研究相关参考文档[[1](#1), [5](#5)]。

## 2. 准备配置文件

### 2.1 `connect-standalone`配置文件

采用默认配置文件`opt/kafka/config/connect-standalone.properties`

```
...
bootstrap.servers=localhost:9092
...
key.converter.schemas.enable=false
value.converter.schemas.enable=false
...
offset.storage.file.filename=/tmp/connect.offsets
...
```

- `Kafka`服务器地址`bootstrap.servers`和`offset`记录文件保持默认
- `converter.schemas`表示是否需要`schemas`转码，本例使用`json`数据故设置成`false`


### 2.2 `source connect`配置文件

在默认配置文件`opt/kafka/config/connect-file-source.properties`的基础上略作修改：

```
name=local-file-source
connector.class=FileStreamSource
tasks.max=1
file=/path/to/test.txt

# topic
topic=connect-test

# new lines for transformations
transforms=MakeMap, InsertSource
transforms.MakeMap.type=org.apache.kafka.connect.transforms.HoistField$Value
transforms.MakeMap.field=line
transforms.InsertSource.type=org.apache.kafka.connect.transforms.InsertField$Value
transforms.InsertSource.static.field=data_source
transforms.InsertSource.static.value=test-file-source
```

- `name`为当前`connector`指定唯一的名字
- `connector.class=FileStreamSource`为内置文件类型的`source connect`，类似于`flume`中`source.type`
- `file=/path/to/test.txt`被监控文件的路径（支持相对路径）
- `topic`是推送到的主题
- `transforms`部分为新增内容（可选），表示在原来消息的基础上作轻量化的在线修改。`Kafka`内置了一些修改，具体类型及其配置参数参考文档[[1](#1)]。

这里示例了两个`transforms`：

- `org.apache.kafka.connect.transforms.HoistField`使用自定义值包装数据为`Struct/Map`类型，本例将原始数据`hello`修改为`{'line': 'hello'}`
- `org.apache.kafka.connect.transforms.InsertField`插入自定义属性，本例将新增键值对`{'data_source': 'test-file-source'}`


### 2.3 `sink connect`配置文件

在默认配置文件`opt/kafka/config/connect-file-sink.properties`的基础上略作修改：

```
name=local-file-sink
connector.class=FileStreamSink
tasks.max=1
file=/path/to/test.sink.txt

# topics
topics=connect-test
```

- `connector.class=FileStreamSink`表明文件类型的`sink connection`，`file`即文件路径
- `topics`指定消费数据的主题，支持多个主题（逗号分隔）


## 3 测试


### 3.1 启动`Kafka`并创建主题

根据前面的练习，使用[`docker-compose.yml`](kafka_basic/docker-compose.yml)文件启动`Kafka`

```bash
$ docker-compose up -d
```

进入`kafka`容器，创建测试主题`connect-test`

```bash
$ kafka-topics.sh --create \
        --zookeeper zookeeper:2181 \
        --replication-factor 1 \
        --partitions 1 \
        --topic connect-test
```

### 3.2 启动`Kafka Connect`开始测试

```bash
$ connect-standalone.sh \
        config/connect-standalone.properties \
        config/connect-file-source.properties \
        config/connect-file-sink.properties
```

向测试文件写入数据：

```bash
$ echo 'hello world' > test.txt
$ echo 'hello kafka' >> test.txt
$ echo 'hello kafka connect' >> test.txt
```

观察结果文件：

```bash
$ cat test.sink.txt
{line=hello world, data_source=test-file-source}
{line=hello kafka, data_source=test-file-source}
{line=hello kafka connect, data_source=test-file-source}
```

## 4. `docker-compose`容器编排

以上实践中，`Kafka`服务和`Kafka Connect`是在同一容器内进行的：手动进入`Kafka`容器执行`connect-standalone.sh`。

在试图使用`docker-compose`自动化上述流程时遇到问题：需要替换`wurstmeister/kafka`默认的启动命令`start-kafka.sh`，将其与`connect-standalone.sh`整合。

后来参考[[6](#6)]发现正确的思路：将`Kafka`服务和`Kafaka Connect`看作独立的服务，分别在各自容器运行。这样既方便容器编排，逻辑上也更合理——一个负责消息队列，一个负责数据采集。

于是，整合后的[`docker-compose.yml`](kafka_connect/docker-compose.yml)及相应[目录结构](./kafka_connect)：

```
├── config
│   ├── connect-standalone.properties
│   ├── sink.properties
│   └── source.properties
├── data
│   ├── test.sink.txt
│   └── test.txt
├── docker-compose.yml
└── start-kafka-connect.sh
```

```yml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"

  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    ports:
      - "9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: 192.168.1.9
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_CREATE_TOPICS: "connect-test:2:1"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  kafka-connect-standalone:
    image: wurstmeister/kafka
    container_name: connect-standalone
    environment:
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"
    depends_on:
      - kafka
    volumes:
      - .:/home
    command: ["/home/start-kafka-connect.sh"]
```

- `kafka`容器中先创建主题`connect-test`
- 自定义配置文件`connect-standalone.properties`中修改`bootstrap.servers=kafka:9092`；如果是`Kafka`集群，逗号分隔填写即可
- 修改`kafka-connect-standalone`入口命令为`start-kafka-connect.sh`，即启动`connect-standalone.sh`

```bash
#!/bin/bash
exec "connect-standalone.sh" \
        "/home/config/connect-standalone.properties" \
        "/home/config/source.properties" \
        "/home/config/sink.properties"
```


---

- [[1] Kafka 2.4 Documentation](https://kafka.apache.org/documentation/#connect)<span id='1'></span>
- [[2] 替代Flume——Kafka Connect简介](https://www.cnblogs.com/tree1123/p/11434047.html)<span id='2'></span>
- [[3] Kafka Connect](https://blog.csdn.net/helihongzhizhuo/article/details/80335931)<span id='3'></span>
- [[4] kafka connect 简单测试](https://blog.csdn.net/helihongzhizhuo/article/details/80335931)<span id='4'></span>
- [[5] Kafka connect介绍、部署及开发](https://my.oschina.net/hnrpf/blog/1555915)<span id='5'></span>
- [[6] Kafka Connect - Crash Course](https://dev.to/thegroo/kafka-connect-crash-course-1chd)<span id='6'></span>