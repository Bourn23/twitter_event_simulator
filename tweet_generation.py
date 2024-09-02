from openai import OpenAI
import getpass
from textblob import TextBlob, Word, Blobber
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


def get_gpt4_response_with_sentiment(role, instruction, hashtags, polarity, subjectivity, max_tokens=150, temperature=0.7):
    """
    Sends a prompt to OpenAI's GPT-4 model, retrieves a response, and analyzes its sentiment.

    Parameters:
        role (str): The role of the assistant (e.g., 'system' content).
        hashtags (str): The input hashtags or prompt to send to the model.
        api_key (str): Your OpenAI API key.
        model (str): The model to use (default is 'gpt-4').
        max_tokens (int): Maximum number of tokens in the generated response (default is 150).
        temperature (float): Sampling temperature (0.7 by default). Higher values make the output more random.

    Returns:
        str: The generated response from the model.
    """
    message = f"{instruction} \n here are the hashtags: \n {hashtags} \n and here is the sentiment: \n polarity: {polarity} \n subjectivity: {subjectivity}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": message}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        blob = TextBlob(response.choices[0].message.content)
        sentiment = blob.sentiment
        return {
            "response": response.choices[0].message.content,
            "sentiment": {
                "polarity": sentiment.polarity,  # -1 to 1, where -1 is negative, 0 is neutral, and 1 is positive
                "subjectivity": sentiment.subjectivity  # 0 to 1, where 0 is very objective and 1 is very subjective
            }
        }
    except Exception as e:
        return f"An error occurred: {str(e)}"


def update_polarity_subjectivity(initial_polarity, initial_subjectivity, users_dict, step_size):
    """
    Updates the initial polarity and subjectivity based on user feedback with weighted averages.

    Core users have a higher weight (3) compared to ordinary users (1).

    Parameters:
        initial_polarity (float): The initial polarity value.
        initial_subjectivity (float): The initial subjectivity value.
        users_dict (dict): Dictionary containing user types and their respective polarity and subjectivity values.
            Example:
                {
                    'core': [
                        {'polarity': 0.5, 'subjectivity': 0.6},
                        {'polarity': 0.4, 'subjectivity': 0.5},
                        ...
                    ],
                    'ordinary': [
                        {'polarity': 0.2, 'subjectivity': 0.3},
                        {'polarity': 0.1, 'subjectivity': 0.2},
                        ...
                    ]
                }
        step_size (float): The step size to control the magnitude of the update.

    Returns:
        tuple: A tuple containing the updated polarity and subjectivity.
    """

    # Define weights for each user type
    weights = {
        'core': 3,
        'ordinary': 1
    }

    weighted_polarity_sum = 0.0
    weighted_subjectivity_sum = 0.0
    total_weight = 0

    # Iterate through each user type and their corresponding user data
    for user_type, users in users_dict.items():
        weight = weights.get(user_type, 1)  # Default weight is 1 if user type is unrecognized

        for user in users:
            polarity = user.get('polarity', 0)
            subjectivity = user.get('subjectivity', 0)

            weighted_polarity_sum += polarity * weight
            weighted_subjectivity_sum += subjectivity * weight
            total_weight += weight

    # Calculate weighted averages
    if total_weight > 0:
        average_polarity = weighted_polarity_sum / total_weight
        average_subjectivity = weighted_subjectivity_sum / total_weight
    else:
        average_polarity = 0
        average_subjectivity = 0

    # Update the initial polarity and subjectivity with the weighted averages scaled by step size
    updated_polarity = initial_polarity + (step_size * average_polarity)
    updated_subjectivity = initial_subjectivity + (step_size * average_subjectivity)

    return updated_polarity, updated_subjectivity


# Call the function with all required parameters
result = get_gpt4_response_with_sentiment(role = "you are an oracle. You should make prediction based on the given twitter hashtags and sentiment analysis data I give you here", instruction = "What is gonna happen in future", hashtags = "#tswift, #AI, #life",polarity =  1, subjectivity = 0.5)

# Print the response
print(result)