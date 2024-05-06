import streamlit as st
from bitbucket import fetch_user_commits, get_pull_requests , encode_credentials
from openai import analyze_text, analyze_pr

def main():
    st.title("Bitbucket Analyzer")
    
    target_user = st.text_input("Target User")
    repo_name = st.text_input("Repository Name")
    username = st.text_input("Bitbucket Username")
    app_password = st.text_input("Bitbucket App Password", type="password")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    
    if st.button("Analyze"):
        st.write("Analyzing...")

        # Fetching data and pull requests
        data = fetch_user_commits(target_user, repo_name, username, app_password, start_date, end_date)
        pull_requests = get_pull_requests(target_user, repo_name, username, app_password, start_date, end_date)
        
        analysis_results = []

        # Check if analysis for commit messages has already been done
        commit_analysis_done = any(result['type'] == 'commit' for result in analysis_results)

        # Analyze commit messages only if not already analyzed
        if not commit_analysis_done:
            all_commit_messages = []
            for commit_info in data:
                commit_message = commit_info.get('message', '').strip()
                if commit_message:
                    all_commit_messages.append(commit_message)

            combined_commit_messages = " ".join(all_commit_messages)
            commit_analysis = analyze_text(combined_commit_messages)

            analysis_results.append({
                'type': 'commit',
                'analysis': commit_analysis
            })

            # Display analysis result for commit messages
            
            st.write("---------------")
            st.write("Analysis Results for commits:")
            st.write(commit_analysis)

        # Analyze pull request comments
        all_comments = []
        for pr in pull_requests:
            for comment in pr['comments']:
                all_comments.append(comment['content'])

        pr_analysis = analyze_pr(target_user, '\n'.join(all_comments))
        analysis_results.append({
            'type': 'pull_request',
            'user': target_user,
            'analysis': pr_analysis
        })

        # Display analysis results for pull requests
        
        st.write("---------------")
        st.write("analysis result for pull requests")
        st.write(pr_analysis)

if __name__ == "__main__":
    main()
