# For more information and other detailed implementation: https://github.com/xymou/HiSim/tree/main/agentverse/abm_model

"""
DeGroot Model:

Agents update their opinions by taking a weighted average of their neighbors' opinions.
Simple but doesn't capture confirmation bias or stubbornness.


Friedkin-Johnsen Model:

Extension of DeGroot model where agents also consider their initial opinions.
Captures both social influence and individual stubbornness.


Voter Model:

Agents randomly adopt the opinion of one of their neighbors.
Simple model for binary opinions.


Sznajd Model:

Pairs of agreeing agents influence their neighbors.
Captures the idea that united groups are more influential.


Deffuant Model:

Agents only interact if their opinions are close enough (bounded confidence).
When interacting, they move their opinions closer to each other.


Hegselmann-Krause Model:

Similar to Deffuant, but agents consider all neighbors within their confidence bound simultaneously.


Social Impact Theory:

Considers the strength, immediacy, and number of sources influencing an agent.
Can model minority influence and other complex social phenomena.
"""

from mesa import Agent
import random
import numpy as np

class BehavioralModel:
    def __init__(self, agent):
        self.agent = agent

    def update_opinion(self):
        raise NotImplementedError("This method should be implemented by subclasses.")

class DeGrootModel(BehavioralModel):
    def update_opinion(self):
        neighbors = self.agent.model.grid.get_neighbors(self.agent.pos, include_center=False)
        if not neighbors:
            return
        
        weighted_opinion_sum = sum(neighbor.opinion for neighbor in neighbors) / len(neighbors)
        self.agent.opinion = weighted_opinion_sum
        self.agent.opinion = max(-1, min(1, self.agent.opinion))

class FriedkinJohnsenModel(BehavioralModel):
    def update_opinion(self):
        neighbors = self.agent.model.grid.get_neighbors(self.agent.pos, include_center=False)
        if not neighbors:
            return
        
        neighbor_opinion_sum = sum(neighbor.opinion for neighbor in neighbors) / len(neighbors)
        self.agent.opinion = self.agent.susceptibility * neighbor_opinion_sum + (1 - self.agent.susceptibility) * self.agent.opinion
        self.agent.opinion = max(-1, min(1, self.agent.opinion))

class BoundedConfidenceModel(BehavioralModel):
    def update_opinion(self):
        neighbors = self.agent.model.grid.get_neighbors(self.agent.pos, include_center=False)
        if not neighbors:
            return

        for neighbor in neighbors:
            if abs(self.agent.opinion - neighbor.opinion) < self.agent.confidence:
                mu = 0.5
                self.agent.opinion += mu * (neighbor.opinion - self.agent.opinion)
                self.agent.opinion = max(-1, min(1, self.agent.opinion))

class OrdinaryUser(Agent):
    def __init__(self, unique_id, model, behavior_model='BoundedConfidence'):
        super().__init__(unique_id, model)
        self.opinion = random.uniform(-1, 1)
        self.confidence = random.random()
        self.susceptibility = random.random()
        self.behavior_model = self.initialize_behavior_model(behavior_model)

    def initialize_behavior_model(self, model_name):
        if model_name == 'DeGroot':
            return DeGrootModel(self)
        elif model_name == 'FriedkinJohnsen':
            return FriedkinJohnsenModel(self)
        elif model_name == 'BoundedConfidence':
            return BoundedConfidenceModel(self)
        else:
            raise ValueError(f"Unknown behavior model: {model_name}")

    def step(self):
        self.update()
        self.take_action()

    def update(self):
        self.behavior_model.update_opinion()

    def take_action(self):
        actions = ['post', 'retweet', 'reply', 'like', 'do_nothing']
        probabilities = self.calculate_action_probabilities()
        chosen_action = np.random.choice(actions, p=probabilities)
        
        if chosen_action == 'post':
            self.post()
        elif chosen_action == 'post_url':
            self.post_url()
        elif chosen_action == 'retweet':
            self.retweet()
        elif chosen_action == 'reply':
            self.reply()
        elif chosen_action == 'like':
            self.like()
        else:
            pass

    def calculate_action_probabilities(self):
        base_probs = {
            'post': 0.1,
            'post_url': 0.1,
            'retweet': 0.2,
            'reply': 0.15,
            'like': 0.25,
            'do_nothing': 0.2
        }
        
        opinion_strength = abs(self.opinion)
        for action in ['post', 'retweet', 'reply', 'like']:
            base_probs[action] *= (1 + opinion_strength)
        
        total = sum(base_probs.values())
        return [base_probs[action] / total for action in ['post', 'retweet', 'reply', 'like', 'do_nothing']]

    def post(self):
        content = self.generate_content()
        self.model.add_post(self, content)

    def retweet(self):
        post = self.select_post_to_retweet()
        if post:
            self.model.add_retweet(self, post)

    def generate_content(self):
        sentiment = "positive" if self.opinion > 0 else "negative"
        strength = abs(self.opinion)
        return f"A {sentiment} post with strength {strength:.2f}"

    def select_post_to_retweet(self):
        visible_posts = self.model.get_visible_posts(self)
        if not visible_posts:
            return None
        
        similarities = [1 - abs(self.opinion - post.opinion) for post in visible_posts]
        return self.random.choices(visible_posts, weights=similarities)[0]
    

