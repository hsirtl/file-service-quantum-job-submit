import json
import logging
import os
import datetime

from urllib.parse import urlparse
import azure.functions as func

from azure.quantum import Workspace
from azure.quantum.optimization import Problem, ProblemType
from azure.quantum.optimization import SimulatedAnnealing

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

    inputBlobUrl = event.get_json().get('url')
    logging.info('Uploaded blob URL: %s', inputBlobUrl)

    inputProblem = blobaccess.downloadBlobContent(inputBlobUrl)

    # Copy the settings for your workspace below
    workspace = Workspace (
        subscription_id = os.environ["SubscriptionId"],
        resource_group = os.environ["ResourceGroup"],
        name = os.environ["WorkspaceName"],
        location = os.environ["WorkspaceLocation"]
    )

    inputProblemType = inputProblem.get("problem").get("type")
    inputProblemData = inputProblem.get("problem").get("data")

    terms = []

    # Create cost function based on inputBlobData problem description
    if inputProblemType == "knapsack":
        terms = knapsack.createCostFunction(inputProblemData)
    
    problem = Problem(name=inputProblemType, problem_type=ProblemType.pubo, terms=terms)
    solver = SimulatedAnnealing(workspace, timeout=100, seed=22)
    job = solver.submit(problem)

    logging.info('Job successfully submitted. Job Id: %s', str(job.id))

    receiptData = {}
    receiptData["problem_data_blob_url"] = inputBlobUrl
    receiptData["problem_type"] = inputProblemType
    receiptData["job_id"] = str(job.id)
    receiptData["no_of_terms"] = str(len(terms))
    receiptData["time_of_job_submission"] = str(datetime.datetime.now())

    u = urlparse(inputBlobUrl)
    inputBlobContainer = os.path.dirname(u.path)[1:]
    blobaccess.uploadBlobContent(inputBlobContainer, str(job.id), json.dumps(receiptData))