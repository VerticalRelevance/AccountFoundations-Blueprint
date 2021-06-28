#!/bin/bash

ENVIRONMENT='dev'
REGION='us-east-1'
ARTIFACT_BUCKET_NAME='artifactsourcebucket'
SOURCE_BUCKET_NAME='accountsourcebucket'

function show_usage (){
  printf "Usage: $0 [options [parameters]]\n"
  printf "\n"
  printf "Options:\n"
  printf " -e|--env [env_name], Environment name (default: dev)\n"
  printf " -r|--region [region_name], Region name (default: us-east-1)\n"
  printf " -a|--artifact [artifact_bucket], Artifact bucket name (default: artifactsourcebucket)\n"
  printf " -s|--source [source_bucket], Source bucket name (default: accountsourcebucket)\n"
  printf " -h|--help, Print help\n"

return 0
}

while [ ! -z "$1" ];do
  case "$1" in
        -h|--help)
          show_usage
          exit
          ;;
        -e|--env)
          shift
          ENVIRONMENT="$1"
          ;;
        -r|--region)
          shift
          REGION="$1"
          ;;
        -a|--artifact)
          shift
          ARTIFACT_BUCKET_NAME="$1"
          ;;
        -s|--source)
          shift
          SOURCE_BUCKET_NAME="$1"
          ;;
        *)
      echo "Incorrect input provided"
      show_usage
      exit
  esac
shift
done

echo "Environment name is ${ENVIRONMENT}"
echo "Region is ${REGION}"
echo "Artifact bucket name is ${ARTIFACT_BUCKET_NAME}"
echo "Source bucket name is ${SOURCE_BUCKET_NAME}"

AWS_DEFAULT_REGION=${REGION} aws cloudformation deploy \
  --stack-name "account-foundations-service-catalog-${ENVIRONMENT}" \
  --template-file pipeline/Service_Catalog_Pipeline_CFT.yml \
  --parameter-overrides Environment=${ENVIRONMENT} ArtifactBucketName=${ARTIFACT_BUCKET_NAME} \
  --capabilities CAPABILITY_NAMED_IAM 

CODEBUILD_REPO_NAME=$(AWS_DEFAULT_REGION=${REGION} aws cloudformation describe-stacks \
  --stack-name "account-foundations-service-catalog-${ENVIRONMENT}" \
  --query 'Stacks[0].Outputs[?OutputKey==`AccountRepoName`].OutputValue' \
  --output text)

AWS_DEFAULT_REGION=${REGION} aws cloudformation deploy \
  --stack-name "account-foundations-codebuild-${ENVIRONMENT}" \
  --template-file pipeline/Pipeline_CodeBuilds.yml \
  --parameter-overrides Environment=${ENVIRONMENT} ArtifactBucketName=${ARTIFACT_BUCKET_NAME} SourceBucketName=${SOURCE_BUCKET_NAME} \
  --capabilities CAPABILITY_NAMED_IAM 

git push codecommit::${REGION}://${CODEBUILD_REPO_NAME} --all

mkdir -p lambda_build
(cd lambda_src; zip -r ../lambda_build/pipeline-account-${ENVIRONMENT}.zip .)

aws s3 sync . s3://${SOURCE_BUCKET_NAME}/
