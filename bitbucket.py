import requests
from datetime import datetime, timezone
import base64
def encode_credentials(username, app_password):
    """Encode credentials to base64 for Basic Auth."""
    credentials = f"{username}:{app_password}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return encoded_credentials

def fetch_user_commits(owner, repo, username, app_password, start_date, end_date):
    print(f"Fetching changed files for {username} in {owner}/{repo}")
    base_url = "https://api.bitbucket.org/2.0"
    commits_url = f"{base_url}/repositories/{owner}/{repo}/commits"

    encoded_credentials = encode_credentials(username, app_password)
    headers = {"Authorization": f"Basic {encoded_credentials}"}

    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    commits_response = requests.get(
        f"{commits_url}?q=author='{username}' AND date>='{start_datetime.isoformat()}' AND date<='{end_datetime.isoformat()}'", headers=headers)
    commits_response.raise_for_status()

    commits_data = commits_response.json().get('values', [])
    user_changed_files = []

    for commit in commits_data:
        commit_date = datetime.strptime(commit['date'], '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=timezone.utc)
        commit_details = {
            'sha': commit['hash'],
            'message': commit['summary']['raw'],
            'changed_files': [],
            'date': commit['date']
        }

        files_url = f"{base_url}/repositories/{owner}/{repo}/commit/{commit['hash']}"
        files_response = requests.get(files_url, headers=headers)
        files_response.raise_for_status()

        files_data = files_response.json().get('files', [])
        for file_info in files_data:
            file_details = {
                'status': file_info.get('status'),
                'path': file_info.get('path'),
                'patch': file_info.get('patch', 'No patch available')
            }
            commit_details['changed_files'].append(file_details)

        user_changed_files.append(commit_details)

    return user_changed_files

def get_pull_requests(repo_owner, repo_slug, bitbucket_username, bitbucket_app_password, start_date, end_date):
    start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    pull_requests_url = f"https://api.bitbucket.org/2.0/repositories/{repo_owner}/{repo_slug}/pullrequests"
    response = requests.get(pull_requests_url, auth=(bitbucket_username, bitbucket_app_password))
    response.raise_for_status()
    pull_requests_data = response.json()["values"]

    pull_requests = []
    for pull_request_data in pull_requests_data:
        creation_date = datetime.strptime(pull_request_data["created_on"], '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=timezone.utc)
        if start_datetime <= creation_date <= end_datetime:
            pull_request = {
                "title": pull_request_data["title"],
                "state": pull_request_data["state"],
                "comments": []
            }

            comments_url = pull_request_data["links"]["comments"]["href"]
            comments_response = requests.get(comments_url, auth=(bitbucket_username, bitbucket_app_password))
            comments_response.raise_for_status()
            comments_data = comments_response.json()["values"]

            for comment_data in comments_data:
                user = comment_data.get("user", {}).get("display_name", "Unknown")
                content = comment_data.get("content", {}).get("raw", "No content")
                pull_request["comments"].append({"user": user, "content": content})

            pull_requests.append(pull_request)

    return pull_requests