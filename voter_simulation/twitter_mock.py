from typing import List, Dict, Any
import random

# Mock Twitter data - in a real application, you would use the Twitter API
TOPICS = [
    "healthcare", "taxes", "education", "climate_change", "immigration",
    "gun_control", "economy", "foreign_policy", "social_security", "infrastructure",
    "technology", "sports", "arts", "religion", "environment", "housing"
]

# Sample tweets for each topic
SAMPLE_TWEETS = {
    "healthcare": [
        "The new healthcare bill will reduce costs for everyone! #healthcare #reform",
        "Why are we paying so much for healthcare when other countries pay less? #healthcare",
        "Healthcare should be a right, not a privilege. #medicare4all",
        "Government should stay out of healthcare decisions. Let the market decide.",
        "Just got my medical bill. This system is completely broken! #healthcarereform"
    ],
    "taxes": [
        "Tax cuts for the wealthy never trickle down. We need fair taxation! #taxreform",
        "Lower taxes mean more jobs and economic growth! #economy",
        "The rich need to pay their fair share of taxes. Period.",
        "My small business is struggling with these high tax rates. #smallbusiness",
        "Tax season is here and I'm shocked at how much I owe this year! #taxes"
    ],
    "education": [
        "Teachers deserve higher pay for the important work they do! #education",
        "School choice is essential for improving education outcomes. #schoolchoice",
        "Student loan forgiveness would help millions of Americans. #studentdebt",
        "Our education system needs to focus more on practical skills. #education",
        "Free college would level the playing field for all Americans. #freecollege"
    ],
    "climate_change": [
        "We need immediate action on climate change before it's too late! #climateaction",
        "The Green New Deal would destroy our economy for minimal impact. #climate",
        "Just planted 50 trees in my community! Every bit helps fight climate change. #environment",
        "Renewable energy is now cheaper than fossil fuels in many places. #renewables",
        "Climate change is the biggest threat facing our planet today. #climatecrisis"
    ],
    "immigration": [
        "We need secure borders AND compassionate immigration policies. #immigration",
        "Immigrants contribute enormously to our economy and culture. #immigration",
        "The border crisis is out of control. We need stricter enforcement. #bordersecurity",
        "DACA recipients deserve a path to citizenship. They're Americans in all but paper. #DACA",
        "Legal immigration should be streamlined and simplified. #immigrationreform"
    ],
    "gun_control": [
        "The Second Amendment is essential to our freedom. #2A",
        "No one needs an assault rifle for self-defense or hunting. #guncontrolnow",
        "Background checks are a common-sense measure most Americans support. #gunreform",
        "More guns in responsible hands make communities safer. #2A",
        "Another tragic mass shooting. When will we finally take action? #gunviolence"
    ],
    "economy": [
        "The stock market hit another record high today! #economy #stocks",
        "Wealth inequality is at an all-time high. The system is broken. #inequality",
        "Small businesses are the backbone of our economy. #smallbusiness",
        "Raising the minimum wage would help millions of workers. #fightfor15",
        "Government regulations are strangling our economic growth. #deregulation"
    ],
    "foreign_policy": [
        "We need to focus on America first and stop being the world's police. #foreignpolicy",
        "Strong alliances make America safer and more prosperous. #NATO",
        "Our trade deals need to protect American workers. #trade",
        "Diplomacy should always be our first option before military action. #peace",
        "We need to stand up to authoritarian regimes around the world. #humanrights"
    ],
    "social_security": [
        "Social Security is a promise we've made to our seniors. We must protect it. #socialsecurity",
        "Social Security will be insolvent soon if we don't reform it. #entitlementreform",
        "Raising the retirement age is unfair to workers in physical jobs. #socialsecurity",
        "We should expand Social Security benefits for our most vulnerable seniors. #seniorsdeservemore",
        "Privatizing parts of Social Security would give people more control over their retirement. #reform"
    ],
    "infrastructure": [
        "Our bridges and roads are crumbling. We need major investment now! #infrastructure",
        "The new infrastructure bill will create millions of good-paying jobs. #rebuilding",
        "High-speed rail would transform transportation in America. #transportation",
        "We need to upgrade our power grid to prevent outages. #infrastructure",
        "Broadband should be available to every American, rural or urban. #digitalinfrastructure"
    ],
    "technology": [
        "AI will transform our economy in ways we can't even imagine yet. #AI #tech",
        "Big Tech has too much power and needs to be regulated. #antitrust",
        "Just got the new smartphone and it's amazing! #tech #gadgets",
        "Working from home has been revolutionized by new collaboration tools. #remotework",
        "Cybersecurity should be a top national priority. #cybersecurity"
    ],
    "sports": [
        "What an amazing game last night! This team is going all the way! #sports",
        "Athletes should stick to sports and stay out of politics. #sticktosports",
        "The new stadium deal is a waste of taxpayer money. #sportsbusiness",
        "Youth sports teach valuable life lessons to kids. #youthsports",
        "College athletes should be paid for their labor. #fairpay"
    ],
    "arts": [
        "The new art exhibition downtown is absolutely stunning! #art",
        "Arts education is being cut from schools and it's a tragedy. #artseducation",
        "Just watched the most amazing film at the independent theater. #cinema",
        "Local music scenes need our support now more than ever. #supportlocalmusic",
        "Public funding for the arts benefits everyone in society. #artsfunding"
    ],
    "religion": [
        "Faith gives me strength through difficult times. #faith",
        "Religion should be kept separate from government policy. #separation",
        "Religious freedom is under attack in our country. #religiousfreedom",
        "My church community does so much good in our neighborhood. #community",
        "All religions teach compassion and love at their core. #interfaith"
    ],
    "environment": [
        "Just saw a shocking documentary about plastic pollution in our oceans. #environment",
        "Environmental regulations kill jobs and hurt businesses. #overregulation",
        "Cleaned up the local park today with volunteers! #community #environment",
        "We need to protect our national parks for future generations. #conservation",
        "Sustainable living doesn't have to be difficult or expensive. #sustainability"
    ],
    "housing": [
        "Housing prices are completely unaffordable for young people today. #housingcrisis",
        "Rent control policies actually make housing shortages worse. #economics",
        "We need more affordable housing in every community. #affordablehousing",
        "Just bought my first home! The American dream is still alive! #homeownership",
        "Homelessness is a solvable problem if we invest in the right solutions. #endhomelessness"
    ]
}

