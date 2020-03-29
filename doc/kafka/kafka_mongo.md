# MongoDB Connector for Apache Kafka

Persists data from `Kafka` topics as a data sink into `MongoDB` as well as publishes changes from `MongoDB` into `Kafka` topics as a data source [[1]](#1).


![MongoDB Connector](https://webassets.mongodb.com/_com_assets/cms/mongodbkafka-hblts5yy33.png)

> Source from [[1](#1)]

[前文](kafka_connect.md)实践了利用`Kafka`自带的`connector`采集文本文件数据到`Kafka`主题，然后从该主题读取数据写入新的文本文件。

本文在以上基础上，借助`MongoDB`官方提供的`MongoDB Kafka Connector`[[2]](#2)，消费`Kafka`主题数据到`MongoDB`。


[hpgrahsl/kafka-connect-mongodb](https://github.com/hpgrahsl/kafka-connect-mongodb)也可以作为一个`MongoDB Sink Connector`的选择，以后有需要再研究。


## 1. Installation

`MongoDB Kafka Connector`同时适用于`Apache Kafka`和`Confluent Kafka`（`Kafka`增强版本）。本系列一直使用`Apache Kafka`的第三方`docker`化版本`wurstmeister/kafka`，因此以下操作都是针对`Apache Kafka`版本。

下载`uber JAR`到自定义的`Kafka`插件目录，例如`/opt/kafka-plugins/` [[3]](#3)，后续需要在配置文件中指定插件目录。

这里将其作为一个新的镜像：

```dockerfile
FROM wurstmeister/kafka:latest

# download MongoDB Kafka Connector
RUN wget https://search.maven.org/remotecontent?filepath=org/mongodb/kafka/mongo-kafka-connect/1.0.1/mongo-kafka-connect-1.0.1-all.jar \
    && mkdir /opt/kafka-plugins \
    && mv mongo-kafka-connect-1.0.1-all.jar /opt/kafka-plugins/

# replace the start command creating a connector instead of starting a kafka broker.
COPY start-kafka.sh /usr/bin/

# permissions
RUN chmod a+x /usr/bin/start-kafka.sh
```

以上镜像基于`wurstmeister/kafka`，并将默认的启动`kafka`集群的命令`start-kafka.sh`替换为自定义的启动`connect-standalone.sh`，其中指定了配置文件的路径（后期以`volumes`挂载）：

- `/home/config/connect-standalone.properties`
- `/home/config/source.properties`
- `/home/config/sink.properties`


## 2. 容器编排

有了前文[kafka](kafka_connect.md)及[mongodb](../mongodb/quickstart.md)容器的基础，本文[目录结构](./kafka_mongo/)及`docker-compose.yml`配置：

```bash
├── connector
│   ├── Dockerfile
│   ├── config
│   │   ├── connect-standalone.properties
│   │   ├── sink.properties
│   │   └── source.properties
│   └── start-kafka.sh
├── data
│   └── test.txt
├── docker-compose.yml
└── mongo
    └── create_user.sh
```

```yml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    expose:
      - "2181"

  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    ports:
      - "9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: 192.168.1.7
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_CREATE_TOPICS: "connect-test:2:1"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  mongo:
    image: mongo:latest
    container_name: mongo
    environment:
        - MONGO_INITDB_ROOT_USERNAME=admin
        - MONGO_INITDB_ROOT_PASSWORD=root
    ports:
        - "37017:27017"
    volumes:
        - "./mongo:/docker-entrypoint-initdb.d"
        - "data_db:/data/db"

  connect-kafka-mongo:
    image: mongo-kafka-connector:1.0.1
    build:
      context: "./connector/"
      dockerfile: Dockerfile
    container_name: connect-kafka-mongo
    depends_on:
      - kafka
      - mongo
    volumes:
      - "./connector/config/:/home/config/"
      - "./data/:/home/data/"


# incompatible file system between windows and mongo,
# so have to use volume:
# docker volume [prefix]_data_db will be created automatically
volumes: 
    data_db:
```

## 3. 配置文件

### 3.1 `connect-standalone`配置文件

在默认配置文件`/opt/kafka/config/connect-standalone.properties`的基础上略作修改：

```bash
# kafka broker
bootstrap.servers=localhost:9092

# schemaless data
key.converter.schemas.enable=false
value.converter.schemas.enable=false

# plugins
plugin.path=/opt/kafka-plugins
```

注意：

- `kafka`服务器地址`bootstrap.servers`
- `mongo kafka connector`插件目录`plugin.path`

### 3.2 `source connect`配置文件

与[前文](kafka_connect.md)设置一致，借助自带的`FileStreamSource`监控文本文件`test.txt`。

### 3.3 `sink connect`配置文件

参考`Mongo Sink Connector`官方配置文档[[4]](#4)及[示例](https://github.com/mongodb/mongo-kafka/blob/master/config/MongoSinkConnector.properties)，得到本文配置文件：

```bash
name=mongo-sink
topics=connect-test
connector.class=com.mongodb.kafka.connect.MongoSinkConnector
tasks.max=1

# Specific global MongoDB Sink Connector configuration
connection.uri=mongodb://tom:goodboy@mongo:27017/test
database=test
collection=mongo_kafka_test
max.num.retries=3
retries.defer.timeout=5000
```

其中几个关键参数：

- `topics` 提供数据的`Kafka`主题，多个则以逗号分隔
- `connection.uri` 连接`MongoDB`的`URI`，注意认证的用户和数据库
- `database` 目标数据库
- `collection` 目标集合


## 4. 测试

启动容器

```bash
$ docker-compose up -d
```

写入测试数据

```bash
$ echo 'hello world' > ./data/test.txt
$ echo 'hello kafka' >> ./data/test.txt
$ echo 'hello mongo-kafka connect' >> ./data/test.txt
```

连接`MongoDB`观察结果

```json
{
  "_id": {
    "$oid": "5e808ecf7899395f4b702bda"
  },
  "line": "hello mongo-kafka connect",
  "data_source": "test-file-source"
}
```

关闭容器结束练习

```bash
$ docker-compose down
```

---

- [[1] MongoDB Connector for Apache Kafka](https://www.mongodb.com/kafka-connector)<span id='1'></span>
- [[2] MongoDB Kafka Connector](https://docs.mongodb.com/kafka-connector/current/)<span id='2'></span>
- [[3] Install the Connector for Apache Kafka](https://docs.mongodb.com/kafka-connector/current/kafka-installation/#kafka-connector-installation-reference)<span id='3'></span>
- [[4] Kafka Sink Connector Configuration Properties](https://docs.mongodb.com/kafka-connector/current/kafka-sink-properties/)<span id='4'></span>