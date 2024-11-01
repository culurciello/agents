# E. Culurciello
# October 2024
# from: https://github.com/yoheinakajima/ditto

# testing agent to search web and generate documents on search results

import os
# import requests
import trafilatura
import json
import traceback
from time import sleep

# Correctly import the completion function from LiteLLM
from litellm import completion, supports_function_calling

import litellm
litellm.set_verbose=True

# Configuration
MODEL_NAME = os.environ.get('LITELLM_MODEL', 'gpt-4o')  # Default model; can be swapped easily
os.environ['LITELLM_LOG'] = 'DEBUG'

LOG_FILE = "agent_log.json"

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize progress tracking
progress = {
    "status": "idle",
    "iteration": 0,
    "max_iterations": 25,
    "output": "",
    "completed": False
}


def create_file(path, content):
    try:
        with open(path, 'x') as f:
            f.write(content)
        return f"Created file: {path}"
    except FileExistsError:
        with open(path, 'w') as f:
            f.write(content)
        return f"Updated file: {path}"
    except Exception as e:
        return f"Error creating/updating file {path}: {e}"

def update_file(path, content):
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"Updated file: {path}"
    except Exception as e:
        return f"Error updating file {path}: {e}"


    
def search_web(web_url):
    # search web for answers
    # data = requests.get(web_url).text
    downloaded = trafilatura.fetch_url(web_url)
    data = trafilatura.extract(downloaded)
    # print(web_url, data)
    return f"Searched web: {web_url} and obtained: {data}"


def task_completed():
    progress["status"] = "completed"
    progress["completed"] = True
    return "Task marked as completed."


# Function to log history to file
def log_to_file(history_dict):
    try:
        with open(LOG_FILE, 'w') as log_file:
            json.dump(history_dict, log_file, indent=4)
    except Exception as e:
        pass  # Silent fail

# Available functions for the LLM
available_functions = {
    "create_file": create_file,
    "update_file": update_file,
    "search_web": search_web,
    "task_completed": task_completed
}

# Define the tools for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Creates a new directory at the specified path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to create."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates or updates a file at the specified path with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to create or update."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write into the file."
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_file",
            "description": "Updates an existing file at the specified path with the new content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to update."
                    },
                    "content": {
                        "type": "string",
                        "description": "The new content to write into the file."
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_completed",
            "description": "Indicates that the assistant has completed the task.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Retrieve web from fully-formed http URL to enhance knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "web_url": {
                        "type": "string",
                        "description": "The URL to search on the web."
                    }
                },
                "required": ["web_url"]
            }
        }
    }
]

