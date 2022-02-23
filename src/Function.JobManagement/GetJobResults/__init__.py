import json
import logging
import os
import datetime

from urllib.parse import urlparse
import azure.functions as func
from azure.storage.blob import BlobClient

from shared_code import knapsack, blobaccess


def main(event: func.EventGridEvent):
    result = json.dumps({
        'id': event.id,
        'data': event.get_json(),
        'topic': event.topic,
        'subject': event.subject,
        'event_type': event.event_type,
    })

    logging.info('Python EventGrid trigger processed an event: %s', result)

    # get the URL of the blob that triggered this function
    resultsBlobUrl = event.get_json().get('url')
    logging.info('Uploaded blob URL: %s', resultsBlobUrl)

    # extract the job ID
    u = urlparse(resultsBlobUrl)
    jobId = os.path.dirname(u.path)[5:]
    logging.info('Job Id: %s', jobId)

    receiptDataUrl = u.scheme + "://" + u.hostname + "/optimization-problems/" + jobId
    receiptData = blobaccess.downloadBlobContent(receiptDataUrl)

    receiptData["time_of_job_completion"] = str(datetime.datetime.now())

    problemDataUrl = receiptData.get("problem_data_blob_url")
    u = urlparse(problemDataUrl)
    problemDataBlob = os.path.basename(u.path)
    inputProblem = blobaccess.downloadBlobContent(problemDataUrl)

    inputProblemType = inputProblem.get("problem").get("type")
    inputProblemData = inputProblem.get("problem").get("data")

    resultRawData = blobaccess.downloadBlobContent(resultsBlobUrl)

    resultData = []

    # depending on the problem type extract business solution from job result
    if inputProblemType == "knapsack":
        resultData = knapsack.extractSolution(inputProblemData, resultRawData)

    solutionData = {}
    solutionData["receipt"] = receiptData
    solutionData["result"] = resultData

    blobaccess.uploadBlobContent("optimization-problems", problemDataBlob + "-solution", json.dumps(solutionData))
    blobaccess.deleteBlob(receiptDataUrl)