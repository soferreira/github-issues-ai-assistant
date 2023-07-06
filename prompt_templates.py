prompt_templates = {
    "bug": """I will provide you a Github Issue opened in a repository. The issue is reporting a bug. You can analyse its description and check if all the information to reproduce the bug is present. If not, you can ask the reporter to provide more information. Here is the description: {input}""",
    "feature": """I will provide you a Github Issue opened in a repository. The issue is requesting a new feature. You can analyse the issue description and tell if the feature is in preview or not. Here is the description: {input}""",
}

prompt_infos = [
    {
        "name": "bug",
        "prompt_template": prompt_templates["bug"],
        "description": "Good for analyse a bug.",
    },
    {
        "name": "feature",
        "prompt_template": prompt_templates["feature"],
        "description": "Good for analyse feature requests.",
    },
]


MULTI_PROMPT_ROUTER_TEMPLATE = """Given a raw text input to a \
    language model select the model prompt best suited for the input. \
    You will be given the names of the available prompts and a \
    description of what the prompt is best suited for. \
    You may also revise the original input if you think that revising\
    it will ultimately lead to a better response from the language model.

    << FORMATTING >>
    Return a markdown code snippet with a JSON object formatted to look like:
    ```json
    {{{{
        "destination": string \ name of the prompt to use or "DEFAULT"
        "next_inputs": string \ a potentially modified version of the original input
    }}}}
    ```

    REMEMBER: "destination" MUST be one of the candidate prompt \
    names specified below OR it can be "DEFAULT" if the input is not\
    well suited for any of the candidate prompts.
    REMEMBER: "next_inputs" can just be the original input \
    if you don't think any modifications are needed.

    << CANDIDATE PROMPTS >>
    {destinations}

    << INPUT >>
    {{input}}

    << OUTPUT (remember to include the ```json)>>"""
