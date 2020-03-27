# PyMongo

`PyMongo` is a Python distribution containing tools for working with `MongoDB`, and is the recommended way to work with `MongoDB` from Python. [[1]](#1)



## 1. Installation

```bash
$ pip install pymongo
```

对于一些莫名其妙的超时问题，可以通过设置安装源`-i`(`--index-url`)或者代理`--proxy`来解决。

查看当前版本`3.10.1`

```bash
$ python3
Python 3.6.9 (default, Nov  7 2019, 10:44:02)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pymongo
>>> pymongo.version
'3.10.1'
```

## 2. Hello World

使用`PyMongo`前先启动`mongodb`服务，这里采用[前文](quickstart.md)`docker-compose.yml`的设置启动`mongodb`：

- 端口`37017`
- 超级用户`admin`及密码`root`
- `first_db`数据库用户`tom`及密码`goodboy`

下面的操作在宿主机器上进行。

使用`MongoClient`连接数据库：

```python
>>> uri = 'mongodb://tom:goodboy@localhost:37017/first_db'
>>> client = pymongo.MongoClient(uri)
```
这里采用`MongoDB URI`的方式，指明了服务器地址与端口，用户名密码及验证权限的数据库`first_db`

切换数据库

```python
>>> db = client.first_db
```

获取`Collection`

```python
>>> posts = db.posts
```

注意`db`和`Collection`都是延时创建的，在添加`Document`时才真正被创建。因此，此时的`Collection`列表应为空：

```python
>>> db.collection_names()
[]
```

插入示例文/数据：

```python
>>> posts.insert_one({'msg': 'hello world'})
```

向一个新的`Collection`插入两条数据：

```python
>>> db.users.insert_many([{'msg': 'hello world'}, {'msg': 'hello mongo'}])
```

再次查看`Collection`情况：

```python
>>> db.collection_names()
['users', 'posts']
```

统计文档数：

```python
>>> posts.count()
1
>>> db.users.count()
2
```

`PyMongo`的探索先到这里，更多练习将在后续实践中展开。


---

- [[1] PyMongo 3.9.0 Documentation](https://api.mongodb.com/python/current/index.html#)<span id='1'></span>

