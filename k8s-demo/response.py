"""
GPT-in-a-Box Streamlit App
This module defines a Streamlit app for interacting with different Large Language models.
"""

import json
import time
import requests


class GetResponse(object):
    def __init__(self, args):
        self.deployment_config = args

    def generate_response(self, input_text):
        """
        Generates a response from the LLM based on the given prompt.
        Parameters:
        - prompt_input (str): The input prompt for generating a response.
        Returns:
        - str: The generated response.
        """
        input_prompt = self.get_json_format_prompt(input_text)
        url = f"http://{self.deployment_config['ingress_host']}:{self.deployment_config['ingress_port']}/v2/models/{self.deployment_config['selected_model']}/infer"
        headers = {"Host": self.deployment_config['service_hostname'], "Content-Type": "application/json; charset=utf-8"}
        try:
            start = time.perf_counter()
            response = requests.post(url, json=input_prompt, timeout=600, headers=headers)
            request_time = time.perf_counter() - start
            print(request_time)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            print("Error in requests: ", url)
            return ""
        output_dict = json.loads(response.text)
        output = output_dict["outputs"][0]["data"][0]
        return output


    def generate_chat_response(self, input_prompt):
        """
        Generates a chat-based response by including the chat history in the input prompt.
        Parameters:
        - prompt_input (str): The user-provided prompt.
        Returns:
        - str: The generated chat-based response.
        """
        # Used [INST] and <<SYS>> tags in the input prompts for LLAMA 2 models.
        # These are tags used to indicate different types of input within the conversation.
        # "INST" stands for "instruction" and used to provide user queries to the model.
        # "<<SYS>>" signifies system-related instructions and used to prime the
        # model with context, instructions, or other information relevant to the use case.

        if selected_model == "tiny-llama":
            string_dialogue = (
                "<|system|>"
                "You are a helpful assistant.</s>"
            )
        else:
            string_dialogue = (
                "[INST] <<SYS>> You are a helpful assistant. "
                " You answer the question asked by 'User' once"
                " as 'Assistant'. <</SYS>>[/INST]" + "\n\n"
            )

        for dict_message in st.session_state.messages[:-1]:
            if dict_message["role"] == "user":
                if selected_model == "tiny-llama":
                    string_dialogue += "<|user|>\n " + dict_message["content"] + "</s>" 
                else:
                    string_dialogue += "User: " + dict_message["content"] + "[/INST]" + "\n\n"
            else:
                if selected_model == "tiny-llama":
                    string_dialogue += "<|assistant|>\n"
                else:
                    string_dialogue += (
                        "Assistant: " + dict_message["content"] + " [INST]" + "\n\n"
                    )
        if selected_model == "tiny-llama":
            string_dialogue += "<|user|>\n " + f"{input_prompt}" + "\n\n"
            input_text = f"{string_dialogue}" + "\n\n" + "<|assistant|>\n"
        else:
            string_dialogue += "User: " + f"{input_prompt}" + "\n\n"
            input_text = f"{string_dialogue}" + "\n\n" + "Assistant: [/INST]"

        output = self.generate_response(input_text)
        # Generation failed
        if len(output) <= len(input_text):
            return ""
        #print(f"\nInput: {input_text}")
        #print(f"\nOutput: {output}")

        # Tiny Llama Specific
        if selected_model == "tiny-llama":
            # We want the portion of text after the second instance of <|assistant|> in the output
            substring = "<|assistant|>"
            first_index = output.find(substring)
            if first_index != -1:
                second_index = output.find(substring, first_index + 1)
                if second_index != -1:
                    response = output[second_index + len(substring):]
                    #print(f"\nResponse: {response}")
            else:
                st.error("Output not in expected format.")
        else:
            response = output[len(input_text) :]

        return response


    def get_json_format_prompt(self, prompt_input):
        """
        Converts the input prompt into the JSON format expected by the LLM.
        Parameters:
        - prompt_input (str): The input prompt.
        Returns:
        - dict: The prompt in JSON format.
        """
        data = [prompt_input]
        data_dict = {
            "id": "1",
            "inputs": [
                {"name": "input0", "shape": [-1], "datatype": "BYTES", "data": data}
            ],
        }
        return data_dict

