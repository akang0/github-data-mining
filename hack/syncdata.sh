#!/bin/sh
export http_proxy="http://host:port"
export HTTP_PROXY="http://host:port"
export https_proxy="http://host:port"
export HTTPS_PROXY="http://host:port"
python3 /root/application/github-data-mining/gdm/mine.py -d {db-name} -o {github-org} -g {github-token}
python3 /root/application/github-data-mining/gdm/business.py -d {db-name}