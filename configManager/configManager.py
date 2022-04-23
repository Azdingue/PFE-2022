#!/usr/bin/env python3

import sys;
import time;
from concurrent import futures;
import grpc;
from grpc_reflection.v1alpha import reflection;
sys.path.append('../grpc/');
import configManager_pb2 as configPb2;
import configManager_pb2_grpc as configGrpc;

sys.path.append("../");
import variables;



MQTTConfig = configPb2.MQTTConfigResponse(
  mqttIp=variables.MQTTServerIp,
  mqttPort=variables.MQTTServerPort,
  brokerIp=variables.BrokerIp,
  brokerPort=variables.BrokerPort
);


ModbusTCPConfig = configPb2.ModbusTCPConfigResponse(
  serverIp=variables.ModbusTCPIp,
  serverPort=variables.ModbusTCPPort
);


class ConfigService(configGrpc.ConfigManagerServicer):
  def getMQTTConfig(self, req, ctx):
    return MQTTConfig;
  def getModbusTCPConfig(self, req, ctx):
    return ModbusTCPConfig;




def serve():
  socket=f"{variables.ConfigManagerIp}:{variables.ConfigManagerPort}";
  server=grpc.server(futures.ThreadPoolExecutor(max_workers=10));
  configGrpc.add_ConfigManagerServicer_to_server(ConfigService(), server);
  server.add_insecure_port(socket);

  SERVICE_NAMES=(
    configPb2.DESCRIPTOR.services_by_name['ConfigManager'].full_name,
    reflection.SERVICE_NAME,
  );
  reflection.enable_server_reflection(SERVICE_NAMES, server);
  server.start();
  print(f"Server Listening on {socket}");
  server.wait_for_termination();


if __name__ == "__main__":
  serve();