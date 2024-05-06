import requests

def analyze_text(combined_messages):
    

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": "gpt-4-turbo-preview",
        "max_tokens": 4000,  # Increased token limit for larger input
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"""
                Task: Evaluate the developer's performance based on their commit messages.

Input:

Commit Messages: {combined_messages} (This will be replaced with the combined commit messages from Bitbucket.)
Output Structure:

Commit Message Quality Rating: [number of ⭐⭐⭐⭐⭐]
Summary:
overall Commit Message Quality Rating: [Evaluate the overall quality of the commit messages, considering technical accuracy, clarity, and completeness]
Areas for Improvement in Commit Messages: [Identify areas such as lack of detailed explanations, inconsistent formatting, or missing references to related issues.]
Recommendations:
Provide suggestions for improving commit message quality, such as using descriptive language, referencing relevant issues or tickets, and adhering to a consistent format.

                
                """
            }
        ]
    }

    url = "https://api.openai.com/v1/chat/completions"

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.ok:
            main_content = response.json()["choices"][0]["message"]["content"]
            return main_content
        else:
            print(f"Error: {response.status_code} - {response.reason}")

    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")

# Example usage
# commit_messages = [commit['message'] for commit in commits_data if commit['message']]
# overall_analysis = analyze_commits(commit_messages)
# print(overall_analysis)


def analyze_pr(user, comments):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": "gpt-4-turbo-preview",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"Evaluate the developer's performance by analyzing comment quality in their pull requests. Analyze {user}'s pull requests comments on a repository and give a rating from 1-5 based on the comments. Consider the following criteria: 1. Positive comments: like +1, bravo, nice, this code looks very good, etc. 2. Code suggestions in comments: Some alternate implementation of current code; this should be considered as neutral. 3. Change Request: This could be considered as negative or if a reviewer says there is a change in requirement, then neutral. Input: User - {user} Comments - {comments} Output Structure: Developer Performance Rating: [number of ⭐⭐⭐⭐⭐]. Summarize the overall comment quality."
            }
        ]
    }

    url = "https://api.openai.com/v1/chat/completions"

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.ok:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Error: {response.status_code} - {response.reason}")

    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")