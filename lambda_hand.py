from ingest import file_ingest
import json
import os

def lambda_call(event, context):
    env = os.environ['env']
    res = file_ingest(env)
    return {
        'statusCode': res,
        'body': json.dumps("download")
    }