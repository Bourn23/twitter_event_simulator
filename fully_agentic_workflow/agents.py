from textwrap import dedent
from crewai import Agent

class TweetGenerationAgents:
    def generator_agent(self):
        return Agent(
            role='Tweet Generator',
            goal='Generate synthetic tweets based on user bios and scenarios',
            backstory=dedent("""\
                You are an advanced AI specializing in creating realistic tweets.
                Your expertise lies in understanding user biographies and adapting
                to various scenarios to produce authentic-sounding tweets. You have
                access to a database of synthetic tweets to inform your generations."""),
            allow_delegation=False,
            verbose=True
        )

    def evaluator_agent(self):
        return Agent(
            role='Tweet Evaluator',
            goal='Evaluate the authenticity and quality of generated tweets',
            backstory=dedent("""\
                You are an expert in analyzing social media content, particularly tweets.
                Your role is to assess the realism and appropriateness of generated tweets
                based on user bios and given scenarios. You have access to a database of
                real tweets to compare against."""),
            allow_delegation=False,
            verbose=True
        )
# TODO: maybe a better description of the tasks
    def meta_optimizer_agent(self):
        return Agent(
            role='Meta-Optimizer',
            goal='Optimize the instructions for the Generator and Evaluator agents',
            backstory=dedent("""\
                You are a highly sophisticated AI system designed to fine-tune and optimize
                the performance of other AI agents. Your expertise lies in analyzing the
                output of the Generator and Evaluator agents and adjusting their instructions
                to improve the overall quality and authenticity of generated tweets."""),
            allow_delegation=True,
            verbose=True
        )

    def foreseer_agent(self):
        return Agent(
            role='Foreseer',
            goal='Determine high-level objectives for tweet generation optimization',
            backstory=dedent("""\
                You are an advanced predictive AI with a deep understanding of social media
                trends and user behavior. Your role is to foresee the most effective objectives
                for tweet generation, considering factors like current events, user demographics,
                and platform dynamics. You communicate these objectives to the Meta-Optimizer
                to guide the overall direction of the tweet generation system."""),
            allow_delegation=False,
            verbose=True
        )