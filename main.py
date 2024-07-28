import networkx as nx
from datetime import datetime, timedelta
import random
from abc import ABC, abstractmethod
import heapq

from datetime import datetime, timedelta

class TwitterAccount:
    def __init__(self, handle, account_type, influence_score):
        self.handle = handle
        self.account_type = account_type
        self.influence_score = influence_score
        self.followers = []
        self.posts = []

    def post_message(self, message, timestamp):
        self.posts.append({"content": message, "timestamp": timestamp})

    def get_recent_posts(self, timeframe):
        current_time = datetime.now()
        return [post for post in self.posts if (current_time - post["timestamp"]) <= timeframe]

class PersonalAccount(TwitterAccount):
    def __init__(self, handle, influence_score):
        super().__init__(handle, "personal", influence_score)

class OfficialAccount(TwitterAccount):
    def __init__(self, handle, influence_score):
        super().__init__(handle, "official", influence_score)

class BotAccount(TwitterAccount):
    def __init__(self, handle, influence_score, behavior_model):
        super().__init__(handle, "bot", influence_score)
        self.behavior_model = behavior_model

    def automated_activity(self, environment, content_generator):
        if random.random() < self.behavior_model.posting_frequency:
            content = content_generator.generate_content("bot", self.behavior_model.persona, environment)
            self.post_message(content, datetime.now())

class SockPuppetAccount(TwitterAccount):
    def __init__(self, handle, influence_score, persona):
        super().__init__(handle, "sock_puppet", influence_score)
        self.persona = persona

class BotBehaviorModel:
    def __init__(self, posting_frequency, response_triggers, amplification_targets, persona):
        self.posting_frequency = posting_frequency
        self.response_triggers = response_triggers
        self.amplification_targets = amplification_targets
        self.persona = persona

class Actor:
    def __init__(self, actor_data):
        self.id = actor_data["aesop_id"]
        self.name = actor_data["name"]
        self.type = actor_data["type"]
        self.title = actor_data["title"]
        self.leads = actor_data["leads"]
        self.age = actor_data["age"]
        self.gender = actor_data["gender"]
        self.race = actor_data["race"]
        self.nationality = actor_data["nationality"]
        self.real_person = actor_data["real_person"]
        self.bio = actor_data["ai_bio"]
        self.description = actor_data["description"]
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def get_total_influence(self):
        return sum(account.influence_score for account in self.accounts)

    def coordinate_action(self, message, accounts_to_use, timestamp):
        for account in accounts_to_use:
            account.post_message(message, timestamp)

    def update_accounts(self, environment, content_generator):
        for account in self.accounts:
            if isinstance(account, BotAccount):
                account.automated_activity(environment, content_generator)
            elif random.random() < 0.1:  # 10% chance of posting for non-bot accounts
                content = content_generator.generate_content(account.account_type, self.title, environment)
                account.post_message(content, datetime.now())


## EXAMPLE USAGE:
# anya = Actor(actor_data)

# # Add accounts for Anya
# personal_account = PersonalAccount("@AnyaCS", 75)
# official_account = OfficialAccount("@EcoVanguardArctic", 90)
# bot_behavior = BotBehaviorModel(0.05, ["climate", "arctic"], ["#SaveTheArctic"], "environmental activist")
# bot_account = BotAccount("@ArcticEcoBot", 60, bot_behavior)

# anya.add_account(personal_account)
# anya.add_account(official_account)
# anya.add_account(bot_account)


class ContentGenerator:
    """
    An actor/organization can generate a twitter account"""
    def __init__(self, llm):
        self.llm = llm

    def generate_content(self, account_type, actor_role, world_state):
        prompt = f"Generate a tweet for a {account_type} account belonging to a {actor_role}. Current world state: {world_state}"
        return self.llm.generate(prompt)
    
