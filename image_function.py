from pystac_client import Client

from shapely.geometry import shape
import pyproj
from shapely.ops import transform
import geopandas

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from tensorflow.keras.utils import normalize

import rioxarray
import rasterio
import folium
import json
import boto3
import os

# Function
# def get_satellite_img(lat=25.6198, lon=85.2043, datetime='2017-05-01/2019-06-01'):

def get_satellite_img(lat, lon, datetime):

    # Defining url of the aws storage where data is stored
    api_url = "https://earth-search.aws.element84.com/v0"
    client = Client.open(api_url)

    # Setting up the name of the collection we want to access: Sentinel-2, Level 2A, COGs
    collection = "sentinel-s2-l2a-cogs"

    # Creating geometry file from inpiut location and size of area wanted
    km2lat = 1/110.574
    km2lon = 1/(111.320*np.cos(lat*np.pi/180))
    coords = []
    km = 5.12
    coords.append([lon-(km*0.5*km2lon), lat-(km*0.5*km2lat)])
    coords.append([lon+(km*0.5*km2lon), lat-(km*0.5*km2lat)])
    coords.append([lon+(km*0.5*km2lon), lat+(km*0.5*km2lat)])
    coords.append([lon-(km*0.5*km2lon), lat+(km*0.5*km2lat)])
    coords.append([lon-(km*0.5*km2lon), lat-(km*0.5*km2lat)])
    geom = {'type': "Polygon", "coordinates": [coords]}

    # Doing a search of all the satellite patches for that location (not necessarily having 100% intersection) for that date
    # having cloud coverage less than 1%. Then getting the last item from all the obtained patches
    mysearch = client.search(collections=[collection], intersects=geom, datetime=datetime, query=["eo:cloud_cover<1"])
    items = mysearch.get_all_items()
    assets = items[-1].assets

    # Getting the visual (rgb) image of the oatch obtained, and downloading it and saving in .tif format
    visual_href = assets["visual"].href
    visual = rioxarray.open_rasterio(visual_href)
    visual.rio.to_raster("/tmp/current.tif", driver="COG")
    # Loading the saved .tif pacth image
    data = rasterio.open('/tmp/current.tif')

    # Getting the coordinate reference system for the data accessed using the API
    dcrs = data.crs

    # Getting rgb layers from the geotif file and bringing in correct order for display
    np_img = data.read([1,2,3])
    patch_img = np.moveaxis(np_img, 0, 2)


    # Projecting the geometry of the area we want into the coordinate refrence system same as that of the obtained patch
    geom_aoi = shape(geom)
    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS(str(dcrs))
    project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    utm_point = transform(project, geom_aoi)
    geomk = geopandas.GeoSeries([utm_point])  
    
    # Follwoing code has been taken from (https://notebooks.githubusercontent.com/view/ipynb?browser=unknown_browser&color_mode=auto&commit=7ffc87bae86867ceef21fbb80e514342054a319a&device=unknown_device&enc_url=68747470733a2f2f7261772e67697468756275736572636f6e74656e742e636f6d2f7368616b61736f6d2f72732d707974686f6e2d7475746f7269616c732f376666633837626165383638363763656566323166626238306535313433343230353461333139612f52535f507974686f6e2e6970796e62&logged_in=false&nwo=shakasom%2Frs-python-tutorials&path=RS_Python.ipynb&platform=unknown_platform&repository_id=194450692&repository_type=Repository&version=0)
    # Cropping out the desired image area using the transformed geometry file and the patch using rasterio.mask
    # Image is downloaded 
    with rasterio.open("/tmp/current.tif") as src:
        out_image, out_transform = rasterio.mask.mask(src, geomk, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})
    with rasterio.open("/tmp/RGB_masked2.tif", "w", **out_meta) as dest:
        dest.write(out_image)

    # Loading the geotiff file of our desired area and converting it to numpy array
    # and into the form that can be displayed
    img_tiff = rasterio.open('/tmp/RGB_masked2.tif')
    np_img = img_tiff.read([1,2,3])
    img = np.moveaxis(np_img, 0, 2)

    ## Saving the image to local directory
    from PIL import Image
    im = Image.fromarray(img)
    random_n = np.random.randint(10000)
    loc = "/tmp/your_area" + str(random_n) + ".jpeg"
    im.save(loc)

    return img, loc

# img = get_satellite_img(25.6198, 85.2043, '2017-05-01/2019-06-01')
# {"lat":25.6198, "lon":85.2043}
