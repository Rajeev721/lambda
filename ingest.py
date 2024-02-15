from datetime import datetime as dt
from datetime import timedelta as td
import uuid
import boto3
from infra import create_client,creating_objects
import requests as rq
# from uuid import uuid5

def insert_dynamo(id, filename, insert_date):
        dy = create_client('dynamodb')
        
        """
        # dy = boto3.resource('dynamodb')
        # tbl = dy.describe_table(TableName='ghactivity')
        # tbl = dy.Table('ghactivity')
        # tbl.put_item(Item =  {'id':'kfjghgjfdgksdfgt',
        #                       'filename': 'dksvhjgasdhjkfgash',
        #                       'start_time': int(dt.now().strftime("%Y%m%d%H%M%s"))
        #                       }
        #                       )
        # print(tbl.scan())
        """
        dy.put_item(TableName='ghactivity',
                Item = {'id' : {"S":id},
                        'filename': {"S":filename},
                        'start_time':{'N': insert_date}
                        }
                    )

def update_dynamo(id, filename, update_date,message,run_status):
        dy = create_client('dynamodb')
        dy.update_item(TableName='ghactivity',
                Key={'id' : {"S":id}},
                UpdateExpression='SET update_time = :val1, message = :val2, run_status = :val3',
                ExpressionAttributeValues={':val1': {'N': update_date},
                                           ':val2': {'S': message},
                                           ':val3': {'S': run_status},
                                           }
                )
def file_ingest():
        creating_objects()
        s3 = create_client('s3')
        # n = int(input("how many latest files you want to ingest: "))
        n = 5
        for i in range(n, 0 , -1):
                file_name = f'{dt.strftime(dt.now() - td(hours = i),"%Y-%m-%d-%-H") + ".json.gz"}'
                print(file_name)
                id = str(uuid.uuid4())
                start_time = dt.now().strftime("%Y%m%d%H%M%s")
                insert_dynamo(id, file_name,  start_time)
                try:
                        res = rq.get(f'https://data.gharchive.org/{file_name}')
                        a = s3.put_object(
                                Bucket = 'ghactivity-rajeev',
                                Key = file_name,
                                Body = res.content
                        )
                        message = str(a)
                        run_status = 'Completed'
                except Exception as e:
                        run_status = 'Failed'
                        message = str(e)
                finally:
                        update_dynamo(id, file_name, dt.now().strftime("%Y%m%d%H%M%s"), message, run_status)

if __name__ == "__main__":
        file_ingest()