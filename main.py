import os
import sys
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from github import Github, Auth

from langchain.chat_models import AzureChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from issue_examples import DEFAULT_ISSUE_BODY, DEFAULT_BUG_BODY

# Uncomment to debug:
import langchain
langchain.debug = True


BING_URL = "https://api.bing.microsoft.com/v7.0/search"


def run_agent(issue_body, repo_issues=None):

    simple_prompt = PromptTemplate.from_template(
    """
    In this task, you will be provided with a description of a Github Issue that was opened in a repository of Terraform modules for Azure services.
    Based on the provided description, you're asked to create a specific comment in response to the issue.
    There are two scenarios:
    - If the issue is a bug report, your task is to thoroughly analyze the description.
      Check if it contains all the necessary information such as the steps to reproduce the bug, the expected and actual results, and the environment in which the bug occurred.
      If all these details are already present, you should proceed to acknowledge the bug report and possibly provide initial troubleshooting steps or confirm that the issue is being looked into.
      However, if any of these crucial details are missing from the description, you need to politely request the reporter to provide the missing information to help in the bug investigation process.
    - If the issue is a feature request, you need to check whether the corresponding feature in Azure is still in the preview phase or not.

    You should then write your response as a GitHub comment. The response should be the exact comment you would post on GitHub, signed off as "GitHub AI Issue Assistant".

    For instance, if the issue is about a feature request that is still in private preview in Azure, your comment might look something like this:

    "Hello, 

    Thanks for opening this issue. 

    I have searched on bing and found that the feature you are requesting is still in private preview. As soon as the feature is promoted to GA we will act on it.
    Thank you for your patience. 

    GitHub AI Issue Assistant"

    Here is the Github Issue description: 
    ```{issue_body}```

    To provide related issues, please include them at the end of your comment before signing off. Only include related issues and avoid adding any unrelated ones. 
    A related issue should be one that is similar to the current by referring to the same Azure service or feature. If you are not sure, you can skip this step.
    For each related issue, please provide the issue number and name and link it to the issue on GitHub using the following format:
    [0001 - Support for AKS API Server VNet Integration](https://github.com/OWNER/REPOSITORY/issues/ISSUE_NUMBER)

    OWNER/REPOSITORY is {repository} and ISSUE_NUMBER is {issue_number}

    List of possible related issues:
    ```{repo_issues}```

    """  # noqa: E501
    )

    llm = AzureChatOpenAI(
        openai_api_base=os.environ["INPUT_OPENAI_API_BASE"],
        openai_api_version="2023-07-01-preview",
        deployment_name="gpt4",
        openai_api_key=os.environ["INPUT_OPENAI_API_KEY"],
        openai_api_type="azure",
        temperature=0,
    )

    bing_key = os.environ["INPUT_BING_SUBSCRIPTION_KEY"]

    tools = load_tools(
        ["bing-search"],
        llm,
        bing_subscription_key=bing_key,
        bing_search_url=BING_URL
    )

    agent = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True
    )
    # temporary fix, remove backticks that confuse the model
    # issue_body = issue_body.replace("```", "")

    result = agent.run(simple_prompt.format(issue_body=issue_body, repo_issues=repo_issues, repository=os.environ["GITHUB_REPOSITORY"], issue_number=os.environ["INPUT_ISSUE_NUMBER"]))
    return result


def run_github_action():
    issue_number = os.environ["INPUT_ISSUE_NUMBER"]
    repository = os.environ["GITHUB_REPOSITORY"]

    print(f"Processing: Issue {issue_number} of {repository}")

    auth = Auth.Token(os.environ["INPUT_REPO-TOKEN"])
    github = Github(auth=auth)
    repo = github.get_repo(repository)
    issue = repo.get_issue(number=int(issue_number))
    repo_issues = repo.get_issues(state="all", sort="created", direction="desc")
    repo_issues = [f"- {i.number} - {i.title}" for i in repo_issues if i.number != issue.number]

    response = run_agent(issue.body, repo_issues)

    issue.create_comment(response)


def run_locally():
    # Load the .env file
    load_dotenv()

    # Run the chain locally with default issue body
    print("Running locally with default issue body")
    response = run_agent(DEFAULT_ISSUE_BODY)
    print(response)

    # Run the chain locally with default bug body
    print("Running locally with default bug body")
    response = run_agent(DEFAULT_BUG_BODY)
    print(response)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        run_locally()
    else:
        run_github_action()
