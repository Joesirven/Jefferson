import json
import random
from typing_extensions import TypedDict, Any
from random import randint, choice
from pydantic import BaseModel
from agents import Agent, function_tool, ModelSettings, RunContextWrapper
from voter_agent import VoterDemographics, create_voter_agent


class Location(TypedDict):
    zip_code: str

class Voter(BaseModel):
    name: str
    age: int
    gender: str
    income: str
    education: str
    location: Location

@function_tool
async def create_voter() -> str:

    """Create a voter Agent based on random attributes that are provided to it.

    Args:

    Returns:
        100 Agent objects with the following attributes:
            name: str
            age: int
            gender: str
            income: int
            education: str
            location: Location

    """
    # create an agent with a name, age, gender, income, education, and location

    name = "Voter" + str(randint(1, 1000000))
    age = randint(18, 80)
    gender = choice(["Male", "Female"])
    income = choice(["low", "middle", "middle", "middle", "middle", "middle", "middle", "high"])
    education = choice(["Bachelor's Degree", "Master's Degree", "PhD"])
    location = Location(zip_code=str(randint(10000, 99999)))
    instrucutions = f"You are a voter in the {location['zip_code']} zip code. You are {age} years old. You are {gender}. You make {income} dollars a year. Your education level is{education}."


    return Agent(
        name=name,
        instructions=instrucutions,
        model_settings=ModelSettings(model="o3-mini"),
        tools=[
        ],
    )

