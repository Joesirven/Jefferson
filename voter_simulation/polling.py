import asyncio
from typing import List, Dict, Any
import statistics
import json

from agents import Runner

async def poll_voters(population: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
    """
    Poll all voters on a specific question.

    Args:
        population: List of voter dictionaries
        question: The question to ask voters

    Returns:
        Dictionary with poll results
    """
    results = []

    print("\n=== POLLING RESULTS ===")
    print(f"Question: {question}\n")

    for voter in population:
        agent = voter["agent"]
        demographics = voter["demographics"]

        # Format existing opinions for the prompt
        opinions_text = ""
        if demographics.opinions:
            opinions_text = "Your current opinions on various topics:\n"
            for topic, rating in demographics.opinions.items():
                opinions_text += f"- {topic}: {rating}/5\n"

        # Format recent interactions for the prompt
        interactions_text = ""
        if demographics.memory:
            interactions_text = "Your recent interactions:\n"
            # Show the last 3 interactions at most
            for interaction in demographics.memory[-3:]:
                interactions_text += f"- {interaction['type']} about {interaction['topic']}: opinion change {interaction['opinion_change']}\n"
                interactions_text += f"  Content: \"{interaction['content']}\"\n"

        # Construct the polling prompt with explicit context
        prompt = f"""Please consider this question: {question}

Your demographic information:
- Name: {demographics.name}
- Age: {demographics.age}
- Gender: {demographics.gender}
- Education: {demographics.education}
- Income Level: {demographics.income_level}
- Political Leaning: {demographics.political_leaning}
- Location: {demographics.location}
- Interests: {', '.join(demographics.interests)}

{opinions_text}
{interactions_text}

Based on your demographic background and existing opinions, how would you respond to this question?

Rate your support on a scale of 1-5, where:
1 = Strongly oppose
2 = Somewhat oppose
3 = Neutral
4 = Somewhat support
5 = Strongly support

Explain your reasoning based on your demographic background and previous opinions.
Then provide ONLY a number 1-5 as your final answer on a separate line.
"""

        # Run the agent with this prompt
        result = await Runner.run(
            starting_agent=agent,
            input=prompt,
            context=demographics
        )

        # Extract the numeric response
        try:
            # Try to extract just the number from the response
            response_text = result.final_output.strip()

            # Look for a single digit at the end of the response or on its own line
            lines = response_text.split('\n')
            score = None

            # First check if the last line is just a number
            if lines[-1].strip().isdigit() and 1 <= int(lines[-1].strip()) <= 5:
                score = int(lines[-1].strip())
                explanation = '\n'.join(lines[:-1]).strip()
            else:
                # Otherwise search for a digit in the response
                for char in response_text:
                    if char.isdigit() and int(char) >= 1 and int(char) <= 5:
                        score = int(char)
                        explanation = response_text
                        break

            if score is None:
                # If no valid digit found, default to 3
                score = 3
                explanation = response_text
                print(f"Warning: Could not parse response from {demographics.name}: '{response_text}'. Using default score 3.")
        except Exception as e:
            score = 3
            explanation = response_text if 'response_text' in locals() else "Error parsing response"
            print(f"Error parsing response from {demographics.name}: {e}. Using default score 3.")

        results.append({
            "name": demographics.name,
            "score": score,
            "explanation": explanation,
            "demographics": demographics
        })

        # Print voter information and response
        print(f"Voter: {demographics.name} ({demographics.age}, {demographics.gender}, {demographics.political_leaning})")
        print(f"Education: {demographics.education}, Income: {demographics.income_level}, Location: {demographics.location}")
        print(f"Interests: {', '.join(demographics.interests)}")

        # Print existing opinions
        if demographics.opinions:
            print("Current opinions:")
            for topic, opinion in demographics.opinions.items():
                print(f"  - {topic}: {opinion}/5")
        else:
            print("No existing opinions recorded.")

        # Print memory of interactions
        if demographics.memory:
            print("Recent interactions:")
            # Show the last 3 interactions at most
            for interaction in demographics.memory[-3:]:
                print(f"  - {interaction['type']} about {interaction['topic']}: opinion change {interaction['opinion_change']}")
        else:
            print("No interactions recorded.")

        print(f"Response: {explanation}")
        print(f"Score: {score}/5")
        print("-" * 50)

        # Store this opinion in the voter's context
        demographics.opinions[question] = score

    # Calculate average score
    scores = [r["score"] for r in results]
    average_score = statistics.mean(scores)

    print(f"\nAverage score: {average_score:.2f}/5")

    # Calculate distribution of scores
    distribution = {i: scores.count(i) for i in range(1, 6)}
    print("\nDistribution of scores:")
    for score, count in distribution.items():
        percentage = (count / len(scores)) * 100
        print(f"  {score}/5: {count} voters ({percentage:.1f}%)")

    # Analyze by demographic factors
    print("\nAnalysis by demographics:")

    # By political leaning
    political_scores = {}
    for r in results:
        leaning = r["demographics"].political_leaning
        if leaning not in political_scores:
            political_scores[leaning] = []
        political_scores[leaning].append(r["score"])

    print("By political leaning:")
    for leaning, scores in political_scores.items():
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {leaning}: {avg:.2f}/5 ({len(scores)} voters)")

    # By age group
    age_groups = {
        "18-29": [],
        "30-44": [],
        "45-64": [],
        "65+": []
    }

    for r in results:
        age = r["demographics"].age
        score = r["score"]
        if age < 30:
            age_groups["18-29"].append(score)
        elif age < 45:
            age_groups["30-44"].append(score)
        elif age < 65:
            age_groups["45-64"].append(score)
        else:
            age_groups["65+"].append(score)

    print("By age group:")
    for group, scores in age_groups.items():
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  {group}: {avg:.2f}/5 ({len(scores)} voters)")

    return {
        "question": question,
        "results": results,
        "average": average_score
    }

async def interactive_polling(population: List[Dict[str, Any]]) -> None:
    """
    Run an interactive polling session where the user can ask multiple questions.

    Args:
        population: List of voter dictionaries
    """
    while True:
        question = input("\nEnter a question to ask the voters (or 'quit' to exit): ")

        if question.lower() in ('quit', 'exit', 'q'):
            break

        print(f"\nPolling {len(population)} voters on: {question}")
        await poll_voters(population, question)
