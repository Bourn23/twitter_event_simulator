## Twitter Simulator using World Model

- world model (propagation module)
- tweet generator
- character generator
- user behavior model (ordinary user)
- tweet scoring model

# Generate users using LLM

1. extract a series of tweets that are then used as seed tweets for LLM to generate characters and tweet history based off
2. now you can run series of 00 through 03 which generates characters using LLM, parses it into json and save the results in the "characters_fixed_ids.json" file.
2.1. for example, once you have scraped enough information, you use 00_character_generator.py to generate characters. there are specifications regarding what the output should look like and other information. you can checkout the file itself.
2.1. then you will run 01_character_txt_to_json.py, this is to convert the initial gen_char.txt generated by 00 file to JSON. there will be some errors, especially regarding parsing tweets that have retweets in them, i.e., "". the file will output this as it being parsed, the user should manually visit the JSON file and add the new tweets to the file. Make sure to change double quotes "" to single quotes '' if they are within the tweet text.
2.2. you can now run 02_character_verify_parsing.py to ensure that all users have 10 tweets (or as many as was requested).
2.3. lastly, since these are LLM generated content there are some duplicate names and ids. 03_fix_ids.py deals with duplicate ids by assigning new uuids to the users. *NOTE* we do not deal with duplicate names for now.
3. congratulations, you have a series of generated users.

# Generate the network

1. we will use a_tweet_distribution.py to assign the number of tweets including original tweets (text only), retweets, replies, and URLs (tweets containing URLs/media).
1.1. we have defined three types of users: core, basic, and organization. The important distinction is between the core and basic users. The core users are more influential and hence more tweets are generated. basic users mainly interact with the content generated by core and organization users. 
1.2. you may adjust the generation probability of each user group in the code as well as the number of users for each group.
2. we can now take the tweet distribution data generated from previous step and generate a social graph from it. to do so, run b_social_graph_from_tweets.py. 
2.1. there are several network settings that allows for adjusting the network topology. you can compare your network statistics with a baseline network for protests. and adjust your numbers accordingly.
3. now you can run some network analysis on your generated social network. this includes finding superspreaders and superfriend groups. [based on Analyzing Social-Cyber Maneuvers for Spreading COVID-19 Pro- and Anti- Vaccine Information]

# Simulate the world

1. at this stage you have a series of synthetic users and a social network. it is now time to populate the network with the users, and start the simulation.
1.1. let's separate the core, basic, and organization users. mainly because core and organization users will have more information.
1.2. assign those to the network.



# Future work
- we can improve network modeling from users. especially, we can have connected users be identified through their tweet histories. or even make users that have the same concerns and tweet about the same concerns and group them together.

# TODOs
[x] fix the users names
[x] connect the worldmodel to LLM to either make decisions / or just tweets and retweets
[x] the LLM should use the org and core users extra information [such as valence, their BEND, and positions] when simulating them
[x] generate organization and core users (bend values)


--> how to get to show all tweets (especially tweets with better visibility) to the user? --> we used a weighting factor.

--> why no one retweets?
--> times need to be adjusted so that not all interactions with the content are all happening at the same time. we can shuffle the timestamp of interactions to anytime after the original tweet's timestamp
--> Tweet styles: content (text, text and emoji) - make sure the tweet length remains within the bounds of twitter.
--> promote hashtag use [ do we have a collection of hashtags? ]
--> we don't want user to continually send new posts (so make sure previous action is also considered) -- especially tendency to post decrease while for active engagement increases
--> there are times where a user is active and then deactive. during protest we want most of our users to be active. especially we want them to organize/coordinate the protest information.


ideas for tweet generation via LLM:
1. it's an oracle/ social media expert simulation.
2. it is the user itself.
3. ??