# Implementation 2
import mesa
import numpy as np
import pandas as pd
import seaborn as sns

# Define the BasicUserAgent class
class BasicUserAgent(mesa.Agent):
    """A basic agent with probabilistic decision-making."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.action_probability = 0.8  # Base action probability
        self.engagement_factor = 1.0   # Engagement factor (dynamic)
        self.tweet_history = []        # Track tweet interactions

    def calculate_engagement_factor(self):
        # Placeholder for a more complex engagement factor calculation
        return np.random.uniform(0.8, 1.2)

    def select_best_action(self, actions_today):
        # Assign weights to actions
        weights = {
            'like': 1.0,
            'reply': 1.5,
            'post': 2.0,
            'retweet': 1.2,
            'post_url': 2.5,
        }

        # Adjust weights based on context (e.g., time of day)
        hour = self.model.schedule.time
        if 6 <= hour < 12:
            weights['post'] *= 1.2
            weights['post_url'] *= 1.1
        elif 18 <= hour < 24:
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
        chosen_action = self.random.choices(list(probabilities.keys()), list(probabilities.values()))[0]
        return chosen_action

    def select_tweet_for_action(self, action, tweets):
        # Randomly select a tweet for the action
        return self.random.choice(tweets) if tweets else None

    def step(self):
        # Dynamically calculate engagement factor and time of day weight
        self.engagement_factor = self.calculate_engagement_factor()

        # Adjust the action probability based on time of day and engagement
        hour = self.model.schedule.time
        time_of_day_weight = 1.0
        if 6 <= hour < 12:
            time_of_day_weight = 1.2
        elif 18 <= hour < 24:
            time_of_day_weight = 1.1
        else:
            time_of_day_weight = 0.8

        action_probability = self.action_probability * time_of_day_weight * self.engagement_factor

        # Decide whether to take an action
        if self.random.random() < action_probability:
            actions_today = self.model.actions_available_today
            user_context = {'time_of_day': 'morning' if 6 <= hour < 12 else 'evening'}
            action = self.select_best_action(actions_today)

            # Select a tweet if the action involves one
            selected_tweet = self.select_tweet_for_action(action, self.model.tweets)

            # Update action and tweet history
            if action:
                self.tweet_history.append((action, selected_tweet))

# Define the BasicUserModel class
class BasicUserModel(mesa.Model):
    """A model with basic user agents."""

    def __init__(self, N, width, height):
        super().__init__()
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)

        # Define actions available today
        self.actions_available_today = {
            'like': 10,
            'reply': 5,
            'post': 3,
            'retweet': 4,
            'post_url': 2
        }

        # Example tweets available in the model
        self.tweets = ["Tweet 1", "Tweet 2", "Tweet 3", "Tweet 4", "Tweet 5"]

        # Create agents
        for i in range(self.num_agents):
            a = BasicUserAgent(i, self)
            self.schedule.add(a)
            # Place agents on the grid randomly
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        # Advance the model by one step
        self.schedule.step()

# Example of running the updated Basic User Model
if __name__ == "__main__":
    # Initialize the model with 10 agents on a 10x10 grid
    model = BasicUserModel(10, 10, 10)

    # Run the model for 20 steps
    for i in range(20):
        model.step()

    # Example of analyzing and visualizing the results
    agent_tweet_history = [agent.tweet_history for agent in model.schedule.agents]
    print(agent_tweet_history)