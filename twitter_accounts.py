
class TwitterAccount:
    def __init__(self, handle, account_type, influence_score):
        self.handle = handle
        self.account_type = account_type
        self.influence_score = influence_score
        self.followers = []

    def post_message(self, message):
        # Implementation depends on account type

class PersonalAccount(TwitterAccount):
    def post_message(self, message):
        # Personal posting logic

class OfficialAccount(TwitterAccount):
    def post_message(self, message):
        # Official account posting logic

class BotAccount(TwitterAccount):
    def __init__(self, handle, influence_score, behavior_model):
        super().__init__(handle, "bot", influence_score)
        self.behavior_model = behavior_model

    def post_message(self, message):
        # Bot-specific posting logic based on behavior model

class SockPuppetAccount(TwitterAccount):
    def post_message(self, message):
        # Sock puppet-specific posting logic