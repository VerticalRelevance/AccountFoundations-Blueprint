from aws_cdk import (
    core as cdk,
    aws_s3_deployment as s3deploy,
    aws_s3
)

class SetupStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create Control Tower asset bucket.
        control_tower_bucket = aws_s3.Bucket(self, "ControlTowerBucket",
            bucket_name='vr-account-foundation-bucket'    
        )

        # Deploy SCP policies.
        s3deploy.BucketDeployment(self, "DeployScpPolicies",
            sources=[s3deploy.Source.asset("./scp_policies")],
            destination_bucket=control_tower_bucket,
            destination_key_prefix="scp-policies"
        )

        # Deploy CFN templates.
        s3deploy.BucketDeployment(self, "DeployCfnTemplates",
            sources=[s3deploy.Source.asset("./cfn_templates")],
            destination_bucket=control_tower_bucket,
            destination_key_prefix="cfn-templates"
        )

        # Deploy supplementary templates.
        s3deploy.BucketDeployment(self, "DeploySupplementaryFiles",
            sources=[s3deploy.Source.asset("./supplementary_scripts")],
            destination_bucket=control_tower_bucket,
            destination_key_prefix="supplementary-files"
        )