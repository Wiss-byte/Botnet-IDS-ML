import time, random, json
import paho.mqtt.client as mqtt

client = mqtt.Client(client_id="burst_sim")
client.connect("localhost", 1883)

while True:
    # normal phase
    for _ in range(50):
        payload = json.dumps({
            "temperature": random.uniform(20, 30),
            "humidity": random.uniform(30, 60)
        })
        client.publish("emsi/esp32/dht22", payload)
        time.sleep(0.5)

    # burst phase (anomaly)
    print("⚠️ BURST")
    for _ in range(500):
        client.publish("emsi/esp32/dht22", "X"*50)
        time.sleep(0.001)