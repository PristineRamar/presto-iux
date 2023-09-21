
import requests
import json
from recommendation.util import getDetailsUsingFuzzySearch
from typing import Optional, List
from pydantic import BaseModel, Field
from recommendation.dataRepository import *
from config.app_config import config

#predictedUserId='ejack'


def create_json_string(data):
    json_string = json.dumps({"jsonString": json.dumps(data)})
    return json_string

def getauthenticationUrl(authentication_url, predictedUserId):
    '''
    print('calling authentication url..')
    userId=getUserDetails(predictedUserId)
    print(userId)
    if userId is  None:
        '''
    userId = {"UserId": "prestolive", "Password": "Prest0livE"}
 
    apiInput = create_json_string(userId) 
    response = requests.post(authentication_url, data=apiInput, headers={"Content-Type": "application/json"})
    response_data = response.json()
    print('from authentication ',response_data)
    return response_data



def get_data (**kwargs):
    print(kwargs)
    api_name = kwargs.get('api_name')
    product_list=kwargs.get('product_name')
    zoneName_List=kwargs.get('location_name')
    zoneNumber_List=kwargs.get('location_id')
    user_id=kwargs.get('user_id')
   
    category_id=getCategoryLevelId()
    print('category_id',category_id)
    productDictionary=getProducts(category_id)

    
    if zoneName_List :
        zoneList=zoneName_List
        zoneDictionary=getZonesByName()
    elif zoneNumber_List :
        zoneList=zoneNumber_List
        zoneDictionary=getZonesById()

    for name in product_list:
      
        categoryName = getDetailsUsingFuzzySearch(productDictionary, name, 1)
      
        product_id = productDictionary.get(categoryName)
        print('categoryName',categoryName ,'product_id ',product_id)
            
        for zone in zoneList:
            zoneName = getDetailsUsingFuzzySearch(zoneDictionary, zone, 1)
            zone_id = zoneDictionary.get(zoneName)
         
            product_location_info = {
            "productId": product_id,
            "productLevelId": category_id,
            "locationId": zone_id,
            "locationLevelId":'6',
            "predictedUserId":'Presto'
           # "predictedUserId": user_id
        }
        if api_name =='recommend':
           print ('calling recommendation service ...')
           response=trigger_recommendation(product_location_info)
           
           if response is not None:
               if response.status_code == 200:
                   response_data = response.json()
                   message = json.loads(response_data["d"])["message"]
                   finalmessage= messageInterpretor(message,categoryName,zoneName)
                 
                   return finalmessage
               else:
                   return 'There was error processing request for  '+ categoryName +'  for zone '+ zoneName 
           else:
             return 'There was error processing request for  '+ categoryName +' and Zone '+ zoneName 

        if api_name =='completeReview':
            print('calling completeReview....' ) 
            response= callCompleteReviewAPI(product_location_info)
            response_data = response.json()
            if response_data is not None:
                message = json.loads(response_data["d"])
             # message={'StatusCode': 2, 'StatusMessage': '0020 (BM 20)-FROZEN G ROCERY:- Already review completed by !', 'Messages': [], 'Result': None, 'ResultData': None}
                print('message  from api',message)
                result = message["Result"]
                if result is not None:
                    if result["StatusCode"] == 3:
                        message = result["StatusMessage"]
                else:
                    message = json.loads(response_data["d"])["StatusMessage"]
                 
                print('message from complete review',message)
                finalmessage= messageInterpretor(message,categoryName,zoneName)
                return finalmessage
            else:
               return 'There was error processing request for  '+ categoryName +'  for zone '+ zoneName 
            
            

def trigger_recommendation(kwargs):
    
    userId= kwargs.get('predictedUserId')
    
    try:
        response_data=getauthenticationUrl(config['general']['authentication_url'],userId)
        
        inner_json_string = response_data["d"]
        inner_data = json.loads(inner_json_string)
        user_token = inner_data.get("UserToken")
        asp_session_id = inner_data.get("ASPDotNetSessionID")
        
        session_id_string = f"ASP.NET_SessionId={asp_session_id}"
        
        url=config['general']['recommendation_service_url']
      
        headers = {"Content-Type": "application/json", "Cookie": session_id_string} 
        
        kwargs["UserToken"]=user_token
        print('trigger_recommendation args  ',kwargs)
        print('url',url)
        print('session_id_string ',session_id_string  ,'user_token ',user_token )
        print('headers',headers)
    
        try:
            response = requests.post(url, headers=headers,json= kwargs)
            return response
           
        except requests.exceptions.RequestException as e:
            print(f"Error in Request to ExecutePriceRecommendationQR: {e}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error in Request to ExecutePriceRecommendationQR: {e}")
        return None
        
       

