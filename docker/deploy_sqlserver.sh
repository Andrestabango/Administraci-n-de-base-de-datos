#!/bin/bash

docker run -d \
  --name sqlserver_reportes \
  --network bd_heterogenea_net \
  -e ACCEPT_EULA=Y \
  -e MSSQL_SA_PASSWORD="SqlSrvProj#2026" \
  -e MSSQL_PID=Developer \
  -e MSSQL_TCP_PORT=1433 \
  -p 1434:1433 \
  -v /u02/docker/sqlserver/data:/var/opt/mssql:Z \
  --memory="3g" \
  --restart unless-stopped \
  mcr.microsoft.com/mssql/server:2022-latest

sleep 30
docker ps
docker logs sqlserver_reportes | tail -30