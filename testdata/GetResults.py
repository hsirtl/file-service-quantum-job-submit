import json
import os
import sys
from time import sleep

from azure.storage.blob import BlobClient

def downloadBlobContent(blobContainer, blobName, timeout):
    connection_string = "[YOUR_AZURE_STORAGE_CONNECTION_STRING]"
    blob = BlobClient.from_connection_string(conn_str=connection_string, container_name=blobContainer, blob_name=blobName)

    for i in range(timeout):
        if (not blob.exists()):
            print('.', end='', flush=True)
            sleep(1)
        else:
            break
    
    streamdownloader = blob.download_blob()
    inputBlobData = json.loads(streamdownloader.readall())

    return inputBlobData

if len(sys.argv) < 2:
    print ("Please pass the name of a problem json file as parameter.")
else:
    problemFileName = str(sys.argv[1])
    problemBlob = downloadBlobContent("optimization-problems", problemFileName, 10)
    solutionBlob = downloadBlobContent("optimization-problems", problemFileName + "-solution", 100)

    # Process the solution
    totalWeight=0
    totalCost=0
    itemsList=[]
    for item in solutionBlob.get('result'):
        totalWeight += int(item.get('weight'))
        totalCost += int(item.get('cost'))
        itemsList.append(str(item.get('id')))

    # Process the problem statement
    print("\n{:>8} {:>8} {:>8}".format('Id', 'Weight', 'Cost'))
    print("-------- -------- -------- -")
    for item in problemBlob.get("problem").get("data").get('items'):
        if (str(item.get('id')) in itemsList):
            print("\33[33m{:>8} {:>8} {:>8} +\33[0m".format(item.get('id'), item.get('weight'), item. get('cost')))
        else:
            print("{:>8} {:>8} {:>8}".format(item.get('id'), item.get('weight'), item. get('cost')))
    print("----------------------------")
    print("Total weight   :  {:>8}".format(totalWeight))
    print("Total cost     :  {:>8}".format(totalCost))
    print("Weight limit   :  {:>8}".format(str(problemBlob.get("problem").get("data").get("weight"))))
    print("----------------------------")
    print("Number of items:  {:>8}".format(len(problemBlob.get("problem").get("data").get('items'))))
    print("Number of terms:  {:>8}".format(solutionBlob.get('receipt').get('no_of_terms')))
