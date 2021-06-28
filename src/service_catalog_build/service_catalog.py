import boto3
import os

####
#           This file reads in the validated information for the requested products and either creates 
#           or updates the product on Service Catalog with the appropriate version
###


# creates required boto3 client
ssm=boto3.client('ssm','us-east-1')


#Determines the version of the updated product
def Version():
    version_list=ssm.get_parameter(Name='UPDATE_VERSION')
    versions=eval(version_list['Parameter']['Value'])
    return versions

#Creates a new product on Service Catalog
def CreateProduct(products, version=0.1, portfolio=os.environ['CATALOG_PORTFOLIO'], source_bucket_name=os.environ['SOURCE_BUCKET_NAME']):
    for product in products:
        os.system(f"echo creating {product} product")
        os.system(f"aws cloudformation create-stack --stack-name {product} --template-body file://service_catalog_cft.yml --parameters ParameterKey=WhichInstance,ParameterValue={product} ParameterKey=CatalogPortfolio,ParameterValue={portfolio} ParameterKey=SourceBucketName,ParameterValue={source_bucket_name} ParameterKey=Version,ParameterValue={version}")

#Updates and existing product on Service Catalog
def UpdateProduct(products, versions=Version(), portfolio=os.environ['CATALOG_PORTFOLIO'], source_bucket_name=os.environ['SOURCE_BUCKET_NAME']): 
    for idx,product in enumerate(products):
        os.system(f"echo updating {product} product")
        os.system(f"aws cloudformation update-stack --stack-name {product} --template-body file://service_catalog_cft.yml --parameters ParameterKey=WhichInstance,ParameterValue={product} ParameterKey=CatalogPortfolio,ParameterValue={portfolio} ParameterKey=SourceBucketName,ParameterValue={source_bucket_name} ParameterKey=Version,ParameterValue={versions[idx]}")

if __name__ == '__main__':
    #collects version numbers for products that need to be updated
    versions=Version()

    #collects list of products to update and products to create from parameter store
    new_products=eval(ssm.get_parameter(Name='NEW_PRODUCT_NAME')['Parameter']['Value'])
    update_products=eval(ssm.get_parameter(Name='UPDATE_PRODUCT_NAME')['Parameter']['Value'])
    
    #determines if there are products to create
    if len(new_products)!=0:
        print("Creating Product")
        CreateProduct(products=new_products)
        print("Finished Creating Product")

    #determines if there are products to update
    if len(versions)>0:
        os.system("echo starting to update product")
        UpdateProduct(products=update_products)
        print("finished updating product")
        



    