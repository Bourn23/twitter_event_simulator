from datetime import datetime

class UserSimulator:
    def __init__(self):
        self.current_time = datetime.strptime('2024-06-01T12:00', '%Y-%m-%dT%H:%M')
        self.users_role = {
            1: 'basic',
            2: 'basic',
            3: 'basic',
        }
        self.basic_bios = [
            {'aesop_id': 1, 'join_time': '2024-05-31T08:00', 'leave_time': '2024-06-01T18:00'},
            {'aesop_id': 2, 'join_time': None, 'leave_time': None},  # User with missing times
            {'aesop_id': 3, 'join_time': '2024-05-31T08:00', 'leave_time': '2024-06-01T09:00'},
        ]

    def get_user_property(self, user, property):
        def get_user_bio(bios, user):
            for bio in bios:
                if bio.get('aesop_id') == user:
                    return bio
            return None
        
        if self.users_role[user] == 'basic':
            user_bio = get_user_bio(self.basic_bios, user)
        else:
            raise ValueError("User not found in any biography data.")
        
        if user_bio is None:
            raise ValueError(f"User with ID {user} not found in the biography data.")
        
        return user_bio.get(property, None)

    def check_active_users(self):
        for user in self.users_role.keys():
            join_time = self.get_user_property(user, 'join_time')
            leave_time = self.get_user_property(user, 'leave_time')
            
            # Check if join_time or leave_time is not None; then check if the user is active at the current time
            if join_time is not None or leave_time is not None: # if it has no join or leave time, it is active all the time
                print("Checking user ", user)
                if self.current_time < datetime.strptime(join_time, '%Y-%m-%dT%H:%M') or \
                self.current_time > datetime.strptime(leave_time, '%Y-%m-%dT%H:%M'):
                    print(f"User {user} is not active at this time.")
                    continue  # Skip the user because they are not active at this time
            
            print(f"User {user} is active at this time.")

# Test the behavior
simulator = UserSimulator()
simulator.check_active_users()