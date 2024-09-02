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

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")



priority_weights = {
    'org': 3,
    'core': 2,
    'basic': 1
}

predetermined_tweets = {
    '2040-05-30': {
        'post': 1936-980,
        'post_url': 980,
        'retweet': 189,
        'reply': 647,
        'like': 2800,
    },
    '2040-05-31': {
        'post': 2354-1197,
        'post_url': 1197,
        'retweet': 227,
        'reply': 732,
        'like': 19000,
    },
    '2040-06-01': {
        'post': 3495-1771,
        'post_url': 1771,
        'retweet': 351,
        'reply': 1109,
        'like': 16520
    },
    '2040-06-02': {
        'post': 2274-1213,
        'post_url': 1213,
        'retweet': 188,
        'reply': 712,
        'like': 9200
    },
    '2040-06-03': {
        'post': 1929-957,
        'post_url': 957,
        'retweet': 185,
        'reply': 600,
        'like': 4333
    }
}

good_hashtags = {
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
}

bad_hashtags = {
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
}
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
        self.client = openai.OpenAI(api_key = openai_api_key)

        self.basic_user_properties = ['name', 'type', 'title', 'age', 'gender', 'race', 'nationality', 'bio', 'tweets']#, "top_topics", "retweet_quote_valence", "retweet_quote_categories", "accounts_to_retweet_quote", "top_hashtags", "percent_tweets_pos_neg_neut"]
        self.core_user_properties = ['name', 'type', 'title', 'leads', 'age', 'gender', 'race', 'nationality', 'bio', 'tweets']#, "top_topics", "num_mentions_per_tweet", "accounts_to_mention", "retweet_quote_valence", "retweet_quote_categories", "accounts_to_retweet_quote", "top_hashtags", "percent_tweets_pos_neg_neut"]
        self.org_user_properties = ['name', 'type', 'title', 'leads', 'age', 'gender', 'race', 'nationality', 'bio', 'tweets', "top_topics", "num_mentions_per_tweet", "accounts_to_mention", "retweet_quote_valence", "retweet_quote_categories", "accounts_to_retweet_quote", "top_hashtags", "percent_tweets_pos_neg_neut"]

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
        with open(biography_path, 'r') as file:
            return json.load(file)

    def simulate_social_media_activity(self):
        for user_type in ['org', 'core', 'basic']:
            graph_nodes = list(self.graph.nodes())
            shuffled_graph_nodes = random.sample(graph_nodes, len(graph_nodes))
            for user in shuffled_graph_nodes:
                if self.users_role[user] == user_type:
                    if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                        # Use the graph to fetch the most relevant tweets
                        recent_tweets = self.get_recent_tweets_from_graph(user)
                         #print("Recent tweets fetched in simualted ", recent_tweets)
                        action_info = self.take_action(user, recent_tweets)
                        if action_info[0]:  # Only process if there's an action

                            # calculate subjectivity and polarity from tweets
                            
                            self.process_action(user, (action_info[0],action_info[1]), action_info[2], action_info[3])

        self.propagate_information()
        self.current_time += timedelta(minutes=15)

    def simulate_social_media_activity_parallel(self):
        users_by_type = {'org': [], 'core': [], 'basic': []}

        # Separate users by type for parallel processing
        list_nodes = list(self.graph.nodes())
        random.shuffle(list_nodes)
        for user in list_nodes:
            user_type = self.users_role[user]
            users_by_type[user_type].append(user)

        # Process each user type in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for user_type in ['org', 'core', 'basic']:
                futures.append(executor.submit(self.process_users, users_by_type[user_type]))

            # Ensure all threads are complete
            concurrent.futures.wait(futures)

        self.propagate_information()
        self.current_time += timedelta(minutes=15)

    def process_users(self, users):
        for user in users:
            if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
                recent_tweets = self.get_recent_tweets_from_graph(user)
                action_info = self.take_action(user, recent_tweets)
                if action_info[0]:  # Only process if there's an action
                    self.self.process_action(user, (action_info[0],action_info[1]), action_info[2], action_info[3])

    # def process_users_batched(self, users):
    #     batched_nodes = []
    #     batched_edges = []
    #     batched_updates = []

    #     for user in users:
    #         if any(action_count > 0 for action_count in self.remaining_actions.get(self.current_time.strftime('%Y-%m-%d'), {}).values()):
    #             recent_tweets = self.get_recent_tweets_from_graph(user)
    #             action_info = self.take_action(user, recent_tweets)
    #             if action_info[0]: # Only process if there's an action
    #                 # self.process_action(user, action_info)
    #                 # Collect the updates in batches
    #                 new_nodes, new_edges, new_updates = self.process_action_batched(user, action_info, collect_only=True)
    #                 batched_nodes.extend(new_nodes)
    #                 batched_edges.extend(new_edges)
    #                 batched_updates.extend(new_updates)
        
    #     # Apply all updates in a batch
    #     self.apply_batched_updates(batched_nodes, batched_edges, batched_updates)

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
        
        return user_bio.get(property)

    # def process_action_batched(self, user, action_info, collect_only=False):
    #     action, target_post_id = action_info
    #     new_post_id = len(self.posts_graph.nodes) + 1

    #     batched_nodes = []
    #     batched_edges = []
    #     batched_updates = []

    #     if action == 'post':
    #         new_post = f"User {self.get_user_property(user, 'name')} posts something interesting."
    #         batched_nodes.append((new_post_id, {'content': new_post, 'owner': user, 'timestamp': self.current_time, 'likes': 0, 'retweets': 0, 'replies': []}))
    #         batched_updates.append(("tweet_history", user, new_post_id))

    #     elif action == 'post_url':
    #         new_post = f"User {self.get_user_property(user, 'name')} posts an interesting URL."
    #         batched_nodes.append((new_post_id, {'content': new_post, 'owner': user, 'timestamp': self.current_time, 'likes': 0, 'retweets': 0, 'replies': []}))
    #         batched_updates.append(("tweet_history", user, new_post_id))

    #     elif action == 'like' and target_post_id:
    #         batched_updates.append(("like", target_post_id, user))
        
    #     elif action == 'retweet' and target_post_id:
    #         target_post_data = self.posts_graph.nodes[target_post_id]
    #         new_content = f"RT: {target_post_data['content']}"
    #         retweeted_post_id = len(self.posts_graph.nodes) + 1 # new id for retweeted post
    #         batched_nodes.append((retweeted_post_id, {'content': new_content, 'owner': user, 'timestamp': self.current_time, 'likes': 0, 'retweets': 0, 'replies': []}))
    #         batched_edges.append((retweeted_post_id, target_post_id, {'interaction': 'retweet', 'timestamp': self.current_time}))
    #         batched_updates.append(("tweet_history", user, retweeted_post_id))
        
    #     elif action == 'reply' and target_post_id:
    #         target_post_data = self.posts_graph.nodes[target_post_id]
    #         reply_content = f"User {self.get_user_property(user, 'name')} replies to {self.get_user_property(target_post_data['owner'], 'name')}: Interesting!"
    #         reply_post_id = len(self.posts_graph.nodes) + 1  # New ID for reply post
    #         batched_nodes.append((reply_post_id, {'content': reply_content, 'owner': user, 'timestamp': self.current_time, 'likes': 0, 'retweets': 0, 'replies': []}))
    #         batched_edges.append((reply_post_id, target_post_id, {'interaction': 'reply', 'timestamp': self.current_time}))
    #         batched_updates.append(("tweet_history", user, reply_post_id))
    #         batched_updates.append(("add_reply", target_post_id, reply_post_id))

    #     if collect_only:
    #         return batched_nodes, batched_edges, batched_updates
    #     else:
    #         # Apply batched updates to the graph
    #         self.apply_batched_updates(batched_nodes, batched_edges, batched_updates)

    # def apply_batched_updates(self, batched_nodes, batched_edges, batched_updates):
    #     # Add all nodes in a batch
    #     self.posts_graph.add_nodes_from(batched_nodes)

    #     # Add all edges in a batch
    #     self.posts_graph.add_edges_from(batched_edges)

    #     # Apply all updates
    #     for update in batched_updates:
    #         if update[0] == 'tweet_history':
    #             self.add_to_tweet_history(update[1], update[2])
    #         elif update[0] == 'like':
    #             self.posts_graph.nodes[update[1]]['likes'] += 1
    #         elif update[0] == 'add_reply':
    #             self.posts_graph.nodes[update[1]]['replies'].append(update[2])

    ## adds to the tweet history of the user and the tweets graph
    def process_action(self, user, action_info, user_polarity, user_subjectivity):
        # print("Chosen action ", action_info)
        action, target_post_id = action_info
         #print("user ", user, "action ", action, "target_post_id ", target_post_id)
        post_id = len(self.posts_graph.nodes) + 1  # Generate a unique post ID


                    # if the character's action is to post_url or post ONLY AND ALWAYS return answer in the format of ["{new_tweet}"].
                    #  if the character's action is to retweet, or like, return answer in the format of ["{action}", "{tweet_id}"]. NOTE the tweet_id is given in the user's prompt.
                    #  if character choose to reply, return answer in the format of ["{tweet_id}", "{new_tweet}"]."""},
        if action == 'post':
            # pass user, user_polarity, user_subjectivity to generate_post
            tweet_feed = self.get_recent_tweets_from_graph(user)
            new_post = self.generate_post(user, action, user_polarity, user_subjectivity, tweet_history=tweet_feed)
            self.posts_graph.add_node(post_id, content=new_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, post_id)

        elif action == 'post_url':
            tweet_feed = self.get_recent_tweets_from_graph(user)
            new_post = self.generate_post(user, action, user_polarity, user_subjectivity, tweet_history=tweet_feed)
            self.posts_graph.add_node(post_id, content=new_post, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, post_id)

        elif action == 'like' and target_post_id:
            # Increment the like count in the post node
            self.posts_graph.nodes[target_post_id]['likes'] += 1
            # Add an edge representing the 'like' interaction
            self.posts_graph.add_edge(user, target_post_id, interaction='like', timestamp=self.current_time)

        elif action == 'retweet' and target_post_id:
            target_post_data = self.posts_graph.nodes[target_post_id]
            tweet_feed = self.get_recent_tweets_from_graph(user)
            rt_content = self.generate_post(user, action, user_polarity, user_subjectivity, original_tweet=target_post_data['content'], tweet_history=tweet_feed)
            # rt_contet is the post_id of the retweet; get the post
            rt_content = self.posts_graph.nodes[rt_content]['content']
            self.posts_graph.add_node(post_id, content=rt_content, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.add_to_tweet_history(user, post_id)
            # Add an edge representing the 'retweet' interaction
            self.posts_graph.add_edge(post_id, target_post_id, interaction='retweet', timestamp=self.current_time)

        elif action == 'reply' and target_post_id:
            target_post_data = self.posts_graph.nodes[target_post_id]
            tweet_feed = self.get_recent_tweets_from_graph(user)
            post = self.generate_post(user, action, user_polarity, user_subjectivity, original_tweet=target_post_data['content'], tweet_history=tweet_feed)
            reply_id, reply_content = post[0], post[1]
            target_post_data = self.posts_graph.nodes[reply_id]['content']
            self.posts_graph.add_node(reply_id, content=reply_content, owner=user, timestamp=self.current_time, likes=0, retweets=0, replies=[])
            self.posts_graph.add_edge(reply_id, target_post_id, interaction='reply', timestamp=self.current_time)
            # Update the original post with the reply reference
            self.posts_graph.nodes[reply_id]['replies'].append(post_id)
            self.add_to_tweet_history(user, reply_content)

    def take_action(self, user, tweets, step_size=0.1):
         #print("Taking action in take_action")
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
            for tweet in tweets:
                tweet = tweet[1]['content']
                blob = TextBlob(tweet)
                sentiment = blob.sentiment
                historical_polarity += sentiment.polarity
                historical_subjectivity += sentiment.subjectivity
            if len(tweets) != 0:
                avg_historical_polarity = historical_polarity / len(tweets)
                avg_historical_subjectivity = historical_subjectivity / len(tweets)
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
    def generate_post(self, user, action, user_polarity, user_subjectivity, original_tweet=None, hashtags=None, tweet_history=None):
        # Use GPT-4 to generate the next action
        prompt = self.construct_prompt(user, action, user_polarity, user_subjectivity, original_tweet, hashtags, tweet_history)
        # print("prepared the prompt", prompt)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",                
                messages = [
                {"role": "system", "content": """You are an advanced social media simulator. Your role is to use your best judgement to generate ONE tweet for the given user. AVOID repetitive tweets, match the tone with the polarity level, more negative polarity levels leads to stronger opposing views to the situation and vice versa. The tweet must contextually match the scenario below and consistent (tone, style, length, etc.) with the user's tweet history.
                 <scenario>
                In 2040, the Arctic sea caps have melted, leading to increased maritime and aerial traffic to Arkhangelsk Oblast. Heliexpress has announced a new series of helicopter tours from Arkhangelsk Oblast, with routes flying over Kong Karls Land. This surge in traffic has sparked concerns among environmentalists, who fear it may pose a threat to the polar bears, walruses, and other wildlife inhabiting the Nordaust-Svalbard Nature Reserve. The area, previously a polar desert, has recently seen a proliferation of deciduous plants. There are also concerns that helicopter landings in this region could damage this burgeoning forestation. In response, a large-scale protest against Heliexpress is scheduled for June 1, 2040. Grass Roots Environmental Organization: The environmental group "If Not Now, Then When?" (INNW) comprises a widespread network of activists around the globe, with significant concentrations in Australia, the United States (particularly the Pacific Northwest), Ireland, and the UK. Kaiara Willowbank, a prominent grassroots blogger for INNW, recently published a blog post addressing the issue at hand. In her post, Willowbank criticizes the Norwegian Government and its President for their silence on the matter. She argues that in such challenging times, it is crucial for leaders and nations to adopt a firmer stance in dealing with companies and countries, like Russia and Heliexpress LTD, that seek to exploit situations to their advantage.
                Grass Roots Primary Source: "In these critical moments, silence is not just absence—it's acquiescence. It's essential that our world leaders, including the Norwegian Government, rise to the challenge and confront those who view our environmental crises as opportunities for exploitation. Russia and Heliexpress LTD are just the tip of the iceberg.
                We need action, commitment, and transparency, now more than ever. Hold Norway to task, #ShameOnNorway," stated Kaiara Willowbank, a vocal advocate and blogger for "If Not Now, Then When?". International Environmental Organization: EcoVanguard Solutions, an international NGO, focuses on environmental issues in the Arctic Sea region, particularly pollution, due to the area's increased activity over recent years.
                Anya Chatterjee-Smith, the Chief Communications Officer of their Arctic Sea Division, has publicly criticized Heliexpress LTD for not being transparent about how they plan to mitigate their impact on endangered species populations. Additionally, she has openly condemned Russia and Igor Petrovich Kuznetsov, the Governor of Arkhangelsk Oblast, for their disregard for the region's escalating environmental challenges, specifically pointing out their lack of concern for this pressing issue.
                International Environmental Organization, Primary Source: "As the Chief Communications Officer of EcoVanguard Solutions' Arctic Sea Division, I must express our profound disappointment in the lack of transparency and concern from Heliexpress LTD, the Russian government, and particularly Governor Igor Petrovich Kuznetsov of Arkhangelsk Oblast. Their disregard for the critical environmental issues facing the Arctic Sea region, especially the threat to endangered species, is unacceptable.
                Immediate action and open dialogue are essential to address these pressing challenges effectively. We need to work together to make sure our children and grandchildren have A Greener Tomorrow™" – Public Statement from Anya Chatterjee-Smith, CCO of EcoVanguard Solutions Arctic Sea Division. Environmental Economist Professor: Rowan Emerson, a socio-ecologist and environmental economist, recently spoke on Planetwise Broadcast Radio (PBR), emphasizing that EcoVanguard Solutions should collaborate with grassroots organizations like "If Not Now, Then When?" (INNW).
                He highlighted that although INNW may lack the funding of larger organizations, they have a broader base of support and can mobilize more voices. Emerson pointed out that EcoVanguard's criticism of the Governor of Arkhangelsk Oblast and the President of Heliexpress, while excluding the Norwegian government, indicates a disconnect from the wider environmental movement—a perspective clearly demonstrated by INNW. Environmental Economist Professor, Primary Source: "Rowan Emerson criticizes EcoVanguard Solutions for their narrow focus on figures like the President of Heliexpress and Governor Igor Kuznetsov, overlooking the potential of grassroots mobilization through 'If Not Now, Then When?' and the need to engage with the Norwegian government and its president.
                'True environmental progress demands that we harness grassroots energy and direct our advocacy towards all pivotal actors, including those at the highest levels of government. By sidelining groups like INNW and not mobilizing against broader targets such as Norway's leadership, we miss critical opportunities for impactful change,' Emerson argues." Yet To Comment: The following organizations and individuals have yet to comment, and therefore do not have any primary source information available. Norway Norwegian Ministry of Foreign Affairs Norwegian President, Ingrid Johansen Russia Ministry of Foreign Affairs of the Russian Federation Governor of Arkhangelsk Oblast, Petrovich Kuznetsov Organizations Heliexpress LTD People Member of Environmental Group "If Not Now, Then When?" Name: Kaiara Willowbank Username: @KaiaraNoBrakesWillow Chief Communications Officer (CCO) of INGO Environmental Organization "EcoVanguard Solutions" Name: Anya Chatterjee-Smith Username: @AnyaEVS Social Movement scholar from the United States (Socio-ecologist and Economics Professor from a small liberal arts college outside of Boston, MA) Name: Rowan Emerson Username: @RowanEmersonPhD Governor of Arkhangelsk Oblast, Russia. Name: Petrovich Kuznetsov Username: @Kuznetsov_RF Norwegian President Name: Ingrid Johansen Username: @IngridJohansen Organizations: "If Not Now, Then When," Grassroots Environmental Group Usernames: @innw & @innw_US Hashtags Used: #INNW #IfNotNowThenWhen #ShameOnNorway "EcoVanguard Solutions," International Non-Governmental Environmental Organization Username: @agreenertomorrowEVS Hashtags: #agreenertomorrow #EcoVanguardSolutions #ecomovement #ProtectNSReserve "Heliexpress LTD," Russian Helicopter Tour Company with new tours from Arkhangelsk Oblast passing over Kong Karls Land.
                Username: @heliexpressLTD Hashtag: #heliexpresstours #helitours_RU Norwegian Ministry of Foreign Affairs Username: @NorwayMFA Ministry of Foreign Affairs of the Russian Federation Username: @MFA_Russia General Use Hashtags: #Artic #ArkhangelskOblast #EcoHellTours #GreenerEco
                <begin summary scenario> 
                "scenario_summary": "In 2040, the Arctic sea caps have melted, leading to increased maritime and aerial traffic to Arkhangelsk Oblast. Heliexpress has announced a new series of helicopter tours from Arkhangelsk Oblast, with routes flying over Kong Karls Land.
                This surge in traffic has sparked concerns among environmentalists, who fear it may pose a threat to the polar bears, walruses, and other wildlife inhabiting the Nordaust-Svalbard Nature Reserve. The area, previously a polar desert, has recently seen a proliferation of deciduous plants. There are also concerns that helicopter landings in this region could damage this burgeoning forestation. In response, a large-scale protest against Heliexpress is scheduled for June 1, 2040. ", "scenario_description": "In the scenario known as Melted Caps, which takes place from May 30th to June 3rd, 2040, the melting of Arctic sea caps has caused significant changes in Northern Europe.
                This has led to increased maritime and aerial traffic to Arkhangelsk Oblast, a region impacted by the melting ice. Addressing this surge in traffic and capitalizing on the new opportunities, Heliexpress, a leading helicopter tour company, has announced a series of tours from Arkhangelsk Oblast. These tours offer breathtaking routes over Kong Karls Land, attracting thrill-seekers and nature enthusiasts alike. The company's decision to expand its operations in the region reflects the growing interest in Arctic tourism and the unique experiences it offers. However, there are concerns raised by environmentalists regarding the impact of this increased traffic on the wildlife and natural habitats in the Nordaust-Svalbard Nature Reserve.
                With the melting ice, polar bears, walruses, and other marine animals already facing challenges to their survival, the rise in helicopter flights could further disturb their fragile ecosystems. Additionally, the Nordaust-Svalbard Nature Reserve, formerly a polar desert, has recently seen an unexpected growth of deciduous plants. This new vegetation signals a significant ecological shift, and environmentalists fear that helicopter landings in the region could cause damage to this burgeoning forestation. To express their concerns and draw attention to the potential harm posed by Heliexpress and other aircraft, environmentalists have organized a large-scale protest against the company. This protest, scheduled for June 1st, 2040, aims to raise awareness about the importance of preserving the delicate balance in the Nordaust-Svalbard Nature Reserve.
                It is expected to attract participants and supporters from various corners, including local communities, conservation organizations, and concerned citizens. Amidst these events, the scenario highlights the ongoing impacts of climate change and the urgent need for sustainable practices in the face of a rapidly changing environment. It underscores the potential conflict between economic opportunities and ecological preservation, as the demand for thrilling experiences clashes with the imperative to protect vulnerable species and habitats. The outcome of this scenario will depend not only on the actions taken by Heliexpress and the protesters but also on the response of the relevant governments and global community to address the broader issues of climate change and its consequences." "scenario_name": "Melted_Caps", "date_range_start": "2040-05-30", "date_range_end": "2040-06-03", "countries_of_interest": [ "Ireland {Republic}", "Norway", "Russian Federation", "United Kingdom", "United States" ],
                "regions_of_interest": [ "Northern Europe" ],
                <end summary scenario>
                 </scenario>
                 
                 Your tweet will be between the <output_format> tags:
                     if the character's action is to post_url or post ONLY AND ALWAYS return answer in the format of ["{new_tweet}"].
                     if the character's action is to retweet, or like, return answer in the format of ["{action}", "{tweet_id}"]. NOTE the tweet_id is given in the user's prompt.
                     if character choose to reply, return answer in the format of ["{tweet_id}", "{new_tweet}"]."""},
                {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            response_post_processed = {
                "response": response.choices[0].message.content,
            }
        except Exception as e:
            return f"An error occurred: {str(e)}"
        # print("response_post_processed in generate_post", response_post_processed)
        # response_post_processed = {'response': '["In light of the alarming news about Heliexpress\' helicopter tours threatening the fragile Arctic ecosystem, we must unite to protect our wildlife and natural habitats. It\'s time to say #NoToHeliTours and stand up for our planet! #EcoActionNow"]'}
        # lets update the response_parsed based on the new output format which is based on the action:
        #if the character's action is to post_url or post ONLY AND ALWAYS return answer in the format of ["{new_tweet}"].
        #if the character's action is to retweet, or like, return answer in the format of ["{action}", "{tweet_id}"]. NOTE the tweet_id is given in the user's prompt.
        #if character choose to reply, return answer in the format of ["{tweet_id}", "{new_tweet}"]."""},
        list_response = json.loads(response_post_processed['response'])
        if action == 'post' or action == 'post_url': # action is to post or post_url
            selected_tweet = ' '.join([lr for lr in list_response])
        elif action == 'retweet': # action can be retweet/like or reply
            selected_tweet = int(list_response[1].replace(" ", ""))
        elif action == 'reply':
            replied_tweet_id = int(list_response[0].replace(" ", ""))
            new_reply = list_response[1]
            selected_tweet = (replied_tweet_id, new_reply)

        return selected_tweet
    
    def process_gpt4_response(self, response, actions_today):
        
        action = None
        selected_tweet = None
        # Parse the GPT-4 response to extract the recommended action
        gpt4_response = response['response'] 
        # whole response is a string that looks like a list: ["post", "Excited to kick off this new journey! Looking forward to sharing updates and connecting with everyone. Let's make great things happen! #NewBeginnings"] let's convert it to a list
        gpt4_response = gpt4_response.replace("[", "").replace("]", "").replace('"', "").split(",") # ["post", "Excited to kick off this new journey! Looking forward to sharing updates and connecting with everyone. Let's make great things happen! #NewBeginnings"]

        
        # check what the length of the response is
        if len(gpt4_response) == 2: # its either post, post_url, retweet, or like
            gpt4_action = gpt4_response[0]
            if gpt4_action == 'retweet':
                selected_tweet = 'RT:' + gpt4_response[1]
            elif gpt4_action == 'post' or gpt4_action == 'post_url':
                selected_tweet = gpt4_response[1]
            elif gpt4_action == 'like':
                selected_tweet = gpt4_response[1]
        if len(gpt4_response) == 3:
            gpt4_action = gpt4_response[0]
            if gpt4_action == 'reply':
                selected_tweet = gpt4_response[0]
                selected_tweet = 'RE:' + gpt4_response[1] + gpt4_response[2]
         #print("parsed gpt4 response in process_gpt4_response")
        # Ensure the action is within the available actions
        if 'post_url' in gpt4_action and actions_today.get('post_url', 0) > 0:
            action = 'post_url'
            actions_today['post_url'] -= 1
            actions_today['post'] -= 1
        elif 'post' in gpt4_action and actions_today.get('post', 0) > 0:
            action = 'post'
            actions_today['post'] -= 1
            actions_today['post_url'] -= 1 # Assume that a tweet with a URL is also a tweet
        elif 'retweet' in gpt4_action and actions_today.get('retweet', 0) > 0:
            action = 'retweet'
            actions_today['retweet'] -= 1
        elif 'reply' in gpt4_action and actions_today.get('reply', 0) > 0:
            action = 'reply'
            actions_today['reply'] -= 1
        elif 'like' in gpt4_action and actions_today.get('like', 0) > 0:
            action = 'like'
            actions_today['like'] -= 1

        # # Select a tweet for retweet, reply, or like if needed
        # if action in ['retweet', 'reply', 'like']:
        #     selected_tweet = random.choice(tweets) if tweets else None
        
        return action, selected_tweet

    def construct_prompt(self, user, action, user_polarity, user_subjectivity, original_tweet, hashtags, tweet_history):
        # based on user role, feed the background info. for each user it is saved in self.basic_user_properties, self.core_user_properties, self.org_user_properties
        # this will be the background info paragraph
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
        
        prompt = (
            f"character role: {self.users_role[user]}.\n" # update this to include user bio, historical tweet, etc.
            f"character background info: {background_info}.\n"
            f"character's sentiment: user's polarity (if + then anti-env and if - then pro-env): {user_polarity}, user tweets' subjectivity: {user_subjectivity}\n"
            f"Current time: {self.current_time}.\n"
            f"character's action: {action}.\n"            
        )

        # add to prompt if the action is retweet, reply, or like
        if float(self.get_user_property(user, 'polarity')) > 0: # the user is a supporter of this negative cause
            prompt += f"Choose one or two hashtags (anti-environment): {[hashtag for hashtag in bad_hashtags]}.\n"
        else:
            prompt += f"Choose one or two hashtags (pro-environment): {[hashtag for hashtag in good_hashtags]}.\n"

        if action in ['retweet', 'reply']:
            prompt += f"\nSelected tweet for {action}: {original_tweet}.\n"
        if action in ['post', 'post_url', 'retweet', 'reply']:
            prompt += f"\nUser's tweet feed in (tweet_id, tweet) format:\n <tweets> \n {[(tweet_id, tweet_data['content']) for tweet_id, tweet_data in tweet_history]}.\n </tweets>\n"

        prompt += f"Considering the user's preferences, bio, time of day, and available actions, "
        prompt += f"Choose the most reasonable action the user should take next (post, post_url, retweet, reply)?"
        return prompt
    
    def take_action_for_basic_user(self, user, tweets, actions_today):
         #print("Taking action for basic user")
        # Define a base action probability for basic users
        base_action_probability = 0.3
        
        # Dynamic adjustment based on context (e.g., time of day, user engagement)
        time_of_day_weight = 1.0
        if 6 <= self.current_time.hour < 12:
            time_of_day_weight = 1.2
        elif 18 <= self.current_time.hour < 24:
            time_of_day_weight = 1.1
        else:
            time_of_day_weight = 0.8
        
        # Adjust probability based on other contextual factors (e.g., user engagement)
        engagement_factor = self.calculate_engagement_factor()


        action_probability = base_action_probability * time_of_day_weight * engagement_factor
        
        # Decide whether to take an action
        if random.random() < action_probability:
            user_context = {'time_of_day': 'morning' if 6 <= self.current_time.hour < 12 else 'evening'}
            action = self.select_best_action(actions_today, user_context)
        else:
            action = None

        selected_tweet = self.select_tweet_for_action(action, tweets)
         #print("action in take_action_for_basic_user", action);  #print("selected tweet ", selected_tweet)
        return action, selected_tweet  

    def take_action_for_advanced_user(self, user, tweets, actions_today):
         #print("Taking action for basic user")
        # Define a base action probability for basic users
        base_action_probability = 0.8
        
        # Dynamic adjustment based on context (e.g., time of day, user engagement)
        time_of_day_weight = 1.0
        if 6 <= self.current_time.hour < 12:
            time_of_day_weight = 1.2
        elif 18 <= self.current_time.hour < 24:
            time_of_day_weight = 1.1
        else:
            time_of_day_weight = 0.8
        
        # Adjust probability based on other contextual factors (e.g., user engagement)
        engagement_factor = self.calculate_engagement_factor()


        action_probability = base_action_probability * time_of_day_weight * engagement_factor
        
        # Decide whether to take an action
        if random.random() < action_probability:
            user_context = {'time_of_day': 'morning' if 6 <= self.current_time.hour < 12 else 'evening'}
            action = self.select_best_action(actions_today, user_context)
        else:
            action = None

        selected_tweet = self.select_tweet_for_action(action, tweets)
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
    
    def select_best_action(self, actions_today, user_context):
        weights = {
            'like': 1.0,
            'reply': 1.5,
            'post': 2.0,
            'retweet': 1.2,
            'post_url': 2.5,
        }

        # Adjust weights based on context
        if user_context.get('time_of_day') == 'morning':
            weights['post'] *= 1.2
            weights['post_url'] *= 1.1
        elif user_context.get('time_of_day') == 'evening':
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
        
        # Calculate the influence score for each tweet
        influence_scores = {tweet[0]: self.calculate_influence_score(tweet[0]) for tweet in tweets}
        
        # Select the tweet with the highest influence score
        return max(influence_scores, key=influence_scores.get)

    def calculate_influence_score(self, tweet):
        # Simple influence score based on likes, retweets, and replies
        tweet_data = self.posts_graph.nodes[tweet]
        return 0.4 * tweet_data.get('likes', 0) + 0.3 * tweet_data.get('retweets', 0) + 0.3 * len(tweet_data.get('replies', []))
    
    def propagate_information(self):
        for edge in self.graph.edges():
            source, target = edge
            source_user = self.graph.nodes[source]
            target_user = self.graph.nodes[target]
            
            for post in self.read_tweet_history(source_user):
                if post not in self.read_tweet_history(target_user):
                    self.add_to_tweet_history(target_user, post)

    def get_world_state(self, user):
        return {
            'current_time': self.current_time,
            'read_tweet_history': self.read_tweet_history(user)[-15:],  # Limit to last 15 tweets
        }
    
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

    def get_recent_tweets_from_graph(self, user, limit=15):
        # TODO (later); more advanced idea to fetch all tweets from the user's network as well as friends of friends
        # TODO (later); we can then have a machine learning model to predict which tweets are most likely to be interacted by the user and show those
        # Start by fetching tweets from the user's own history
        user_tweets = [(n, data) for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == user]
         #print(f"{user_tweets=}")
        
        # Sort by timestamp to get the most recent tweets
        ## updated the sorted_user_tweets to the new data structure: [(1, {'content': None, 'owner': 'fa3bd4fe-30ee-48cd-bf25-6ec16c76ff52', 'timestamp': datetime.datetime(2040, 5, 30, 0, 0), 'likes': 0, 'retweets': 0, 'replies': []})]
        sorted_user_tweets = sorted(user_tweets, key=lambda n: n[1]['timestamp'], reverse=True)

         #print(f"{sorted_user_tweets=}")
        # Now expand to connected users (neighbors) to fetch their tweets
        connected_users = list(self.graph.neighbors(user))
        connected_tweets = []

        for connected_user in connected_users:
            connected_tweets.extend([(n,data) for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == connected_user])
         #print(f"{connected_tweets=}")
        # Sort connected tweets by timestamp as well
        sorted_connected_tweets = sorted(connected_tweets, key=lambda n: n[1]['timestamp'], reverse=True)
        
        # Combine the user's tweets with connected tweets and limit the result
        all_sorted_tweets = sorted_user_tweets + sorted_connected_tweets
         #print(f"{all_sorted_tweets=}")
         #print(f"{sorted_connected_tweets=}")
        #TODO: Choose tweets based on their weight instead of just selecting the first n - we can use calculate_influence_score
        tweet_weights = [self.calculate_influence_score(tweet[0]) for tweet in all_sorted_tweets]
        # check if the tweet_weights is empty or has zero values
        if len(tweet_weights) == 0 or sum(tweet_weights) == 0:
            return all_sorted_tweets[:limit]
        recent_tweets = [tweet for tweet in random.choices(all_sorted_tweets, weights=tweet_weights, k=limit)]
        
        return recent_tweets
    
    def get_influential_tweets(self, user, limit=15):
        # Calculate degree centrality for each tweet in the user's neighborhood
        user_tweets = [n for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == user]
        connected_users = list(self.graph.neighbors(user))
        
        connected_tweets = []
        for connected_user in connected_users:
            connected_tweets.extend([n for n, data in self.posts_graph.nodes(data=True) if data.get('owner') == connected_user])
        
        all_tweets = user_tweets + connected_tweets
        
        # Sort tweets by their degree (number of interactions)
        influential_tweets = sorted(all_tweets, key=lambda n: self.posts_graph.degree(n), reverse=True)

        # Randomly sample n_limit of all_tweets weighted by their degree
        sampled_tweets = random.choices(influential_tweets, weights=[self.posts_graph.degree(n) for n in influential_tweets], k=limit)
        
        return sampled_tweets

    def save_tweets(self, filepath):
        all_tweets = []
        
        # Extract information from nodes (tweets)
        for node, data in self.posts_graph.nodes(data=True):
            tweet_info = {
                'post_id': node,
                'content': data.get('content'),
                'owner': data.get('owner'),
                'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None,
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
                'timestamp': data.get('timestamp').isoformat() if data.get('timestamp') else None
            }
            all_interactions.append(interaction_info)

        # Save the tweets and interactions to a file
        save_data = {
            'tweets': all_tweets,
            'interactions': all_interactions
        }

        with open(filepath, 'w') as file:
            json.dump(save_data, file, indent=4)

# Simulation Runner
def run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets):
    world = WorldModel(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
    
    # Measure the time taken for the simulation
    start_time = time.time()
    while world.current_time <= world.end_date:
        world.simulate_social_media_activity()
        # world.simulate_social_media_activity_parallel()
        
        if world.current_time.minute == 0:  # Log every hour
            print(f"Simulation time: {world.current_time}, time elapsed: {time.time() - start_time:.2f} seconds.")
            world.save_tweets(f'simulation_results_{world.current_time}.json')


    print("Execution time:", time.time() - start_time)
    return world.save_tweets('simulation_results.json')


if __name__ == "__main__":
    # Run the simulation
    network_path = 'social_network_small_308.gml'
    core_biography_path = 'sep2_core_characters_fixed_ids.json'
    basic_biography_path = 'sep2_basic_characters_fixed_ids.json'
    org_biography_path = 'sep2_org_characters_fixed_ids.json'

    start_date = datetime(2040, 5, 30)
    end_date = datetime(2040, 5, 31)
    final_state = run_simulation(network_path, core_biography_path, basic_biography_path, org_biography_path, start_date, end_date, predetermined_tweets)
     #print("Simulation completed.")




"""
Network statistics:

core: a66abb59-d2eb-43e7-adf3-2741d9fdce0c followers_count: 108 following_count: 88
core: ebcc0709-261b-4fce-b821-23f8dda526e7 followers_count: 189 following_count: 199
core: 23513aa9-c847-4afb-a3a3-13c0a0db91aa followers_count: 231 following_count: 146
core: 51f24c53-4e0e-4891-ae11-ea66951e2f1a followers_count: 163 following_count: 107
core: 4da3d144-7cc3-4718-bd36-b7029042bded followers_count: 64 following_count: 55
core: 2cd0e9c2-8e77-44d1-894d-b7ab3beb73f6 followers_count: 164 following_count: 143
core: a4a622db-0c6c-4962-962c-d0593d8f745b followers_count: 193 following_count: 143
core: 90b69cc3-bc90-4564-8b5e-1050548b1e7d followers_count: 200 following_count: 147
core: 44e5406c-34ba-46d5-a147-3b2392126b1a followers_count: 121 following_count: 105
core: 7578d56f-32ac-426a-881a-b4312d842675 followers_count: 207 following_count: 309
core: 2fee640c-033e-49b4-936a-99cdf99a2130 followers_count: 103 following_count: 102
core: acd6737d-0059-4a13-b1da-92430441ed80 followers_count: 173 following_count: 67
core: 542d15ad-0f1a-44d6-b5a3-5f6de900ec40 followers_count: 133 following_count: 50
core: 38b18218-7012-4665-8d9c-36ea93775c91 followers_count: 167 following_count: 97
core: 4829ffc4-4367-4b9c-886e-5f1b44d7f5a3 followers_count: 126 following_count: 105
core: e55c2ae2-b70e-4204-82ee-1084d385b2db followers_count: 161 following_count: 130
core: eb143385-8bf4-478e-a6c7-6ae5ce65b79a followers_count: 191 following_count: 280
core: 4820bed5-7975-4f16-bb1a-aadd7df8be63 followers_count: 63 following_count: 54
core: 2fbaffb8-474d-4adb-9115-46e185a00116 followers_count: 179 following_count: 89
core: 3aef6ddb-0e96-4eb6-829d-39de7adc3c1c followers_count: 61 following_count: 58
core: ba33eafa-f10b-43f1-8acb-75b33ffb0274 followers_count: 94 following_count: 57
core: a50d143f-382b-4d73-9c73-657120f07ddc followers_count: 77 following_count: 50
core: 95f86e93-27d3-407e-887d-8af83aaf3646 followers_count: 93 following_count: 118
core: ced67978-5c90-46f0-b464-3db1ead00860 followers_count: 142 following_count: 68
core: 347e50e7-b24a-43e1-9549-1d7fecf875a7 followers_count: 129 following_count: 166
core: c0cf72d3-eb9b-4b35-b2ae-b10e2bb77946 followers_count: 183 following_count: 205
core: a6ced74c-d867-4f37-af9a-d792a6fb4f4d followers_count: 72 following_count: 48
core: a860656c-3f55-4aa4-b84b-803708ddb469 followers_count: 75 following_count: 92
core: 1369a446-b2de-445f-a20b-ac0da4b97808 followers_count: 50 following_count: 47
core: 455fe71a-30b0-4184-912f-1f1a3985959b followers_count: 261 following_count: 347
core: 1cb626e6-a78f-4a2d-8663-e0643adcda80 followers_count: 151 following_count: 139
core: 7a2704f1-b8ac-4ad4-b80d-444f200decd7 followers_count: 23 following_count: 16
core: e298cee8-3534-4262-b922-65bea50e3e4f followers_count: 158 following_count: 191
core: 22282b8e-4600-45db-a435-55a5b3fdfdf0 followers_count: 75 following_count: 31
core: 3208c73e-9a1c-4696-8616-b7b36c767d4c followers_count: 136 following_count: 155
core: 06646035-78bb-4dde-9c1b-0aac661de922 followers_count: 123 following_count: 112
core: 34f23a02-50b2-4843-9517-8fa7e2e3b8c0 followers_count: 135 following_count: 118
core: 7e29cad8-dd3e-4261-8f15-469c5c4df4fe followers_count: 151 following_count: 216
core: 57e42613-1d6d-4ebe-afc7-c912641a6aa5 followers_count: 191 following_count: 152
core: 8c06c4f6-324e-4bb5-b835-b10d17683578 followers_count: 80 following_count: 35
core: 9cddbcd6-99d5-42d3-b738-a84f99a4ac0d followers_count: 88 following_count: 82
core: 49c5470f-6881-4c1a-947b-f441844f2b8a followers_count: 134 following_count: 197
core: 688ee700-73ad-4982-90b5-dc0d9acc5793 followers_count: 121 following_count: 55
core: 1959f568-5139-44b2-a0c1-7e1b5d9e0fed followers_count: 46 following_count: 17
core: 46205835-b579-4650-b8ed-e54e1584f12c followers_count: 62 following_count: 66
core: 0078e3dd-1312-4498-a722-77de0c2fe3bc followers_count: 111 following_count: 163
core: de36444a-6f73-4c11-8134-88e1d1000eb3 followers_count: 131 following_count: 172
core: fd549aa6-1bb2-4d40-a674-b64bce695762 followers_count: 102 following_count: 45
core: 2866b68f-28a6-4c3f-acf3-0807aa3f121d followers_count: 115 following_count: 46
core: 14bd5fc8-e139-4ac7-bc68-e297a8db854b followers_count: 92 following_count: 38
core: 3d332545-1cef-442f-8e46-1b788dd72590 followers_count: 132 following_count: 35
core: 5b081d21-bd67-46cf-ae35-9ef95b01f50d followers_count: 129 following_count: 101
core: 5b2ba544-b18c-412a-ba22-275ae379ec08 followers_count: 17 following_count: 16
core: 54146ee9-7e4c-4708-b8e4-65f09cefb764 followers_count: 138 following_count: 140
core: bf1c7a0d-e271-41d1-91ad-52fb23427e74 followers_count: 84 following_count: 19
core: 5cb28153-231f-4165-b7d2-4257f0947468 followers_count: 244 following_count: 329
core: b1dd630d-8f3d-4a07-ba82-5c6e44cfd840 followers_count: 112 following_count: 104
core: dbcb95f0-3d78-4155-9856-0a4438abca18 followers_count: 135 following_count: 163
core: 934ac794-3738-421a-9b7f-cecf6d3d16f2 followers_count: 168 following_count: 141
core: 17a2b3fa-d3b7-40de-b3a6-38e1bee327bb followers_count: 58 following_count: 75
core: 999f734b-96f5-436d-a5b8-52123d00899d followers_count: 107 following_count: 55
core: 723b5e2a-d958-446c-b27c-f51858f226dd followers_count: 84 following_count: 49
core: 645d9b32-7689-43cf-9727-adef5def0fb4 followers_count: 89 following_count: 58
core: a5d731cb-7e50-43e7-bf92-29138bb0044d followers_count: 61 following_count: 18
core: 87bc1bcc-f184-4bff-a29d-d442b886f1a1 followers_count: 80 following_count: 107
core: 8ffe9a9a-0a3f-4ebf-9c59-f41f1dbc6667 followers_count: 157 following_count: 134
core: 388670d3-e443-40a1-b8ec-2f3dd9bb7ca7 followers_count: 165 following_count: 106
core: f6bd8333-62eb-426f-9711-c20923517e96 followers_count: 51 following_count: 53
core: c7a741ad-9d55-45b7-9317-c3d63dd6e50c followers_count: 152 following_count: 177
core: 5134357d-a538-4d9e-90d3-8d478a0a5e35 followers_count: 192 following_count: 191
core: 9f585999-c9a9-449a-9dd9-3d4c9bad26f6 followers_count: 128 following_count: 107
core: 87a6af1f-9f8c-46c4-bcc0-c21b4caa14f9 followers_count: 110 following_count: 131
core: 22cfa79f-e57f-4100-832b-6a4de5dbe472 followers_count: 98 following_count: 137
core: 815cc3b0-2034-4dbd-9007-dd2f78eef8e3 followers_count: 171 following_count: 243
core: 875ff047-e708-4c46-8e83-8ba15faf8841 followers_count: 84 following_count: 86
core: 707b8d3c-9938-4baf-b8c7-06a41b1d6623 followers_count: 86 following_count: 123
core: 9219dac2-4cb5-4d57-951f-75205b0ac08b followers_count: 37 following_count: 39
core: 5ce536e5-5de0-4077-b775-d5f3eff3b008 followers_count: 43 following_count: 58
core: 01d25ed1-4a4f-47e9-bc61-0d88958a597d followers_count: 88 following_count: 118
core: 14a6d173-8823-4a86-909c-345c3774184d followers_count: 149 following_count: 145
core: 77753e32-209d-41df-bfb8-5442c42484d0 followers_count: 142 following_count: 186
core: 093527f7-a6be-425e-a7bf-2f1695293ab9 followers_count: 186 following_count: 124
core: f09587db-b082-4584-b218-dbf918ba2f91 followers_count: 112 following_count: 56
core: 3d6b3ce3-a408-495d-a255-160768692800 followers_count: 125 following_count: 46
core: 50eccec1-f349-43cf-b40e-3ae8f2a70478 followers_count: 68 following_count: 22
core: 43b1e34d-3cd0-4ccc-aec6-79780c662a37 followers_count: 184 following_count: 124
core: 889f5303-79f3-4c4d-8b1a-bb394374b2ba followers_count: 27 following_count: 37
core: f0abc26a-6831-4ff0-8104-a40918761365 followers_count: 56 following_count: 67
core: 50fc2536-e0a7-4492-a085-a7126aba629b followers_count: 98 following_count: 74
core: 0f267aa3-3734-4360-9c74-0c86e5b2b0f6 followers_count: 193 following_count: 71
core: e805900b-f841-422c-93b8-4b1a1349dc48 followers_count: 69 following_count: 18
core: da32f6e9-fea7-471f-91e5-30bfe2d5798f followers_count: 145 following_count: 196
core: e8f90f30-f901-4264-8579-8749a6129b94 followers_count: 37 following_count: 50
core: 2d8c7ce9-b434-4caf-bab9-e52af282d190 followers_count: 178 following_count: 212
core: f264ca26-ab05-426a-8eff-df993db7a5f3 followers_count: 156 following_count: 189
core: ffb8b737-9d1d-4341-85dc-9862adf33f5e followers_count: 235 following_count: 217
core: c48eed35-43bf-49f3-94b8-036abad346b4 followers_count: 125 following_count: 129
core: 91834db0-cecf-46aa-98e7-a62346a0af37 followers_count: 101 following_count: 25
core: 566c9ce2-9466-41e1-988e-d3ca06055596 followers_count: 65 following_count: 83
core: 15edeb3d-4080-4e1d-8874-b670b5b8044b followers_count: 141 following_count: 88
basic: a066365e-a38f-4532-939a-07396eeb5998 followers_count: 80 following_count: 67
basic: 9895697e-d285-4350-8836-641c09d25cd7 followers_count: 22 following_count: 4
basic: 38af2955-07dd-4cec-9b6b-ad6d97420d08 followers_count: 63 following_count: 60
basic: 9d525637-b5eb-4cde-aec7-758007a0d7ff followers_count: 69 following_count: 71
basic: 0505c333-f0cc-4c8a-bd9d-6da42a305b47 followers_count: 41 following_count: 4
basic: c4858cd8-65da-4ab2-901c-13e13428db57 followers_count: 37 following_count: 35
basic: 87189618-5aa5-410a-886f-f459b1bbf693 followers_count: 68 following_count: 32
basic: 5f0e829e-d964-43c5-9ee8-2e73aa2e1e04 followers_count: 65 following_count: 36
basic: 7a508079-7efa-4191-9396-912761ead6e2 followers_count: 49 following_count: 33
basic: f4579d05-37ac-4270-b5b7-72a291bab2da followers_count: 59 following_count: 45
basic: 2efee8fd-d4f3-4b16-922a-55080f6cdda1 followers_count: 58 following_count: 19
basic: 351b0839-5ac2-4593-a11e-572dc720fa4b followers_count: 40 following_count: 21
basic: e02bf153-07ef-4ab3-b8cc-008cdd4f0915 followers_count: 52 following_count: 30
basic: c01d5eda-191e-4e71-a792-c439198aaf3c followers_count: 37 following_count: 37
basic: 2d9f19da-d203-4c44-a56b-e4e782bbd148 followers_count: 17 following_count: 9
basic: 579b5add-1a20-4def-9b73-76fdf6dfec9d followers_count: 66 following_count: 33
basic: 37553be7-f467-45a9-beb7-3ad595d13395 followers_count: 74 following_count: 40
basic: a1e6d91d-f560-4e0d-b752-f5dc52aee3aa followers_count: 54 following_count: 28
basic: 9f2bc656-50e2-4a8c-a253-d666d7d2a218 followers_count: 65 following_count: 63
basic: 21d14576-7154-4381-880f-23b727027e62 followers_count: 39 following_count: 4
basic: 4a63ea59-a499-4601-a4f0-8e4fdf4ec056 followers_count: 39 following_count: 18
basic: ddbd5271-ecf0-4385-9ae9-baedc42b5d7c followers_count: 28 following_count: 7
basic: 1f2d9399-6232-4e4c-a72c-705a72e8682a followers_count: 71 following_count: 37
basic: d784f105-5a0c-4c44-81f2-dcc81eab53a5 followers_count: 35 following_count: 36
basic: 21a36ae0-d355-4e70-bcee-a44193812b59 followers_count: 77 following_count: 88
basic: f25210b2-1d2c-4cc1-8e50-69260e81877f followers_count: 54 following_count: 51
basic: b7c20942-17d8-41d6-80ea-b6bb2e64b1c0 followers_count: 66 following_count: 22
basic: 007aa06e-f048-46b6-b07e-f80c6a84244f followers_count: 31 following_count: 13
basic: a0f8dbf8-d75b-49ec-bb06-a71cd4ae9b82 followers_count: 36 following_count: 22
basic: a34be83a-cb4b-4f51-a2bc-b9a17afc1a43 followers_count: 54 following_count: 63
basic: d83b5dfc-fa3d-4982-bebe-92c031a5f5d9 followers_count: 40 following_count: 36
basic: f8fe5bbf-f243-47a6-9ca2-e0ca2a5c077d followers_count: 41 following_count: 48
basic: 1a3cf93a-ab09-4f7a-a6da-4ffba889c228 followers_count: 43 following_count: 22
basic: 05ef5008-15f2-4ea7-b5fa-15d63d3aef36 followers_count: 23 following_count: 5
basic: db25c818-d73b-4e4d-b88f-ce488e5bde3e followers_count: 40 following_count: 6
basic: 21bdd710-32eb-42e2-9541-723d1e5840f9 followers_count: 44 following_count: 6
basic: 2cdcc322-4363-4a9e-ba8c-65d5f344501b followers_count: 38 following_count: 7
basic: 5cfbae87-9036-4001-b987-c429d36b01be followers_count: 72 following_count: 67
basic: 548dd440-a039-443c-8612-3591ba67b38b followers_count: 39 following_count: 23
basic: fbe9efa7-aa6e-42b9-9424-ab0b805dd645 followers_count: 44 following_count: 38
basic: 614d477d-3832-4f1f-a60b-1762f5d9d58b followers_count: 56 following_count: 55
basic: d56f12fa-9309-4c6f-8413-bd26e2edf74b followers_count: 57 following_count: 21
basic: 65827e90-ffc7-46ef-b95f-f82ac4935869 followers_count: 24 following_count: 4
basic: c1e725a6-b373-48e4-9602-8e984f943f9f followers_count: 64 following_count: 22
basic: ed195f19-6a6d-41ba-afde-f48bfd7a41c1 followers_count: 25 following_count: 26
basic: 07cee576-be28-4c30-8f39-a870ac4d25f5 followers_count: 53 following_count: 62
basic: 4e0fed9c-8920-4368-990e-06af72e3a85a followers_count: 57 following_count: 29
basic: 93afb998-15f7-4635-836b-a0c21b3efeaf followers_count: 38 following_count: 10
basic: a832c789-8751-470a-8165-f11712ce6625 followers_count: 42 following_count: 29
basic: 4ea88139-b00b-48c4-8a78-5f26b78218b1 followers_count: 49 following_count: 8
basic: 39fd869e-a0bc-468b-9fa4-e434a608d3fc followers_count: 55 following_count: 36
basic: d80cb428-3d71-4cf7-86ca-071e2bb227c8 followers_count: 65 following_count: 26
basic: 9f07f77f-12ec-4bac-aa06-e070f09ac610 followers_count: 48 following_count: 33
basic: b3c1237b-3694-442a-a4cd-c6751e973994 followers_count: 62 following_count: 54
basic: 2d9ae9fd-44a9-4e6b-bf82-9fa8d2be9113 followers_count: 69 following_count: 17
basic: 9cd58707-c497-45db-9bea-1df9343c09a7 followers_count: 58 following_count: 15
basic: 419f3d51-fe3a-41f9-8985-d439f590d7ee followers_count: 49 following_count: 21
basic: 4932731a-8a19-4664-8ce4-09ff9524ea8e followers_count: 55 following_count: 63
basic: 324a1f44-ef5d-4888-a730-b9703544faf5 followers_count: 70 following_count: 48
basic: 0f73e182-bb4d-4f94-b2d7-5dffba21b74f followers_count: 64 following_count: 37
basic: 67addfc5-c9c3-4354-b2f4-7fde0b205b1a followers_count: 70 following_count: 37
basic: 6f6003f8-6cf9-4077-ae6f-6609f337d643 followers_count: 62 following_count: 6
basic: 9c522939-3ef9-4b1c-93eb-697e1be4ca68 followers_count: 53 following_count: 20
basic: 680c8400-855c-4a73-b4f6-c2389e954b3f followers_count: 51 following_count: 35
basic: 7c226e42-5441-4cde-880f-7bb24b70ae5c followers_count: 36 following_count: 11
basic: 5a68035a-e5e0-474d-baf6-cd0a9e1dc7f1 followers_count: 80 following_count: 61
basic: b75395be-badb-4c8e-a6c8-dcc766887149 followers_count: 60 following_count: 20
basic: b4881347-f1c7-4bef-a03a-6f09bacc7858 followers_count: 42 following_count: 13
basic: c308d69e-5a8a-4b12-bd27-dc31bd808743 followers_count: 60 following_count: 28
basic: ae5633e4-b9d4-4b27-973f-6783007f0249 followers_count: 74 following_count: 60
basic: 31e072f2-7391-4193-840e-964cce908736 followers_count: 37 following_count: 15
basic: 5369610d-4b6b-4332-8273-dc29346c9b77 followers_count: 57 following_count: 64
basic: 960a6cea-0b7c-47ce-bc22-6d74d51148c1 followers_count: 72 following_count: 15
basic: 5bf4e968-bd6f-4db1-a589-d9a2039de081 followers_count: 35 following_count: 4
basic: b557c8eb-dbe9-48ef-a3ab-8c43ea4e5b62 followers_count: 57 following_count: 6
basic: 82bf4248-925c-4f38-a8e9-b79c99d7f5e2 followers_count: 45 following_count: 29
basic: 252a4b9c-8888-4366-b6d0-3a32944e32d2 followers_count: 53 following_count: 9
basic: 6988daef-a97d-46c4-8888-f919e08ca64d followers_count: 63 following_count: 39
basic: a7a8c05a-f246-4a98-acc3-aa2a06671fa0 followers_count: 70 following_count: 73
basic: 74df0e5c-cbaf-4358-8963-9d9ab9532cb9 followers_count: 37 following_count: 26
basic: 36d2f734-be42-4751-bc58-eaa16a8ae7a3 followers_count: 34 following_count: 11
basic: e2e44086-921a-4537-a659-2a3683b0afcb followers_count: 75 following_count: 31
basic: 1ceedfa2-7345-4a7d-966f-81b03530f549 followers_count: 61 following_count: 12
basic: 3d646ea6-2cfb-416a-95c0-da4596aa7b08 followers_count: 79 following_count: 46
basic: edca2ae5-bbdb-41de-a826-a26808e5cb9b followers_count: 65 following_count: 10
basic: eec118af-1455-4e6f-9df6-cd1613943d21 followers_count: 61 following_count: 26
basic: e81fa74f-3f83-43cb-9297-fad4a5b77087 followers_count: 52 following_count: 24
basic: 238211ef-4c09-4978-9182-fe97cb770ffd followers_count: 33 following_count: 3
basic: 6d075bd3-75cd-4bff-8df8-850a0b8f0522 followers_count: 43 following_count: 17
basic: ef0ea395-0e15-4214-9480-2a5af68d0c61 followers_count: 78 following_count: 23
basic: 2055d41a-e6ec-4911-99e9-706fa223c17f followers_count: 33 following_count: 12
basic: f1ff7836-3de2-4577-bafa-687eb3feff48 followers_count: 36 following_count: 20
basic: fdb4c829-8305-452c-b27d-568319a1c46f followers_count: 52 following_count: 45
basic: c0aad6c5-3e17-425e-95e4-fda20d7d9986 followers_count: 60 following_count: 21
basic: 0c359940-f4d1-45e7-bdc2-90e1ae58e853 followers_count: 39 following_count: 44
basic: 5fd381cf-e2a6-4340-b137-e0dbcf7807f2 followers_count: 44 following_count: 11
basic: b4be1f53-29c9-48ce-83cd-6b5f09b5669d followers_count: 61 following_count: 62
basic: b2e94751-dd2e-4027-b883-b10d6add925d followers_count: 61 following_count: 40
basic: bf730f88-077b-47b8-9dcf-2d389aeaf809 followers_count: 56 following_count: 22
basic: 7f4116df-0dd7-47df-a4de-bc76e7cab3bb followers_count: 50 following_count: 5
basic: d6923c4e-659a-41bd-807d-1d81245828d3 followers_count: 45 following_count: 35
basic: dc7e5ce8-e576-486c-85d0-78491da39cfe followers_count: 17 following_count: 5
basic: c9123494-52ca-4867-bcc6-ff4d8fce18a2 followers_count: 22 following_count: 23
basic: 31a04c69-1c96-4de9-a24e-b3423b863c5a followers_count: 53 following_count: 15
basic: ee4ca3be-6e17-4e39-a543-0c8eda3b0933 followers_count: 46 following_count: 18
basic: f7a25421-fac2-47c0-a49c-83c0027c1a52 followers_count: 58 following_count: 18
basic: a3a998e6-013f-4667-88c6-7e2881c940c3 followers_count: 58 following_count: 35
basic: ad46b37a-0b77-43f0-8805-9b7e549b8243 followers_count: 49 following_count: 11
basic: 3f7f8735-3bd3-4581-90c2-a154115a24ea followers_count: 50 following_count: 24
basic: dd0e6745-3eb6-4d38-b433-5dd96b156d39 followers_count: 70 following_count: 38
basic: ad82eea5-98b7-4d46-9490-0ddc1daaf2c9 followers_count: 75 following_count: 71
basic: 4aa8b1f6-151c-4288-88a6-cb254814f88d followers_count: 71 following_count: 75
basic: f9d10109-e1c0-4de6-8dc6-2139cc4dcfce followers_count: 55 following_count: 45
basic: 4b975afb-cac6-4fd6-81e1-d76e9449b02d followers_count: 33 following_count: 36
basic: 0d27ab62-785d-48f5-aafa-82a0408e61e8 followers_count: 71 following_count: 83
basic: 3acfa21b-13e1-4ae5-a7b2-2d48e1f463a3 followers_count: 41 following_count: 25
basic: 176319c6-39da-4cbe-89f5-dbcd0b185d5f followers_count: 31 following_count: 37
basic: e05ac416-96bd-4425-a660-104dddf8e64d followers_count: 48 following_count: 23
basic: 29b5842d-82bd-4c72-83cd-ace94bb6ae38 followers_count: 32 following_count: 29
basic: 085907b2-babe-48df-9e92-56dce029be76 followers_count: 58 following_count: 15
basic: c6daf48d-36cd-409e-a64c-a0778130e036 followers_count: 66 following_count: 10
basic: f054d59e-561d-4bb9-bc84-e61cafc6c653 followers_count: 60 following_count: 14
basic: bf2c8b7a-b798-4c81-ac98-94577ea0a266 followers_count: 46 following_count: 44
basic: 2ddb25cc-76cd-4dd1-b586-ed0a506e07f3 followers_count: 13 following_count: 7
basic: d602c2dc-41d0-4fc3-b6c6-1c0f2dcb86bc followers_count: 78 following_count: 76
basic: 71bc814f-06ca-459e-98a8-bd5407e0826a followers_count: 15 following_count: 9
basic: c95ff50e-9f8f-472f-b49f-4b071fe0cc77 followers_count: 57 following_count: 23
basic: e7c5162d-c18f-47e4-88ab-721cede965a7 followers_count: 31 following_count: 30
basic: 5f67d277-8ec9-4ac2-b412-810699e16ba2 followers_count: 32 following_count: 15
basic: 76c64c1e-92e2-4a39-a7e4-f7648cb609eb followers_count: 51 following_count: 42
basic: d895a794-a499-4169-9cc9-40bcec0d08d9 followers_count: 23 following_count: 12
basic: bf33ac55-4e1c-4857-a4be-0b7439765e9d followers_count: 29 following_count: 7
basic: 487cca26-5c12-4499-9d1d-1fe7635cc55e followers_count: 44 following_count: 41
basic: 3858dc0e-76c6-47b8-a4e8-e5f5abce9a2e followers_count: 25 following_count: 19
basic: f452aaba-9382-4f6f-b7e8-e511440df764 followers_count: 59 following_count: 30
basic: 1c5ba855-3c49-467e-93b3-84e25a2bc811 followers_count: 59 following_count: 13
basic: 3f81d1f9-975b-446c-babe-129db9cd2acd followers_count: 51 following_count: 53
basic: 78d4ff9b-bfcf-41ea-96bf-f3333b6c1e20 followers_count: 64 following_count: 61
basic: 14181b65-8870-432e-ac36-16bb0a33ebf2 followers_count: 57 following_count: 52
basic: 2e526b63-e28c-4abd-9fd6-94b9d9dfcab8 followers_count: 57 following_count: 30
basic: 3c3bdbf6-20bc-4d60-9f60-d4095af2ac92 followers_count: 44 following_count: 15
basic: 18bdc3c5-e457-4231-8da5-767aab0d2621 followers_count: 41 following_count: 37
basic: 50c7f421-1d44-4cec-aba8-0d96ff5d4c85 followers_count: 45 following_count: 11
basic: ffe37d54-4dde-49da-992b-8a4591e63423 followers_count: 27 following_count: 13
basic: e59d69c6-97ff-4198-acbb-0c1285bfc9dc followers_count: 76 following_count: 83
basic: 3a571f42-51f7-40b8-a7aa-7d3dff97dcf3 followers_count: 74 following_count: 36
basic: 6bd8eaf8-a351-4a24-bbc3-135be02d6d21 followers_count: 27 following_count: 9
basic: 8e1e08d8-229a-46ab-a2e9-bfdb19dd983c followers_count: 52 following_count: 41
basic: 7a3129b5-ca1b-4cbf-8a2d-88bff0a77d6d followers_count: 59 following_count: 7
basic: 394d7576-6381-446d-8c1e-01edc9871c71 followers_count: 73 following_count: 71
basic: 802909d1-50c5-44f5-a250-009eb0b49997 followers_count: 50 following_count: 23
basic: d931c0d4-c0f1-4533-a9cf-0f3fe35ddf9a followers_count: 54 following_count: 50
basic: 1f79aecb-a8bc-4e48-a165-9fb991b0afcd followers_count: 62 following_count: 33
basic: f6648c12-daa3-4799-a80e-8eff3bf0e683 followers_count: 47 following_count: 21
basic: 338c0fc3-3710-4509-a832-6d4589845936 followers_count: 73 following_count: 75
basic: 0899d5dd-8c74-4efe-af12-9cc208be8a4c followers_count: 27 following_count: 24
basic: dff8d449-3155-4d46-aab7-683f900f48be followers_count: 55 following_count: 35
basic: 187f2530-baac-4130-918b-5273ec402cba followers_count: 34 following_count: 39
basic: f829f944-d001-438b-b98f-e9e7ae5f18bd followers_count: 17 following_count: 17
basic: 28cd4a6a-fcba-42dc-9ded-5adadc24ad86 followers_count: 43 following_count: 49
basic: 52df3199-75e8-47b9-af7e-c46b5284b967 followers_count: 49 following_count: 57
basic: 7470ed7f-c5fe-49f0-a4ad-d67465c088b3 followers_count: 44 following_count: 31
basic: 48ba7baf-1714-406d-8629-286b969a283a followers_count: 63 following_count: 14
basic: c1fba776-bc09-461a-84e3-d7652d2d7dbd followers_count: 29 following_count: 8
basic: 5b9599cf-9b80-4b5e-add2-38f066cebd17 followers_count: 55 following_count: 46
basic: 995f9683-01a6-4ce5-b539-69d2365e62b3 followers_count: 29 following_count: 27
basic: ea883938-40a2-4327-b827-aed9538fc9f3 followers_count: 73 following_count: 56
basic: d5921bc2-789f-43b5-a503-e5bd22e0cb27 followers_count: 58 following_count: 21
basic: 18425520-640f-4fbc-9a77-933d1f433c28 followers_count: 37 following_count: 41
basic: 88ebf94f-d010-4cea-99a5-464b5e1845ea followers_count: 39 following_count: 14
basic: 3cdcbfdc-5dd6-4ff3-b949-6c2bf42c327c followers_count: 53 following_count: 12
basic: cac9f36c-ac8d-4747-854e-e3782cdb9ab2 followers_count: 23 following_count: 21
basic: 66cffde0-0a4e-458a-9128-cdb47ec819c1 followers_count: 72 following_count: 74
basic: 04bd3ba8-775f-427e-8df1-518dc68cfa0a followers_count: 25 following_count: 10
basic: d7d50c7f-166e-4e02-b573-3f3099d6f6e2 followers_count: 35 following_count: 15
basic: 6124a069-ea72-4454-b0ca-171472ee855c followers_count: 30 following_count: 27
basic: 480c6734-7758-40c2-96b6-a0f8760d6d59 followers_count: 29 following_count: 10
basic: 0cd1262c-b4e0-4003-b44f-22dab5ad93d5 followers_count: 23 following_count: 12
basic: dae233b3-4a61-4553-a465-88043fd2fa1d followers_count: 62 following_count: 9
basic: ab1bd2c6-57b7-4f56-9184-b7f0e210c165 followers_count: 72 following_count: 75
basic: 6df163a5-d38d-4f18-bf6e-1e71be1050b9 followers_count: 62 following_count: 70
basic: 319b9aa2-c144-4e55-ad64-530b11d72541 followers_count: 48 following_count: 12
basic: 5290fefb-68da-4b33-970a-628a716c6467 followers_count: 17 following_count: 16
basic: 51ab2fe3-1238-42c5-a870-0cb11c5dbc2b followers_count: 52 following_count: 13
basic: 38413166-1b0a-44ed-aacd-73646a05491f followers_count: 59 following_count: 22
basic: 80979556-49a4-4b28-8198-7558d7dac21d followers_count: 41 following_count: 21
basic: eeda21bd-4a7b-4cdd-8a0e-0d7ef885aad7 followers_count: 73 following_count: 76
basic: 41778a3e-b2b0-4782-8358-a8e9cf36e3d1 followers_count: 24 following_count: 28
basic: f630dba6-2f72-43f7-900b-2fdfa82b64f0 followers_count: 38 following_count: 26
basic: 5901b565-d662-4407-8553-85e0fe12a821 followers_count: 60 following_count: 14
basic: 42985940-8a63-480c-9ec7-ec471217a3ad followers_count: 46 following_count: 49
basic: 49fae61e-ffac-4e8b-8f4b-ab420a86eb2d followers_count: 31 following_count: 4
basic: 797af500-f569-43f2-8754-eca6d79b21f6 followers_count: 78 following_count: 17
basic: 35f5027b-704d-442b-a901-6d684170a963 followers_count: 71 following_count: 77
basic: a0511b84-5652-47af-b60b-5c705f6d7cf5 followers_count: 42 following_count: 42
basic: 7872e111-62c1-49f2-b7c3-6f85d3038739 followers_count: 68 following_count: 46
basic: c20bcdbb-1ca6-4512-ad94-6fc9b0bafda2 followers_count: 75 following_count: 13
basic: 48d1a17a-2161-401c-9095-6c7160431e53 followers_count: 71 following_count: 65
basic: 363940c1-ca18-43fe-a7e2-16688d94d27a followers_count: 30 following_count: 30
basic: 0804d3f8-3938-41ad-8343-8e11ed76f9a2 followers_count: 62 following_count: 41
basic: ac8980f1-9227-47e6-9798-8bde67bd1c81 followers_count: 12 following_count: 2
basic: 7675084c-4f89-45f5-9fea-636e8b564dc7 followers_count: 61 following_count: 66
basic: be528af0-bc4f-4227-a80f-1ecd79ce3935 followers_count: 39 following_count: 28
basic: 9b1a02b4-ad5e-414d-b4b1-418304ef6fd2 followers_count: 52 following_count: 16
basic: d14d2789-48ff-4393-a770-27b5ff0962b4 followers_count: 54 following_count: 46
basic: 44fa59cd-cbf1-495f-b61a-211f5140cdeb followers_count: 69 following_count: 34
basic: 7f069f6b-491e-4c0d-b72b-d328f83bf5a2 followers_count: 16 following_count: 2
basic: e54815ff-0d2c-4fd3-bb9a-0e5d1e1e69ad followers_count: 70 following_count: 25
basic: 55010b91-a5e6-4888-be34-07c06717843e followers_count: 68 following_count: 70
basic: 65672613-87cd-4716-86dc-cd4f47e79bb2 followers_count: 60 following_count: 20
basic: acc79a03-f13c-4a6f-b3f9-e2f5077f5933 followers_count: 71 following_count: 12
basic: ea328ef9-e235-434f-8673-4dcc1436e426 followers_count: 62 following_count: 31
basic: fe0f4bde-c3a6-4e55-b60c-f2cc93ffb474 followers_count: 72 following_count: 62
basic: 7fd7a5cf-4d89-4bf9-bd79-4cce28b4c17e followers_count: 41 following_count: 45
basic: 91a0ace7-f5a4-4fdb-b51f-0d1ab1cab149 followers_count: 19 following_count: 10
basic: 9c287977-225f-4eee-b052-a5fe83607761 followers_count: 57 following_count: 44
basic: 0c90a53b-4343-49a7-b13a-b2663712383b followers_count: 52 following_count: 37
basic: d5223a86-ea06-4f60-be9a-958a6b0ab5b9 followers_count: 12 following_count: 2
basic: d5c07631-741a-486a-b5ef-42fc026204b3 followers_count: 54 following_count: 17
basic: c1379caa-3507-44cd-9f35-35884a4c7703 followers_count: 61 following_count: 27
basic: a5447d93-ab8d-4797-9a24-f6bf66584d42 followers_count: 70 following_count: 24
basic: 0afadb7c-1313-43ba-ac98-0a8603707caa followers_count: 62 following_count: 49
basic: 43467c53-b332-46d2-8bd6-7b0461ea46e9 followers_count: 54 following_count: 54
basic: 17d3b2e9-c5f5-4a82-b0d7-0448036a5ec1 followers_count: 70 following_count: 29
basic: 59052d17-b44d-401b-ba0d-d6a3288566b6 followers_count: 42 following_count: 33
basic: 2af65527-afba-4f44-a8ce-d8d9978d6d17 followers_count: 62 following_count: 49
basic: ae83cfd5-2583-4fd4-88a9-51b38285188b followers_count: 27 following_count: 24
basic: 31e5be70-6291-40c1-8c2d-f487ee17efd2 followers_count: 47 following_count: 13
basic: 6db4be2c-bdaf-4ae5-b725-d8af202933eb followers_count: 24 following_count: 5
basic: 12c97c24-bee6-47fd-b47f-7c0a027cacee followers_count: 77 following_count: 65
basic: a5fdd736-da25-429f-8095-88c6a2cd6857 followers_count: 53 following_count: 16
basic: de801f2a-0125-4dc6-afff-15ea1fdf8d94 followers_count: 44 following_count: 25
basic: 2d8258c4-3c16-40b3-80c7-81592b21eed2 followers_count: 31 following_count: 14
basic: 7472999e-bbe0-44f2-a37d-cf5e09585a0f followers_count: 38 following_count: 22
basic: 387a4a20-531e-413e-ae2b-66b512c4689b followers_count: 64 following_count: 59
basic: 7242ce1f-cb91-4c6e-a5a3-2301795baa1c followers_count: 75 following_count: 46
basic: 7977df00-1421-4a07-bc6e-5c74c40cae9d followers_count: 48 following_count: 55
basic: cead5b6d-9f4f-43d6-90c4-06db8a24a8f0 followers_count: 22 following_count: 17
basic: e2b2e963-1dd0-436b-ab34-0796a7f8488c followers_count: 17 following_count: 14
basic: 4963460d-8320-47c9-bd21-556384fdacd9 followers_count: 49 following_count: 6
basic: 5babf504-32b8-469e-b0e0-20b2727f816b followers_count: 56 following_count: 23
basic: 2e086bbf-2ce8-4be8-b153-7980235b52dd followers_count: 37 following_count: 33
basic: a94f1ab2-7b0b-4631-b758-6a3df65bb037 followers_count: 47 following_count: 36
basic: 10c544a3-1899-4c87-9d9e-c21d495d2849 followers_count: 42 following_count: 34
basic: 223bde24-952d-4bfc-bcaa-b21c2121910d followers_count: 38 following_count: 44
basic: a93eb943-1dc5-4ce9-beef-a15c394fd20d followers_count: 66 following_count: 16
basic: 2c649737-d89b-4259-bed5-3f509a20e75b followers_count: 75 following_count: 79
basic: 60a80983-7db4-4aa0-a430-738e51ca05e7 followers_count: 51 following_count: 44
basic: 702b85e9-dfe6-469d-9650-e5f0a8048be4 followers_count: 53 following_count: 41
basic: 7f8d79cf-1e4a-4ad4-9434-9f2b7cd3eb5c followers_count: 48 following_count: 42
basic: 4e8a3dd1-f86f-4aa6-8986-4128eb9f2ca1 followers_count: 46 following_count: 24
basic: 18f58e2d-dbb2-4b5a-b23c-0ff3ca2a68f4 followers_count: 45 following_count: 11
basic: 0c4c731b-9f49-4d9b-af12-4a0ee2196c47 followers_count: 41 following_count: 45
basic: 0526572b-77e9-4eda-9296-2fb2a4d11774 followers_count: 41 following_count: 5
basic: 2d835eb5-15e9-4044-a610-3961f234afd1 followers_count: 48 following_count: 36
basic: c82e6c98-65c8-4da7-9cb8-49d763165743 followers_count: 28 following_count: 17
basic: 0ccc9264-aca7-4d10-b563-390e4fa81614 followers_count: 52 following_count: 15
basic: 08ba97ac-9cfa-4a51-9c3d-16e511ac4a8b followers_count: 75 following_count: 19
basic: 94e8836d-255a-47a8-a2b1-619d16f51379 followers_count: 43 following_count: 7
basic: 273e369c-5e1b-4a0e-9c94-6dea53e4f80f followers_count: 70 following_count: 28
basic: 94fb3f65-21e0-494b-998c-a63ba8c4453d followers_count: 42 following_count: 8
basic: f84669fe-660a-4bc5-9be2-eaddd5061f01 followers_count: 40 following_count: 18
basic: 920aa1ae-8bbb-4dae-88e8-11101e676ef9 followers_count: 27 following_count: 18
basic: d84c3791-68c1-438a-a8a3-73808515773d followers_count: 72 following_count: 67
basic: 7610c984-b76c-4afc-a6a8-ea3c136707f4 followers_count: 56 following_count: 57
basic: 673e236c-e4bf-41d3-b1ec-664194e09a9e followers_count: 40 following_count: 25
basic: 782e0411-096f-4924-9a26-5a5440407d1d followers_count: 25 following_count: 17
basic: 6009731e-1f97-4135-98b5-79044be0dc7b followers_count: 37 following_count: 34
basic: 3d3d2eb0-5269-43f8-adc9-f2c69360e0ee followers_count: 17 following_count: 4
basic: 39d0ea54-3f07-4539-b4f9-9254eb377d94 followers_count: 61 following_count: 53
basic: 8ef00524-91e8-4b3a-b574-83e80b0f2672 followers_count: 14 following_count: 15
basic: 08edbff0-ff69-4fc8-985a-a37eb30af54e followers_count: 20 following_count: 10
basic: 48cdf153-6868-45e0-9098-4e867cb57dcd followers_count: 79 following_count: 29
basic: bbcd42bb-39ae-468d-b0ec-6e23c3861ff4 followers_count: 62 following_count: 37
basic: c352640e-5739-43ef-a731-29495f946a8c followers_count: 31 following_count: 21
basic: 2c3a262a-8358-4d8a-8c97-85513925dc20 followers_count: 65 following_count: 33
basic: 13a35b19-240f-4b19-bf28-3ef5940da0e6 followers_count: 80 following_count: 23
basic: 672be2ab-ef5e-42be-8665-e814fa870a8a followers_count: 60 following_count: 54
basic: 1d900db3-cf33-44d5-aebe-bbed30c0f5b6 followers_count: 53 following_count: 34
basic: 51b29767-03ba-4cde-be4c-1dedc624a842 followers_count: 46 following_count: 39
basic: 364318f2-98f2-42e0-8d13-8dd7827e3892 followers_count: 59 following_count: 26
basic: 47a430e4-2bac-42e5-a8d0-a0c69719c6a5 followers_count: 57 following_count: 38
basic: 8db0a2ce-66f0-41a8-8d6f-01607c84ec06 followers_count: 67 following_count: 31
basic: de1e2fa6-47dd-42e7-aa57-2e82b790147c followers_count: 29 following_count: 7
basic: 154bc290-657e-4271-b247-4a9448261316 followers_count: 46 following_count: 38
basic: c1ca794b-e21e-4ceb-9d9a-bbfd58c291f9 followers_count: 61 following_count: 19
basic: c703f8db-86ef-43a8-9720-e0413a2de462 followers_count: 50 following_count: 41
basic: 83d858d8-4706-4763-b35a-e2156fc5cce3 followers_count: 66 following_count: 68
basic: f4264820-6815-4f66-ac57-349e866eb2ba followers_count: 67 following_count: 67
basic: a7ed9aed-c6df-4824-820b-ee789e424cec followers_count: 43 following_count: 48
basic: 72f43990-24c0-43f9-8ade-e1690e28d92a followers_count: 36 following_count: 38
basic: d82aeba0-7467-4a2a-bf04-589076a99a37 followers_count: 59 following_count: 30
basic: b82c956d-8e5b-4f63-807c-0ca2b47b54ff followers_count: 65 following_count: 34
basic: 9c74a868-b882-415d-80b1-21f8e490d723 followers_count: 61 following_count: 62
basic: 987aee01-2085-46b5-abe8-893190ba3e1a followers_count: 17 following_count: 16
basic: 158f5249-b957-4078-9f70-8764775d436c followers_count: 67 following_count: 47
basic: 60b4f402-95b5-4b69-a75a-f1d389df8470 followers_count: 54 following_count: 56
basic: 735e12e1-47b5-40f5-bb0d-23c983a344d2 followers_count: 68 following_count: 51
basic: 50257d50-81a4-4fb1-b7e1-c06baadb8eea followers_count: 75 following_count: 75
basic: 64e3fe95-e9d8-4ed3-bf70-9e167ca7c19b followers_count: 48 following_count: 26
basic: 5d9f64b2-7393-4937-9a05-e1d0b6f87e79 followers_count: 32 following_count: 28
basic: 40705740-3ceb-4893-a0c0-b35f8ac33660 followers_count: 75 following_count: 20
basic: 99e6a4fd-549d-4829-9619-e000b05b310c followers_count: 54 following_count: 31
basic: 55dfcecc-de4d-4fb2-b29c-db2c5f55f857 followers_count: 53 following_count: 23
basic: 0264ac99-5947-40de-a0b2-99d1abfdbfae followers_count: 55 following_count: 6
basic: b3f72391-100f-49f3-93dd-617a4fdf8e26 followers_count: 53 following_count: 54
basic: 89738599-45ea-417b-8519-7c707047f287 followers_count: 48 following_count: 33
basic: 4d5d562e-21e0-4c3a-a525-5318d730978b followers_count: 42 following_count: 35
basic: 708baa8d-999b-4c34-81c7-a93baf85a7f0 followers_count: 52 following_count: 8
basic: db9936e6-3491-490a-a6c8-dd030aa0134b followers_count: 55 following_count: 6
basic: 850a5c6b-7ee0-4cb6-b584-80c139ad955d followers_count: 48 following_count: 9
basic: a8195b6a-81c2-435d-a6c3-4cbc6a28ee8d followers_count: 77 following_count: 15
basic: d58b2000-db1d-4019-abe4-dc6e8beccef9 followers_count: 49 following_count: 44
basic: e99e8b72-0c3c-40ff-8faa-abe73ec454bd followers_count: 62 following_count: 35
basic: a5931413-cc35-4267-9f5c-faa2619bd50e followers_count: 67 following_count: 74
basic: 2b546c4a-f245-4f62-b12d-954d89c17976 followers_count: 55 following_count: 40
basic: c3314e21-acc9-4cb7-9db4-ebb11d53b079 followers_count: 68 following_count: 71
basic: 4724b1a1-79bf-41d1-b43c-6c0d402740bd followers_count: 42 following_count: 27
basic: 45a29345-f66f-4c9a-b734-9d4fd1a3c824 followers_count: 40 following_count: 21
basic: 144162ef-b24a-4c06-8cd7-54ebe3e658c2 followers_count: 67 following_count: 58
basic: eff1befb-0c75-4035-85b7-d74544011006 followers_count: 48 following_count: 49
basic: 20b43e1b-f933-4fae-b11d-e25bdb87ba8a followers_count: 64 following_count: 36
basic: b94d450a-80a6-4641-9b61-9a1383fee537 followers_count: 60 following_count: 64
basic: d7b69f8c-f3df-446c-aad7-b7f8d5479e26 followers_count: 47 following_count: 27
basic: 5ba861b0-675e-4997-b37b-5660f01304dd followers_count: 31 following_count: 8
basic: a05c2d9a-9b90-4a67-b16d-64b0e7c32b2a followers_count: 60 following_count: 11
basic: 26d5b4e8-f784-4148-9ca4-6213f6163668 followers_count: 19 following_count: 4
basic: 4469a23b-9d67-47cc-b0e6-9dff9631dd46 followers_count: 10 following_count: 3
basic: 9f696976-f47d-4627-9043-e3e53bd34a81 followers_count: 66 following_count: 40
basic: 89c5979e-16b5-407b-9f83-276d6572a47f followers_count: 79 following_count: 39
basic: b34cb123-afba-476c-a8a4-87279b48b54e followers_count: 41 following_count: 20
basic: 426f3fc1-2175-43d3-bdd3-c123031a9521 followers_count: 65 following_count: 13
basic: fcf531bc-1142-4ab5-900e-75ebcaa749eb followers_count: 18 following_count: 9
basic: 13f20238-15ae-41fb-86c9-ea4eeb2e36c4 followers_count: 66 following_count: 79
basic: 62556a45-c47e-4e17-8b56-2d5b2f948f3d followers_count: 41 following_count: 6
basic: d256f6f9-4ec6-4789-a88f-824477daf569 followers_count: 73 following_count: 24
basic: 5c4150e3-8b98-4976-9809-cc2a2750c462 followers_count: 33 following_count: 30
basic: 10034690-d403-47a7-9b15-71dc5836fea3 followers_count: 79 following_count: 26
basic: 9a123194-0c0f-40bf-b58d-32ca0fd2e859 followers_count: 77 following_count: 36
basic: f5f9d57e-91bc-4ed0-b0ac-f5e2b4889fc1 followers_count: 54 following_count: 35
basic: 866165a2-c422-4668-9ef9-3fd929b1a763 followers_count: 66 following_count: 11
basic: 38465aea-c368-4c93-b8dd-c664f1f7fce2 followers_count: 51 following_count: 40
basic: a9685f08-58dc-460e-ad61-082f83c4067d followers_count: 62 following_count: 40
basic: 4aa8415a-6c86-4283-978b-b2fac607ad59 followers_count: 72 following_count: 35
basic: fa0c8c5e-70a7-4ad0-b7a1-d53910d65d29 followers_count: 47 following_count: 31
basic: 581ccb2e-998c-4991-822d-d059b45f1fa3 followers_count: 16 following_count: 1
basic: 08638607-4525-4b93-8da9-8999f31f0a3c followers_count: 21 following_count: 4
basic: aff636ff-2dd7-40b8-b0c6-d6df8cbb192a followers_count: 38 following_count: 22
basic: 1a90be86-d1e7-4655-92aa-80334642ccd0 followers_count: 41 following_count: 14
basic: 6c65a6c3-f345-4637-b4ff-a1070aa66d2e followers_count: 40 following_count: 31
basic: 0dd92e04-161c-4036-8ae7-83362dcee4cb followers_count: 8 following_count: 7
basic: 3517060f-0ca6-4a3f-82a8-4376d9a1d473 followers_count: 27 following_count: 16
basic: 2cf698d6-2e66-4bbd-9797-21cdbc756bdc followers_count: 68 following_count: 37
basic: d5f84616-728d-4e36-baf3-7f6a17718e2e followers_count: 27 following_count: 22
basic: b0fc2d89-3323-4ed3-a4c0-ba2bdfead514 followers_count: 50 following_count: 25
basic: 4d98aac8-c8be-4415-9289-c11f8507b0a1 followers_count: 46 following_count: 21
basic: 801a5c2c-0b02-4908-9dc1-d31a097605f7 followers_count: 65 following_count: 53
basic: 2d9e993c-881c-4f8e-b8f5-959fdc40cd9e followers_count: 74 following_count: 66
basic: 7a759456-48fb-45ff-b0de-25ccc610a82b followers_count: 54 following_count: 38
basic: b102926a-7319-4cdd-bba3-fcd89b4a0a22 followers_count: 39 following_count: 33
basic: 2ea6fd00-6c69-4930-a177-44da1a56f014 followers_count: 47 following_count: 4
basic: 0f24de26-48d4-4f09-a785-3c9a78d36971 followers_count: 28 following_count: 32
basic: 296539eb-6872-4ba1-b700-1be40ad87298 followers_count: 61 following_count: 47
basic: 5e1bec3e-5f52-4a82-8091-27dc32572ad2 followers_count: 25 following_count: 26
basic: 7103354c-d2f8-4dd0-a829-0a6435a582b6 followers_count: 79 following_count: 40
basic: ff99faaa-b0f7-4608-b705-7074685ff8f7 followers_count: 47 following_count: 38
basic: 5e2a8159-6476-4b2e-9723-47462ecebe19 followers_count: 11 following_count: 9
basic: 5c58fc97-240c-4ca9-9210-69a24a6ec718 followers_count: 12 following_count: 2
basic: 42d41430-5426-4d6a-a141-fa5d7cdbd3b3 followers_count: 36 following_count: 38
basic: 5c01e155-bb3c-4914-951f-ffa0050560cc followers_count: 62 following_count: 29
basic: 68faeb22-1746-44fe-b761-73096cf81388 followers_count: 59 following_count: 56
basic: 1da6d74a-1dbd-467b-89ed-131ab79f0a58 followers_count: 19 following_count: 13
basic: d9c0a635-24b1-4045-920c-23f63b31bc30 followers_count: 56 following_count: 22

"""