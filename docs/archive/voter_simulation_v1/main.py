import sys
import os

# Add the agents source directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "agents/src"))

import asyncio
from master_agent import create_voter_population
from simulation import run_simulation
from polling import interactive_polling

async def main():
    # Create a population of 10 voter agents (reduced for testing)
    print("Creating voter population...")
    population = create_voter_population(count=10)
    print(f"Created {len(population)} voter agents")

    # Run the simulation for 1 round (reduced for testing)
    await run_simulation(population, rounds=1)

    # Start interactive polling
    print("\n--- Interactive Polling ---")
    print("You can now ask questions to all voters.")
    await interactive_polling(population)

if __name__ == "__main__":
    asyncio.run(main())