def messageInterpretor(message,categoryName,zoneName):
     
    if "Recommendation is already queued for selected Zone and Category" in message:
       return'Recommendation is already queued for ' + categoryName + ' and zone '+ zoneName + ' .Please check the status on Presto by clicking Show Running Recs'
          
    elif "Recommendation added to Queue" in message:
        return'Recommendation is  queued for ' + categoryName + ' and  zone '+ zoneName + ' .Please check the status on Presto by clicking Show Running Recs'
    
    elif "Review Completed" in message:
           return'Review completed for  ' + categoryName + ' and  zone '+ zoneName
   
    elif " Already review completed " in message:
            return'Review is already completed for ' + categoryName + ' and zone '+ zoneName 
     
    elif "Recommedation data not found" in message :
          return 'Recommedation data not found for '+ categoryName + ' and zone '+ zoneName +' Please run recommendation for this combination'
    
    elif "No permission to do Price Recommendation" in message :
           return 'No permission to do Price Recommendation for selected category  ' + categoryName
   
    elif "REVIEW COMPLETED" in message:
           return'Review completed for  ' + categoryName + ' and zone '+ zoneName
    else: 
           return message
      


def callCompleteReviewAPI(kwargs):
     print('kwargs',kwargs)
     product_id= kwargs.get('productId')
     product_level_id=kwargs.get('productLevelId')
     location_id=kwargs.get('locationId')
     location_level_id=kwargs.get('locationLevelId')
     
    # print(product_id, ';' ,product_level_id,';' , location_id,';' , location_level_id)
    
     run_id=getLatestRunId(product_id,product_level_id,location_id,location_level_id)
     
     if run_id is None:
         run_id=0
         
     print('run_id fetched :', run_id)
         
         
     complete_review_parameters = [{
     "run-Id": run_id,
     "prod-lev-id": product_level_id,
     "prod-id": product_id,
     "loc-lev-id": location_level_id,
     "loc-id": location_id
     }]
     
     response_data= getauthenticationUrl(config['general']['authentication_url'],'prestolive')
     
     inner_json_string = response_data["d"]
     inner_data = json.loads(inner_json_string)
     user_token = inner_data.get("UserToken")
     asp_session_id = inner_data.get("ASPDotNetSessionID")
     
     session_id_string = f"ASP.NET_SessionId={asp_session_id}"
     url=config['general']['completeRevieweview_url']
     headers = {"Content-Type": "application/json", "Cookie": session_id_string}
     
     data_dict = {
     "completeReviewParameters": json.dumps(complete_review_parameters),
     "userId": "prestolive",
     "UserToken": user_token
     }
     print(json.dumps(data_dict))
     try:
        response = requests.post(url, data=json.dumps(data_dict), headers=headers)
        print('response from api', response )
        return response
     except requests.exceptions.RequestException as e:
         print(f"Error in Request to ExecutePriceRecommendationQR: {e}")
         return None   
    
class APICallParameters(BaseModel):
        
     
        """Inputs for get_data_by_api"""
        api_name: str = Field(
            ...,
            description="APIs to call: 1. Recommendation API: it returns the status; 2. Complete Review API :It returns the status ; 3.PriceReviewApproval: it Returns the status",
            enum=["recommend", "completeReview", "approve"]
        )
        product_name:List[str] = Field(
            ...,
            description="Used to specify the category names the user wants to recommend.It can be a list of categories or single category For example, UPPER RESPIRATORY,GROCERY,AUTOMOTIVE_BATTERIES_RU' would be valid ways of using this argument."
        )
       
        location_name: Optional[List[str]] = Field(
            None,
            description="Used to specify the zone name  for which the user wants to recommend.It can be a list of zone names or single zone name  For example, It will be a name like EAST BASE, ZONE EAST BASE, BM 11 would be valid ways of using this argument."
        )
        location_id : Optional[List[str]] = Field(
            None,
            description="Used to specify the zone number  for which the user wants to recommend.It can be a list of zone number  or single zone number For example,  zone 4, zone 16, or 4  or 4,16,ZP6200  would be valid ways of using this argument."
        )
       
        user_id: Optional[List[str]] = Field(
            None,
            description="Used to specify the user who has made the request .prestolive would be a valid way to identify this request "
        )
        
