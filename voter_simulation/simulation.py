import random
import asyncio
from typing import List, Dict, Any

from agents import Runner, RunContextWrapper
from twitter_mock import get_tweets_for_interests

async def simulate_twitter_reading(voter: Dict[str, Any]) -> None:
    """
    Simulate a voter reading Twitter.

    Args:
        voter: Dictionary containing the voter agent and demographics
    """
    agent = voter["agent"]
    demographics = voter["demographics"]

    try:
        # Get tweets based on voter interests
        tweets = get_tweets_for_interests(demographics.interests)

        for tweet in tweets:
            try:
                # Construct a prompt about reading the tweet
                prompt = f"""You're browsing Twitter and see this tweet about {tweet['topic']}:

"{tweet['text']}"

This tweet has {tweet['likes']} likes and {tweet['retweets']} retweets.

Based on your demographic background and current opinions, how does this tweet affect your view on {tweet['topic']}?
Decide if your opinion changes, and by how much (-4 to +4).
Use the remember_interaction tool to record this interaction and any opinion change.
"""

                # Run the agent with this prompt
                await Runner.run(
                    starting_agent=agent,
                    input=prompt,
                    context=demographics
                )
            except Exception as e:
                print(f"Error during Twitter reading for {demographics.name} on topic {tweet['topic']}: {str(e)}")
                continue
    except Exception as e:
        print(f"Error during Twitter simulation for {demographics.name}: {str(e)}")

async def simulate_conversation(voter1: Dict[str, Any], voter2: Dict[str, Any]) -> None:
    """
    Simulate a conversation between two voters.

    Args:
        voter1: First voter
        voter2: Second voter
    """
    agent1 = voter1["agent"]
    demographics1 = voter1["demographics"]
    agent2 = voter2["agent"]
    demographics2 = voter2["demographics"]

    try:
        # Choose a random topic from either voter's interests
        all_interests = list(set(demographics1.interests + demographics2.interests))
        topic = random.choice(all_interests)

        # First voter starts the conversation
        prompt1 = f"""You're having a conversation with another voter named {demographics2.name} about {topic}.

Start the conversation by sharing your thoughts on {topic}.
"""

        try:
            result1 = await Runner.run(
                starting_agent=agent1,
                input=prompt1,
                context=demographics1
            )
        except Exception as e:
            print(f"Error during conversation initiation by {demographics1.name}: {str(e)}")
            return

        # Second voter responds
        prompt2 = f"""You're having a conversation with another voter named {demographics1.name} about {topic}.

They said: "{result1.final_output}"

Respond to their comment and share your own perspective on {topic}.
After responding, use the remember_interaction tool to record this conversation and any opinion change.
"""

        try:
            result2 = await Runner.run(
                starting_agent=agent2,
                input=prompt2,
                context=demographics2
            )
        except Exception as e:
            print(f"Error during conversation response by {demographics2.name}: {str(e)}")
            return

        # First voter gets final response
        prompt3 = f"""Continuing your conversation with {demographics2.name} about {topic}.

They responded: "{result2.final_output}"

Consider their perspective. Has it changed your opinion on {topic}? By how much (-4 to +4)?
Use the remember_interaction tool to record this conversation and any opinion change.
"""

        try:
            await Runner.run(
                starting_agent=agent1,
                input=prompt3,
                context=demographics1
            )
        except Exception as e:
            print(f"Error during conversation conclusion by {demographics1.name}: {str(e)}")
    except Exception as e:
        print(f"Error during conversation between {demographics1.name} and {demographics2.name}: {str(e)}")

async def run_simulation(population: List[Dict[str, Any]], rounds: int = 10) -> None:
    """
    Run the voter simulation for a specified number of rounds.

    Args:
        population: List of voter dictionaries
        rounds: Number of simulation rounds to run
    """
    print(f"Starting simulation with {len(population)} voters for {rounds} rounds...")

    for round_num in range(1, rounds + 1):
        print(f"\nRound {round_num} of {rounds}")

        # For each voter, decide whether to read Twitter or talk to another voter
        for i, voter in enumerate(population):
            print(f"Simulating voter {i+1}/{len(population)}: {voter['demographics'].name}")

            try:
                # 50% chance of reading Twitter, 50% chance of conversation
                if random.random() < 0.5:
                    print(f"  - Reading Twitter")
                    await simulate_twitter_reading(voter)
                else:
                    # Choose a random different voter to talk to
                    other_voters = [v for j, v in enumerate(population) if j != i]
                    if other_voters:  # Make sure there are other voters
                        other_voter = random.choice(other_voters)
                        print(f"  - Conversing with {other_voter['demographics'].name}")
                        await simulate_conversation(voter, other_voter)
                    else:
                        print(f"  - No other voters to converse with, reading Twitter instead")
                        await simulate_twitter_reading(voter)
            except Exception as e:
                print(f"Error simulating voter {voter['demographics'].name}: {str(e)}")
                continue

        print(f"Completed round {round_num}")

    print("\nSimulation complete!")
