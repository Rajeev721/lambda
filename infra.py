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
    buckets_list = s3.list_buckets()['Buckets']
    if s3_name in buckets_list:
        print("The S3 buckets is already available")
    else:
        try:
            s3.create_bucket(Bucket=s3_name, CreateBucketConfiguration = {'LocationConstraint': 'us-east-2'})
        except Exception as e:
            print(e)

def delete_resources(table_name = None, bucket = None):
    del_resp = {}
    if table_name:
        dynamo = create_client('dynamodb')
        try:
            if table_name in dynamo.list_tables()['TableNames']:
                print(f"Proceeding to delete the table {table_name}")
                response = dynamo.delete_table(
                TableName=table_name
            )
                session = botocore.session.get_session()
                dynamodb = session.create_client('dynamodb', region_name='us-east-2')
                waiter = dynamodb.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name)
                print('Table Deleted:', response['TableDescription']['TableArn'])
                del_resp[table_name] = response
        
        except Exception as e:
            del_resp[table_name] = str(e)
    
    if bucket:
        s3 = create_client('s3')

        if bucket in [buck['Name'] for buck in s3.list_buckets()['Buckets']]:

            objects = s3.list_objects(Bucket=bucket).get('Contents')
            if objects is not None:
                print(f"Bucket is not empty deleting the objects")
                for file in objects:
                    s3.delete_object(Bucket='ghactivity-rajeev', Key = file['Key'])
            print(f"Proceeding to delete the bucket {bucket}")
            response = s3.delete_bucket(Bucket=bucket)
            del_resp[bucket] = response

if __name__ == "__main__":
    # pass

    from configparser import ConfigParser
    conf = ConfigParser()
    conf.read('config.ini')

    if conf.has_section('S3'):
        items = dict(conf.items('S3'))
        bucket = items['bucketname']
    if conf.has_section('Dyanmo'):
        items = dict(conf.items('Dyanmo'))
        table_name = items['tablename']
    
    if conf.has_section('Drop_Objects'):
        items = dict(conf.items('Drop_Objects'))
        need_to_drop = items['drop_objects']
        if need_to_drop:
            print("Deleting the resources")
            delete_resources(table_name, bucket)
    print("Creating the resources...")
    create_dynamo(table_name)
    create_s3(bucket)