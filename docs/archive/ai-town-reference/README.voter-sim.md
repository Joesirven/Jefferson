# AI Town Voter Behavior Simulation

This project extends AI Town to create a simulation of voter behavior in a small town of 100 people using large language models (LLMs) via API calls, inspired by the Generative Agents paper. The simulation models human-like behavior where agents' opinions on issues (economy, healthcare, environment) evolve through interactions and influence their voting decisions.

## Overview

The simulation creates 100 agents with randomly assigned attributes:
- Age (18-80)
- Income level (low, medium, high)
- Education level (high school, college, graduate)
- Initial opinions on economy, healthcare, and environment (values between 0-1)

These agents interact with each other, discussing various issues, and their opinions evolve based on these interactions. After 50 simulation steps, they vote for one of two candidates based on their final opinions.

## Setup

1. Make sure you have AI Town set up and running locally. Follow the instructions in the main README.md file.

2. Install the Anthropic SDK for Claude API access:
   ```
   npm install @anthropic-ai/sdk
   ```

3. Set up your Anthropic API key:
   ```
   npx convex env set ANTHROPIC_API_KEY 'your-api-key'
   ```

## Running the Simulation

1. Start the AI Town development server:
   ```
   npm run dev
   ```

2. Open the AI Town interface in your browser.

3. Create a new world or use an existing one.

4. Use the Convex CLI to initialize the voter simulation:
   ```
   npx convex run voterSim:initVoterSim.initVoterSimulation '{"worldId": "your-world-id"}'
   ```

5. Run the full simulation:
   ```
   npx convex run voterSim:simulationSteps.runFullSimulation '{"worldId": "your-world-id"}'
   ```

6. View the voting results:
   ```
   npx convex run voterSim:getVotingResults '{"worldId": "your-world-id"}'
   ```

## How It Works

### Agent Interactions

During each simulation step, agents are randomly paired up and engage in conversations about one of three issues: economy, healthcare, or environment. The Claude API generates these conversations based on the agents' current opinions and backgrounds.

After each conversation, the Claude API determines if an agent's opinion on the discussed issue has changed, and if so, by how much. These interactions are stored in each agent's memory.

### Reflection

After every 10 interactions, agents reflect on their recent conversations, which may further influence their opinions on all issues. This reflection process is also powered by the Claude API.

### Voting

After 50 simulation steps, each agent votes for either Candidate A (more conservative) or Candidate B (more progressive) based on their final opinions and background. The Claude API determines each agent's vote based on their profile.

## Implementation Details

The simulation is implemented as an extension to AI Town with the following components:

- `voterAgent.ts`: Defines the VoterAgent class with attributes for age, income, education, opinions, and memory.
- `voterAgentOperations.ts`: Implements the logic for agent interactions, reflections, and voting using the Claude API.
- `voterAgentQueries.ts` and `voterAgentMutations.ts`: Handle database operations for retrieving and updating agent data.
- `initVoterSim.ts`: Initializes the simulation with 100 agents.
- `simulationSteps.ts`: Manages the simulation steps, including triggering interactions and voting.

## Analyzing Results

The simulation provides detailed voting results, including:
- Total votes for each candidate
- Demographic breakdowns by age, income, and education
- Individual agent voting decisions

These results can be used to analyze how different factors influence voting behavior and how opinions evolve through social interactions.

## Extending the Simulation

You can extend the simulation in various ways:
- Add more issues for agents to discuss
- Implement more complex voting systems (e.g., ranked choice)
- Add external events that influence agent opinions
- Create visualizations of opinion changes over time
- Implement different agent personalities that affect how easily their opinions change

## Troubleshooting

- If you encounter errors related to the Claude API, check your API key and ensure you have sufficient quota.
- If agents aren't being created properly, check the AI Town world configuration.
- If the simulation seems stuck, you can reset it using `npx convex run voterSim:simulationSteps.resetSimulation '{"worldId": "your-world-id"}'`
