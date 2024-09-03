import openai
import os
import json
import random
import tiktoken
from pydantic import BaseModel
import time
import concurrent.futures
from threading import Lock

lock = Lock()
total_input_token_count = 0
total_output_token_count = 0

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

from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=5, max=60))
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
    
    max_tokens = 1000
    while True:
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",                
                messages = [
                    {"role": "system", "content": "You are a social media simulation assistant. You are helping a user generate tweets based on their profile. You are allowed to generate a variety of tweets with different sentiments, and tonalities."},
                    {"role": "user", "content": background_info},
                ],
                max_tokens=max_tokens,
                temperature=random.uniform(0.5, 0.9),
                response_format=TweetResponse
            )
            
            output_token_count += len(enc.encode(response.choices[0].message.content))
            parsed_response = response.choices[0].message.parsed

            if parsed_response:
                user['observation'] = [f'{ub.explanation}' for ub in parsed_response.user_behavior]
                user['behavior'] = [f'{ub.final_behavior}' for ub in parsed_response.user_behavior]
                user['scenario_tweets'] = [tweet.tweet for tweet in parsed_response.tweets]
                break
            else:
                print(f"Unexpected response format for user {user['aesop_id']}. Retrying...")
                max_tokens += 250  # Increase max_tokens for the next attempt
        
        except openai.LengthFinishReasonError:
            print(f"LengthFinishReasonError for user {user['aesop_id']}. Increasing max_tokens and retrying...")
            max_tokens += 250  # Increase max_tokens and retry
        
        except Exception as e:
            print(f"Error processing user {user['aesop_id']}: {str(e)}")
            user['error'] = str(e)
            break

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

def process_user(entry):
    global total_input_token_count, total_output_token_count
    print(f"Processing user: {entry['aesop_id']}")
    try:
        user, input_token_count, output_token_count = generate_user_tweets(entry)
        
        with lock:
            total_input_token_count += input_token_count
            total_output_token_count += output_token_count

        # Replace the original entry with the processed user data
        entry.update(user)
    except Exception as e:
        print(f"Error processing user {entry['aesop_id']}: {str(e)}")
        entry['error'] = str(e)
    
    return entry, input_token_count, output_token_count

def assign_new_tweets(data):
    last_pause = time.time()
    processed_users = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        
        for idx, entry in enumerate(data):
            now = time.time()
            last_pause = check_to_pause(now, last_pause, total_input_token_count, total_output_token_count)
            
            futures.append(executor.submit(process_user, entry))
            
            # Save results every 10 users
            if idx % 10 == 0 and idx > 0:
                concurrent.futures.wait(futures)  # Ensure all previous tasks are completed
                for future in futures:
                    try:
                        result, _, _ = future.result()
                        processed_users[result['aesop_id']] = result
                    except Exception as e:
                        print(f"Error processing future: {str(e)}")
                
                with open('data_characters_basic_borna_activation_time_updated_tweets.json', 'a', encoding='utf-8-sig') as file:
                    json.dump(list(processed_users.values()), file, indent=4, ensure_ascii=False)
                print(f"Saved results for users up to index {idx}")
                futures = []
        
        # Process any remaining futures
        for future in concurrent.futures.as_completed(futures):
            try:
                result, _, _ = future.result()
                processed_users[result['aesop_id']] = result
                print(f"User processed and updated: {result['aesop_id']}")
            except Exception as e:
                print(f"Error processing future: {str(e)}")
    
    return list(processed_users.values())
# Load your JSON data
with open('data_characters_basic_borna_activation_time.json', 'r', encoding='utf-8-sig') as file:
    data = json.load(file)

# skip the first 100 users
# data = data[11:]
# Process each entry in the JSON data
new_data = assign_new_tweets(data)

# Save the updated JSON data
with open('data_characters_basic_borna_activation_time_updated_tweets_final.json', 'w' ,encoding='utf-8-sig') as file:
    json.dump(new_data, file, indent=4, ensure_ascii=False)

print("Tweet history have been updated and saved to _updated_tweets.json")
