#!/bin/bash
# 停止gunicorn并启动nexus服务
pkill -9 -f gunicorn 2>/dev/null
sleep 1
systemctl start nexus
systemctl enable nexus
systemctl status nexus | head -10
