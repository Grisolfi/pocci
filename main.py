from bottle import get, post, request, run
from tool.auth_helper import *
from os import environ as ENV
import requests
import time

def create_check_run(payload, installation_id, repository_full_name):
    endpoint = f'{BASE_URL}/repos/{repository_full_name}/check-runs'
    data = {
        'head_sha': payload.get('check_run') if payload.get('check_run') else payload.get('check_suite').get('head_sha'),
        'accept' : 'application/vnd.github.v3+json',
        'name' : 'My Custom CI Check',
        'status': 'queued'
    }
    response = requests.post(
        auth=InstallAuth(installation_id),
        url=endpoint,
        json=data
    )
    response.raise_for_status()

def initiate_check_run(payload, installation_id, repository_full_name):
    check_run_id = payload['check_run']['id']
    endpoint = f'{BASE_URL}/repos/{repository_full_name}/check-runs/{check_run_id}'
    
    data = {
      'accept' : 'application/vnd.github.v3+json',
      'name' : 'My Custom CI Check',
      'status' : 'in_progress',
      'started_at' : f'{datetime.now().replace(microsecond=0).isoformat()}Z'
    }

    updated_check_run = requests.patch(
        auth=InstallAuth(installation_id),
        url=endpoint,
        json=data
    )
    updated_check_run.raise_for_status()

    print("PROCESSING......")
    time.sleep(30)

    data.update({
        'status': 'completed',
        'conclusion': 'success',
        'completed_at': f'{datetime.now().replace(microsecond=0).isoformat()}Z'
    })

    
    updated_check_run = requests.patch(
        auth=InstallAuth(installation_id),
        url=endpoint,
        json=data
    )
    updated_check_run.raise_for_status()


@post('/event_handler')
def event_handler():
    ghevent = request.headers.get('X-Github-Event')
    print(ghevent, 'received')

    payload = request.json
    installation_id = payload['installation']['id']
    action = payload.get('action')
    repository_full_name = payload['repository']['full_name']

    if ghevent == 'check_suite':
        if action == 'requested' or action == 'rerequested': # Could be also completed
            create_check_run(payload, installation_id, repository_full_name)
    elif ghevent == 'check_run':
        if action == 'created' and str(payload['check_run']['app']['id']) == ENV.get('GH_APPLICATION_ID'):
            initiate_check_run(payload, installation_id, repository_full_name)
        elif action == 'rerequested':
            create_check_run(payload, installation_id, repository_full_name)

if __name__ == '__main__':
    run(host='localhost', port=3000, debug=True)