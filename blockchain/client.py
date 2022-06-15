import ctypes
import hashlib
from multiprocessing.sharedctypes import Value
from os import kill
import random
import string
import paho.mqtt.client as mqtt
import time
import multiprocessing
import desafios
import json
import random

cur_tid = -1
cur_challenge = -1
mqttBroker = '127.0.0.1'
# mqttBroker = 'broker.emqx.io'
clientID = 777
# mqttBroker = "public.mqtthq.com"

def on_publish(client, userdata, mid):
    print(f"Client: published message: {mid}")
    
def brute(tdata: desafios.Challenge, thread_id, s: multiprocessing.Value, kill_threads: multiprocessing.Value):
    finish=0
    resultado=False
    res = ""
    while(finish==0 and kill_threads.value == 0):

        res = ''.join(random.choices(string.ascii_lowercase +
                                string.digits, k = 7))
        ct=desafios.Challenge(tdata.transactionID,tdata.challenge,seed=str(res))
        
        resultado=ct.check_seed(ct.seed)

        if(resultado):
            break
            
       
    if(resultado):
        vars(ct)["clientID"]=clientID
        kill_threads.value = 1
        s.value = res   


def on_message(client, userdata, message):
    msg=json.loads(message.payload.decode("utf-8"))
    global cur_tid
    global cur_challenge
    if(message.topic=='ppd/challenge'):
        if cur_tid == -1:
            print('received on ppd/challenge ',msg)
            challenge=desafios.Challenge(transactionID=msg["transactionID"],challenge=msg["challenge"])
            cur_challenge = challenge.challenge
            cur_tid = int(msg["transactionID"])
            processes = []
            manager = multiprocessing.Manager()
            s = manager.Value(ctypes.c_wchar_p, 'aaa')
            kill_threads = manager.Value('i', 0)
            for i in range(10):
                p = multiprocessing.Process(target=brute, args=(challenge,i, s, kill_threads))
                processes.append(p)
                p.start()
               
            for proc in processes:
                proc.join()
            ct=desafios.Challenge(cur_tid,challenge.challenge,clientID=clientID,seed=s.value)
            obj = vars(ct).copy()
            obj.__delitem__("challenge")
            client.publish("ppd/seed",json.dumps(obj), qos=2)
            print("Just published ", obj, " to topic ppd/seed")
            
    if(message.topic=='ppd/result'):
        print('received on ppd/result ',msg)
        if cur_tid == msg["transactionID"]:
            cur_tid = -1
            

client = mqtt.Client("Node_3")
client.connect(mqttBroker)
client.loop_start()
client.subscribe("ppd/challenge",qos=2)
client.subscribe("ppd/result", qos=2)


client.on_message=on_message
client.on_publish = on_publish
time.sleep(30000)
client.loop_stop()
# client.loop_forever() ##verificar isso