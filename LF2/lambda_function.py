import json
import boto3
import requests
import ast

def lambda_handler(event, context):
    print(event)
    inputText = event['q']
    print(inputText)
    client = boto3.client('lexv2-runtime')
    
    DOMAIN_ENDPOINT = "https://search-photos-1-4jicn37nt6b2iuttodfow3ct2m.us-east-1.es.amazonaws.com/photos-1/_search"
    headers = {"Authorization":"Basic bWFzdGVyOlJhbmRvbSMxMjM=", "Content-Type":'application/json'}

    respHeaders ={        "Access-Control-Allow-Origin":'*',
                        "Access-Control-Allow-Headers":'*',
                        "Access-Control-Request-Allow-Headers":'*',
                        "Access-Control-Allow-Methods":'*',
                        "Access-Control-Allow-Credentials": True
                }

    response = client.recognize_text(
            botId='HOSLVESBVR', # MODIFY HERE
            botAliasId='JWOPQM9R16', # MODIFY HERE
            localeId='en_US',
            sessionId = "user",
            text=inputText)
    
    print(response)
    if response['interpretations'][0]['intent']['name'] == "SearchIntent":
        searchKey = []
        try:
            for key in response['interpretations'][0]['intent']['slots']:
                if response['interpretations'][0]['intent']['slots'][key]:
                    searchKey.append(response['interpretations'][0]['intent']['slots'][key]["value"]["interpretedValue"])
    
            print("Search Keys obtained are:",searchKey)
            
            shouldArray= []
            requestBody = {"size":20,"query":{"bool":{}}}
            
            for key in searchKey:
                shouldArray.append({"match":{"labels":{"query":key,"fuzziness":"AUTO"}}})
            
            if not len(shouldArray):
                shouldArray.append({"labels":{"query":"*"}})
                
            requestBody['query']['bool']['should'] = shouldArray
    
            resp = requests.post(DOMAIN_ENDPOINT,data=json.dumps(requestBody),headers=headers)
            
            #content = str(resp.content)
            
            content = json.loads((resp.content.decode('utf-8')))
            
            nameList= []
            content["hits"]["hits"].sort(key = lambda x: x["_score"],reverse = True)

            s3urlClient =  boto3.client('s3')
            
            for hitObj in content["hits"]["hits"]:
                url = s3urlClient.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': 'photo2store', 'Key': hitObj["_id"]},ExpiresIn=3600)
                nameList.append({"url":url,"name":hitObj["_id"]})
    
            print(content)
            if resp.status_code == 200:
                return {
                    "status_code":200,
                    "headers":respHeaders,
                    "body": nameList
                    
                }
        except:
            return {
                "status_code":500,
                "headers":respHeaders,
                "body": {}
            }
            
            
            
    return {
                "status_code":500,
                "headers":respHeaders,
                "body": {}
            }
                
    
        
