#! /bin/bash
# install dependencies and enveronment.
pip install --upgrade pip
echo install bs4
sudo pip3 install bs4 

echo install networkx
sudo pip3 install networkx

echo creating graph_bank directory
mkdir graph_bank

echo creating graph_img directory
mkdir graph_img


echo Done.
