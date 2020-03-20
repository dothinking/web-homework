之前的练习中，消息的生产和消费都是基于`Kafka`自带的控制台命令，这一篇将使用`Python`客户端消费`kafka`数据。`Kafka`官方没有提供`Python`客户端，但推荐了一些选择[[1]](#1)，这里采用的是`kafka-python`[[2]](#2)：

- python 3.6
- kafka-python 2.0.1

## 1 环境搭建

之前已经创建了启动`Kafka`服务的`docker-compose.yml`文件，虽然可以直接在宿主环境进行`Python`试验，但这里选择在容器中进行。

### 1.1 创建镜像 `python-kafka:3.6`

选择轻量化的`python:3.6-alpine`作为基础镜像，然后

- 设置工作目录`/app`
- 使用国内`Pypi`源安装`kafka-python`

```dockerfile
FROM python:3.6-alpine

# create project path
WORKDIR /app

# copy and install packages
COPY requirements.txt .

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

对于本次试验，`requirements.txt`中就一行

```
kafka-python
```

于是构建包含`kafka-python`的镜像`python-kafka:3.6`

```bash
$ docker build -t python-kafka:3.6 .
```

### 1.2 网络设置

`Python`环境和`Kafka`服务分布在不同的容器，但显然它们之间需要保持通信。

简单做法：将`Python`容器的启动写到`Kafka`相同的`docker-compose.yml`中以保证它们处在相同的网络。但是到目前为止，`Python`容器中尚未加入任何自定义代码，该容器将在启动后马上退出。因为，容器的入口进程执行完了所有命令，顺利退出了。

为了方便进入容器，需要使用`docker run -itd`使其以交互式方式保持在后台等待，后续还可以`docker exec -it`再次进入容器。

那么就要考虑共享网络的问题，方案是：

- 新建外部网络
- 分配给`docker-compose`启动的`Kafka`容器
- 共享给`docker run`启动的`Python`容器

**新建`app_net`**

```bash
# 后面多处用到，故保存为环境变量
$ export APP_NET=app_net
$ docker network build ${APP_NET}
```

**分配给`Kafka`容器**

```yml
version: '3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    networks:
      - ${APP_NET}

  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: 192.168.1.2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_CREATE_TOPICS: "my-topics:2:1"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - ${APP_NET}

networks:
  ${APP_NET}:
    external: true
```

**共享给`Python`容器**

```bash
$ name=python-kafka

$ docker run -itd  --name ${name} -v $(pwd):/app python-kafka:3.6

$ docker network connect ${APP_NET} ${name}
```

最后即可进入`Python`容器写代码

```bash
$ docker exec -it ${name} /bin/sh
```

### 1.3 流程自动化

将以上过程写为脚本`run.sh`方便启动和销毁整个环境

```bash
PY_IMAGE_NAME=python-kafka:3.6
PY_CONTAINER_NAME=python-kafka
APP_NET=app_net

# network
echo "creating network: ${APP_NET}..."
if [ -n "$(docker network ls -f name=${APP_NET} -q)" ]; then
    docker network rm  ${APP_NET}
else
    docker network create ${APP_NET}
fi

# kafka
echo "starting kafka..."
export APP_NET
docker-compose up -d

# kafka-python
if [ ! -n "$(docker image ls ${PY_IMAGE_NAME} -q)" ]; then 
    echo "building python image..."
    docker build -t ${PY_IMAGE_NAME} .
fi
echo "starting python container..."
docker run  -itd \
            --name ${PY_CONTAINER_NAME} \
            -v $(pwd):/app \
            python-kafka:3.6

# share network
echo "connecting kafka and python network..."
docker network connect ${APP_NET} ${PY_CONTAINER_NAME}

echo "entering python continer..."
docker exec -it ${PY_CONTAINER_NAME} /bin/sh

# shut down
echo "shutting down..."
docker-compose down
docker rm -f ${PY_CONTAINER_NAME}
docker network rm ${APP_NET}

echo "goodbye!"
```

## 2 `kafka-python`消费数据

本例采用控制台生产消息，然后借助`kafka-python`提供的`API`消费数据。代码参考官方文档 [[3]](#3)。

- `Kafka`启动时创建了主题`my-topics`，这里指定给`KafkaConsumer`
- 因为共享了网络，`Broker`地址列表直接使用`kafka:9092`，逗号拼接集群的多个地址


```python
# test.py

from kafka import KafkaConsumer

if __name__ == '__main__': 
    
    # create a consumer
    consumer = KafkaConsumer(
        "my-topics",                    # subscribe topics
        bootstrap_servers="kafka:9092", # comma separated kafka servers list
        group_id="my.group"             # consumer group ID
    )

    # produce data
    # kafka-console-producer.sh --broker-list localhost:9092 --topic my-topics

    # receive messages
    for msg in consumer:
        print(msg)
```

当然，`kafka-python`也支持生产数据，这里不做练习。


## 3 测试

宿主机终端输入数据

```bash
$ kafka-console-producer.sh \
    --broker-list localhost:9092 \
    --topic my-topics
>hello python
>hi there
```

`python`容器内执行脚本`test.py`

```bash
$ python test.py
ConsumerRecord(topic='my-topics', partition=0, offset=0, timestamp=1584729767499, timestamp_type=0, key=None, value=b'hello python', headers=[], checksum=None, serialized_key_size=-1, serialized_value_size=12, serialized_header_size=-1)
ConsumerRecord(topic='my-topics', partition=1, offset=0, timestamp=1584729770865, timestamp_type=0, key=None, value=b'hi there', headers=[], checksum=None, serialized_key_size=-1, serialized_value_size=8, serialized_header_size=-1)
```

每条消息是一个`ConsumerRecord`对象，包含了主题、所在分区、当前读取位置、时间戳、消息内容等。例如，可以使用`ConsumerRecord.value.decode()`获取消息字符串。


---

- [[1] Apache Kafka Clients](https://cwiki.apache.org/confluence/display/KAFKA/Clients)<span id='1'></span>
- [[2] dpkp/kafka-python](https://github.com/dpkp/kafka-python)<span id='2'></span>
- [[3]  kafka-python usage overview](https://kafka-python.readthedocs.io/en/master/usage.html)<span id='3'></span>
