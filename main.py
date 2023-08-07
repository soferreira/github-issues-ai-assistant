import os
import sys
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from github import Github, Auth

from langchain.llms.openai import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# Uncomment to debug:
# import langchain
# langchain.debug = True

from issue_examples import DEFAULT_ISSUE_BODY, DEFAULT_BUG_BODY

bingurl = "https://api.bing.microsoft.com/v7.0/search"


def runagent(issue_body):
    simpleprompt = PromptTemplate.from_template(
        """
        I will provide you a Github Issue opened in a repository of Terraform modules for Azure. You have to write a comment on the issue. The comment should be one of the following:
        1. If the issue is reporting a bug, you can analyse its description and check if all the information to reproduce the bug is present. If not, you can ask the reporter to provide more information.
        2. If the issue is requesting a new feature for the Terraform module, you can analyse the issue description and tell if the corresponding Azure feature is in preview or not.

        Here is the description: ```{issue_body}```

        Your output must be only the GitHub comment as it will appear on GitHub. Sign your comment with the name GitHub AI Issue Assistant.
        """
    )

    llm = AzureChatOpenAI(
        openai_api_base=os.environ["INPUT_OPENAI_API_BASE"],
        openai_api_version="2023-07-01-preview",
        deployment_name="gpt-35-turbo-16k",
        openai_api_key=os.environ["INPUT_OPENAI_API_KEY"],
        openai_api_type="azure",
        temperature=0,
    )

    bing_key = os.environ["INPUT_BING_SUBSCRIPTION_KEY"]

    tools = load_tools(
        ["bing-search"], llm, bing_subscription_key=bing_key, bing_search_url=bingurl
    )

    agent = initialize_agent(
        tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False
    )

    # issue_body = issue_body.replace("```", "")  # temporary fix, remove backticks that confuse the model

    result = agent.run(simpleprompt.format(issue_body=issue_body))
    return result


def run_github_action():
    issue_number = os.environ["INPUT_ISSUE_NUMBER"]
    repository = os.environ["GITHUB_REPOSITORY"]

    print(f"Processing: Issue {issue_number} of {repository}")

    auth = Auth.Token(os.environ["INPUT_REPO-TOKEN"])
    github = Github(auth=auth)
    repo = github.get_repo(repository)
    issue = repo.get_issue(number=int(issue_number))

    response = runagent(issue.body)
    issue.create_comment(response)


def run_locally():
    # Load the .env file
    load_dotenv()

    # Run the chain locally with default issue body
    print("Running locally with default issue body")
    response = runagent(DEFAULT_ISSUE_BODY)
    print(response)

    # Run the chain locally with default bug body
    print("Running locally with default bug body")
    response = runagent(DEFAULT_BUG_BODY)
    print(response)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        run_locally()
    else:
        run_github_action()
