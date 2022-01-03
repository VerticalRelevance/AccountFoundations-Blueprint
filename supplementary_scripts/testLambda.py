import logging
import cfnresponse
import boto3

def handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    try:
        # Initialize EC2 client.
        client = boto3.client('ec2')
        # Pull the security group info for the account.
        security_groups = client.describe_security_groups()
        # Assign the name of the security group that will be deleted.
        sg_name = 'test-sg'
        # Loop through each security group to find the one that should be deleted.
        for i in range(len(security_groups['SecurityGroups'])):
            if security_groups['SecurityGroups'][i]['GroupName'] == sg_name:
                delete_sg_response = client.delete_security_group(GroupName=sg_name)
                logger.info(sg_name, 'has been deleted')
            else:
                print('Security group name not found')
        logger.info('Exiting Successfully')
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
    except Exception:
        logger.exception('Signaling failure to CloudFormation.')
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})