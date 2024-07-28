class Actor:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def get_total_influence(self):
        return sum(account.influence_score for account in self.accounts)

    def coordinate_action(self, message, accounts_to_use):
        #TODO: probably since we are going to use an LLM, we could batch this operation so that the LLM generates a central message and based on the number of accounts it generates that many variation of that message
        for account in accounts_to_use:
            account.post_message(message)
