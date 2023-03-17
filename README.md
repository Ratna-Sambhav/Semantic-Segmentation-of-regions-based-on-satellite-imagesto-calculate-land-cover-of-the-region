# Semantic-Segmentation-of-regions-based-on-satellite-imagesto-calculate-land-cover-of-the-region
Function deployed on aws lambda that recieves location data from api request, get satellite image of that location using Sentinel satellite image API (PyStac), use UNet architecture deep learning model to do semantic segmentation. 
The processed satellite image and pie chart (of land cover) is saved in s3 bucket using boto3 and pulic link is returned through the same API request back to the user.

![1](https://user-images.githubusercontent.com/72562461/225895010-d154a719-049a-4077-bd45-4126b368bb9e.PNG)
![2](https://user-images.githubusercontent.com/72562461/225895026-d2fcc7d3-9b8f-42e6-8527-67a5e984b2d1.PNG)