def interact(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Interact with the voter agent.

    Args:
        path: The path to the file to read.
        directory: The directory to read the file from.
    """
    # In real life, we'd read the file from the file system
    return "<file contents>"


agent = Agent(
    name="God",
    tools=[
        create_voter,

    ],
)

# DEMOGRAPHICS data for generating diverse voters
DEMOGRAPHICS = {
    "age_ranges": [(18, 29), (30, 44), (45, 64), (65, 90)],
    "genders": ["Male", "Female", "Non-binary"],
    "education_levels": ["High School", "Some College", "Bachelor's Degree", "Graduate Degree"],
    "income_levels": ["Low", "Middle", "Upper Middle", "High"],
    "political_leanings": ["Very Liberal", "Liberal", "Moderate", "Conservative", "Very Conservative"],
    "locations": ["Urban", "Suburban", "Rural"],
    "names": [
        "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
        "Matthew", "Margaret", "Anthony", "Betty", "Mark", "Sandra", "Donald", "Ashley",
        "Steven", "Dorothy", "Paul", "Kimberly", "Andrew", "Emily", "Joshua", "Donna",
        "Kenneth", "Michelle", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa"
    ],
    "interests": [
        "healthcare", "taxes", "education", "climate change", "immigration",
        "gun control", "economy", "foreign policy", "social security", "infrastructure",
        "technology", "sports", "arts", "religion", "environment", "housing"
    ],
    # Key topics that voters might have opinions on
    "key_topics": [
        "healthcare", "taxes", "education", "climate change", "immigration",
        "gun control", "abortion", "military", "police", "religion",
        "lgbtq", "marijuana", "minimum wage", "welfare"
    ]
}

# Demographic correlations to make more realistic voters
# These are simplified correlations for simulation purposes
DEMOGRAPHIC_CORRELATIONS = {
    # Political leaning correlations with age
    "age_political": {
        (18, 29): {"Very Liberal": 0.3, "Liberal": 0.3, "Moderate": 0.2, "Conservative": 0.1, "Very Conservative": 0.1},
        (30, 44): {"Very Liberal": 0.2, "Liberal": 0.3, "Moderate": 0.2, "Conservative": 0.2, "Very Conservative": 0.1},
        (45, 64): {"Very Liberal": 0.1, "Liberal": 0.2, "Moderate": 0.3, "Conservative": 0.3, "Very Conservative": 0.1},
        (65, 90): {"Very Liberal": 0.1, "Liberal": 0.2, "Moderate": 0.2, "Conservative": 0.3, "Very Conservative": 0.2}
    },
    # Political leaning correlations with location
    "location_political": {
        "Urban": {"Very Liberal": 0.3, "Liberal": 0.3, "Moderate": 0.2, "Conservative": 0.1, "Very Conservative": 0.1},
        "Suburban": {"Very Liberal": 0.1, "Liberal": 0.2, "Moderate": 0.4, "Conservative": 0.2, "Very Conservative": 0.1},
        "Rural": {"Very Liberal": 0.1, "Liberal": 0.1, "Moderate": 0.2, "Conservative": 0.3, "Very Conservative": 0.3}
    },
    # Education correlations with income
    "education_income": {
        "High School": {"Low": 0.5, "Middle": 0.4, "Upper Middle": 0.1, "High": 0.0},
        "Some College": {"Low": 0.3, "Middle": 0.5, "Upper Middle": 0.2, "High": 0.0},
        "Bachelor's Degree": {"Low": 0.1, "Middle": 0.3, "Upper Middle": 0.5, "High": 0.1},
        "Graduate Degree": {"Low": 0.0, "Middle": 0.2, "Upper Middle": 0.5, "High": 0.3}
    }
}

def weighted_choice(options_dict):
    """Choose an option based on weighted probabilities."""
    options = list(options_dict.keys())
    weights = list(options_dict.values())
    return random.choices(options, weights=weights, k=1)[0]

def generate_random_voter() -> VoterDemographics:
    """Generate a random voter with realistic demographics."""
    # Choose age range first
    age_range = random.choice(DEMOGRAPHICS["age_ranges"])
    age = random.randint(age_range[0], age_range[1])

    # Choose location
    location = random.choice(DEMOGRAPHICS["locations"])

    # Choose political leaning based on age and location
    age_political_weights = DEMOGRAPHIC_CORRELATIONS["age_political"][age_range]
    location_political_weights = DEMOGRAPHIC_CORRELATIONS["location_political"][location]

    # Combine weights (simple average)
    combined_weights = {}
    for leaning in DEMOGRAPHICS["political_leanings"]:
        combined_weights[leaning] = (age_political_weights[leaning] + location_political_weights[leaning]) / 2

    political_leaning = weighted_choice(combined_weights)

    # Choose education level
    education = random.choice(DEMOGRAPHICS["education_levels"])

    # Choose income level based on education
    income_weights = DEMOGRAPHIC_CORRELATIONS["education_income"][education]
    income_level = weighted_choice(income_weights)

    # Choose gender
    gender = random.choice(DEMOGRAPHICS["genders"])

    # Choose name
    name = random.choice(DEMOGRAPHICS["names"])

    # Select 2-5 random interests
    interests_count = random.randint(2, 5)
    interests = random.sample(DEMOGRAPHICS["interests"], interests_count)

    # Generate initial opinions on some key topics
    initial_opinions = {}

    # Opinion map based on political leaning
    opinion_map = {
        "Very Liberal": {
            "healthcare": (4, 5), "taxes": (3, 5), "education": (4, 5),
            "climate change": (4, 5), "immigration": (4, 5), "gun control": (4, 5),
            "abortion": (4, 5), "military": (1, 3), "police": (1, 3),
            "religion": (1, 3), "lgbtq": (4, 5), "marijuana": (3, 5),
            "minimum wage": (4, 5), "welfare": (4, 5)
        },
        "Liberal": {
            "healthcare": (3, 5), "taxes": (3, 4), "education": (3, 5),
            "climate change": (3, 5), "immigration": (3, 5), "gun control": (3, 5),
            "abortion": (3, 5), "military": (2, 4), "police": (2, 4),
            "religion": (2, 4), "lgbtq": (3, 5), "marijuana": (3, 5),
            "minimum wage": (3, 5), "welfare": (3, 5)
        },
        "Moderate": {
            "healthcare": (2, 4), "taxes": (2, 4), "education": (2, 4),
            "climate change": (2, 4), "immigration": (2, 4), "gun control": (2, 4),
            "abortion": (2, 4), "military": (2, 4), "police": (2, 4),
            "religion": (2, 4), "lgbtq": (2, 4), "marijuana": (2, 4),
            "minimum wage": (2, 4), "welfare": (2, 4)
        },
        "Conservative": {
            "healthcare": (1, 3), "taxes": (1, 3), "education": (2, 4),
            "climate change": (1, 3), "immigration": (1, 3), "gun control": (1, 3),
            "abortion": (1, 3), "military": (3, 5), "police": (3, 5),
            "religion": (3, 5), "lgbtq": (1, 3), "marijuana": (1, 3),
            "minimum wage": (1, 3), "welfare": (1, 3)
        },
        "Very Conservative": {
            "healthcare": (1, 2), "taxes": (1, 2), "education": (1, 3),
            "climate change": (1, 2), "immigration": (1, 2), "gun control": (1, 2),
            "abortion": (1, 2), "military": (4, 5), "police": (4, 5),
            "religion": (4, 5), "lgbtq": (1, 2), "marijuana": (1, 2),
            "minimum wage": (1, 2), "welfare": (1, 2)
        }
    }

    # Generate opinions on 3-6 random topics
    num_topics = random.randint(3, 6)
    topics_to_opine = random.sample(DEMOGRAPHICS["key_topics"], num_topics)

    for topic in topics_to_opine:
        # Get opinion range based on political leaning
        opinion_range = opinion_map[political_leaning].get(topic, (1, 5))
        # Generate opinion within that range
        opinion = random.randint(opinion_range[0], opinion_range[1])
        initial_opinions[topic] = opinion

    return VoterDemographics(
        name=name,
        age=age,
        gender=gender,
        education=education,
        income_level=income_level,
        political_leaning=political_leaning,
        interests=interests,
        location=location,
        opinions=initial_opinions,
        memory=[]
    )

def create_voter_population(count: int = 100) -> list[dict[str, Any]]:
    """
    Create a population of voter agents.

    Args:
        count: Number of voter agents to create

    Returns:
        List of dictionaries containing the agent and its demographics
    """
    population = []

    for _ in range(count):
        demographics = generate_random_voter()
        agent = create_voter_agent(demographics)

        population.append({
            "agent": agent,
            "demographics": demographics
        })

    return population

for tool in agent.tools:
    print(tool.name)
    print(tool.description)
    print(json.dumps(tool.params_json_schema, indent=2))
    print()
