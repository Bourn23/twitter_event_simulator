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
openai_api_key = "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"



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
        max_workers = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
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
                    self.process_action(user, (action_info[0],action_info[1]), action_info[2], action_info[3])

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
            print("API error in generate_post", e)
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
        # world.simulate_social_media_activity()
        world.simulate_social_media_activity_parallel()
        
        if world.current_time.minute == 0:  # Log every hour
            print(f"Simulation time: {world.current_time}, time elapsed: {time.time() - start_time:.2f} seconds.")
            world.save_tweets(f'simulation_results_{world.current_time}-parallel-10workers.json')


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
    print("Simulation completed.")