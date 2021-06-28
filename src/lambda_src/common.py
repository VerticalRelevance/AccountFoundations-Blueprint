import boto3

from datetime import datetime,timezone

# Return the state from the event if it's one of SUCCEEDED or FAILED
def get_final_state(event):
    if 'detail' in event and 'state' in event['detail']:
        if any(event['detail']['state'] in s for s in ['SUCCEEDED', 'FAILED']):
            return event['detail']['state']

    return None

# Return the execution summary for a given execution id
def get_execution(pipeline_name, execution_id):
    client = boto3.client('codepipeline')
    response = client.list_pipeline_executions(pipelineName=pipeline_name)

    for e in response['pipelineExecutionSummaries']:
        if e['pipelineExecutionId'] == execution_id:
            return e

    return None

# Return the execution summary for the most prior final execution before a given execution id
def get_prior_execution(pipeline_name, execution_id):
    client = boto3.client('codepipeline')
    response = client.list_pipeline_executions(pipelineName=pipeline_name)
    found_current = False
    
    for e in response['pipelineExecutionSummaries']:
        if found_current and any(e['status'] in s for s in ['Succeeded', 'Failed']):
            return e
        
        elif e['pipelineExecutionId'] == execution_id:
            found_current = True

    return None

# Return the execution summary for the most prior final successful execution before a given execution id
def get_prior_successful_execution(pipeline_name, execution_id):
    prior_execution = get_prior_execution(pipeline_name, execution_id)

    if not prior_execution:
        return None

    if prior_execution['status'] == 'Succeeded':
        return prior_execution
    else:
        return get_prior_successful_execution(pipeline_name, prior_execution['pipelineExecutionId'])

# Return the execution summary for the most prior+one final successful execution before a given execution id
def get_prior_success_plus_one_execution(pipeline_name, execution_id):
    prior_execution = get_prior_execution(pipeline_name, execution_id)

    if not prior_execution:
        return None

    if prior_execution['status'] == 'Succeeded':
        return True
    else:
        # If a prior execution was successful, return this execution
        if get_prior_successful_execution(pipeline_name, prior_execution['pipelineExecutionId']):
            return get_prior_execution(pipeline_name, execution_id)

def format_metric(metric_name, event, seconds=0, count=0):
    data = {
        'MetricName': metric_name,
        'Dimensions': [],
        'Timestamp': datetime.strptime(event['time'], '%Y-%m-%dT%H:%M:%SZ'),
    }

    resource_parts = []
    if 'pipeline' in event['detail']:
        data['Dimensions'].append({
            'Name': 'PipelineName',
            'Value': event['detail']['pipeline']
        })
        resource_parts.append(event['detail']['pipeline'])

    if 'stage' in event['detail']:
        data['Dimensions'].append({
            'Name': 'StageName',
            'Value': event['detail']['stage']
        })
        resource_parts.append(event['detail']['stage'])

    if 'action' in event['detail']:
        data['Dimensions'].append({
            'Name': 'ActionName',
            'Value': event['detail']['action']
        })
        resource_parts.append(event['detail']['action'])

    if seconds > 0:
        data['Value'] = seconds
        data['Unit'] = 'Seconds'
    elif count > 0:
        data['Value'] = count
        data['Unit'] = 'Count'
    else:
        return None

    print("resource=%s metric=%s value=%s" % ('.'.join(resource_parts), metric_name, data['Value']))

    return data

def put_metrics(metric_data):
    if len(metric_data) > 0:
        client = boto3.client('cloudwatch')

        client.put_metric_data(
            Namespace='Pipeline',
            MetricData=metric_data
        )
