分布式消息队列(`Message Queue`)，**解耦**消息的生产和消费。


## 1. Architecture

![Kafka Architecture – Kafka Cluster](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/sites/2/2018/04/Kafka-Architecture.png)

![Kafka Architecture – Topic Replication Factor](https://d2h0cx97tjks2p.cloudfront.net/blogs/wp-content/uploads/sites/2/2018/04/kafka-topic-replication.png)

> source from [[1]](#1)

基本概念参考官方文档 [[2]](#2)及博文 [[3](#3), [4](#4)]


- `topic` 消息队列
- `partition` 同一个`topic`可以分区存储
- `broker` 集群中的节点（kafka服务器），平均分配`topic`的`partition`及其副本
- `consumer group` 消费者集合，订阅`topic`；消费组订阅的`topic`中的某个`partition`只能被一个`consumer`消费，但`consumer`可以消费多个`partition`


## 2. Installation

安装过程类似于`Flume`，需要先安装java

```bash
# install jdk
apt install -y default-jdk

# download and unzip kafka 2.4.1
wget --no-check-certificate https://mirrors.tuna.tsinghua.edu.cn/apache/kafka/2.4.1/kafka_2.12-2.4.1.tgz
tar -xzf kafka_2.12-2.4.1.tgz -C /opt
rm -f kafka_2.12-2.4.1.tgz
mv /opt/kafka_2.12-2.4.1 /opt/kafka

# set up env. var: /etc/profile
JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
PATH=$PATH:$JAVA_HOME/bin:/opt/kafka/bin
export JAVA_HOME
```

## 3. Launch

`Kafka`需要用到`ZooKeeper`服务器。作为练习，启动`Kafka`自带的简易版本：

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
```

接着启动`Kafka`

```bash
bin/kafka-server-start.sh config/server.properties
```

`Kafka`需要根据配置文件（例如此处默认的`server.properties`）启动相应的服务，关键配置项：

- `broker.id`
- `log.dirs`
- `zookeeper.connect`

更多配置项，参考文档[[5]](#5)。


## 4. Hello World

### 4.1 新建主题

```bash
$ bin/kafka-topics.sh --create \
                      --zookeeper localhost:2181 \
                      --replication-factor 1 \  # 副本数
                      --partitions 1 \          # 分区数
                      --topic test
Created topic test.
```

### 4.2 生产者向指定主题发送数据

```bash
$ bin/kafka-console-producer.sh \
        --broker-list localhost:9092 \
        --topic test
>hello world
>hello kafka
```

### 4.3 消费者接收数据

```bash
$ bin/kafka-console-consumer.sh \
        --bootstrap-server localhost:9092 \
        --topic test \
        --from-beginning
hello world
hello kafka
```


---

- [[1] Kafka Architecture and Its Fundamental Concepts](https://data-flair.training/blogs/kafka-architecture/)<span id='1'></span>
- [[2] Kafka 2.4 Documentation](https://kafka.apache.org/documentation/)<span id='2'></span>
- [[3] Kafka 入门介绍](https://lotabout.me/2018/kafka-introduction/)<span id='3'></span>
- [[4] 深入浅出理解基于 Kafka 和 ZooKeeper 的分布式消息队列](https://gitbook.cn/books/5ae1e77197c22f130e67ec4e/index.html)<span id='4'></span>
- [[5] Kafka 2.4 Documentation：CONFIGURATION](https://kafka.apache.org/documentation/#configuration)<span id='5'></span>