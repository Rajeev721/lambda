from ingest import file_ingest
import json

def lambda_call(event, context):
    res = file_ingest()
    return {
        'statusCode': res.status_code,
        'body': json.dumps("download")
    }