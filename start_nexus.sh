#!/bin/bash
systemctl restart nexus.service
systemctl status nexus.service --no-pager | head -10
