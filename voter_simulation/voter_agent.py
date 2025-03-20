from dataclasses import dataclass, field
from typing import List, Dict, Any
import random
from agents import Agent, function_tool, RunContextWrapper

@dataclass
class VoterDemographics:
    name: str
    age: int
    gender: str
    education: str
    income_level: str
    political_leaning: str
    interests: List[str]
    location: str

    # Initial opinions on various issues (1-5 scale)
    opinions: Dict[str, int] = field(default_factory=dict)

    # Memory of interactions
    memory: List[Dict[str, Any]] = field(default_factory=list)

def create_voter_agent(demographics: VoterDemographics) -> Agent[VoterDemographics]:
    """Create a voter agent with the given demographics."""

    # Define tools for the voter agent
    @function_tool
    def remember_interaction(ctx: RunContextWrapper[VoterDemographics],
                            interaction_type: str,
                            topic: str,
                            content: str,
                            opinion_change: int) -> str:
        """
        Store an interaction in the voter's memory.

        Args:
            interaction_type: Either "twitter" or "conversation"
            topic: The topic of the interaction
            content: The content of the interaction
            opinion_change: How much the voter's opinion changed (-4 to +4). Use 0 if no change.
        """
        memory_entry = {
            "type": interaction_type,
            "topic": topic,
            "content": content,
            "opinion_change": opinion_change
        }

        ctx.context.memory.append(memory_entry)

        # Update opinion if topic exists in opinions
        if topic in ctx.context.opinions:
            old_opinion = ctx.context.opinions[topic]
            new_opinion = max(1, min(5, old_opinion + opinion_change))
            ctx.context.opinions[topic] = new_opinion

            return f"Remembered {interaction_type} about {topic}. Opinion changed from {old_opinion} to {new_opinion}."
        else:
            # If topic doesn't exist yet, initialize it with a middle value plus the change
            initial_opinion = 3
            new_opinion = max(1, min(5, initial_opinion + opinion_change))
            ctx.context.opinions[topic] = new_opinion

            return f"Remembered {interaction_type} about {topic}. Initial opinion set to {new_opinion}."

    @function_tool
    def get_opinion(ctx: RunContextWrapper[VoterDemographics], topic: str) -> str:
        """
        Get the voter's opinion on a topic.

        Args:
            topic: The topic to get an opinion on
        """
        # If we already have an opinion on this topic, return it
        if topic in ctx.context.opinions:
            return f"My opinion on {topic} is {ctx.context.opinions[topic]}/5"

        # Otherwise, form an opinion based on demographics
        demographics = ctx.context

        # Normalize the topic (lowercase, remove extra spaces)
        normalized_topic = topic.lower().strip()

        # Map of topics to their typical opinion biases based on political leaning
        # Format: {topic: {political_leaning: base_opinion}}
        topic_opinion_map = {
            "healthcare": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "taxes": {
                "very liberal": 4, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "education": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 3, "very conservative": 2
            },
            "climate change": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "immigration": {
                "very liberal": 4, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "gun control": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "abortion": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "military": {
                "very liberal": 2, "liberal": 3, "moderate": 3, "conservative": 4, "very conservative": 5
            },
            "police": {
                "very liberal": 2, "liberal": 3, "moderate": 3, "conservative": 4, "very conservative": 5
            },
            "religion": {
                "very liberal": 2, "liberal": 3, "moderate": 3, "conservative": 4, "very conservative": 5
            },
            "lgbtq": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "marijuana": {
                "very liberal": 4, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 2
            },
            "minimum wage": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "universal basic income": {
                "very liberal": 4, "liberal": 3, "moderate": 2, "conservative": 1, "very conservative": 1
            },
            "welfare": {
                "very liberal": 4, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "capitalism": {
                "very liberal": 2, "liberal": 3, "moderate": 3, "conservative": 4, "very conservative": 5
            },
            "socialism": {
                "very liberal": 4, "liberal": 3, "moderate": 2, "conservative": 1, "very conservative": 1
            },
            "free speech": {
                "very liberal": 4, "liberal": 4, "moderate": 4, "conservative": 4, "very conservative": 5
            },
            "death penalty": {
                "very liberal": 1, "liberal": 2, "moderate": 3, "conservative": 4, "very conservative": 4
            },
            "patriotism": {
                "very liberal": 3, "liberal": 3, "moderate": 4, "conservative": 5, "very conservative": 5
            },
            "elon musk": {
                "very liberal": 2, "liberal": 2, "moderate": 3, "conservative": 4, "very conservative": 4
            },
            "donald trump": {
                "very liberal": 1, "liberal": 1, "moderate": 2, "conservative": 4, "very conservative": 5
            },
            "joe biden": {
                "very liberal": 3, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "barack obama": {
                "very liberal": 5, "liberal": 4, "moderate": 3, "conservative": 2, "very conservative": 1
            },
            "hitler": {
                "very liberal": 1, "liberal": 1, "moderate": 1, "conservative": 1, "very conservative": 1
            },
            "democracy": {
                "very liberal": 5, "liberal": 5, "moderate": 5, "conservative": 5, "very conservative": 4
            }
        }

        # Find the closest matching topic
        matching_topic = None
        for known_topic in topic_opinion_map.keys():
            if known_topic in normalized_topic or normalized_topic in known_topic:
                matching_topic = known_topic
                break

        # If we found a matching topic, use its opinion map
        if matching_topic:
            # Get the base opinion based on political leaning
            political_leaning = demographics.political_leaning.lower()
            base_opinion = topic_opinion_map[matching_topic].get(political_leaning, 3)

            # Add some randomness (-1, 0, or +1) to make it more realistic
            opinion_variation = random.choice([-1, 0, 0, 0, 1])
            final_opinion = max(1, min(5, base_opinion + opinion_variation))
        else:
            # For unknown topics, generate an opinion based on political leaning with more randomness
            political_scale = {
                "very liberal": 4,
                "liberal": 3.5,
                "moderate": 3,
                "conservative": 2.5,
                "very conservative": 2
            }

            # Start with a base opinion based on political leaning
            base = political_scale.get(demographics.political_leaning.lower(), 3)

            # Add more randomness for unknown topics (-2 to +2)
            variation = random.randint(-2, 2)
            final_opinion = max(1, min(5, round(base + variation)))

        # Store the opinion for future reference
        demographics.opinions[topic] = final_opinion

        return f"My opinion on {topic} is {final_opinion}/5"

    # Create the agent with appropriate instructions
    instructions = f"""You are a voter named {demographics.name}.

Your demographic information:
- Age: {demographics.age}
- Gender: {demographics.gender}
- Education: {demographics.education}
- Income Level: {demographics.income_level}
- Political Leaning: {demographics.political_leaning}
- Location: {demographics.location}
- Interests: {', '.join(demographics.interests)}

When you read Twitter or have conversations with other voters, you should:
1. Consider how the information aligns with your demographic background
2. Decide if and how much your opinion changes on the topic (from -4 to +4)
3. Use the remember_interaction tool to store this interaction and opinion change
4. Be realistic about how your demographic would respond to information

When asked for your opinion on a topic, use the get_opinion tool to provide your current stance.
Rate all opinions on a scale of 1-5 where 1 means strongly against and 5 means strongly support.

When answering polling questions:
1. Consider your demographic background and political leaning
2. Reference any past interactions or existing opinions you have on the topic
3. Provide a thoughtful response explaining your reasoning
4. End with a clear numerical rating from 1-5
"""

    return Agent[VoterDemographics](
        name=f"Voter_{demographics.name}",
        instructions=instructions,
        tools=[remember_interaction, get_opinion]
    )
