from kafka import KafkaConsumer

if __name__ == '__main__': 
    
    # create a consumer
    consumer = KafkaConsumer(
        "my-topics",                      # subscribe topics
        bootstrap_servers = "kafka:9092", # comma separated kafka servers list
        group_id = "my.group"             # consumer group ID
    )

    # produce data
    # kafka-console-producer.sh --broker-list localhost:9092 --topic my-topics

    # receive messages
    for msg in consumer:
        print(msg)