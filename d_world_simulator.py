import networkx as nx
import json
import random
from datetime import datetime, timedelta
import openai
import os
import concurrent.futures
import time
from textblob import TextBlob
from dotenv import load_dotenv
from advanced_social_media_agent import AdvancedSocialMediaAgent
from datetime import datetime
import pytz


from threading import Lock
lock = Lock()
total_input_token_count = 0
total_output_token_count = 0

load_dotenv()
openai_api_key_1 = os.getenv("OPENAI_API_KEY")
# openai_api_key_1 = "sk-proj-Z0kpKJr6_7h26WURhjLr78y4FhtDkTo_rQ5ml2otc_yh0ZK0BmEdP5KQsgT3BlbkFJz7zzVT_cMJ4vwO3SSAporim3HuW2d"
openai_api_key_2 = os.getenv("OPENAI_API_KEY2")
# openai_api_key_2 = "sk-proj-Z0kpKJr6_7h26WURhjLr78y4FhtDkTo_rQ5ml2otc_yh0ZK0BmEdP5KQsgT3BlbkFJz7zzVT_cMJ4vwO3SSAporim3HuW2d"


from pydantic import BaseModel
import tiktoken
from tenacity import retry, stop_after_attempt, wait_random_exponential


# define an output format for the user tweets and reasoning
class UserTweets(BaseModel):
    action: str
    inspired_by_behavior: str
    tweet: str
    reply_tweet_id: int
    retweet_tweet_id: int



enc = tiktoken.encoding_for_model('gpt-4o-mini')


priority_weights = {
    'org': 3,
    'core': 2,
    'basic': 1
}

# 2040-05-30: 1752 tweets (URLs: 898, Retweets: 188, Replies: 558)
# 2040-05-31: 2161 tweets (URLs: 1097, Retweets: 213, Replies: 705)
# 2040-06-01: 3185 tweets (URLs: 1587, Retweets: 329, Replies: 1055)
# 2040-06-02: 2118 tweets (URLs: 1088, Retweets: 195, Replies: 674)
# 2040-06-03: 1797 tweets (URLs: 934, Retweets: 168, Replies: 605)

predetermined_tweets = {
    '2040-05-30': {
        'post': 4500,
        'post_url': 2000,
        'retweet': 500,
        'reply': 780,
        'like': 2800,
    },
    '2040-05-31': {
        'post': 5800,
        'post_url': 4197,
        'retweet': 980,
        'reply': 732,
        'like': 19000,
    },
    '2040-06-01': {
        'post': 8500,
        'post_url': 4800,
        'retweet': 1050,
        'reply': 1109,
        'like': 16520
    },
    '2040-06-02': {
        'post': 4274,
        'post_url': 2213,
        'retweet': 1088,
        'reply': 1712,
        'like': 9200
    },
    '2040-06-03': {
        'post': 1929,
        'post_url': 1500,
        'retweet': 185,
        'reply': 600,
        'like': 4333
    }
}

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
    "#Artic",
    "#ArkhangelskOblast",
    "#EcoHellTours",
    "#GreenerEco",
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
    "#Artic",
    "#ArkhangelskOblast",
    "#EcoHellTours",
    "#GreenerEco",
]

