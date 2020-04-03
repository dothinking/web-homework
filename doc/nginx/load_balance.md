# Nginx负载均衡

load balance HTTP traffic to a group of servers

处理高并发问题时的两个策略：

- 硬件：添加负载均衡器分发大量请求
- 软件：在高并发瓶颈处（数据库和web服务器）添加解决方案

其中web服务器前面一层最常用的的添加负载方案就是使用`nginx`实现负载均衡。


![load_balancer](https://www.nginx.com/wp-content/uploads/2019/01/nginx-plus-behind-hardware-lb.png)

> source from [[1]](#1)

## 1. 配置方法

首先用`upstream`定义一组服务器（例如`backend`），然后将请求发往这个组。

```
http {
    upstream backend {
        server backend1.example.com;
        server backend2.example.com;
        server 192.0.0.1 backup;
    }
    
    server {
        location / {
            proxy_pass http://backend;
        }
    }
}
```

不同的策略决定了将请求发送到具体哪个服务器上，例如轮询、权重分配、哈希分配等，具体定义及其配置参数参考文档[[2](#2), [3](#3)]。




## 2. Hello World

真正高可用的负载均衡方案不仅需要冗余的独立服务器，还需要冗余的负载均衡器即此处的`nginx`服务器。

本文仅在单机上通过不同端口模拟练习，关键[配置信息]("./conf/nginx-loadbalance.conf")：

```
http {
    # load balancer
    server {
        listen       80;
        server_name  localhost;
        location / {
            proxy_pass http://backend;
        }
    }

    # server group
    upstream backend {
        server localhost:8080;
        server localhost:8081;
    }

    # dummy server 1
    server {
        listen       8080;
        server_name  localhost;
        
        location / {
            root   /usr/share/nginx/html;
            index  index1.html;
        }
    }

    # dummy server 2
    server {
        listen       8081;
        server_name  localhost;
        
        location / {
            root   /usr/share/nginx/html;
            index  index2.html;
        }
    }
}
```

- 在容器内`8080`和`8081`两个端口创建了两个虚拟服务器，为了直观体现不同服务器的请求效果，分别设置了不同的主页`index[1|2].html`
- 将这两个服务器作为一个组`backend`，响应`80`端口的请求

启动容器：

```bash
$ docker run --name nginx_test -d \
    -p 8080:80 \
    -v $PWD/conf/nginx-loadbalance.conf:/etc/nginx/nginx.conf \
    -v $PWD/www:/usr/share/nginx/html \
    -v $PWD/logs:/var/log/nginx \
    --rm nginx
```

不断刷新`http://localhost:8080/`将依次得到：

```
Hello Nginx! I'm Server 1.
```

和

```
Hello Nginx! I'm Server 2.
```





---

- [[1] NGINX Load Balancing Deployment Scenarios](https://www.nginx.com/blog/nginx-load-balance-deployment-models/)<span id='1'></span>
- [[2] HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)<span id='2'></span>
- [[3] Nginx - 负载均衡配置](https://juejin.im/post/5d5277d5f265da03e71ae9ce)<span id='3'></span>