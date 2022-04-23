import paho.mqtt.client as paho
import time
import grpc;
import sys;
from concurrent import futures
sys.path.append("../grpc");
import MQTT_pb2 as mqttPb2;
import MQTT_pb2_grpc as mqttGrpc;
import configManager_pb2 as configPb2;
import configManager_pb2_grpc as configGrpc;
sys.path.append("../");
import variables;

from grpc_reflection.v1alpha import reflection





def on_message(client, userdata, msg):
  print(f"Topic: {msg.topic}, Message: {msg.payload.decode()}");

class ConfigManagerClient():
  def __init__(self):
    self.ip = variables.ConfigManagerIp;
    self.port = variables.ConfigManagerPort;
    self.channel = grpc.insecure_channel(f"{self.ip}:{self.port}");
    self.stub = configGrpc.ConfigManagerStub(self.channel);

  def getSettings(self):
    settings = self.stub.getMQTTConfig(configPb2.NoParam());
    return settings;



class MQTTService(mqttGrpc.MQTTServiceServicer):
  def __init__(self, settings):
    self.topicResponse="";
    self.msgResponse="";
    self.ip=settings.mqttIp;
    self.port=settings.mqttPort;
    self.brokerIp = settings.brokerIp;
    self.brokerPort = settings.brokerPort;
    self.socket= f"{self.ip}:{self.port}";
    self.mqttc = paho.Client()
    self.mqttc.on_connect = self.on_connect;
    self.mqttc.on_message = self.on_message;


  def publish(self, req, ctx):
    self.connectToBroker();
    self.mqttc.publish(req.topic, req.message);
    self.disconnectFromBroker();
    return mqttPb2.NoParam();


  def on_connect(self, mosq, obj, flags, rc):
    print(f"Connected with result code {rc}");

  def on_message(self, client, userdata, msg):
    self.topicResponse=msg.topic;
    self.msgResponse=msg.payload.decode();
    print(f"topic: {self.topicResponse}, Message: {self.msgResponse}");
    client.disconnect();

  def connectToBroker(self):
    self.mqttc.connect(self.brokerIp, self.brokerPort, 60);

  def disconnectFromBroker(self):
    self.mqttc.disconnect();


def serve():
  client = ConfigManagerClient();
  settings = client.getSettings();

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10));
  mqttService=MQTTService(settings);

  mqttGrpc.add_MQTTServiceServicer_to_server(mqttService, server);
  server.add_insecure_port(mqttService.socket);

  SERVICE_NAMES = (
    mqttPb2.DESCRIPTOR.services_by_name['MQTTService'].full_name,
    reflection.SERVICE_NAME,
  );

  reflection.enable_server_reflection(SERVICE_NAMES, server);
  server.start()
  print(f"Server Listening on Socket: {mqttService.socket}");
  server.wait_for_termination()

if __name__ == "__main__":
  serve();
