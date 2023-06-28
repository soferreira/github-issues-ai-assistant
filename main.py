import os
from github import Github
from github import Auth


def main():
    issuenumber = os.environ["INPUT_ISSUE_NUMBER"]
    print(f'Processing: {issuenumber}')
    auth = Auth.Token(os.environ["INPUT_REPO-TOKEN"])
    g = Github(auth=auth)
    repo = g.get_repo("zioproto/github-issues-ai-assistant")
    issue = repo.get_issue(number=int(issuenumber))
    issue.create_comment("Test")


if __name__ == "__main__":
    main()
