from datetime import datetime as dt
from datetime import timedelta as td
import uuid
import boto3
from infra import create_client
import requests as rq
# from uuid import uuid5

def insert_dynamo(table_name, id, filename, insert_date):
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
        dy.put_item(TableName=table_name,
                Item = {'id' : {"S":id},
                        'filename': {"S":filename},
                        'start_time':{'N': insert_date}
                        }
                    )

def update_dynamo(table_name, id, filename,start_time, update_date,message,run_status):
        dy = create_client('dynamodb')
        dy.update_item(TableName=table_name,
                Key={'id' : {"S":id}, 'start_time' : {'N': start_time}},
                UpdateExpression='SET update_time = :val1, message = :val2, run_status = :val3',
                ExpressionAttributeValues={':val1': {'N': update_date},
                                           ':val2': {'S': message},
                                           ':val3': {'S': run_status},
                                           }
                )
def get_latest_run(table_name):
        dy = create_client('dynamodb')
        response = dy.scan(TableName=table_name)
        sorted_items = sorted(
                response['Items'],
                key=lambda item: item['start_time']['S'],
                reverse=True
                )
        return sorted_items[0]['start_time']['N'][:15]
def config_details(env):
        from configparser import ConfigParser
        conf = ConfigParser()
        conf.read('config.ini')
        if conf.has_section(env):
                items = dict(conf.items(env))
                bucket = items['bucketname']
                table_name = items['tablename']
        return bucket,table_name       

def file_ingest(env):
        # creating_objects()
        
        bucket_name, table_name = config_details(env)
        
        latest_data = get_latest_run(table_name)

        if latest_data:
                file_name = f'{dt.strftime(dt.strptime(latest_data, "%Y%m%d%H%M%S") - td(hours = 1),"%Y-%m-%d-%-H") + ".json.gz"}'
        else:
                file_name = f'{dt.strftime(dt.now() - td(hours = 1),"%Y-%m-%d-%-H") + ".json.gz"}'

        s3 = create_client('s3')

        id = str(uuid.uuid4())
        start_time = dt.now().strftime("%Y%m%d%H%M%s")
        insert_dynamo(table_name, id, file_name,  start_time)
        try:
                res = rq.get(f'https://data.gharchive.org/{file_name}')
                a = s3.put_object(
                        Bucket = bucket_name,
                        Key = file_name,
                        Body = res.content
                )
                message = str(a)
                run_status = 'Completed'
        except Exception as e:
                run_status = 'Failed'
                message = str(e)
        finally:
                update_dynamo(table_name, id, file_name,start_time, dt.now().strftime("%Y%m%d%H%M%s"), message, run_status)
        return message