class WorldModel:
    def __init__(self, network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets):
        self.start_date = start_date
        self.end_date = end_date
        self.current_time = start_date
        self.graph = self.load_network(network_path)
        self.actors = []
        self.core_bios = self.load_biographies(core_biography_path)
        self.basic_bios = self.load_biographies(basic_biography_path)
        self.org_bios = self.load_biographies(org_biography_path)
        self.users_role = self.initialize_users_db()
        self.remaining_actions = predetermined_tweets
        self.posts_graph = nx.MultiDiGraph()  # Initialize the posts graph from the start
        # try loading the post_graph from the file
        # self.posts_graph = nx.read_gml('posts_graph_2040-05-30 14:00:00-network438.gml')
        self.client = openai.OpenAI(api_key = openai_api_key_1)
        self.client2 = openai.OpenAI(api_key = openai_api_key_2)
        self.active_client = self.client
        self.who_active_client = 'client1'

        self.basic_user_properties = ['name', 'type', 'title', 'age', 'gender', 'race', 'nationality', 'bio', 'behavior', 'scenario_tweets']#, "top_topics", "retweet_quote_valence", "retweet_quote_categories", "accounts_to_retweet_quote", "top_hashtags", "percent_tweets_pos_neg_neut"]
        self.core_user_properties = ['name', 'type', 'title', 'leads', 'age', 'gender', 'race', 'nationality', 'bio', 'behavior', 'scenario_tweets']#, "top_topics", "num_mentions_per_tweet", "accounts_to_mention", "retweet_quote_valence", "retweet_quote_categories", "accounts_to_retweet_quote", "top_hashtags", "percent_tweets_pos_neg_neut"]
        self.org_user_properties = ['name', 'type', 'title', 'leads', 'age', 'gender', 'race', 'nationality', 'bio', 'behavior', 'scenario_tweets', "top_topics", "num_mentions_per_tweet", "accounts_to_mention", "retweet_quote_valence", "retweet_quote_categories", "accounts_to_retweet_quote", "top_hashtags", "percent_tweets_pos_neg_neut"]

    def switch_client(self):
        if self.who_active_client == 'client1':
            self.active_client = self.client2
            self.who_active_client = 'client2'
        else:
            self.active_client = self.client
            self.who_active_client = 'client1'


    def initialize_users_db(self): 
        user_types = {}
        for user in self.core_bios:
            user_types[user['aesop_id']] = 'core'
        for user in self.basic_bios:
            user_types[user['aesop_id']] = 'basic'
        for user in self.org_bios:
            user_types[user['aesop_id']] = 'org'
        return user_types

    def load_network(self, network_path):
        return nx.read_gml(network_path)
    
    def load_biographies(self, biography_path):
        with open(biography_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def simulate_social_media_activity(self):
        for user_type in ['basic']:
            graph_nodes = list(self.graph.nodes())
            shuffled_graph_nodes = random.sample(graph_nodes, len(graph_nodes))
            for user in shuffled_graph_nodes:
                if self.users_role[user] != user_type: # Skip users that are not of the current type
                    continue
                # check if the time at users' nationality and convert the current time to their timezone
                user_nationality = self.get_user_property(user, 'nationality')
                user_time = self.convert_time_by_nationality(self.current_time, "American", user_nationality)
                current_hour = user_time.hour
                if current_hour <= random.uniform(6, 10) and current_hour < random.uniform(21, 24):
                    continue

                if self.users_role[user] == user_type:
                    if any(action_count > 0 for action_count in
                        self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                        # Use the graph to fetch the most relevant tweets
                        recent_tweets = self.get_recent_tweets_from_graph(user)
                        # print("Recent tweets fetched in simulated ", recent_tweets)
                        action_info = self.take_action(user, recent_tweets)
                        if action_info[0]:  # Only process if there's an action
                            print(user_nationality, user_time, "user is up and is taking action")
                            # calculate subjectivity and polarity from tweets
                            self.process_action(user, (action_info[0], action_info[1]), action_info[2], action_info[3])

        # self.propagate_information() # redundant???
        self.current_time += timedelta(minutes=15)

    def check_to_pause(self, now, last_pause):
        global total_input_token_count, total_output_token_count
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
            
        return last_pause

    def simulate_social_media_activity_parallel2(self):
        last_pause = time.time()
        processed_users = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            # shuffle so that it's not always the same users being processed first
            list_nodes = list(self.graph.nodes())
            random.shuffle(list_nodes)
            for idx, user in enumerate(list_nodes):
                # check if we have exceeded our token limit
                now = time.time()
                last_pause = self.check_to_pause(now, last_pause)#, total_input_token_count, total_output_token_count)

                # check if any actions left today
                if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                    futures.append(executor.submit(self.process_users, user))

                if idx % 100 == 0:
                    concurrent.futures.wait(futures)
                    for future in futures:
                        try:
                            # print(future.result())
                            result, _, _ = future.result()
                            processed_users[str(result[-1])] = {result[0]: [result[1], result[2]]}
     
                        except Exception as e:
                            print(f"Error processing user [in concurrent]: {e}")

                    with open('processed_users.txt', 'w') as file:
                        # print("processed users ", len(processed_users.keys()))
                        # print("sample processed users ", list(processed_users.values())[:5])
                        file.write(f'{processed_users.values()}')
        # self.propagate_information() ## redundant???
        self.current_time += timedelta(minutes=15)

    # def simulate_social_media_activity_parallel(self):
    #     global total_input_token_count, total_output_token_count
    #     users_by_type = {'org': [], 'core': [], 'basic': []}

    #     # Separate users by type for parallel processing
    #     list_nodes = list(self.graph.nodes())
    #     random.shuffle(list_nodes)
    #     for user in list_nodes:
    #         user_type = self.users_role[user]
    #         users_by_type[user_type].append(user)

    #     # Process each user type in parallel
    #     max_workers = 3
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         futures = []
    #         for user_type in ['org', 'core', 'basic']:
    #             futures.append(executor.submit(self.process_users, users_by_type[user_type]))

    #         # Ensure all threads are complete
    #         concurrent.futures.wait(futures)

    #     self.propagate_information()
    #     self.current_time += timedelta(minutes=15)

    @staticmethod
    def convert_time_by_nationality(time: datetime, from_nationality: str, to_nationality: str) -> datetime:
        # Dictionary mapping nationalities to time zones
        # Note: This is a simplified mapping and may not cover all cases

    
        nationality_to_timezone = {
            'Polish': 'Europe/Warsaw',
            'Scottish': 'Europe/London',
            'English': 'Europe/London',
            'Canadian': 'America/Toronto',
            'Italian': 'Europe/Rome',
            'Spanish': 'Europe/Madrid',
            'German': 'Europe/Berlin',
            'French': 'Europe/Paris',
            'Croatian': 'Europe/Zagreb',
            'Indian': 'Asia/Kolkata',
            'Danish': 'Europe/Copenhagen',
            'Chinese': 'Asia/Shanghai',
            'Russian': 'Europe/Moscow',
            'Mexican': 'America/Mexico_City',
            'Pakistani': 'Asia/Karachi',
            'Egyptian': 'Africa/Cairo',
            'USA': 'America/New_York',
            'UK': 'Europe/London',
            'Japan': 'Asia/Tokyo',
            'Australia': 'Australia/Sydney',
            'France': 'Europe/Paris',
            'China': 'Asia/Shanghai',
            'Brazil': 'America/Sao_Paulo',
            'Russia': 'Europe/Moscow',
            'Finnish': 'Europe/Helsinki',
            'Russia': 'Europe/Moscow',
            'Norway': 'Europe/Oslo',
            'International': 'UTC',
            'European': 'Europe/Paris',
            'Icelandic': 'Atlantic/Reykjavik',
            'American': 'America/New_York',
            'British': 'Europe/London',
            'Australian': 'Australia/Sydney',
            'Irish': 'Europe/Dublin',
            'Norwegian': 'Europe/Oslo',
            'Swedish': 'Europe/Stockholm',
            None: 'UTC'
        }

        # Check if nationalities are in our dictionary
        if from_nationality not in nationality_to_timezone:
            raise ValueError(f"Unsupported 'from' nationality: {from_nationality}")
        if to_nationality not in nationality_to_timezone:
            raise ValueError(f"Unsupported 'to' nationality: {to_nationality}")

        # Get the time zones
        from_tz = pytz.timezone(nationality_to_timezone[from_nationality])
        to_tz = pytz.timezone(nationality_to_timezone[to_nationality])

        # Localize the time to the 'from' time zone
        # If the input time is naive (no timezone info), assume it's in the 'from' timezone
        if time.tzinfo is None:
            time_with_tz = from_tz.localize(time)
        else:
            time_with_tz = time.astimezone(from_tz)

        # Convert to the 'to' time zone
        converted_time = time_with_tz.astimezone(to_tz)

        return converted_time
    
    def process_users(self, user):
        global total_input_token_count, total_output_token_count
        # print("Users being processed ", user)
        input_token_count = 0
        output_token_count = 0
        if self.users_role[user] != 'basic':
            return (user,"NO ACTION", "N/A", self.current_time), 0, 0
        try:
            # skip users if they are deactive
            join_time = self.get_user_property(user, 'join_time')
            leave_time = self.get_user_property(user, 'leave_time')
            print("current time", self.current_time, "jointime ", join_time,  " IS it smaller? ", self.current_time < datetime.strptime(join_time, '%Y-%m-%dT%H:%M'))
            if join_time is not None or leave_time is not None:
                if self.current_time < datetime.strptime(join_time, '%Y-%m-%dT%H:%M') or self.current_time > datetime.strptime(leave_time, '%Y-%m-%dT%H:%M'):
                    return (user,"NO ACTION - USER IS DISABLED", "N/A", self.current_time), 0, 0 # skip the user because they are not active at this time

             # check if the time at users' nationality and convert the current time to their timezone
            user_nationality = self.get_user_property(user, 'nationality')
            user_time = self.convert_time_by_nationality(self.current_time, "American", user_nationality)
            current_hour = user_time.hour
            if current_hour <= random.uniform(6, 10) and current_hour < random.uniform(21, 24):
                return (user,"NO ACTION - USER IS ASLEEP", "N/A", self.current_time), 0, 0

            # check if any actions left today - then take action
            if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                recent_tweets = self.get_recent_tweets_from_graph(user)
                action_info = self.take_action(user, recent_tweets)
                if action_info[0]:  # Only process if there's an action
                    input_token_count, output_token_count = self.process_action(user, (action_info[0],action_info[1]), action_info[2], action_info[3])
                
            with lock:
                total_input_token_count += input_token_count
                total_output_token_count += output_token_count

        except Exception as e:
            print(f"Error processing users: {e}")
            return (user,"N/A", "N/A", self.current_time), 0, 0
        return (user,action_info[0], action_info[1], self.current_time), total_input_token_count, total_output_token_count
    

    # def process_users(self, users):
    #     # sleep 10 s with 50% chance, 20s with 10% chance, and 5s with 40% chance
    #     time.sleep(random.choice([10, 20, 30]))
    #     for user in users:
    #         join_time = self.get_user_property(user, 'join_time')
    #         leave_time = self.get_user_property(user, 'leave_time')
    #         if join_time is not None or leave_time is not None:
    #             # basic users have a join_time and leave_time: "join_time": "2024-05-30T08:23", "leave_time": "2024-06-03T12:42" if the current time is not within the join_time and leave_time, skip the user
    #             if self.current_time < datetime.strptime(join_time, '%Y-%m-%dT%H:%M') or self.current_time > datetime.strptime(leave_time, '%Y-%m-%dT%H:%M'):
    #                 continue # skip the user because they are not active at this time
    #         if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
    #             recent_tweets = self.get_recent_tweets_from_graph(user)
    #             action_info = self.take_action(user, recent_tweets)
    #             if action_info[0]:  # Only process if there's an action
    #                 input_token_count, output_token_count = self.process_action(user, (action_info[0],action_info[1]), action_info[2], action_info[3])
        
    def get_tweets_for_user(self, user):
        connected_nodes = list(self.graph.neighbors(user))
        tweets = []

        for connected_user_id in connected_nodes:
            tweets.extend(self.read_tweet_history(connected_user_id)[-5:])  # Get the last 5 posts

        return random.sample(tweets, min(15, len(tweets)))

    def get_user_property(self, user, property):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None
        
        if user == {}:
            return []
        if self.users_role[user] == 'org':
            user_bio = get_user_bio(self.org_bios, user)
        elif self.users_role[user] == 'core':
            user_bio = get_user_bio(self.core_bios, user)
        elif self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        return user_bio.get(property, None)

    ## adds to the tweet history of the user and the tweets graph
    def process_action(self, user, action_info, user_polarity, user_subjectivity):
        action, target_post_id = action_info
        post_id = len(self.posts_graph.nodes) + 1  # Generate a unique post ID
        print('user is taking action ', self.users_role[user], action)
        input_token_count = 0
        output_token_count = 0

        if action == 'post':
            # pass user, user_polarity, user_subjectivity to generate_post
            tweet_feed = self.get_recent_tweets_from_graph(user)
            new_post, input_token_count, output_token_count = self.generate_post(user, action, user_polarity, user_subjectivity, tweet_history=tweet_feed)
            print("adding post to the graph ", new_post, post_id)
            self.posts_graph.add_node(post_id, content=new_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, post_id)

        elif action == 'post_url':
            tweet_feed = self.get_recent_tweets_from_graph(user)
            new_post,input_token_count, output_token_count = self.generate_post(user, action, user_polarity, user_subjectivity, tweet_history=tweet_feed)
            self.posts_graph.add_node(post_id, content=new_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, post_id)

        elif action == 'like' and target_post_id:
            # Increment the like count in the post node
            self.posts_graph.nodes[target_post_id]['likes'] += 1
            # Add an edge representing the 'like' interaction
            self.posts_graph.add_edge(user, target_post_id, interaction='like', timestamp=self.current_time)
            input_token_count = 0
            output_token_count = 0
            

        elif action == 'retweet' and target_post_id:
            target_post_data = self.posts_graph.nodes[target_post_id]
            tweet_feed = self.get_recent_tweets_from_graph(user)
            rt_content, rt_target_id, input_token_count, output_token_count = self.generate_post(user, action, user_polarity, user_subjectivity, reaction_to_tweet=target_post_data['content'], tweet_history=tweet_feed, screen_name=target_post_data['owner'])
            self.posts_graph.add_node(post_id, content=f"RT: {target_post_data['content']}" + rt_content, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            # self.add_to_tweet_history(user, post_id) #redundant
            # Add an edge representing the 'retweet' interaction
            self.posts_graph.add_edge(post_id, target_post_id, interaction='retweet', timestamp=self.current_time)
            # Update the original post with the retweet reference
            self.posts_graph.nodes[target_post_id]['retweets'] += 1

        elif action == 'reply' and target_post_id:
            target_post_data = self.posts_graph.nodes[target_post_id]
            tweet_feed = self.get_recent_tweets_from_graph(user)
            #TODO: we can later pass more than just the reply_tweet, for instance we could pass the replies made to that tweet too.
            replied_post_generated, _, input_token_count, output_token_count = self.generate_post(user, action, user_polarity, user_subjectivity, reaction_to_tweet=target_post_data['content'], tweet_history=tweet_feed, screen_name=target_post_data['owner'])
            self.posts_graph.add_node(post_id, content=f"RE: {target_post_data['content']}" + replied_post_generated, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.posts_graph.add_edge(post_id, target_post_id, interaction='reply', timestamp=self.current_time)
            # Update the original post with the reply reference
            self.posts_graph.nodes[target_post_id]['replies'].append(post_id)
            # self.add_to_tweet_history(user, reply_content) # redundant
        
        return input_token_count, output_token_count
    
    def take_action(self, user, tweets, step_size=0.1):
        current_date = self.current_time.strftime('%Y-%m-%d')
        
        if current_date not in self.remaining_actions and current_date in predetermined_tweets:
            self.remaining_actions[current_date] = predetermined_tweets[current_date].copy()

        actions_today = self.remaining_actions.get(current_date, {})
        user_role = self.users_role[user]

         #print("calculatng subjectivity and polarity")
        # calculate subjectivity and polarity from tweets only for basic users
        if user_role == 'basic':
            historical_subjectivity = 0
            historical_polarity = 0

            #print("tweets in take_action", tweets)
            for tweet in tweets['neighbors_tweets']:
                tweet = tweet[1]['content']
                blob = TextBlob(tweet)
                sentiment = blob.sentiment
                historical_polarity += sentiment.polarity
                historical_subjectivity += sentiment.subjectivity
            if len(tweets['neighbors_tweets']) != 0:
                avg_historical_polarity = historical_polarity / len(tweets['neighbors_tweets'])
                avg_historical_subjectivity = historical_subjectivity / len(tweets['neighbors_tweets'])
            else:
                avg_historical_polarity = 0
                avg_historical_subjectivity = 0

            # read initial polarity and subjectivity from user json based on its role
            initial_polarity = self.get_user_property(user, 'polarity')
            initial_subjectivity = self.get_user_property(user, 'subjectivity')

            user_updated_polarity =initial_polarity + (step_size * avg_historical_polarity)
            user_updated_subjectivity = initial_subjectivity + (step_size * avg_historical_subjectivity)
        else:
            user_updated_polarity = self.get_user_property(user, 'polarity')
            user_updated_subjectivity = self.get_user_property(user, 'subjectivity')
        
         #print("user updated polarity and subjectivity", user_updated_polarity, user_updated_subjectivity)
        if user_role in ['org', 'core']:
            # action, selected_tweet = self.take_action_with_gpt4(user, tweets, actions_today, user_updated_subjectivity, user_updated_polarity)
            action, selected_tweet = self.take_action_for_advanced_user(user, tweets, actions_today)

        else:
            action, selected_tweet = self.take_action_for_basic_user(user, tweets, actions_today)

        return action, selected_tweet, user_updated_polarity, user_updated_subjectivity

    # def take_action_with_gpt4(self, user, tweets, actions_today, subjectivity, polarity):
    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(min=5, max=40))
    def generate_post(self, user: dict, action: str, updated_user_polarity: int, updated_user_subjectivity: int, tweet_history: list, screen_name: str=None, reaction_to_tweet: str=None):
        input_token_count = 0
        output_token_count = 0
        background_info = ""
        if self.users_role[user] == 'org':
            for prop in self.org_user_properties:
                background_info += f"{prop}: {self.get_user_property(user, prop)}.\n"
        elif self.users_role[user] == 'core':
            for prop in self.core_user_properties:
                background_info += f"{prop}: {self.get_user_property(user, prop)}.\n"
        elif self.users_role[user] == 'basic':
            for prop in self.basic_user_properties:
                background_info += f"{prop}: {self.get_user_property(user, prop)}.\n"

        background_info += f"Considering the user's information, write a tweet such that it would be relevant to their profile."
        background_info += f"To do that, you should make shrewd note on the users profile, a relevant key points from the user's profile and behavior and generate a realistic tweet based on those points."
        background_info += f"Please make sure the tweets are relevant to the user's profile and it is okay to be creative with the tweets, some tweets might be aggressive or sensitive (a little) and that is okay."
        background_info += f"Once done with making those points, please generate a tweet matching the observations made concerning the following situation and user's tweet feed: "
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
                    Environmental groups: INNW and EcoVanguard Solutions\n"""

        user_nationality = self.get_user_property(user, 'nationality')
        user_time = self.convert_time_by_nationality(self.current_time, "American", user_nationality)
        background_info += f"User's current time: {user_time}.\n"
        # background_info += f"Once done with making those points, please ONLY return the new tweets in the following format: [<list_of_inferences_on_character>][<list_of_new_tweets_based_on_inferences>]."
        if updated_user_polarity > 0:
            background_info += f"The user supports the viewpoint of Heliexpress LTD with a subjectivity score of {updated_user_subjectivity}. "
            if action in ['post', 'post_url']:
                background_info += f"User may choose to use these hashtags: {random.sample(bad_hashtags, 3)}"
        elif updated_user_polarity < 0:
            background_info += f"The user has is not happy with what Heliexpress LTD is doing with a subjectivity score of {updated_user_subjectivity}."            
            if action in ['post', 'post_url']:
                background_info += f"User may choose to use these hashtags: {random.sample(good_hashtags, 3)}"
        
        if len(tweet_history['user_tweets']) > 0:
            background_info += f"User's 5 most recent tweets: {tweet_history['user_tweets']}."

        if action in ['retweet', 'reply']:
            background_info += f"\nYou are {action}'ing to the following tweet, make an appropriate {action} to this tweet: username: {reaction_to_tweet} - tweet: {reaction_to_tweet}.\n"
        elif action in ['post', 'post_url']:
            background_info += f"\nUser's action is {action}\n"
            if action == 'post_url':
                background_info += f"When posting url you need to include a (seemingly real) url in the tweet.\n"
        if action in ['post', 'post_url', 'retweet', 'reply']:
            background_info += f"\nUser's tweet feed in (tweet_id, tweet) format:\n <tweets_feed> \n {list(set((tweet_id, tweet_data['content']) for tweet_id, tweet_data in tweet_history['neighbors_tweets']))}.\n </tweets_feed>\n"


        input_token_count += len(enc.encode(background_info))
        input_token_count += len("You are a social media simulation assistant. You are helping a user generate tweets based on their profile. You are allowed to generate a variety of tweets with different sentiments, and tonalities.")
        
        max_tokens = 150

        while True:
            try:
                response = self.client.beta.chat.completions.parse(
                    model="gpt-4o-mini",                
                    messages = [
                        {"role": "system", "content": "You are a social media simulation assistant. You are helping a user generate tweets based on their profile. You are allowed to generate a variety of tweets with different sentiments, and tonalities. Action must be the same as provided by the user. Allowed actions are 'post', 'post_url', 'retweet', 'reply'"},
                        {"role": "user", "content": background_info},
                    ],
                    max_tokens=max_tokens,
                    temperature=random.uniform(0.5, 0.9),
                    response_format=UserTweets
                )
                
                output_token_count += len(enc.encode(response.choices[0].message.content))
                parsed_response = response.choices[0].message.parsed
                # print("Parsed response ", parsed_response)
                if parsed_response:
                    action_by_gpt = parsed_response.action
                    if action_by_gpt == action:
                        print(f"Action by {self.users_role[user]} user", parsed_response, '\n', user)
                        break
                    else:
                        background_info += f"Your action must match the action provided by the user. You need to generate {action} but the generated action is {action_by_gpt}."
                        print(f"Unexpected response format for user {user['aesop_id']}. Retrying...")
                        time.sleep(30)
                        max_tokens += 50
                    break
                else:
                    print(f"Unexpected response format for user {user['aesop_id']}. Retrying...")
                    time.sleep(30)
                    max_tokens += 50  # Increase max_tokens for the next attempt
            
            except openai.LengthFinishReasonError:
                print(f"LengthFinishReasonError for user {user['aesop_id']}. Increasing max_tokens and retrying...")
                max_tokens += 50  # Increase max_tokens and retry
            
            except Exception as e:
                print(f"Error processing user {user['aesop_id']}: {str(e)}")
                user['error'] = str(e)
                break
        
        # print("Parsed response ", parsed_response)
        if action == 'post' or action == 'post_url': # action is to post or post_url
            return parsed_response.tweet, input_token_count, output_token_count
        elif action == 'retweet': # action can be retweet/like or reply
            return parsed_response.tweet, parsed_response.retweet_tweet_id, input_token_count, output_token_count
        elif action == 'reply':
            return parsed_response.tweet, parsed_response.reply_tweet_id, input_token_count, output_token_count


    def take_action_for_basic_user(self, user, tweets, actions_today):
         #print("Taking action for basic user")
        # Define a base action probability for basic users
        base_action_probability = 0.9
        
        # Dynamic adjustment based on context (e.g., time of day, user engagement)
        time_of_day_weight = 1.0
        if 6 <= self.current_time.hour < 12:
            time_of_day_weight = 1.6
        elif 18 <= self.current_time.hour < 24:
            time_of_day_weight = 1.4
        else:
            time_of_day_weight = 0.8
        
        # Adjust probability based on other contextual factors (e.g., user engagement)
        engagement_factor = self.calculate_engagement_factor()


        action_probability = base_action_probability * time_of_day_weight * engagement_factor
        
        # Decide whether to take an action
        if random.random() < action_probability:
            user_context = {'time_of_day': 'morning' if 6 <= self.current_time.hour < 12 else 'evening'}
            action = self.select_best_action(user, actions_today, user_context)
            # action = 'retweet' #change this
        else:
            action = None

        selected_tweet = self.select_tweet_for_action(action, tweets['neighbors_tweets'])
         #print("action in take_action_for_basic_user", action);  #print("selected tweet ", selected_tweet)
        return action, selected_tweet  

    def take_action_for_advanced_user(self, user, tweets, actions_today):
         #print("Taking action for basic user")
        # Define a base action probability for basic users
        base_action_probability = 0.9
        
        # Dynamic adjustment based on context (e.g., time of day, user engagement)
        time_of_day_weight = 1.0
        if 6 <= self.current_time.hour < 12:
            time_of_day_weight = 1.5
        elif 18 <= self.current_time.hour < 24:
            time_of_day_weight = 1.9
        else:
            time_of_day_weight = 0.8
        
        # Adjust probability based on other contextual factors (e.g., user engagement)
        engagement_factor = self.calculate_engagement_factor()


        action_probability = base_action_probability * time_of_day_weight * engagement_factor
        
        # Decide whether to take an action
        if random.random() < action_probability:
            user_context = {'time_of_day': 'morning' if 6 <= self.current_time.hour < 12 else 'evening'}
            action = self.select_best_action(user, actions_today, user_context)
            # action = 'reply' #change this
        else:
            action = None

        selected_tweet = self.select_tweet_for_action(action, tweets['neighbors_tweets'])
         #print("action in take_action_for_basic_user", action);  #print("selected tweet ", selected_tweet)
        return action, selected_tweet
    
    def calculate_engagement_factor(self):
        """Calculate engagement factor based on the proximity to the protest day."""
        protest_day = datetime(2040, 6, 1)
        days_until_protest = (protest_day - self.current_time).days
        
        if days_until_protest > 0:
            engagement_factor = 1 + 0.2 * max(0, days_until_protest - 30)
        else:
            engagement_factor = 1  # No additional engagement boost after the protest day
        
        return engagement_factor
    
    def select_best_action(self, user, actions_today, user_context):
        # TODO (later): users weights/preferences can be different, not all users act alike.
        # load from user json file
        # Define weights for each action
        weights_factors = self.get_user_property(user, 'action_weight')
        weights = {
            'like': weights_factors['like_weight'],
            'reply':  weights_factors['reply_weight'],
            'post': weights_factors['tweet_weight'],
            'retweet': weights_factors['retweet_weight'],
            'post_url': weights_factors['tweet_url_weight'],
        }

        # Adjust weights based on context
        if user_context.get('time_of_day') == 'morning':
            weights['post'] *= 1.2
            weights['post_url'] *= 1.1
        elif user_context.get('time_of_day') == 'evening':
            weights['retweet'] *= 1.1
            weights['like'] *= 1.3
            weights['reply'] *= 1.2

        # Calculate the scores
        action_scores = {action: count * weights[action] for action, count in actions_today.items() if count > 0}
        if not action_scores:
            return None

        # Convert scores to probabilities
        total_score = sum(action_scores.values())
        probabilities = {action: score / total_score for action, score in action_scores.items()}

        # Choose an action based on probabilities
        chosen_action = random.choices(list(probabilities.keys()), list(probabilities.values()))[0]
        return chosen_action

    def select_tweet_for_action(self, action, tweets):
         #print("Selecting tweet for action")
        if action in ['retweet', 'reply', 'like']:
            return self.get_most_influential_tweet(tweets)
        return None

    def get_most_influential_tweet(self, tweets):
        if not tweets:
            return None
        
        influence_weights_by_role = {
            'org': 6,
            'core': 5,
            'basic': 1,
        }

        # first check who the owner's rules of tweets are, it's stored in each tweet's data
        # if the owner is an org, then the tweet is more likely to be influential
        # if the owner is a core, then the tweet is less likely to be influential
        # if the owner is a basic, then the tweet is less likely to be influential
        owner_roles = [self.users_role[tweet[1]['owner']] for tweet in tweets]
        
        # Calculate the influence score for each tweet
        influence_scores = {tweet[0]: self.calculate_influence_score(tweet[0]) for tweet in tweets}


        # Apply the role-based weights
        for tweet, role in zip(tweets, owner_roles):
            influence_scores[tweet[0]] *= influence_weights_by_role[role]


        # Randomly select a tweet based on the influence score
        total_score = sum(influence_scores.values())
        if total_score == 0:
            return random.choice(tweets)[0]
        probabilities = {tweet: score / total_score for tweet, score in influence_scores.items()}
        chosen_tweet = random.choices(list(probabilities.keys()), list(probabilities.values()))[0]

        return chosen_tweet
        
        

    def calculate_influence_score(self, tweet):
        # Simple influence score based on likes, retweets, and replies
        tweet_data = self.posts_graph.nodes[tweet]
        return 0.4 * tweet_data.get('likes', 0) + 0.3 * tweet_data.get('retweets', 0) + 0.3 * len(tweet_data.get('replies', []))
    
    # def propagate_information(self):
    #     for edge in self.graph.edges():
    #         source, target = edge
    #         source_user = self.graph.nodes[source]
    #         target_user = self.graph.nodes[target]
            
    #         # for post in self.read_tweet_history(source_user):
    #         #     if post not in self.read_tweet_history(target_user):
    #         #         self.add_to_tweet_history(target_user, post)
    #         # replace this with graph retrieval
    #         source_tweets = self.get_recent_tweets_from_graph(source_user)
    #         target_tweets = self.get_recent_tweets_from_graph(target_user)
    #         for tweet in source_tweets['user_tweets']:
    #             if tweet not in target_tweets['user_tweets']:
    #                 self.add_to_tweet_history(target_user, tweet[0])

    # def get_world_state(self, user):
    #     return {
    #         'current_time': self.current_time,
    #         'read_tweet_history': self.read_tweet_history(user)[-15:],  # Limit to last 15 tweets
    #     }
    
    def read_tweet_history(self, user):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None
        
        if user == {}:
            return []
        if self.users_role[user] == 'org':
            user_bio = get_user_bio(self.org_bios, user)
        elif self.users_role[user] == 'core':
            user_bio = get_user_bio(self.core_bios, user)
        elif self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        if user_bio.get("tweets_simulation"):
            return user_bio["tweets_simulation"]
        else:
            user_bio["tweets_simulation"] = []
            return user_bio.get("tweets", [])

    def add_to_tweet_history(self, user, tweet):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None

        if self.users_role[user] == 'org':
            user_bio = get_user_bio(self.org_bios, user)
        elif self.users_role[user] == 'core':
            user_bio = get_user_bio(self.core_bios, user)
        elif self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        if "tweets_simulation" not in user_bio:
            user_bio["tweets_simulation"] = []

        user_bio["tweets_simulation"].append(tweet)

    @staticmethod
    def parse_timestamp(timestamp):
            if isinstance(timestamp, str):
                try:
                    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M')
            return timestamp
    
    def get_recent_tweets_from_graph(self, user, limit=15, user_past_tweet_limit=5):
        # TODO (later); more advanced idea to fetch all tweets from the user's network as well as friends of friends
        # TODO (later); we can then have a machine learning model to predict which tweets are most likely to be interacted by the user and show those
        # Start by fetching tweets from the user's own history
        user_tweets = [(n, data) for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == user]
        # Convert all timestamps to datetime objects
        for tweet in user_tweets:
            tweet[1]['timestamp'] = self.parse_timestamp(tweet[1]['timestamp'])
        sorted_user_tweets = sorted(user_tweets, key=lambda n: n[1]['timestamp'], reverse=True)

        user_tweet_weights = [self.calculate_influence_score(tweet[0]) for tweet in sorted_user_tweets]
        if len(user_tweet_weights) == 0 or sum(user_tweet_weights) == 0: # check if the there are no tweets history or interactions
            sorted_user_tweets = sorted_user_tweets[:user_past_tweet_limit]
        else:
            sorted_user_tweets = [tweet for tweet in random.choices(sorted_user_tweets, weights=user_tweet_weights, k=user_past_tweet_limit)]
        

         #print(f"{sorted_user_tweets=}")
        # Now expand to connected users (neighbors) to fetch their tweets
        connected_users = list(self.graph.neighbors(user))
        connected_tweets = []

        for connected_user in connected_users:
            connected_tweets.extend([(n,data) for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == connected_user])
        # Sort connected tweets by timestamp as well
        for tweet in connected_tweets:
            tweet[1]['timestamp'] = self.parse_timestamp(tweet[1]['timestamp'])
        sorted_connected_tweets = sorted(connected_tweets, key=lambda n: n[1]['timestamp'], reverse=True)

        network_tweet_weights = [self.calculate_influence_score(tweet[0]) for tweet in sorted_connected_tweets]
        if len(network_tweet_weights) == 0 or sum(network_tweet_weights) == 0: # check if the there are no tweets history or interactions
            sorted_connected_tweets = sorted_connected_tweets[:limit]
        else:
            sorted_connected_tweets = [tweet for tweet in random.choices(sorted_connected_tweets, weights=network_tweet_weights, k=limit)]
        
        #TODO: Choose tweets based on their weight instead of just selecting the first n - we can use calculate_influence_score


        return {'user_tweets' : sorted_user_tweets, 'neighbors_tweets': sorted_connected_tweets}
    
    # def get_influential_tweets(self, user, limit=15):
    #     # Calculate degree centrality for each tweet in the user's neighborhood
    #     user_tweets = [n for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == user]
    #     connected_users = list(self.graph.neighbors(user))
        
    #     connected_tweets = []
    #     for connected_user in connected_users:
    #         connected_tweets.extend([n for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == connected_user])
        
    #     all_tweets = user_tweets + connected_tweets
        
    #     # Sort tweets by their degree (number of interactions)
    #     influential_tweets = sorted(all_tweets, key=lambda n: self.posts_graph.degree(n), reverse=True)

    #     # Randomly sample n_limit of all_tweets weighted by their degree
    #     sampled_tweets = random.choices(influential_tweets, weights=[self.posts_graph.degree(n) for n in influential_tweets], k=limit)
        
    #     return sampled_tweets

    def save_tweets(self, filepath):
        all_tweets = []
        
        # Extract information from nodes (tweets)
        for node, data in self.posts_graph.nodes(data=True):
            tweet_info = {
                'post_id': node,
                'content': data.get('content'),
                'owner': data.get('owner'),
                'timestamp': data.get('timestamp').isoformat() if isinstance(data.get('timestamp'), datetime) else data.get('timestamp'),
                'likes': data.get('likes', 0),
                'retweets': data.get('retweets', 0),
                'replies': data.get('replies', [])
            }
            all_tweets.append(tweet_info)

        # Extract information from edges (interactions)
        all_interactions = []
        for source, target, data in self.posts_graph.edges(data=True):
            interaction_info = {
                'source_post_id': source,
                'target_post_id': target,
                'interaction': data.get('interaction'),
                'timestamp': data.get('timestamp').isoformat() if isinstance(data.get('timestamp'), datetime) else data.get('timestamp'),
            }
            all_interactions.append(interaction_info)

        # Save the tweets and interactions to a file
        save_data = {
            'tweets': all_tweets,
            'interactions': all_interactions
        }

        with open(filepath, 'w') as file:
            json.dump(save_data, file, indent=4)

        # Convert datetime attributes to strings before saving
        def convert_datetime_to_string(graph):
            for node, attr in graph.nodes(data=True):
                for key, value in attr.items():
                    if isinstance(value, datetime):
                        attr[key] = value.isoformat()

            for u, v, attr in graph.edges(data=True):
                for key, value in attr.items():
                    if isinstance(value, datetime):
                        attr[key] = value.isoformat()

        # Convert datetime objects in the graph
        convert_datetime_to_string(self.posts_graph)
        
        # Save the graph to a GML file
        nx.write_gml(self.posts_graph, f'posts_graph_{self.current_time}-network340.gml')

# Simulation Runner
def run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets):
    world = WorldModel(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
    
    # Measure the time taken for the simulation
    start_time = time.time()
    while world.current_time <= world.end_date:
        # world.simulate_social_media_activity()
        world.simulate_social_media_activity_parallel2()
        
        if world.current_time.minute == 0:  # Log every hour
            print(f"Simulation time: {world.current_time}, time elapsed: {time.time() - start_time:.2f} seconds.")
            world.save_tweets(f'simulation_results_{world.current_time}-parallel2-sep3-network13-ordinary-only.json')



    time.sleep(20) # wait until all data is fetched
    print("Execution time:", time.time() - start_time)
    return world.save_tweets('simulation_results_tiny_13.json')


if __name__ == "__main__":
    # Run the simulation
    network_path = 'social_network_tiny_13.gml'
    core_biography_path = 'sep2.1-core_final-username_added.json'
    basic_biography_path = 'sep2.1-ordinary_final-username_added_fixedtime.json'
    org_biography_path = 'sep2.1-org_final-username_added.json'

    start_date = datetime(2040, 5, 31, 1)
    end_date = datetime(2040, 5, 31, 2)
    # end_date = datetime(2040, 6, 4)
    final_state = run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
    print("Simulation completed.")