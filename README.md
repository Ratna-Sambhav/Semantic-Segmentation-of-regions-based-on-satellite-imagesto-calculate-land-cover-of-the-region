# Semantic-Segmentation-of-regions-based-on-satellite-imagesto-calculate-land-cover-of-the-region
Function deployed on aws lambda that recieves location data from api request, get satellite image of that location using Sentinel satellite image API (PyStac), use UNet architecture deep learning model to do semantic segmentation. 
The processed satellite image and pie chart (of land cover) is saved in s3 bucket using boto3 and pulic link is returned through the same API request back to the user.
