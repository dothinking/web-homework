在实践了`Kafka`的[基本操作](../kafka/quickstart.md)、[集群配置](../kafka/kafka_cluster.md)后，练习`Flume`与`Kafka`的集成 [[1]](#1)：

- `Flume`监听`netcat`数据
- 作为生产者`sink`给`Kafka`集群
- 启动消费者控制台获取数据

## 1 容器编排

`Kafka`集群（两个节点为例）参考之前的[配置](../kafka/kafka_cluster.md)

| Broker | advertised.listeners port | listeners port |
| --- | --- | ---|
| kafka-1 | 1111 | 9092 |
| kafka-2 | 2222 | 9092 |

`flume`监听`44444`端口，并依赖`kafka`节点启动。


```yml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"

  kafka-1:
    image: wurstmeister/kafka
    container_name: kafka-1
    ports:
      - "1111:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_LISTENERS: PLAINTEXT://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.2:1111
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_CREATE_TOPICS: "topics_flume_kafka:2:2"
    depends_on:
      - zookeeper
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  kafka-2:
    image: wurstmeister/kafka
    container_name: kafka-2
    ports:
      - "2222:9092"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_LISTENERS: PLAINTEXT://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.2:2222
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181      
    depends_on:
      - zookeeper
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  flume:
    image: flume:1.9.0
    container_name: flume
    ports:
      - "44444:44444"
    depends_on:
      - kafka-1
      - kafka-2
    volumes:
      - ./flume:/opt/flume/conf/usr
```

- `KAFKA_CREATE_TOPICS: "topics_flume_kafka:2:2"` - 启动容器后创建一个两分区两副本的主题`topics_flume_kafka`，方便后续收发消息的测试。



## 2 `Flume`配置文件

- 本例`source`端类型为`netcat`
- `sink`端采用`Flume`提供的`Kafka Sink`[[2]](#2)，两个关键参数
    - `type` – `org.apache.flume.sink.kafka.KafkaSink`
    - `kafka.bootstrap.servers` - `Broker`地址列表
    - `kafka.topic` - 可选参数，指定了投递消息的`kafka`主题

第一部分的容器编排脚本可知`Flume`容器和`kafka`容器处于相同的默认网络中，因此可以直接采用已经定义的`service name`和内部端口，即`kafka-1:9092,kafka-2:9092`。

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
a1.sinks.k1.type = org.apache.flume.sink.kafka.KafkaSink
a1.sinks.k1.kafka.bootstrap.servers = kafka-1:9092,kafka-2:9092
a1.sinks.k1.kafka.topic = topics_flume_kafka
a1.sinks.k1.channel = c1

# channel
a1.channels.c1.type = memory
a1.channels.c1.capacity = 1000
a1.channels.c1.transactionCapacity = 100
```

## 3 测试

启动容器

```bash
$ docker-compose up -d
```

通过`44444`端口向`flume`发送数据

```bash
$ telnet localhost 44444
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
hello kafka from flume
OK
```

新建终端模拟`kafka`消费者接收数据

```bash
$ kafka-console-consumer.sh \
        --bootstrap-server localhost:1111,localhost:2222 \
        --topic topics_flume_kafka \
        --from-beginning
hello kafka from flume
```

关闭容器结束测试

```bash
$ docker-compose down
```


---

- [[1] Flume+Kafka整合案例实现](https://blog.csdn.net/a_drjiaoda/article/details/85003929?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task)<span id='1'></span>
- [[2] Flume 1.9.0 User Guide: Kafka Sink](http://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html#kafka-sink)<span id='2'></span>