class Memory:
    def __init__(self):
        #TODO: initialize their memory from last twitter
        """
        idea1: (randomly-smartly) choose 10-20 tweets from previous corpora, and then ask the LLM to generate a personality and memory for each user
        idea2: provide the corpora to the LLM and ask it to generate 10-20 personality and memory for each user
        """
        self.personal_experience = []
        self.event_memory = []

    def write(self, observation, memory_type):
        if memory_type == 'personal':
            self.personal_experience.append(observation)
        elif memory_type == 'event':
            self.event_memory.append(observation)

    def retrieve(self, current_situation, k=5):
        """
        The score_memory function is a crucial component of the memory retrieval process. It assigns a numerical score to each memory based on several factors, allowing us to rank and select the most relevant memories for the current situation. Here's a breakdown of its components:

        Recency: This measures how recently the memory was created or accessed. The formula 1 / (1 + memory['timestamp'].total_seconds()) gives higher scores to more recent memories. As the time difference increases, the score approaches zero.
        Relevance: This measures how related the memory is to the current situation. It's calculated by the calculate_relevance method, which we'll brainstorm shortly.
        Importance: This is a pre-assigned value indicating how significant the memory is. It could be based on factors like emotional intensity, uniqueness, or potential impact on decision-making.
        Immediacy: This indicates how urgently the memory needs attention or action. High immediacy could be assigned to memories related to time-sensitive tasks or critical information.
        """
        def score_memory(memory):
            recency = 1 / (1 + memory['timestamp'].total_seconds())
            relevance = self.calculate_relevance(memory, current_situation)
            importance = memory.get('importance', 0)
            immediacy = memory.get('immediacy', 0)
            return recency + relevance + importance + immediacy

        all_memories = self.personal_experience + self.event_memory
        return heapq.nlargest(k, all_memories, key=score_memory)

    def calculate_relevance(self, memory, current_situation):
        #TODO: discuss and choose one method to calculate the relevance score
        relevance_score = 0

        # 1. Keyword Matching
        memory_keywords = set(self.extract_keywords(memory['content']))
        situation_keywords = set(self.extract_keywords(current_situation))
        keyword_overlap = len(memory_keywords.intersection(situation_keywords))
        relevance_score += keyword_overlap * 0.5

        # 2. Semantic Similarity
        memory_embedding = self.get_embedding(memory['content'])
        situation_embedding = self.get_embedding(current_situation)
        semantic_similarity = self.cosine_similarity(memory_embedding, situation_embedding)
        relevance_score += semantic_similarity * 2

        # 3. Entity Matching
        memory_entities = set(self.extract_entities(memory['content']))
        situation_entities = set(self.extract_entities(current_situation))
        entity_overlap = len(memory_entities.intersection(situation_entities))
        relevance_score += entity_overlap

        # 4. Temporal Relevance
        if 'timestamp' in memory and 'timestamp' in current_situation:
            time_diff = abs((memory['timestamp'] - current_situation['timestamp']).total_seconds())
            temporal_relevance = 1 / (1 + time_diff / (24 * 3600))  # Higher relevance for memories within 24 hours
            relevance_score += temporal_relevance

        # 5. Emotional Congruence
        if 'emotion' in memory and 'emotion' in current_situation:
            emotion_similarity = self.compare_emotions(memory['emotion'], current_situation['emotion'])
            relevance_score += emotion_similarity

        # 6. Action Similarity
        if 'action' in memory and 'action' in current_situation:
            action_similarity = self.compare_actions(memory['action'], current_situation['action'])
            relevance_score += action_similarity * 1.5

        # 7. Topic Modeling
        memory_topics = self.extract_topics(memory['content'])
        situation_topics = self.extract_topics(current_situation)
        topic_similarity = self.compare_topics(memory_topics, situation_topics)
        relevance_score += topic_similarity * 1.5

        return relevance_score

    def reflect(self, llm):
        #TODO: make that k = 10 a variable that is randomly generated from a distribution with prior information on how active the users are
        recent_experiences = self.retrieve(None, k=10)  # Get recent experiences
        questions = llm.generate_questions(recent_experiences)
        insights = llm.extract_insights(recent_experiences, questions)
        self.write({'type': 'reflection', 'content': insights}, 'event')