def get_tweets_for_interests(interests: List[str], count: int = 3) -> List[Dict[str, Any]]:
    """
    Get a list of tweets related to the user's interests.

    Args:
        interests: List of interest topics
        count: Number of tweets to return

    Returns:
        List of tweet objects
    """
    # Find overlap between user interests and available topics
    relevant_topics = []
    for interest in interests:
        # Convert interest to format matching TOPICS (replace spaces with underscores)
        formatted_interest = interest.lower().replace(" ", "_")
        # Find exact matches first
        if formatted_interest in TOPICS:
            relevant_topics.append(formatted_interest)
        else:
            # Find partial matches
            for topic in TOPICS:
                if formatted_interest in topic or topic in formatted_interest:
                    relevant_topics.append(topic)
                    break

    # If no relevant topics found, pick random ones
    if not relevant_topics:
        relevant_topics = random.sample(TOPICS, min(3, len(TOPICS)))

    tweets = []
    for _ in range(count):
        topic = random.choice(relevant_topics)
        # Make sure we have tweets for this topic
        if topic in SAMPLE_TWEETS:
            tweet_text = random.choice(SAMPLE_TWEETS[topic])
        else:
            # Fallback to a random topic with tweets
            topic = random.choice(list(SAMPLE_TWEETS.keys()))
            tweet_text = random.choice(SAMPLE_TWEETS[topic])

        tweets.append({
            "topic": topic,
            "text": tweet_text,
            "likes": random.randint(5, 1000),
            "retweets": random.randint(0, 200)
        })

    return tweets
