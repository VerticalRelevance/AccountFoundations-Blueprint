import json
import os
import boto3

### 
#     The path_creation function reads in the information from each product's datafile and determines whether the product needs to be created or updated.  
#     If the product does not exist on Service Catalog, the function adds the path of the template to be tested and then created.
#     If the product exists on Service Catalog, the function adds the path and new version of the template to be tested and then updated

#     The validation function executes cfn-lint and detect-secrets testing on the requested templates
def path_creation():
    #Creates required boto3 clients
    service_catalog = boto3.client('servicecatalog','us-east-1' )
    ssm=boto3.client('ssm','us-east-1')

    #Creates lists of the paths that need to be created/updated
    new_products={'paths':[],'products':[]}
    to_update={'paths':[],'products':[],'versions':[]}

    # a list of the products
    folders=os.listdir('service_catalog_products')

    #counter to iterate through products
    x=0

    #iterates through products
    for t in folders:
        #Removes hidden files from product list
        if not t.startswith('.'):
            #Reads in information from product datafile
            datafile=dict()

            try:
                datafile['RequestType'] = 'Old'
                datafile['Version'] = int(ssm.get_parameter(Name=f'{t}Version')['Parameter']['Value']) + 1
            except:
                datafile['RequestType'] = 'New'
                datafile['Version'] = 0

            #Determines whether existing product needs to be updated
            if datafile['RequestType']=='Old': 
                #Reads product information from service catalog 
                all_products=service_catalog.search_products_as_admin()
                product_info=service_catalog.describe_product_as_admin(Id=all_products['ProductViewDetails'][x]['ProductViewSummary']['ProductId'])
                version=product_info['ProvisioningArtifactSummaries'][0]['Name']

                #Adds new version information to be tested
                if datafile['Version'] != version:   
                    print("this is an old product")
                    path=f'service_catalog_products/{t}/{t}_template.yml' 
                    to_update['paths'].append(path)  # add path to template for testing
                    to_update['versions'].append(str(datafile['Version']))  # add version for updating the product
                    to_update['products'].append(f"{t}")

                #increases counter        
                x+=1

            #Determines if product needs to be created
            if datafile['RequestType']=='New':  
                print("this is a new product")
                #Adds new product information to be tested and created
                path=f'service_catalog_products/{t}/{t}_template.yml'
                new_products['paths'].append(path)  #add path to template for testing
                new_products['products'].append(f"{t}")  #add name of product for creation
                datafile['RequestType']='Old'

            ssm.put_parameter(Name=f'{t}Version',Value=f"{datafile['Version']}", Type='String', Overwrite=True)

    #Puts New product information in Parameter Store
    ssm.put_parameter(Name='NEW_PRODUCT_NAME',Value=f"{new_products['products']}", Type='String', Overwrite=True)
    
    #Puts Updated product information in Parameter Store
    ssm.put_parameter(Name='UPDATE_VERSION',Value=f"{to_update['versions']}", Type='String', Overwrite=True)     
    ssm.put_parameter(Name='UPDATE_PRODUCT_NAME',Value=f"{to_update['products']}", Type='String', Overwrite=True)       
    
    return [new_products, to_update]

    
def validation(new_products, to_update): 
    #executes tests on new products
    if len(new_products['paths'])>=1:
        for idx,path in enumerate(new_products['paths']): 
            os.system(f"echo starting testing on {new_products['products'][idx]}")
            os.system(f"cfn-lint -b {path}")
            os.system(f"detect-secrets scan {path}")
            os.system(f"echo finished testing on {new_products['products'][idx]}")

    #executes tests on updated products
    if len(to_update['paths'])>=1:
        for idx,path in enumerate(to_update['paths']): 
            os.system(f"echo starting testing on {to_update['products'][idx]}")
            os.system(f"cfn-lint -b {path}")
            os.system(f"detect-secrets scan {path}")
            os.system(f"echo finished testing on {to_update['products'][idx]}")    

if __name__=='__main__': 
    #creates list of products to create and list of products to update and executes tests
    newProducts, toUpdate= path_creation()
    validation(new_products=newProducts,to_update=toUpdate)