def run_main_loop(user_input):
    # Reset the history_dict for each run
    history_dict = {
        "iterations": []
    }

    if not supports_function_calling(MODEL_NAME):
        progress["status"] = "error"
        progress["output"] = "Model does not support function calling."
        progress["completed"] = True
        return "Model does not support function calling."

    max_iterations = progress["max_iterations"]  # Prevent infinite loops
    iteration = 0

    # Updated messages array with enhanced prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert web crawling agent and research editor. You are tasked to generate a document based on the user's description."
                "Before starting, carefully plan out all the files, directories needed. "
                "Follow these steps:\n"
                "1. **Understand the Requirements**: Analyze the user's input to fully understand the research needed.\n"
                "2. **Plan the Research**: Use the web browser to list possible web sources that need to be considered. Do not replicate searches.\n"
                "3. **Implement Step by Step**: For each web source, run a search, read the article and summarize it. Ensure each step is thoroughly completed before moving on.\n"
                "4. **Review and Refine**: Once you have all the summaries, provide a final summary.\n"
                "5. **Ensure Completeness**: Do not leave any search incomplete. You need all data to run your research.\n"
                "6. **Finalize**: Once everything is complete, write the report in a markdown file called 'output.md', then call `task_completed()` to finish.\n\n"
                "Constraints and Notes:\n"
                "- The report must have the following sections: Summary, Report, Conclusions, Reference list`.\n"
                "- Summary: in approximately 100 word provide a summary of the overall document.\n"
                "- Report: in approximately 1000 word provide the body of the report.\n"
                "- Conclusions: in approximately 100 word draw your conclusions and prospects.\n"
                "- Reference List: provide a complete list of all website searched for this research.\n"
                "- Handle any errors internally and attempt to resolve them before proceeding.\n\n"
                "- Remember to write the output file 'output.md' in markdown format.\n"
                "Available Tools:\n"
                "- `create_file(path, content)`: Create or overwrite a file with content.\n"
                "- `update_file(path, content)`: Update an existing file with new content.\n"
                "- `search_web(web_url)`: Retrieve website data to enhance knowledge.\n"
                "- `task_completed()`: Call this when the application is fully built and ready.\n\n"
                "Remember to think carefully at each step, ensuring the application is complete, functional, and meets the user's requirements."
            )
        },
        {"role": "user", "content": user_input},
        {"role": "system", "content": f"History:\n{json.dumps(history_dict, indent=2)}"}
    ]

    output = ""

    while iteration < max_iterations:
        progress["iteration"] = iteration + 1
        # Create a new iteration dictionary for each loop
        current_iteration = {
            "iteration": iteration + 1,  # Start from 1
            "actions": [],
            "llm_responses": [],
            "tool_results": [],
            "errors": []
        }
        history_dict['iterations'].append(current_iteration)

        try:
            response = completion(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            if not response.choices[0].message:
                error = response.get('error', 'Unknown error')
                current_iteration['errors'].append({'action': 'llm_completion', 'error': error})
                log_to_file(history_dict)
                sleep(5)
                iteration += 1
                continue

            # Extract LLM response and append to current iteration
            response_message = response.choices[0].message
            content = response_message.content or ""
            current_iteration['llm_responses'].append(content)

            # Prepare the output string
            output += f"\n<h2>Iteration {iteration + 1}:</h2>\n"

            tool_calls = response_message.tool_calls

            if tool_calls:
                output += "<strong>Tool Call:</strong>\n<p>" + content + "</p>\n"
                messages.append(response_message)

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions.get(function_name)

                    if not function_to_call:
                        error_message = f"Tool '{function_name}' is not available."
                        current_iteration['errors'].append({
                            'action': f'tool_call_{function_name}',
                            'error': error_message,
                            'traceback': 'No traceback available.'
                        })
                        continue

                    try:
                        function_args = json.loads(tool_call.function.arguments)

                        # Call the tool function and store result
                        function_response = function_to_call(**function_args)

                        # Append the tool result under the current iteration
                        current_iteration['tool_results'].append({
                            'tool': function_name,
                            'result': function_response
                        })

                        # Include tool result in the output
                        output += f"<strong>Tool Result ({function_name}):</strong>\n<p>{function_response}</p>\n"

                        # Add tool call details to the conversation
                        messages.append(
                            {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": function_response}
                        )

                        # Check if the assistant called 'task_completed' to signal completion
                        if function_name == "task_completed":
                            progress["status"] = "completed"
                            progress["completed"] = True
                            output += "\n<h2>COMPLETE</h2>\n"
                            progress["output"] = output
                            log_to_file(history_dict)
                            return output  # Exit the function

                    except Exception as tool_error:
                        error_message = f"Error executing {function_name}: {tool_error}"
                        current_iteration['errors'].append({
                            'action': f'tool_call_{function_name}',
                            'error': error_message,
                            'traceback': traceback.format_exc()
                        })

                # Second response to include the tool call
                second_response = completion(
                    model=MODEL_NAME,
                    messages=messages
                )
                if second_response.choices and second_response.choices[0].message:
                    second_response_message = second_response.choices[0].message
                    content = second_response_message.content or ""
                    current_iteration['llm_responses'].append(content)
                    output += "<strong>LLM Response:</strong>\n<p>" + content + "</p>\n"
                    messages.append(second_response_message)
                else:
                    error = second_response.get('error', 'Unknown error in second LLM response.')
                    current_iteration['errors'].append({'action': 'second_llm_completion', 'error': error})

            else:
                output += "<strong>LLM Response:</strong>\n<p>" + content + "</p>\n"
                messages.append(response_message)

            progress["output"] = output

        except Exception as e:
            error = str(e)
            current_iteration['errors'].append({
                'action': 'main_loop',
                'error': error,
                'traceback': traceback.format_exc()
            })

        iteration += 1
        log_to_file(history_dict)
        sleep(2)

    if iteration >= max_iterations:
        progress["status"] = "completed"

    progress["completed"] = True
    progress["status"] = "completed"

    return output

if __name__ == '__main__':
    prompt = "Search the web for at least 5 news articles about Vinicius Jr. soccer player and report a summary of the research."
    run_main_loop(prompt)
    print("Done")