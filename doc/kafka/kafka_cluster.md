[前文](kafka_basic.md)实践了用`docker-compose scale`便捷地扩展`kafka`容器数量，但是容器名和对外端口号都是自动生成的，无法自主控制。这一篇练习在`docker-compose`的控制文件中显式配置`Kafka`节点信息，侧重点在**端口号的设置**。

`docker-compose.yml`主体结构[参考](kafka_basic/docker-compose.yml)，下面以配置两个`Broker`节点为例。

与端口设置相关的两个参数[[1]](#1)：

- `listeners` - `Kafka`监听地址/端口列表（逗号分隔多个值），默认`PLAINTEXT://:9092`
- `advertised.listeners` - 发布到`ZooKeeper`供客户端（即生产者和消费者）使用的侦听地址，默认采用与`listeners`相同的设置


## 1 相同端口号 [[2]](#2)

保守的做法：

- 不同节点采用不同端口，例如`kafka-1`使用`9092`，`kafka-2`使用`9093`
- 同一节点采用相同的`listeners`和`advertised.listeners`端口，例如`kafka-1`的`ports`使用`9092:9092`

```yml
kafka-1:
    image: wurstmeister/kafka
    container_name: kafka-1
    ports:
        - "9092:9092"
    environment:
        KAFKA_BROKER_ID: 1
        KAFKA_LISTENERS: PLAINTEXT://:9092
        KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.2:9092
        KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
        KAFKA_CREATE_TOPICS: "topics_flume_kafka:2:2"

kafka-1:
    image: wurstmeister/kafka
    container_name: kafka-2
    ports:
        - "9093:9093"
    environment:
        KAFKA_BROKER_ID: 1
        KAFKA_LISTENERS: PLAINTEXT://:9093
        KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.2:9093
        KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
        KAFKA_CREATE_TOPICS: "topics_flume_kafka:2:2"
```

## 2 不同端口号

如果希望宿主机使用不同的端口号，例如映射关系为`1111:9092`，则根据两个监听端口的含义，需要设置：

- `advertised.listeners=1111`
- `listeners=9092`

```yml
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

kafka-2:
    image: wurstmeister/kafka
    container_name: kafka-2
    ports:
        - "2222:9093"
    environment:
        KAFKA_BROKER_ID: 2
        KAFKA_LISTENERS: PLAINTEXT://:9093
        KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.2:2222
        KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
```

接下来如果进入容器内消费数据，注意`Broker`列表是`kafka-1:9092,kafka-2:9093`

```bash
$ docker exec -it kafka-1 \
        kafka-console-consumer.sh \
        --bootstrap-server kafka-1:9092,kafka-2:9093 \
        --topic topics_flume_kafka \
        --from-beginning
```

如果在宿主机消费数据，则`Broker`列表是`localhost:1111,localhost:2222`

```bash
$ kafka-console-consumer.sh \
        --bootstrap-server localhost:1111,localhost:2222 \
        --topic topics_flume_kafka \
        --from-beginning
```

## 3 容器内相同端口号 [[3]](#3)

容器之间具有隔离性，因此不需要为不同`Broker`设置不同的`listeners`——直接使用默认值`PLAINTEXT://:9092`更为方便。于是，在上一版本基础上修改`kafka-2`：

- 内部端口由`9093`改为默认的`9092`
- 同理修改`KAFKA_LISTENERS: PLAINTEXT://:9092`

```yml
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
```


更多关于`Docker`部署`Kafka`时的网络配置参考[[4](#4), [5](#5)]。

---

- [[1] KAFKA Documentation: CONFIGURATION](https://kafka.apache.org/documentation/#brokerconfigs)<span id='1'></span>
- [[2] Docker环境下搭建Kafka集群](https://blog.csdn.net/noaman_wgs/article/details/103757791)<span id='2'></span>
- [[3] Apache Kafka 集群环境搭建](https://www.ctolib.com/topics-143446.html)<span id='3'></span>
- [[4] kafka的docker容器化配置](https://www.jianshu.com/p/e11c6c16114c)<span id='4'></span>
- [[5] 使用Docker部署Kafka时的网络应该如何配置](https://www.jianshu.com/p/52a505354bbc)<span id='5'></span>