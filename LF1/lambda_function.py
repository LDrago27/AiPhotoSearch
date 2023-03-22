import json
import boto3
import requests



def lambda_handler(event, context):
    # TODO implement

    MASTER_NODE =  "master"
    MASTER_PASSWORD = "Random#123"
    DOMAIN_ENDPOINT = "https://search-photos-gr5ieevykic5qmohaxjhnkaqpm.us-east-1.es.amazonaws.com"

    session = boto3.Session()
    client = session.client('rekognition')

    records = event["Records"]
    
    for record in records:
        
        bucketName = record["s3"]["bucket"]["name"]
        itemKey = record["s3"]["object"]["key"]
        
        s3 = boto3.client('s3')
        response = client.head_object(bucketName, itemKey)
        timestamp = response["LastModified"]
        
        # Using Rekognition client to obtain the custom labels in the image
        labelResponse = client.detect_labels(Image={'S3Object':{'Bucket':bucketName,'Name':itemKey}} )
        
        labelList = []
        for label in labelResponse['Labels']:
            labelList.append(label["Name"])

        # Making the POSt call to index the entry
        requestBody = { "objectKey": itemKey,"bucket": bucketName,"createdTimestamp": timestamp, "labels": labelList}
        headers = {"Authorization":"Basic bWFzdGVyOlJhbmRvbSMxMjM=", "Content-Type":'application/json'}

        resp = requests.post(DOMAIN_ENDPOINT,data=requestBody,headers=headers)
    
    

            