#TODO: ordinary user has a confidence level that is updated based on the world state; and a core user has a predefined profile and valence
class User(ABC):
    def __init__(self, user_id):
        self.user_id = user_id
        self.sentiment = {}
        self.knowledge = set()

    @abstractmethod
    def update(self, world_state):
        pass

    @abstractmethod
    def take_action(self, world_state):
        pass

class OrdinaryUser(User):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.confidence = random.random()  # For Bounded Confidence Model

    def update(self, world_state):
        # Implement Bounded Confidence Model logic
        pass

    def take_action(self, world_state):
        # Simpler action model for ordinary users
        actions = ['post', 'retweet', 'reply', 'like', 'do_nothing']
        return random.choice(actions)

class CoreUser(User):
    def __init__(self, user_id, llm):
        super().__init__(user_id)
        self.llm = llm  # Large Language Model
        self.profile = self.initialize_profile()
        self.memory = Memory()


    def initialize_profile(self):
        # TODO: implement initialization of user profile according to the competition
        return {
            'demographics': {},
            'social_traits': {},
            'communication_role': '',
            'valence_score': 0,
        }

    def update(self, world_state):
        self.update_memory(world_state)
        if random.random() < 0.1:  # 10% chance to reflect each update
            self.memory.reflect(self.llm)

    def take_action(self, world_state):
        relevant_memories = self.memory.retrieve(world_state)
        action = self.llm.decide_action(self.profile, relevant_memories, world_state)
        return action

    def update_memory(self, world_state):
        # Write new observations to event memory
        self.memory.write({'type': 'observation', 'content': world_state}, 'event')

