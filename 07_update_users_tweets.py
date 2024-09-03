import openai
import os
import json
import random
import tiktoken
from pydantic import BaseModel
import time


good_hashtags = [
    "#SaveArcticWildlife",
    "#ProtectPolarBears",
    "#NoToHeliTours",
    "#NordaustSvalbardCrisis",
    "#EcoActionNow",
    "#ClimateCrisis2040",
    "#HeliTourHazards",
    "#EndangeredArctic",
    "#PreserveKongKarlsLand",
    "#GreenArcticFuture",
    "#ResistHeliexpress",
    "#FightForTheArctic",
    "#StopHeliMadness",
    "#ArcticTourismThreat",
    "#ArcticEmergency",
    "#NatureOverProfit",
    "#SaveSvalbard",
    "#EcoWarriorsUnite",
    "#GreenAgainstHeli",
    "#ArcticPreservation",
]

bad_hashtags = [
    "#SupportHeliTours",
    "#ArcticOpportunities",
    "#EcoOverreaction",
    "#TourismForProgress",
    "#HeliexpressForAll",
    "#ExploreTheArctic",
    "#JobsOverProtests",
    "#ArcticAdventure",
    "#TourismBoost",
    "#HeliToursNotHarm",
    "#ProgressNotPanic",
    "#EconomicGrowthFirst",
    "#EmbraceTheFuture",
    "#InnovationOverObstruction",
    "#ArcticAccessNow",
    "#OpportunityInTheNorth",
    "#ResponsibleTourism",
    "#ArcticGateway",
    "#AdventureAwaits",
    "#HeliTourSupporters",
]

# define an output format for the user tweets and reasoning
class UserBehavior(BaseModel):
    explanation: str
    final_behavior: str

class UserTweets(BaseModel):
    inspired_by_behavior: str
    tweet: str

class TweetResponse(BaseModel):
    user_behavior: list[UserBehavior]
    tweets: list[UserTweets]

enc = tiktoken.encoding_for_model('gpt-4o-mini')

openai_api_key = os.environ.get('OPENAI_API_KEY')
client = openai.OpenAI(api_key=openai_api_key)

user_properties = ['name', 'type', 'title', 'age', 'gender', 'race', 'nationality', 'bio', 'polarity', 'subjectivity', 'tweets']
def get_user_property(user: dict, prop: str) -> str:
    return user.get(prop, "N/A")

