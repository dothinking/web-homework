在本机启动4个`Kafka`服务/容器模拟`Kafka`集群，通过实例操作[[1](#1), [2](#2)]理解`Kafka`基本原理：

- 主题的分区特性与生产者的负载均衡
    - 分区尽量均匀分布在`Broker`上，建立主副本
    - 主副本向其他`Broker`均匀复制副本（副本数不大于`Broker`数）
- 消费者读取消息时只保证分区内有序
- 分布式模型与故障容错


## 1 `Kafka`集群

`Kafka`没有提供官方镜像，这里采用`Docker Hub`上Star数最多的`wurstmeister/kafka`及配套`wurstmeister/zookeeper` [[3]](#3)。


### 1.1 启动服务

建立如下`docker-compose.yml`文件，并启动容器：

```bash
$ docker-compose up -d
```


```bash
# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"

  kafka:
    image: wurstmeister/kafka
    ports:
      - "9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: 192.168.1.2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "false"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

> `KAFKA_ADVERTISED_HOST_NAME`为宿主机IP地址

### 1.2 扩展broker

```bash
$ docker-compose scale kafka=4
```

此时通过`docker container ls`可以看到创建的1个`zookeeper`容器和4个`kafka`容器，及其分配的端口号。

| container name | port |
|---|---|
| kafkacluster_zookeeper_1 | 2181  |
| kafkacluster_kafka_1     | 32768 |
| kafkacluster_kafka_2     | 32771 |
| kafkacluster_kafka_3     | 32770 |
| kafkacluster_kafka_4     | 32769 |

### 1.3 请求服务

接下来可以进入容器内部，使用官方自带的`CLI`工具开始实验。例如进入容器`kafkacluster_kafka_1`查看话题：

```bash
$ docker exec kafkacluster_kafka_1 \
kafka-topics.sh --list --zookeeper kafkacluster_zookeeper_1:2181
```

不过既然使用了容器，可以直接在宿主机进行相应的操作（前提是宿主机已经安装了`Kafka`）。

```bash
$ kafka-topics.sh --list --zookeeper localhost:2181
```
宿主机上无需启动`kafka`服务，只需借助`CLI`命令向容器中的服务请求数据即可。例如此处通过`localhost:2181`向`kafkacluster_zookeeper_1:2181`请求主题列表信息。

## 2 创建多分区多副本主题

创建一个分区数为5、副本数为3的主题`partitioned-topics`

```bash
$ kafka-topics.sh --create \
    --zookeeper localhost:2181 \
    --replication-factor 3 \
    --partitions 5 \
    --topic partitioned-topics
```

查看指定主题的详细信息

```bash
$ kafka-topics.sh --describe \
    --zookeeper localhost:2181 \
    --topic partitioned-topics

Topic: partitioned-topics    PartitionCount: 5       ReplicationFactor: 3 Configs:
Topic: partitioned-topics    Partition: 0    Leader: 1002    Replicas: 1002,1001,1003    Isr: 1002,1001,1003
Topic: partitioned-topics    Partition: 1    Leader: 1003    Replicas: 1003,1002,1004    Isr: 1003,1002,1004
Topic: partitioned-topics    Partition: 2    Leader: 1004    Replicas: 1004,1003,1001    Isr: 1004,1003,1001
Topic: partitioned-topics    Partition: 3    Leader: 1001    Replicas: 1001,1004,1002    Isr: 1001,1004,1002
Topic: partitioned-topics    Partition: 4    Leader: 1002    Replicas: 1002,1003,1004    Isr: 1002,1003,1004
```
输出信息：

- `Topic` 主题名称
- `Partition` 分区编号，0, 1, 2 ...
- `Leader` 当前分区主副本所在节点编号（只有主副本才会接受消息的读写）
- `Replicas` 当前分区所有副本所在节点
- `Isr` 同步状态的副本（存活节点），`Replicas`的子集

从以上输出可以看出：

- 主题`partitioned-topics`5个分区的主副本尽量均匀地分布在集群的4个节点上，多出的一个随机重复到了`1002`号节点
- 副本列表的第一个即为主副本节点，其余副本从主副本向其他节点均匀复制。本例`5*3=15`个区分布在集群4个节点上，结果`1001`节点得到3个区，其余3个节点都有4个区，趋于均匀分布。
- 此时所有节点都存活，所以`Isr`列表和副本列表`Replicas`是一样的


## 3 节点故障与恢复

### 3.1 节点故障

暂停节点`kafkacluster_kafka_4`模拟故障

```bash
$ docker container stop kafkacluster_kafka_4
```

然后查看主题的详情

```bash
$ kafka-topics.sh --describe \
    --zookeeper localhost:2181 \
    --topic partitioned-topics

Topic: partitioned-topics    PartitionCount: 5       ReplicationFactor: 3    Configs:
Topic: partitioned-topics    Partition: 0    Leader: 1002    Replicas: 1002,1001,1003    Isr: 1002,1001
Topic: partitioned-topics    Partition: 1    Leader: 1002    Replicas: 1003,1002,1004    Isr: 1002,1004
Topic: partitioned-topics    Partition: 2    Leader: 1004    Replicas: 1004,1003,1001    Isr: 1004,1001
Topic: partitioned-topics    Partition: 3    Leader: 1001    Replicas: 1001,1004,1002    Isr: 1001,1004,1002
Topic: partitioned-topics    Partition: 4    Leader: 1002    Replicas: 1002,1003,1004    Isr: 1002,1004
```

*对比之前的输出可以看出容器`kafkacluster_kafka_4`对应`Broker`节点编号`1003`。*

- `Partition: 1`主副本`1003`故障后，自动从副本列表`1003,1002,1004`中选取了`1002`作为新的主副本
- 副本列表保持故障前的样子，但同步列表`Isr`中去掉了故障节点`1003`

### 3.2 节点恢复

接下来重启`kafkacluster_kafka_4`模拟故障恢复，然后查看主题详情

```bash
$ docker container start kafkacluster_kafka_4

$ kafka-topics.sh --describe     --zookeeper localhost:2181     --topic partitioned-topics
Topic: partitioned-topics    PartitionCount: 5       ReplicationFactor: 3    Configs:
Topic: partitioned-topics    Partition: 0    Leader: 1002    Replicas: 1002,1001,1003    Isr: 1002,1001,1003
Topic: partitioned-topics    Partition: 1    Leader: 1002    Replicas: 1003,1002,1004    Isr: 1002,1004,1003
Topic: partitioned-topics    Partition: 2    Leader: 1004    Replicas: 1004,1003,1001    Isr: 1004,1001,1003
Topic: partitioned-topics    Partition: 3    Leader: 1001    Replicas: 1001,1004,1002    Isr: 1001,1004,1002
Topic: partitioned-topics    Partition: 4    Leader: 1002    Replicas: 1002,1003,1004    Isr: 1002,1004,1003
```

对比可以看出：`1003`已经恢复到同步列表`Isr`中了，但是主副本`Leader`依旧保持故障后的状态——`1002`上有3个主副本，`1003`却空闲。为了保证主副本会负载均衡到所有节点，可以手动执行平衡操作，即选择`Replicas`副本列表的第一个副本作为分区的主副本。

```bash
$ kafka-preferred-replica-election.sh --zookeeper localhost:2181
```

再次查看主题详情可知，主副本已经恢复到故障前状态。


## 4 生产/消费主题

在宿主机上启动一个终端模拟生产数据

```bash
$ kafka-console-producer.sh --broker-list localhost:32770 --topic partitioned-topics
>A
>B
>C
>D
>E
>F
>G
```

在宿主机上启动一个终端模拟消费数据

```bash
$ kafka-console-consumer.sh --bootstrap-server localhost:32770 --topic partitioned-topics --from-beginning
B
D
C
A
E
F
G
```

可见消息并没有按照生产者的顺序读取出来。接下来进入到容器内部查看各个分区实际存储的消息：

- log目录`/kafka/kafka-logs-container-ID/`
- `strings`查看`log`文件存储的消息

```bash
$ docker exec -it kafkacluster_kafka_1 /bin/bash
bash-4.4 cd /kafka/kafka-logs-66e95ce9b107/ 
bash-4.4 strings partitioned-topics-0/00000000000000000000.log
B
D
```

即分区`Partition: 0`中存储`B`和`D`。同理得到以上7条消息在分区中的分布（至少需要进入两个节点查看）：

| Partition | Messages |
|---|---|
| 0 | B, D |
| 1 | E, G |
| 2 | A    |
| 3 |      |
| 4 | C, F |

从而可知`Kafka`不保证消息的全局顺序，只保证分区内的顺序。例如：

- 分区间无序：分区4的读取可能在分区2之前，所以`C`出现在`A`之前
- 分区内有序：对于分区0，`B`总会出现在`D`之前，其余同理


最后，关闭集群，结束练习。

```bash
 docker-compose down
 ```


---


- [[1] Kafka 入门教程](https://juejin.im/entry/5af21ade6fb9a07acb3cd66d)<span id='1'></span>
- [[2] Kafka技术内幕—图文详解Kafka源码设计与实现：第1章](https://www.ituring.com.cn/book/tupubarticle/18689)<span id='2'></span>
- [[3] wurstmeister/kafka-docker](https://github.com/wurstmeister/kafka-docker)<span id='3'></span> 