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

class OrdinaryUser(Agent):
    #TODO: impelement user initialization using the competition information and then update the functions accordingly
    """
    This implementation uses the Bounded Confidence Model for opinion updates. Users only influence each other if their opinions are close enough (within the confidence interval). The take_action method now uses probabilities based on opinion strength to determine actions, making more opinionated users more likely to engage.
    To fully implement this in a Mesa model, you'd need to create a model class that manages the overall simulation, including the grid, scheduling, and data collection. You'd also need to implement methods like add_post, add_retweet, and get_visible_posts in your model class.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.opinion = random.uniform(-1, 1)  # Opinion on a scale from -1 to 1
        self.confidence = random.random()  # For Bounded Confidence Model
        self.susceptibility = random.random()  # Susceptibility to influence

    def step(self):
        # This method will be called at each step of the simulation
        self.update()
        self.take_action()

    def update(self):
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        if not neighbors:
            return

        other = self.random.choice(neighbors)
        if isinstance(other, OrdinaryUser):  # Ensure we're interacting with another OrdinaryUser
            opinion_difference = abs(self.opinion - other.opinion)
            
            if opinion_difference < self.confidence:
                # The 'mu' parameter determines the speed of convergence
                mu = 0.5
                self.opinion += mu * (other.opinion - self.opinion)
                
                # Ensure opinion stays within [-1, 1]
                self.opinion = max(-1, min(1, self.opinion))

    def take_action(self):
        actions = ['post', 'retweet', 'reply', 'like', 'do_nothing']
        probabilities = self.calculate_action_probabilities()
        chosen_action = np.random.choice(actions, p=probabilities)
        
        if chosen_action == 'post':
            self.post()
        elif chosen_action == 'retweet':
            self.retweet()
        # ... implement other actions ...

    def calculate_action_probabilities(self):
        # Base probabilities
        base_probs = {
            'post': 0.1,
            'retweet': 0.2,
            'reply': 0.15,
            'like': 0.25,
            'do_nothing': 0.3
        }
        
        # Adjust probabilities based on opinion strength
        opinion_strength = abs(self.opinion)
        for action in ['post', 'retweet', 'reply', 'like']:
            base_probs[action] *= (1 + opinion_strength)
        
        # Normalize probabilities
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
        # Generate content based on the user's opinion
        sentiment = "positive" if self.opinion > 0 else "negative"
        strength = abs(self.opinion)
        return f"A {sentiment} post with strength {strength:.2f}"

    def select_post_to_retweet(self):
        # Select a post to retweet based on opinion similarity
        visible_posts = self.model.get_visible_posts(self)
        if not visible_posts:
            return None
        
        similarities = [1 - abs(self.opinion - post.opinion) for post in visible_posts]
        return self.random.choices(visible_posts, weights=similarities)[0]

    def take_action(self):
        actions = ['post', 'retweet', 'reply', 'like', 'do_nothing']
        chosen_action = random.choice(actions)
        # Implement the chosen action
        if chosen_action == 'post':
            self.post()
        elif chosen_action == 'retweet':
            self.retweet()
        # ... implement other actions ...

    def post(self):
        # Logic for posting a new message
        pass

    def retweet(self):
        # Logic for retweeting an existing message
        pass

    # ... other action methods ...