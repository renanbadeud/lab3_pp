from pydoc import cli
import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import multiprocessing
import desafios
import json

def oi(tdata):
    print("thread")

def on_message(client, userdata, message):
    
    dcd_msg = json.loads(message.payload.decode("utf-8"))
    # print(dcd_msg)
    tid = dcd_msg["transactionID"]
    seed = dcd_msg["seed"]
    if message.topic == "ppd/seed":
        if len(listaDesafios) > int(tid):
            if listaDesafios[tid].clientID == -1 and listaDesafios[tid].check_seed(seed):
                print('received on ppd/seed',message.payload.decode("utf-8"))
                listaDesafios[tid].clientID = dcd_msg["clientID"]
                listaDesafios[tid].seed = seed
                obj = vars(listaDesafios[tid]).copy()
                obj.__delitem__("challenge")
                client.publish("ppd/result", json.dumps(obj),qos=2)
                print("Just published ", json.dumps(obj), " to topic ppd/result")
                ultimo_desafio = listaDesafios[-1]
                listaDesafios.append(desafios.Challenge(ultimo_desafio.transactionID+1, ultimo_desafio.challenge+1))
                # time.sleep(1)
                client.publish("ppd/challenge", json.dumps(vars(listaDesafios[-1])), qos=2)
                print("Just published ", json.dumps(vars((listaDesafios[-1]))), " to topic ppd/challenge")
    return

mqttBroker = '127.0.0.1'
# mqttBroker = 'public.mqtthq.com'

client = mqtt.Client("Node_1")
client.connect(mqttBroker)

listaDesafios = [desafios.Challenge(0, 1)]
client.loop_start()

client.publish("ppd/challenge", json.dumps(vars((listaDesafios[-1]))), qos=2)
print("Just published ", 
        json.dumps(vars((listaDesafios[-1]))), 
        " to topic ppd/challenge")



client.subscribe("ppd/seed",qos=2)
client.on_message=on_message


# client.publish("ppd/challenge", json.dumps(vars(listaDesafios[-1])))
time.sleep(30000)

       
client.loop_stop()    
# client.loop_forever()