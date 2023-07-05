import os
from github import Github
from github import Auth
import openai


def get_completion(prompt, model="gpt-35-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        engine="gpt-35-turbo",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]


def main():
    openai.api_type = "azure"
    openai.api_key = os.environ["INPUT_OPENAI_API_KEY"]
    openai.api_base = os.environ["INPUT_OPENAI_API_BASE"]
    openai.api_version = "2023-05-15"
    issuenumber = os.environ["INPUT_ISSUE_NUMBER"]
    repository = os.environ["GITHUB_REPOSITORY"]
    
    print(f'Processing: Issue {issuenumber} of {repository}')
    print(f'baseurl: {openai.api_base}')

    auth = Auth.Token(os.environ["INPUT_REPO-TOKEN"])
    g = Github(auth=auth)
    repo = g.get_repo(repository)
    issue = repo.get_issue(number=int(issuenumber))
    # Create a langchain agent:

    prompt = f"""Make a short summary of the following GitHub issue:\
          ```{issue.body}```"""
    response = get_completion(prompt)
    issue.create_comment(response)


if __name__ == "__main__":
    main()
