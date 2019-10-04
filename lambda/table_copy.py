import json
import boto3

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
     existing_table = dynamodb.Table('account_allocations')
     items = existing_table.scan()['Items']

     table = dynamodb.create_table(
        TableName='account_allocations_copy',
        KeySchema=existing_table.key_schema,
        AttributeDefinitions=existing_table.attribute_definitions,
        BillingMode='PAY_PER_REQUEST')
     print("Table status:", table.table_status)

     table.wait_until_exists()
     table.reload()

     print("Table status:", table.table_status)
     print("Updating table with data...")
     if table.table_status == 'ACTIVE':
         for item in items:
             response = table.put_item(Item=item)
             print("PutItem status:",
                   response['ResponseMetadata']['HTTPStatusCode'])

     print("Total items created:", table.scan()['Count'])
