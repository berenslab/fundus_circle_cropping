#!/bin/bash

mkdir -p data/images                        
cd data/images                           
curl -sS https://www5.cs.fau.de/fileadmin/research/datasets/fundus-images/healthy.zip > images.zip 
unzip images.zip                                  
rm images.zip

cd data/images
cd ..
cd ..   
cd download_data
python ids_file.py
