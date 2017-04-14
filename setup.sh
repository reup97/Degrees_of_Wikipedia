#! /bin/bash
# This script helps you install dependencies that
# are required for degrees of wikipedia.

echo creating graph_bank directory
mkdir graph_bank

echo creating graph_img directory
mkdir graph_img

sudo -H pip3 install --upgrade pip
echo install bs4
sudo -H pip3 install bs4

echo install networkx
sudo -H pip3 install networkx

echo Done.
