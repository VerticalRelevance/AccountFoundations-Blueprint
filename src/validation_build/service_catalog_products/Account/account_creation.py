#!/usr/local/env python

import boto3
import json
import sys


SC_CLIENT = client = boto3.client('servicecatalog')

def usage():
    print("Usage: {} <param_file.json>".format(sys.argv[0]))

def create_account(prod_id, pa_id, params_file_name):
    params_file = process_params_file(params_file_name)
    params_json = json.loads(params_file)
    res = SC_CLIENT.provision_product(
        ProductId=prod_id,
        ProvisioningArtifactId=pa_id,
        ProvisioningParameters=params_json,
        ProvisionedProductName="CatalogFor{}".format(params_json[4]['Value'])
    )
    print(res)

def get_account_factory_product_id():
    res = SC_CLIENT.search_products(Filters={"FullTextSearch":["AWS Control Tower Account Factory"]})
    return res['ProductViewSummaries'][0]['ProductId']

def get_account_factory_product_artifact_id(product_id):
    res = SC_CLIENT.describe_product(Id=product_id)
    return res['ProvisioningArtifacts'][0]['Id']

def process_params_file(params_file_name):
    with open(params_file_name) as file:
        return file.read()

def main(params_file_name):
    product_id = get_account_factory_product_id()
    pa_id = get_account_factory_product_artifact_id(product_id)
    create_account(product_id, pa_id, params_file_name)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
    else:
        params_file_name = sys.argv[1]
        main(params_file_name)