from openai import OpenAI
import getpass
from textblob import TextBlob, Word, Blobber
api_key = "API_KEY"

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
            model="gpt-4o",
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



# Call the function with all required parameters
result = get_gpt4_response_with_sentiment(role = "you are an oracle. You should make prediction based on the given twitter hashtags and sentiment analysis data I give you here", instruction = "What is gonna happen in future", hashtags = "#tswift, #AI, #life",polarity =  1, subjectivity = 0.5)

# Print the response
print(result)


