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
                },
                {
                    'AttributeName':"filename",
                    'KeyType':'RANGE'
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName':"id",
                    'AttributeType':'S'
                },
                {
                    'AttributeName':"filename",
                    'AttributeType':'S'
                }
            ]
        )
        session = botocore.session.get_session()
        dynamodb = session.create_client('dynamodb', region_name='us-east-2')
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
        print('Table created:', response['TableDescription']['TableArn'])

if __name__ == "__main__":
    pass
# create_dynamo('ghactivity')
    # from configparser import ConfigParser
    # conf = ConfigParser()
    # conf.read('config.ini')
    # print(conf.sections())
    # if conf.has_section('S3'):
    #     items = conf.items('S3')