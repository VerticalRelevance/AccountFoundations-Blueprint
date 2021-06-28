import boto3
import json

import common

from datetime import datetime,timezone

def handler(event, context):
    state = common.get_final_state(event)
    if state is None:
        return

    event_time = datetime.strptime(event['time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    metric_data = []

    if event['detail-type'] == "CodePipeline Pipeline Execution State Change":
        print(f'Received event: {json.dumps(event)}')

        current_execution = common.get_execution(event['detail']['pipeline'], event['detail']['execution-id'])
        
        print(f'current_execution: {current_execution}')
        
        if current_execution and current_execution['status'] == 'Failed':
            duration = (current_execution['lastUpdateTime'] - current_execution['startTime']).total_seconds()

            print(f'duration: {duration}')

            formatted_duration = common.format_metric("FailureLeadTime", event, seconds=duration)

            print(f'formatted_duration: {formatted_duration}')

            if formatted_duration:
                metric_data.append(formatted_duration)

    common.put_metrics(metric_data)
