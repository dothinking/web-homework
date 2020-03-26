# MongoDB

基于分布式文件存储的数据库，为WEB应用提供可扩展的高性能数据存储解决方案。

![Databases and Collections](https://docs.mongodb.com/manual/_images/crud-annotated-collection.bakedsvg.svg)

![Documents](https://docs.mongodb.com/manual/_images/crud-annotated-document.bakedsvg.svg)


## 1. 安装

官网有详尽的安装文档[[1](#1)]，这里采用`docker`镜像安装当前最新版本

```bash
$ docker pull mongo
```

参考`mongo`镜像的说明文档[[2]](#2)，几个关键参数：

- 配置文件路径`--config /etc/mongo/mongod.conf`
- 脚本目录`/docker-entrypoint-initdb.d`下的`.sh`或`.js`文件会在容器第一次启动时被自动执行（多个文件则按文件名顺序执行）
- 数据库存储路径`/data/db`
- 环境变量`MONGO_INITDB_ROOT_USERNAME`和` MONGO_INITDB_ROOT_PASSWORD`创建相应`root`权限用户，并开启用户认证
- 环境变量`MONGO_INITDB_ROOT_USERNAME_FILE`和`MONGO_INITDB_ROOT_PASSWORD_FILE`以文件形式指定用户名和密码

## 2 启动服务

启动`mongoDB`服务，其中`--dbpath`指定数据库存储位置，默认端口`--port=27017`，更多配置选项参考 [[3](#3)]。

```bash
$ mongod --dbpath <path to data directory>
```

## 3. Hello World

以后台进程模式启动容器，同时已经启动了`mongod`服务

```bash
$ docker run -d --name my-mongo mongo:latest
```

进入容器
```
$ docker exec -it my-mongo /bin/bash
```

查看版本

```bash
$ mongod --version
db version v4.2.3
...
```

使用`mongoDB`自带客户端连接数据库

```bash
$ mongo
MongoDB shell version v4.2.3
...
MongoDB server version: 4.2.3
Welcome to the MongoDB shell.
...
>
```

创建数据库`first_db`，显示当前所在数据库名称

```bash
> use first_db
switched to db first_db

> db
first_db
```

当前数据库中没有数据，故不会显示在数据库列表中 

```bash
> show dbs
admin   0.000GB
config  0.000GB
local   0.000GB
```

向当前数据库的自定义集合`first_collection`写入一条数据/文档，此时数据库`first_db`被正真创建。

```bash
> db.first_collection.insert({'msg': 'hello world'})
WriteResult({ "nInserted" : 1 })

> show dbs
admin   0.000GB
config  0.000GB
first_db   0.000GB
local   0.000GB
```

更多`CRUD`操作参考官方文档 [[4]](#4)。

## 4. 开启用户认证

`mongodb`默认无需验证即可操作数据库，这显然具有安全隐患。于是，新建一个容器，并强制开启权限验证`--auth`：

```bash
$ docker run -d --name my-mongo mongo:latest --auth
```

进入容器，新建数据库`first`，并尝试写入数据
```
$ docker exec -it my-mongo /bin/bash

root@d3d2d1a0610c:/# mongo
> use first_db
switched to db first_db

> db.first_collection.insert({'msg': 'hello world'})
WriteCommandError({
        "ok" : 0,
        "errmsg" : "not authorized on first_db to execute command { ... }",
        "code" : 13,
        "codeName" : "Unauthorized"
})
```

`use first_db`时并没有真正创建数据库，所以可以顺利通过；`db.first_collection.insert`时出现未授权错误，说明已经启用用户认证机制。

于是，切换到系统`admin`数据库，创建用户

```bash
> use admin
switched to db admin

> db.createUser({user:"root",pwd:"root",roles:[{role:'root',db:'admin'}]})
```

**在开启鉴权且当前数据库没有用户的情况下，`mongodb`允许创建新用户 [[5](#5), [6](#6)]**。

通过用户验证`db.auth`后（返回值`1`），成功执行数据库操作

```bash
> db.auth('root', 'root')
1

> use first_db
switched to db first_db

> db.first_collection.insert({'msg': 'hello world'})
WriteResult({ "nInserted" : 1 })
```

也可以直接使用用户名/密码连接，登陆后即可正常进行数据库操作

```bash
$ mongo -u root -p root
```

以上操作基于：以`--auth`参数启动容器并在容器内部创建用户，更直接的方式是在启动容器时就创建授权用户

```bash
docker run -d \
        --name my-mongo \
        -e MONGO_INITDB_ROOT_USERNAME=root \
        -e MONGO_INITDB_ROOT_PASSWORD=root \
        mongo:latest
```


## 5. `docker-compose`版本

综合以上实验，可以将容器的启动参数都写入`docker-compose.yml`[[7](#7)]

- 挂载数据卷
- 创建默认`root`账户
- 启动容器后以`root`账户连接数据库执行脚本创建目标数据库对应的用户

```yml
version: '3'
services:
  mongo:
    image: mongo:latest
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=root
    ports:
      - "37017:27017"
    volumes:
      - "$PWD/entrypoint/:/docker-entrypoint-initdb.d/"
      - "$PWD/data:/data/db"
```

其中，`/entrypoint/any_name.sh`为数据库`first_db`创建具有读写权限的用户`tom`

```bash
#!/bin/bash
echo "Creating mongo users..."
mongo -u root -p root << EOF
use first_db
db.createUser({user: 'tom', pwd: 'goodboy', roles:[{role:'readWrite',db:'first_db'}]})
EOF
```

上面挂载数据卷的做法在`Windows`上会导致`mongodb`启动失败，原因参考 [[8](#8)]：

> Windows和OS X上的默认Docker设置使用VirtualBox VM来托管Docker守护程序。不幸的是，VirtualBox用于在主机系统和Docker容器之间共享文件夹的机制与MongoDB使用的内存映射文件不兼容（请参阅vbox bug，docs.mongodb.org和相关的jira.mongodb.org错误）。这意味着无法运行映射到主机的数据目录的MongoDB容器。

解决方法为新建`docker`数据卷`volume`，然后挂载为数据持久化目录

```bash
$ docker volume create --name volume_name
```

---

- [[1] Install MongoDB](https://docs.mongodb.com/guides/server/install/)<span id='1'></span>
- [[2] How to use this image](https://github.com/docker-library/docs/tree/master/mongo)<span id='2'></span>
- [[3] mongod](https://docs.mongodb.com/manual/reference/program/mongod/)<span id='3'></span>
- [[4] MongoDB CRUD Operations](https://docs.mongodb.com/manual/crud/)<span id='4'></span>
- [[5] Secure your MongoDB Deployment](https://docs.mongodb.com/guides/server/auth/)<span id='5'></span>
- [[6] Enable Access Control](https://docs.mongodb.com/manual/tutorial/enable-authentication/)<span id='6'></span>
- [[7] 基于 Docker 中的 MongoDB Auth 使用](https://www.jianshu.com/p/03bbfb8307df)<span id='7'></span>
- [[8] 关于widows系统使用docker部署mongo时报错：Operation not permitted](https://blog.csdn.net/qq506930427/article/details/99658808)<span id='7'></span>
