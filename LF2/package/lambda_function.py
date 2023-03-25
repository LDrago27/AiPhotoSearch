import json
import boto3
import requests

def lambda_handler(event, context):
    inputText = event["queryStringParameters"]['q']

    client = boto3.client('lexv2-runtime')
    
    DOMAIN_ENDPOINT = "https://search-photos-gr5ieevykic5qmohaxjhnkaqpm.us-east-1.es.amazonaws.com/photos/_doc/"
    headers = {"Authorization":"Basic bWFzdGVyOlJhbmRvbSMxMjM=", "Content-Type":'application/json'}

    try:
        response = client.recognize_text(
                botId='KWLYLAGIR8', # MODIFY HERE
                botAliasId='UXITOPHKUG', # MODIFY HERE
                localeId='en_US',
                text=inputText)
        
        if response['interpretations'][0]['intent']['name'] == "SearchIntent":
            searchKey = []
            for key in response['slots']:
                searchKey.append(response['slots'][key])

            print("Search Keys obtained are:",searchKey)
            
            shouldArray= []
            requestBody = {"query":{"bool":{}}}

            for key in searchKey:
                shouldArray.append({"term":{"labels":key}})
            
            requestBody['query']['bool']['should'] = shouldArray

            resp = requests.post(DOMAIN_ENDPOINT,data=json.dumps(requestBody),headers=headers)
            if resp.status_code == 200:
                return resp["hits"]
            else:
                return []
    except:
        return []

