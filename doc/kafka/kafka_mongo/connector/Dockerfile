FROM wurstmeister/kafka:latest

# download MongoDB Kafka Connector
RUN wget https://search.maven.org/remotecontent?filepath=org/mongodb/kafka/mongo-kafka-connect/1.0.1/mongo-kafka-connect-1.0.1-all.jar \
    && mkdir /opt/kafka-plugins \
    && mv mongo-kafka-connect-1.0.1-all.jar /opt/kafka-plugins/

# replace the start command creating a connector instead of starting a kafka broker.
COPY start-kafka.sh /usr/bin/

# permissions
RUN chmod a+x /usr/bin/start-kafka.sh