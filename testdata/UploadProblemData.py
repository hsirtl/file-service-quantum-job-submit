import json
import os
import sys

from azure.storage.blob import BlobClient

if len(sys.argv) < 2:
    print ("Please pass the name of a problem json file as parameter.")
else:
    problemFileName = str(sys.argv[1])

    connection_string = "[YOUR_AZURE_STORAGE_CONNECTION_STRING]"
    blobClient = BlobClient.from_connection_string(conn_str=connection_string, container_name="optimization-problems", blob_name=problemFileName)

    try:
        with open(problemFileName,"rb") as f:
            blobClient.upload_blob(f)
            print('{} successfully uploaded.'.format(problemFileName))

    except Exception as e:
        print(e)
