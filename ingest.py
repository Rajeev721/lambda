import boto3
from infra import create_client

dy = create_client('dynamodb')

# tbl = dy.describe_table(TableName='ghactivity')
# print(dir(dy))
# print(help(dy.put_item))

dy.put_item(TableName='ghactivity',
             Item = {'id' : {"S":'kfjghgjfdgksdfgt'},
                     'filename': {"S":'dksvhjgasdhjkfgash'}
                    }
                    )

print(dy.scan(TableName='ghactivity'))