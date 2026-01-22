from openai import OpenAI, AuthenticationError, OpenAIError
import joblib

evaluation_criteria_dict = {
    "Coherence (Logical)": {
        "description": "Logical response forms a narrative without contradictions. E.g., Is the response well-structured in terms of content?",
        "scoring": {
            5: "clearly structured line of reasoning; individual statements are understandable and without contradictions",
            4: "between 5 and 3",
            3: "partly structured line of reasoning; individual statements are confusing or contradicting",
            2: "between 3 and 1",
            1: "unstructured/missing line of reasoning; confusing or contradicting statements"
        }
    },
        "Coherence (Stylistic)": {
        "description": "Uniform language use E.g. Does the writing tone stay consistent? Use of visual text formatting E.g. is highlighting or bullet points used?",
        "scoring": {
            5: "uniform language use; appropriate use of paragraphs and formatting (highlighting, bullet points etc.)",
            4: "between 5 and 3",
            3: "uniform language use; structured with paragraphs, formatting (highlighting, bullet points etc.) is missing or lacking",
            2: "between 3 and 1",
            1: "no uniform language use and/or no clear sections or paragraphs, no formatting (highlighting, bullet points etc.)"
        }
    },
    "Correctness (User Intent)": {
        "description": "Information aligns with user's thematic information need (statement fits user intent)",
        "scoring": {
            5: "response fits the thematic context of the prompt",
            4: "between 5 and 3",
            3: "response fits the thematic context of the prompt partially",
            2: "between 3 and 1",
            1: "response fails to fit the thematic context of user's needs/prompt"
        }
    },
    "Consistency (Language)": {
        "description": "Consistent language use. E.g., “Does the writing tone stay consistent?”",
        "scoring": {
            5: "consistent language use",
            4: "between 5 and 3",
            3: "partially consistent language use",
            2: "between 3 and 1",
            1: "inconsistent language use"
        }
    },
    "Correctness (Language)": {
        "description": "Lexically and grammatically correct language",
        "scoring": {
            5: "completely correct language (lexically and grammatically)",
            4: "between 5 and 3",
            3: "partially correct language (lexically and grammatically)",
            2: "between 3 and 1",
            1: "incorrect language (lexically and grammatically)"
        }
    },
    "Clarity (Language)": {
        "description": "Concise, comprehensible, user- accessible and well - spoken language",
        "scoring": {
            5: "clear language / meeting conversation style",
            4: "between 5 and 3",
            3: "unclarity / missing conversation style partially",
            2: "between 3 and 1",
            1: "unclear language / missing conversation style"
        }
    },
        "Clarity (Saliency)": {
        "description": "how well key information is placed within the textual response.",
        "scoring": {
            5: "key information is completely salient",
            4: "between 5 and 3",
            3: "key information is partially salient",
            2: "between 3 and 1",
            1: "key information is not salient"
        }
    },
	 "Cyclicality (Content)": {
        "description": "Does the output contain content-related or literal repetitions?",
        "scoring": {
            5: "no repetitions (content-related or literal)",
            4: "between 5 and 3",
            3: "one repetition (content-related or literal)",
            2: "between 3 and 1",
            1: "quite a lot of repetitions (content-related or literal)"
        }
    }
}

def evaluate_outputs_single_chat(api_key, prompt_output_dict, response_cache, cache_file, evaluation_criteria_dict = evaluation_criteria_dict ):
    """Uses the LLM to evaluate prompt-output pairs."""
    client = OpenAI(api_key=api_key)
    ratings = {}
    used_cache_once = False
    for user_prompt, output in prompt_output_dict.items():
        if user_prompt not in ratings:
            ratings[user_prompt] = {}
        if output not in ratings[user_prompt]:
            ratings[user_prompt][output] = {}
        for evaluation_criterion, criterion_information in evaluation_criteria_dict.items():
            system_prompt = (
            "You are an impartial evaluator. Your task is to assess AI-generated answers about research papers to user prompts based on specific criteria. "
            "You will receive:\n"
            "1. The original user prompt.\n"
            "2. The AI-generated output.\n"
            "3. An evaluation criterion and its description.\n\n"
            "Based only on the provided criterion and its description, rate the output on a scale from 1 to 5.\n"
            "Do not use a criterion other than the provided criterion and its description for rating.\n"
            "Explain your rating in one sentence, referencing specific parts of the output as justification."
            )

            prompt = (f"Please rate the output {output} which is related to the prompt {user_prompt}."
                      f"Use the {criterion_information} which is related to {evaluation_criterion} for your rating."
                      f"Provide one sentence of explanation with an example from the text, why you chose this rating.")
            
            if prompt in response_cache:
                ratings[user_prompt][output][evaluation_criterion] = response_cache[prompt][user_prompt][output][evaluation_criterion]
                if not used_cache_once:
                    print("using cached response")
                    used_cache_once = True
            else:
                response_cache[prompt] = {}
                response_cache[prompt][user_prompt] = {}
                response_cache[prompt][user_prompt][output] = {}
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                        temperature=0
                     )
                    ratings[user_prompt][output][evaluation_criterion] = response.choices[0].message.content
                    response_cache[prompt][user_prompt][output][evaluation_criterion] = response.choices[0].message.content
                    joblib.dump(response_cache, cache_file)
                except AuthenticationError:
                    return None, "❌ Invalid API key. Please check your OpenAI credentials."
                except OpenAIError as e:
                    return None, "⚠️ OpenAI API error: {e}"
    return ratings, None