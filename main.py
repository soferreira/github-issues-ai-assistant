import os
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import (
    LLMRouterChain, RouterOutputParser)
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from github import Github
from github import Auth
from prompt_templates import prompt_infos, MULTI_PROMPT_ROUTER_TEMPLATE


def langchain_router_chain(input_prompt):
    llm = AzureChatOpenAI(
        openai_api_base=os.environ["INPUT_OPENAI_API_BASE"],
        openai_api_version="2023-05-15",
        deployment_name="gpt-35-turbo",
        openai_api_key=os.environ["INPUT_OPENAI_API_KEY"],
        openai_api_type="azure",
        temperature=0,
    )

    destination_chains = {}

    for p_info in prompt_infos:
        prompt = ChatPromptTemplate.from_template(
            template=p_info["prompt_template"]
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        destination_chains[p_info["name"]] = chain

    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = "\n".join(destinations)

    default_prompt = ChatPromptTemplate.from_template("{input}")
    default_chain = LLMChain(llm=llm, prompt=default_prompt)

    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
        destinations=destinations_str
    )

    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser(),
    )

    router_chain = LLMRouterChain.from_llm(llm, router_prompt)

    multi_prompt_chain = MultiPromptChain(
        router_chain=router_chain,
        destination_chains=destination_chains,
        default_chain=default_chain, verbose=True
    )

    response = multi_prompt_chain.run(input_prompt)
    print(response)

    return response


def main():

    issue_number = os.environ["INPUT_ISSUE_NUMBER"]
    repository = os.environ["GITHUB_REPOSITORY"]

    print(f'Processing: Issue {issue_number} of {repository}')

    auth = Auth.Token(os.environ["INPUT_REPO-TOKEN"])
    github = Github(auth=auth)
    repo = github.get_repo(repository)
    issue = repo.get_issue(number=int(issue_number))

    response = langchain_router_chain(issue.body)
    issue.create_comment(response)


if __name__ == "__main__":
    main()