#TODO: a user may form or lose connections over time, and the network structure may evolve
#TODO: weight of the network (edges between nodes) should show the strength of the connection/influence
class WorldModel:
    def __init__(self, start_date, end_date, num_core_users, num_ordinary_users, llm):
        self.start_date = start_date
        self.end_date = end_date
        self.current_time = start_date
        self.graph = nx.Graph()
        self.llm = llm
        self.initialize_users(num_core_users, num_ordinary_users)
        self.actors = []
        self.environment = Environment()
        self.content_generator = ContentGenerator(llm)

    def add_actor(self, actor):
        self.actors.append(actor)
        for account in actor.accounts:
            self.add_twitter_account_to_graph(account)

    def add_twitter_account_to_graph(self, account):
        self.graph.add_node(account.handle, account=account)
        #TODO: Add edges based on followers

    def simulate_social_media_activity(self):
        for actor in self.actors:
            for account in actor.accounts:
                if isinstance(account, BotAccount):
                    account.automated_activity(self.environment)
                else:
                    account.human_like_activity(self.environment)

    def initialize_users(self, num_core_users, num_ordinary_users):
        # Simulate the process of selecting core and ordinary users
        all_users = self.generate_all_users(num_core_users + num_ordinary_users)
        
        # Select top 100 influential users based on retweets
        influential_users = sorted(all_users, key=lambda u: u['retweets'], reverse=True)[:100]
        
        # Select additional 200 active users from their networks
        active_users = self.select_active_users(influential_users, 200)
        
        core_users = influential_users + active_users
        ordinary_users = [u for u in all_users if u not in core_users][:num_ordinary_users]

        # Create the graph
        self.graph.add_nodes_from(range(len(core_users) + len(ordinary_users)))
        
        for i, user_data in enumerate(core_users):
            self.graph.nodes[i]['user'] = CoreUser(i, self.llm)
            self.initialize_user_history(self.graph.nodes[i]['user'], user_data)
        
        for i, user_data in enumerate(ordinary_users, start=len(core_users)):
            self.graph.nodes[i]['user'] = OrdinaryUser(i)
            self.initialize_user_history(self.graph.nodes[i]['user'], user_data)

        # Add edges based on social network data
        self.add_edges_from_social_network(all_users)

    def generate_all_users(self, num_users): #TODO:AMIR
        #TODO: update the user generation process; we need more specific details on the users
        #TODO: generate all users based on a distribution of Edelman’s topology of influence (TOI)
        #TODO: add information about their background too (previous history) -- it's addressed in initialize_user_history
        # Simulate generating user data
        return [{'id': i, 'retweets': random.randint(0, 1000), 'tweets': random.randint(0, 500)} for i in range(num_users)]

    def select_active_users(self, influential_users, num_active):
        # Simulate selecting active users from the networks of influential users
        return sorted(influential_users, key=lambda u: u['tweets'], reverse=True)[:num_active]

    def initialize_user_history(self, user, user_data): #TODO:AMIR
        #TODO: we need bunch of histroical tweets to initialize the user's memory
        #TODO: update the user_data to include more details
        # Initialize user's personal experience based on historical tweets
        for _ in range(user_data['tweets']):
            user.memory.write({'type': 'tweet', 'content': 'Historical tweet'}, 'personal')

    def add_edges_from_social_network(self, all_users):
        # Simulate adding edges based on social network data
        #TODO: make this 5 a variable that is randomly generated from a distribution with prior information on how active the users are
        for _ in range(len(all_users) * 5):  # Assuming an average of 5 connections per user
            u, v = random.sample(range(len(all_users)), 2)
            self.graph.add_edge(u, v)

    def update_world_state(self):
        #TODO: the world state should be user-dependent, i.e., each user should have a different view of the world or could observe different/limited things
        world_state = self.get_world_state() # let's start with previous messages (for the entire history of the world)
            

        for node in self.graph.nodes():
            user = self.graph.nodes[node]['user']
            user.update(world_state) #TODO 1: retrieve their adjacent nodes tweets; #TODO 2: we can also employ twitter's information propagation algorithm #TODO 2: the passed information should be user-dependent + weighted randomness based on content popularity
            action = user.take_action(world_state) #TODO: generate tweets using LLMs
            self.process_action(node, action)

            # if user is an actor
            if self.graph.nodes[node]['user'] in self.actors:
                self.environment.update_environment(action) # the actors/organizations can influence the world state
                user.update_accounts(self.environment, self.content_generator)

        self.propagate_information()
        self.current_time += timedelta(minutes=15)

    def process_action(self, node, action):
        #TODO 4??: Implement logic for processing user actions (post, retweet, reply, like)
        pass

    def propagate_information(self):
        for edge in self.graph.edges():
            source, target = edge
            source_user = self.graph.nodes[source]['user']
            target_user = self.graph.nodes[target]['user']
            #TODO 3: work on the how to simulate information flow between connected users;
            # do we want to only share knowledge? do we not want to update their valence score (-1, 1)
            # also consider the weight of the edge (strength of the connection)
            shared_info = source_user.knowledge & target_user.knowledge
            target_user.knowledge.update(shared_info)

    def get_world_state(self):
        #TODO 4: think carefully what the world state contains and should be passed to the users
        return {
            'current_time': self.current_time,
            'graph': self.graph,
            # Other relevant state information
        }

#TODO: feed scenario to the world model; how does the world model gets affected by the scenario?
# is it the user generation? or the network structure ? or the user's memory?
# we need to generate a few users from the scenario database
# we need to populate their memory with historical tweets (from that database)
# we need to adjust the network structure for those known users
 #TODO 1: scenario based modeling
def run_simulation(start_date, end_date, num_core_users, num_ordinary_users, llm):
    world = WorldModel(start_date, end_date, num_core_users, num_ordinary_users, llm)
    
    while world.current_time <= world.end_date:
        world.update_world_state()
        
        if world.current_time.minute == 0:  # Log every hour
            print(f"Simulation time: {world.current_time}")
    
    return world.get_world_state()

# Usage
start_date = datetime(2024, 5, 30)
end_date = datetime(2024, 6, 3)
num_core_users = 300
num_ordinary_users = 700
llm = None  # This should be replaced with actual LLM implementation

final_state = run_simulation(start_date, end_date, num_core_users, num_ordinary_users, llm)