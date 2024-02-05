import boto3
import botocore.session

def create_client(cl):
    return boto3.client(f'{cl}')

def create_dynamo(*args):
    table_name = args[0]
    print(table_name)
    dynamo = create_client('dynamodb')
    table_list = dynamo.list_tables()['TableNames']

    if table_name in table_list:
        print("the table you want to create already exists, proceeding with next phase!")
    
    else:
        print("Proceeding with the table creation")
        # Create a table, wait until it exists, and print its ARN
        response = dynamo.create_table(
            TableName = table_name,
            BillingMode = "PAY_PER_REQUEST",
            KeySchema = [
                {
                    'AttributeName':"id",
                    'KeyType':'HASH'
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName':"id",
                    'AttributeType':'S'
                }
            ]
        )
        session = botocore.session.get_session()
        dynamodb = session.create_client('dynamodb', region_name='us-east-2')
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        print('Table created:', response['TableDescription']['TableArn'])

def create_s3(*args):
    s3_name = args[0]
    s3 = create_client('s3')
    buckets_list = s3.list_buckets()['ResponseMetadata']['Buckets']
    if s3_name in buckets_list:
        print("The S3 buckets is already available")
    else:
        try:
            s3.create_bucket(Bucket=s3_name, CreateBucketConfiguration = {'LocationConstraint': 'us-east-2'})
        except Exception as e:
            print(e)
if __name__ == "__main__":
    # pass
# create_dynamo('ghactivity')
# create_s3('ghactivity-rajeev')
    from configparser import ConfigParser
    conf = ConfigParser()
    conf.read('config.ini')
    print(conf.sections())
    if conf.has_section('S3'):
        items = dict(conf.items('S3'))
        print(items['bucketname'])