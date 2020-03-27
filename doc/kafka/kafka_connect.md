# Kafka Connect

`Kafka`不仅是一个分布式的消息队列，更是一个流处理平台——源于它于`0.9.0.0`和`0.10.0.0`引入的两个全新的组件`Kafka Connect`与`Kafka Streaming`。

`Kafka Connect`是一款可扩展并且可靠地在`Kafka`和其他系统之间进行数据传输的工具。消息队列需要上下游来生产和消费数据，例如`Flume`采集日志写入`Kafka`；而借助`Kafka Connect`即可替代Flume，让数据传输这部分工作由`Kafka Connect`来完成[[1](#1), [2](#2)]。




---

- [[1] KAFKA CONNECT](http://kafka.apachecn.org/documentation.html#connect)<span id='1'></span>
- [[2] 替代Flume——Kafka Connect简介](https://www.cnblogs.com/tree1123/p/11434047.html)<span id='2'></span>