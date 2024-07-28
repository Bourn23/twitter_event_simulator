from textwrap import dedent
from crewai import Task

class TweetGenerationTasks:
    def generate_tweets_task(self, agent, user_bios, scenarios):
        return Task(
            description=dedent(f"""\
                Generate synthetic tweets based on the following user biographies and scenarios:
                User Biographies:
                {user_bios}
                Scenarios:
                {scenarios}
                
                Instructions:
                1. Analyze the user biographies and scenarios provided.
                2. Generate realistic tweets that align with each user's background and the given scenarios.
                3. Ensure the tweets are diverse in style, length, and content.
                4. Use appropriate hashtags, mentions, and emojis where relevant.
                5. Your final answer should be a list of generated tweets, one for each user biography and scenario combination.
                """),
            agent=agent
        )

    def evaluate_tweets_task(self, agent, generated_tweets, user_bios, scenarios):
        return Task(
            description=dedent(f"""\
                Evaluate the authenticity and quality of the following generated tweets:
                Generated Tweets:
                {generated_tweets}
                
                User Biographies:
                {user_bios}
                Scenarios:
                {scenarios}
                
                Instructions:
                1. Assess each tweet for realism, consistency with the user biography, and relevance to the scenario.
                2. Check for appropriate use of language, hashtags, mentions, and emojis.
                3. Evaluate the diversity and creativity of the tweets.
                4. Identify any potential issues or improvements.
                5. Your final answer should be a detailed evaluation report for each tweet, including a score out of 10 and specific feedback.
                """),
            agent=agent
        )

    def optimize_instructions_task(self, agent, generator_performance, evaluator_feedback):
        return Task(
            description=dedent(f"""\
                Optimize the instructions for the Generator and Evaluator agents based on their recent performance:
                Generator Performance:
                {generator_performance}
                Evaluator Feedback:
                {evaluator_feedback}
                
                Instructions:
                1. Analyze the Generator's performance and the Evaluator's feedback.
                2. Identify areas for improvement in tweet generation and evaluation processes.
                3. Formulate updated instructions for both the Generator and Evaluator agents.
                4. Ensure the new instructions address any weaknesses or biases observed.
                5. Your final answer should be two sets of updated instructions: one for the Generator and one for the Evaluator.
                """),
            agent=agent
        )

    def determine_objectives_task(self, agent, current_trends, user_demographics):
        return Task(
            description=dedent(f"""\
                Determine high-level objectives for tweet generation optimization based on current trends and user demographics:
                Current Trends:
                {current_trends}
                User Demographics:
                {user_demographics}
                
                Instructions:
                1. Analyze the provided current trends and user demographics.
                2. Identify key factors that should influence tweet generation.
                3. Predict emerging patterns or shifts in user behavior on the platform.
                4. Formulate clear, actionable objectives for optimizing tweet generation.
                5. Your final answer should be a list of 3-5 high-level objectives, each with a brief explanation of its importance and potential impact.
                """),
            agent=agent
        )