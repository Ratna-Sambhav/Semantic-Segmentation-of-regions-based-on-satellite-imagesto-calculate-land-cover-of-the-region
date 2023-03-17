from pystac_client import Client

from shapely.geometry import shape
import pyproj
from shapely.ops import transform
import geopandas

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

import rioxarray
import rasterio
import folium
import json
import boto3
import os

from image_function import get_satellite_img

## Collecting all the images
## Getting the dates on per month basis from Jan, 2016 to Sep, 2022
def collect_images(lt, ln, year, month):
    years = [year]

    date_list, image_list = [], []
    for year in years:
        for n in range(1):
            start_date = year + '-' + month + '-' +'01'
            end_date = year + '-' + month + '-' + '28'
            date = start_date +'/'+end_date
            date_list.append(year + '_Q' + str(n))
            print(f"Getting satellite image for {year}_Q{n}")

            # Try to get the image for this date: If not then fill will NA
            try:
                img, loc = get_satellite_img(lat=lt, lon=ln, datetime=date)
                image_list.append(img)
            except:
                image_list.append(None)
    
    ## Make four images of 256*256 for each large size image
    new_list = []
    for i in image_list:
        if str(type(i)) != "<class 'NoneType'>":
            img_list = []
            img_list.append(i[:256, :256])
            img_list.append(i[:256, 256:512])
            img_list.append(i[256:512, :256])
            img_list.append(i[256:512, 256:512])
            new_list.append(img_list)
        else:
            new_list.append(None)

    # Filtering the image: Removing images of different sizes and also removing images containing binary colors only
    tiled_img = []
    for i in new_list:
        if str(type(i)) != "<class 'NoneType'>":
            img_list = []
            for img in i:
                # Checking if the number of unique values in the image is less than 100, it will most probably be not a good image
                # Also choosing only the desired size and removing others.
                if img.shape == (256, 256, 3) or len(np.unique(img)) > 100:
                    img_list.append(img)
                else:
                    img_list.append(None)
            tiled_img.append(img_list)
        else:
            tiled_img.append(None)

    return tiled_img, loc