def generate_user_tweets(user: dict):
    input_token_count = 0
    output_token_count = 0
    background_info = ""
    for prop in user_properties:
        background_info += f"{prop}: {get_user_property(user, prop)}.\n"

    background_info += f"Considering the user's information, re-write the tweets such that it would be relevant to their profile."
    background_info += f"To do that, you should make shrewd note on the users profile, extract at least 4-6 key points from the user's profile and generate realistic tweets based on those points. Use those inferences to generate one key point about their tweet style."
    background_info += f"Please make sure the tweets are relevant to the user's profile and it is okay to be creative with the tweets, some tweets might be aggressive or sensitive (a little) and that is okay."
    background_info += f"Once done with making those points, please generate 10 varying tweets matching the observations made concerning the following situation: "# : [<list_of_inferences_on_character>][<list_of_new_tweets_based_on_inferences>]."
    background_info += """
                The Situation::
                In 2040, Arctic sea ice has melted significantly.
                This has led to more ships and aircraft traveling to Arkhangelsk Oblast in Russia.
                A company called Heliexpress is now offering helicopter tours over Kong Karls Land.

                Environmental Concerns::
                The increased traffic might harm polar bears, walruses, and other wildlife in the Nordaust-Svalbard Nature Reserve.
                The area, once a polar desert, now has trees and plants growing.
                There are worries that helicopter landings could damage this new plant life.

                Reactions::
                Environmental Group "If Not Now, Then When?" (INNW):
                Planning a big protest on June 1, 2040
                Criticizing the Norwegian government for not speaking up

                EcoVanguard Solutions:
                Asking Heliexpress to explain how they'll protect endangered animals
                Criticizing Russian officials for not caring about environmental issues

                Expert Opinion:
                Professor Rowan Emerson suggests big organizations should work with smaller groups like INNW for better results

                Key Players::
                Heliexpress LTD: The company offering helicopter tours
                Norwegian and Russian governments
                Environmental groups: INNW and EcoVanguard Solutions"""
    # background_info += f"Once done with making those points, please ONLY return the new tweets in the following format: [<list_of_inferences_on_character>][<list_of_new_tweets_based_on_inferences>]."
    if user['polarity'] > 0:
        background_info += f"The user supports the viewpoint of Heliexpress LTD with a subjectivity score of {user['subjectivity']}."
        background_info += f"Supporting hashtags: {random.sample(bad_hashtags, 3)}"
    elif user['polarity'] < 0:
        background_info += f"The user has is not happy with what Heliexpress LTD is doing with a subjectivity score of {user['subjectivity']}."
        background_info += f"Supporting hashtags: {random.sample(good_hashtags, 3)}"

    input_token_count += len(enc.encode(background_info))
    input_token_count += len("You are a social media simulation assistant. You are helping a user generate tweets based on their profile. You are allowed to generate a variety of tweets with different sentiments, and tonalities.")
    response =client.beta.chat.completions.parse(
        model="gpt-4o-mini",                
        messages = [
            {"role": "system", "content": "You are a social media simulation assistant. You are helping a user generate tweets based on their profile. You are allowed to generate a variety of tweets with different sentiments, and tonalities."},
            {"role": "user", "content": background_info},
        ],
        max_tokens=750,
        temperature=random.uniform(0.5, 0.9),
        response_format=TweetResponse
    )
    output_token_count += len(enc.encode(response.choices[0].message.content))
    parsed_response = response.choices[0].message.parsed

    # parse the response to get the tweets
    with open('amended_users_basic_tweets.txt', 'a') as f:
        f.write(f'user_id : {user["aesop_id"]}, response: {response.choices[0].message.content,}\n')
        

    user['observation'] = [f'{ub.explanation}' for ub in parsed_response.user_behavior]
    user['behavior'] = [f'{ub.final_behavior}' for ub in parsed_response.user_behavior]
    user['scenario_tweets'] = [tweet.tweet for tweet in parsed_response.tweets]

    # print(f"User observation: {user['observation']}\n\n")
    # print(f"User behavior: {user['behavior']}\n\n")
    # print(f"User tweets: {user['scenario_tweets']}\n\n")
    
    return user, input_token_count, output_token_count


def check_to_pause(now, last_pause, total_input_token_count, total_output_token_count):
    if total_input_token_count + total_output_token_count >= 1850000:
        # check if it has been 1 minute since the last pause
        if now - last_pause < 60:
            print(f"Pausing for {1.15 * (now-last_pause)} seconds to avoid exceeding the token limit...")
            time.sleep(1.15*(now - last_pause))
            last_pause = time.time()
            total_input_token_count = 0
            total_output_token_count = 0
            print("Resuming...")
        else:
            print("Waiting for 1 minute before resuming...")
            time.sleep(10)
            last_pause = time.time()
        
    return last_pause, total_input_token_count, total_output_token_count

# Function to randomly assign an start_date_time to each entry (more activation towards the protest day - july 1st 2040); it must be skewed towards the protest day
def assign_new_tweets(data):
    total_input_token_count = 0
    total_output_token_count = 0
    last_pause = time.time()
    for idx, entry in enumerate(data):
        last_pause, total_input_token_count, total_output_token_count = check_to_pause(time.time(), last_pause, total_input_token_count, total_output_token_count)
        # choose based on the user index
        user, input_token_count, output_token_count = generate_user_tweets(entry)
        print(f"Total token count: {input_token_count}, {output_token_count}")
        total_input_token_count += input_token_count
        total_output_token_count += output_token_count
        entry = user

        # save results every 10 users
        if idx % 10 == 0:
            with open('data_characters_basic_borna_activation_time_updated_tweets.json', 'a' ,encoding='utf-8-sig') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            print(f"Saved results for users up to index {idx}")
    return data

# Load your JSON data
with open('data_characters_basic_borna_activation_time.json', 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# Process each entry in the JSON data
new_data = assign_new_tweets(data)

# Save the updated JSON data
with open('data_characters_basic_borna_activation_time_updated_tweets.json', 'w' ,encoding='utf-8-sig') as file:
    json.dump(new_data, file, indent=4, ensure_ascii=False)

print("Tweet history have been updated and saved to _updated_tweets.json")
