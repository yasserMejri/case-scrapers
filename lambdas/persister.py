
#
# For more information, see:
# https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/data-api.html
#
# Prerequisites:
#  - Required permissions to Secrets Manager and RDS Data API
#  - Latest boto3 SDK in local package. Run the following in Cloud9 shell:
#     - `pip install boto3 -t boto3`
#
###############################################################################

import os
import os.path
import sys



# Use latest boto3 from local environment
LAMBDA_TASK_ROOT = os.environ["LAMBDA_TASK_ROOT"]
sys.path.insert(0, LAMBDA_TASK_ROOT+"/boto3")

# Required imports
import botocore
import boto3
import json

# Imports for your app
from datetime import datetime
from botocore.exceptions import ClientError

# Update your cluster and secret ARNs
#cluster_arn = 'arn:aws:rds:us-west-2:532956249000:cluster:eta-db' 
#secret_arn = 'arn:aws:secretsmanager:us-west-2:532956249000:secret:rds-db-credentials/cluster-JZIGQCO63HFEEMSC3GJEBE4Y2Q/postgres-HpbDdd'
#######
#CONSTANTS

CLUSTER_ARN = 'arn:aws:rds:us-west-2:532956249000:cluster:eta-db-2'
SECRET_ARN = 'arn:aws:secretsmanager:us-west-2:532956249000:secret:rds-db-credentials/cluster-523EDKSHZUW6M5RO6BM3HQFZNA/postgres-nEm0Wj'
DATABASE = 'postgres'


ACTION = 'action'
DOB = 'dob'
STATUS = 'status'
RESULT = 'result'
LNAME = 'lname'
FNAME = 'fname'
QUERY_KEY = 'query_key'
RESULT_SET = 'result_set'
COURT = 'court'
US_STATE = 'state'
JURISDICTION = 'jurisdiction'

HTTP_OK = 200

###########


# 
# Use cases: 
#1. Create a new record - action = create, fields = dob, lname, fname, query_key, court, jurisdiction, us_state
#2. update an existing record action = update, fields =  result_set, query_key
#3. update an existing record action = query, fields = query_key
# Request must be sent with key 'lanbda'


def lambda_handler(event, context):
    print("hello from handler ", event)
    print(event["lambda"])
    response = scraperjob(event["lambda"])
    return response
    
   # return (
#        "response": response.http_response,
 #       )

    # if 'Records' not in event or 'Sns' not in event['Records'][0]:
    #     print('Not an SNS event!')
    #     print(str(event))
    #     return
    # print("printing record")
    # for record in event['Records']:
    #     print(record)
    #     data = json.loads(record['Sns']['Message'])
    #     print("data is ", data)
    #     call_rds_data_api(record['Sns']['Timestamp'], data['lambda'])


def scraperjob(message):
    rds_data = boto3.client('rds-data')
    action = message[ACTION]
    
    if action == 'create':
        response = do_create(message)
    elif action == 'update':
        do_update(message)
    elif action == 'query':
        do_query(message)
    else:
        print ("Invalid action type ", action)
    
    print("returning to gateway ", response)
    
    return response
    

#1. Create a new record - 
#action = create, 
#fields = dob, lname, fname, query_key, court, jurisdiction, us_state

#########################################################################
# Every time we create a new job it must specify the individual info (dob, lname, fname)
# and the court info (jurisdiction, court, state)
# This function will create a new scraper_info  capturing court info if it does not exist and 
# a new record in scrape resuts with a foriegn key to the court info
#########################################################################

def do_create(message):
    dob = message[DOB]
    lname = message[LNAME]
    fname = message[FNAME]
    court = message[COURT]
    jurisdiction = message[JURISDICTION]
    us_state = message[US_STATE]
    
    # 
    # Ensure mandatory parameters are present
    #
    if not dob or not lname or not fname or not court or not jurisdiction or not us_state:
        print ("invalid query", message)
        return
    
    # python 3.6 f syntax
    create_scraper_sql = f"insert into scraper_info(jurisdiction, court, us_state) VALUES('{jurisdiction}','{court}','{us_state}') ON CONFLICT DO NOTHING"
    print(create_scraper_sql)
    info_response = query_db(create_scraper_sql)
    print ("response is", info_response)
    
    
    #INSERT INTO scrape_results (dob,lname, scraper_info_fk) VALUES ('01-01-1970','Ram', (SELECT scraper_info_pk FROM scraper_info WHERE jurisdiction='Maricopa'))
    ##query_tz
    
    #note: \ needed on multiline f to remove \n
    create_result_sql = f"insert into scrape_results(dob,lname,fname,status,scraper_info_fk)" \
                        f"VALUES('{dob}','{lname}','{fname}', 'open', "\
                        f"(SELECT scraper_info_pk FROM scraper_info WHERE jurisdiction='{jurisdiction}' "\
                        f"AND court='{court}' AND us_state='{us_state}')) RETURNING query_key"
                        
    print(create_result_sql)
    job_response = query_db(create_result_sql)
    print("response for result ", job_response)
    
   # query_key = f"SELECT query_key FROM scrape_results WHERE 
    
    http_code = 200 if (info_response["ResponseMetadata"]["HTTPStatusCode"] == 200  
                    and job_response["ResponseMetadata"]["HTTPStatusCode"] == 200) else 500
    
    query_key = job_response["records"][0][0]["stringValue"]
    print("query_key ", query_key)
    
    return({
        "http_response": http_code,
        'query_key': query_key
        })
        
    
                    
    
    

        
    
def query_db(qsql):
    rds_data = boto3.client('rds-data')
    try:
        response = rds_data.execute_statement(
            resourceArn = CLUSTER_ARN,
            secretArn = SECRET_ARN,
            database = DATABASE,
            sql = qsql
       # sql = "insert into scraper_info(jurisdiction, court, us_state) VALUES('Calcutta','court','CA')"
        )
    # response = rds_data.execute_statement(
    #     resourceArn = cluster_arn, 
    #     secretArn = secret_arn, 
    #     database = 'eta', 
    #     sql = sql,
    #     parameters = param_set)
    except ClientError as e:
        print("failed to update ", e)
        if e.response['Error']['Code'] == 'BadRequestException':
            print("ooh bad request Exception")
    
    if response['ResponseMetadata']['HTTPStatusCode'] != HTTP_OK:
        print("error saving to db ", response)
    return response
    
def do_update(message):
    print("hello")
    #update scrape_results set result_tz=current_timestamp(1) where scrape_results_pk=1;
    
def do_query(message):
    print ("query")