from crewai import Crew, Process, AgentPlanner
from tasks import TweetGenerationTasks
from agents import TweetGenerationAgents
from tools import TweetGenerationTools

def generate_tweets(user_bios, scenarios, current_trends, user_demographics):
    tasks = TweetGenerationTasks()
    agents = TweetGenerationAgents()
    tools = TweetGenerationTools()

    # Create Agents
    generator_agent = agents.generator_agent()
    evaluator_agent = agents.evaluator_agent()
    meta_optimizer_agent = agents.meta_optimizer_agent()
    foreseer_agent = agents.foreseer_agent()

    # Assign tools to agents
    generator_agent.add_tool(tools.access_synth_database)
    generator_agent.add_tool(tools.write_synth_database)
    generator_agent.add_tool(tools.interact_with_llm)

    evaluator_agent.add_tool(tools.access_real_database)
    evaluator_agent.add_tool(tools.interact_with_llm)

    meta_optimizer_agent.add_tool(tools.modify_agent_instructions)
    meta_optimizer_agent.add_tool(tools.interact_with_llm)

    foreseer_agent.add_tool(tools.interact_with_llm)

    # Create Tasks
    determine_objectives = tasks.determine_objectives_task(foreseer_agent, current_trends, user_demographics)
    generate_tweets = tasks.generate_tweets_task(generator_agent, user_bios, scenarios)
    evaluate_tweets = tasks.evaluate_tweets_task(evaluator_agent, "{{generate_tweets.result}}", user_bios, scenarios)
    optimize_instructions = tasks.optimize_instructions_task(meta_optimizer_agent, "{{generate_tweets.result}}", "{{evaluate_tweets.result}}")

    # Create Crew
    crew = Crew(
        agents=[generator_agent, evaluator_agent, meta_optimizer_agent, foreseer_agent],
        tasks=[determine_objectives, generate_tweets, evaluate_tweets, optimize_instructions],
        process=Process.hierarchical,
        memory=True,
        verbose=True,
        planning=True
    )

    # Execute the crew
    results = crew.kickoff()

    return results

if __name__ == "__main__":
    print("## Welcome to the Tweet Generation System")
    print('----------------------------------------')

    # Get user input
    user_bios = input("Please enter user biographies (comma-separated):\n").split(',')
    scenarios = input("Please enter scenarios (comma-separated):\n").split(',')
    current_trends = input("Please enter current trends (comma-separated):\n").split(',')
    user_demographics = input("Please enter user demographics (comma-separated):\n").split(',')

    # Generate tweets
    results = generate_tweets(user_bios, scenarios, current_trends, user_demographics)

    # Print results
    print("\n\n########################")
    print("## Here are the results")
    print("########################\n")
    print("Objectives:")
    print(results[0])
    print("\nGenerated Tweets:")
    print(results[1])
    print("\nTweet Evaluation:")
    print(results[2])
    print("\nOptimized Instructions:")
    print(results[3])