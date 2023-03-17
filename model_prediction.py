print('Importing np, pd libraries ...')
import pandas as pd
import numpy as np
import boto3
import matplotlib.pyplot as plt


def lambda_handler(event, context):
    
    ## Import all the remaining libraries
    from image_collection import collect_images
    print('Importing tensorflow ...')
    import tensorflow as tf
    from tensorflow.keras.utils import normalize

    # Loading the pre-trained model
    s3 = boto3.client("s3")
    localModelFile = '/tmp/model.h5'
    # Follwoing command has been used to download the s3 object 
    with open(localModelFile, 'wb') as f:
        s3.download_fileobj('semantic-segmentation-model-bucket', 'unet_model.h5', f)
    print('Loading model ...')
    model = tf.keras.models.load_model('/tmp/model.h5')

    ## Start collecting the images
    print('Collecting images ...')
    try:
        lat, lon, year, month = event['lat'], event['lon'], event['year'], event['month']
    except:
        lat, lon, year, month = 25.6198, 85.2043, '2022', '01'
    all_img_list, loc = collect_images(lat, lon, year, month)

    ## Get predictions from the model: normalizing the image, model prediction, argmax, count, percentages
    class_dict = []
    for image_list in all_img_list:
        if str(type(image_list)) != "<class 'NoneType'>":
            image_class_list = []
            for image in image_list:
                if str(type(image)) != "<class 'NoneType'>":
                    img = np.expand_dims(normalize(image), axis=0)
                    pred = model.predict(img)
                    class_pred = np.argmax(pred[0,:,:,:], axis=2)
                    classes, count = np.unique(class_pred, return_counts=True)[0], np.unique(class_pred, return_counts=True)[1]
                    image_class_list.append([[i,0] if (i not in classes) else [i,count[np.where(classes==i)[0][0]]] for i in range(7)])
                else:
                    image_class_list.append([[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]])
            mean = np.mean(np.array(image_class_list), axis=0)
            class_dict.append(mean)
        else:
            class_dict.append(None)

    final_df = pd.DataFrame([])
    final_df['Urban'] = [None if str(i)=='None' else i[1][1] for i in class_dict]
    final_df['Agriculture'] = [None if str(i)=='None' else i[2][1] for i in class_dict]
    final_df['Rangeland'] = [None if str(i)=='None' else i[3][1] for i in class_dict]
    final_df['Forest'] = [None if str(i)=='None' else i[4][1] for i in class_dict]
    final_df['Water'] = [None if str(i)=='None' else i[5][1] for i in class_dict]
    final_df['BarrenLand'] = [None if str(i)=='None' else i[6][1] for i in class_dict]
    final_df['Others'] = [None if str(i)=='None' else i[0][1] for i in class_dict]
    final_df.iloc[0,:] = 100 * final_df.iloc[0,:]/np.sum(list(final_df.iloc[0,:]))

    ## Plotting
    values = list(final_df.iloc[0,:].values)
    cover_types = list(final_df.columns)

    # creating the bar plot
    fig = plt.figure(figsize = (9, 5))
    plt.bar(cover_types, values, color ='maroon',
            width = 0.8)
    plt.xlabel("Landcover Types")
    plt.ylabel("% of total area covered")
    plt.title("Landover distribution in 5km square area")
    plt.savefig("/tmp/plot.jpg")

    ## Save to S3
    bucket_name = 'sentinel-output-images'
    img_object = 'your_area.jpg'
    plot_object = "plot.jpg"
    s3 = boto3.resource('s3')    
    s3.Bucket(bucket_name).upload_file(loc, img_object)
    s3.Bucket(bucket_name).upload_file("/tmp/plot.jpg", plot_object)

    # Get presigned url of the object
    s3_client = boto3.client('s3')
    img_obj_loc = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': img_object},
                                                    ExpiresIn=600)
    plt_obj_loc = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': plot_object},
                                                    ExpiresIn=600)

    return {'Satellite_img': img_obj_loc, 'Plot': plt_obj_loc}