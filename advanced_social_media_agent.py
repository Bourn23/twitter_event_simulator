import random
import numpy as np
from mesa import Agent

class AdvancedSocialMediaAgent(Agent):
    def __init__(self, unique_id, model, world_model, user_data):
        super().__init__(unique_id, model)
        self.world_model = world_model
        self.user_data = user_data
        self.influence = 1
        self.engagement_rate = random.uniform(0.1, 0.9)
        self.content_quality = random.uniform(0.1, 0.9)
        self.inactive_steps = 0

    def step(self):
        self.move()
        if self.influence > 0:
            self.interact()
        self.adjust_attributes()

    def move(self):
        # This function can be implemented if spatial movement is required
        pass

    def interact(self):
        tweets = self.world_model.get_recent_tweets_from_graph(self.unique_id)
        actions_today = self.world_model.remaining_actions.get(self.world_model.current_time.strftime('%Y-%m-%d'), {})
        
        action, selected_tweet = self.take_action(tweets, actions_today)
        
        if action:
            user_polarity = self.user_data.get('polarity', 0)
            user_subjectivity = self.user_data.get('subjectivity', 0)
            self.world_model.process_action(self.unique_id, (action, selected_tweet), user_polarity, user_subjectivity)
            self.inactive_steps = 0
        else:
            self.inactive_steps += 1

    def take_action(self, tweets, actions_today):
        base_action_probability = 0.9
        time_of_day_weight = self.calculate_time_of_day_weight()
        engagement_factor = self.world_model.calculate_engagement_factor()

        action_probability = base_action_probability * time_of_day_weight * engagement_factor
        
        if random.random() < action_probability:
            user_context = {'time_of_day': 'morning' if 6 <= self.world_model.current_time.hour < 12 else 'evening'}
            action = self.select_best_action(actions_today, user_context)
        else:
            action = None

        selected_tweet = self.select_tweet_for_action(action, tweets)
        return action, selected_tweet

    def calculate_time_of_day_weight(self):
        hour = self.world_model.current_time.hour
        if 6 <= hour < 12:
            return 1.5
        elif 18 <= hour < 24:
            return 1.9
        else:
            return 0.8

    def select_best_action(self, actions_today, user_context):
        weights = {
            'like': 0.5,
            'reply': 1.5,
            'post': 4.0,
            'retweet': 1.2,
            'post_url': 3.5,
        }

        if user_context.get('time_of_day') == 'morning':
            weights['post'] *= 1.2
            weights['post_url'] *= 1.1
        elif user_context.get('time_of_day') == 'evening':
            weights['like'] *= 1.3
            weights['reply'] *= 1.2

        action_scores = {action: count * weights[action] for action, count in actions_today.items() if count > 0}
        if not action_scores:
            return None

        total_score = sum(action_scores.values())
        probabilities = {action: score / total_score for action, score in action_scores.items()}

        return random.choices(list(probabilities.keys()), list(probabilities.values()))[0]

    def select_tweet_for_action(self, action, tweets):
        if action in ['retweet', 'reply', 'like']:
            return self.world_model.get_most_influential_tweet(tweets)
        return None

    def adjust_attributes(self):
        if self.inactive_steps > 5:
            self.engagement_rate = max(0.1, self.engagement_rate * 0.95)
        else:
            self.engagement_rate = min(0.9, self.engagement_rate * 1.05)
        
        if self.influence > self.world_model.average_influence:
            self.content_quality = min(0.9, self.content_quality * 1.02)
        else:
            self.content_quality = max(0.1, self.content_quality * 0.98)

    def calculate_interaction_strength(self, other):
        return (self.engagement_rate * other.content_quality + 
                other.engagement_rate * self.content_quality) / 2