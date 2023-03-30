import json
import boto3
import requests
from urllib.parse import unquote_plus


def lambda_handler(event, context):
    # TODO implement
    #try:
    MASTER_NODE =  "master"
    MASTER_PASSWORD = "Random#123"
    DOMAIN_ENDPOINT = "https://search-photos-1-4jicn37nt6b2iuttodfow3ct2m.us-east-1.es.amazonaws.com/photos-1/_doc/"
    print(event)
    session = boto3.Session()
    client = session.client('rekognition')
    records = event["Records"]

    for record in records:

        bucketName = record["s3"]["bucket"]["name"]
        itemKey = record["s3"]["object"]["key"]
        
        itemKey = unquote_plus(itemKey)

        s3Client = boto3.client('s3')
        response = s3Client.head_object(Bucket = bucketName, Key = itemKey)
        timestamp = str(response["LastModified"])

        print(response)
        if "x-amz-meta-customlabels" in response["ResponseMetadata"]["HTTPHeaders"]:
            customLabels = [ele.strip().lower() for ele in response["ResponseMetadata"]["HTTPHeaders"]["x-amz-meta-customlabels"].split(",")]
        else:
            customLabels = []

        # Using Rekognition client to obtain the custom labels in the image
        labelResponse = client.detect_labels(Image={'S3Object':{'Bucket':bucketName,'Name':itemKey}} )

        labelList = []
        for label in labelResponse['Labels']:
            labelList.append(label["Name"])

        if customLabels:
            labelList = labelList + customLabels

        # Making the POSt call to index the entry
        requestBody = { "objectKey": itemKey,"bucket": bucketName,"createdTimestamp": timestamp, "labels": labelList}
        headers = {"Authorization":"Basic bWFzdGVyOlJhbmRvbSMxMjM=", "Content-Type":'application/json'}

        print(labelList)
        resp = requests.put(DOMAIN_ENDPOINT+itemKey,data=json.dumps(requestBody),headers=headers)

        if resp.status_code == 201 or resp.status_code == 200:
            return {"statusCode":200,"message":"Index Created Successfully"}
        else:
            return {"statusCode":500,"message":"Internal Server Error"}
    #except:
        #return {"statusCode":500,"message":"Internal Server Error"}
    

            
