import { v } from 'convex/values';
import { ActionCtx, internalAction, internalMutation } from '../_generated/server';
import { Id } from '../_generated/dataModel';
import { internal } from '../_generated/api';
import { GameId, agentId, playerId } from '../aiTown/ids';
import { LLMMessage, chatCompletion } from '../util/llm';
import { Opinion } from './voterAgent';

// Import Anthropic SDK for Claude API
// Note: This would need to be added to package.json
// npm install @anthropic-ai/sdk
import Anthropic from '@anthropic-ai/sdk';

// Initialize Anthropic client
// In a real implementation, this would use environment variables
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || 'dummy-key', // Replace with actual key in production
});

// Helper function to call Claude API
async function callClaude(prompt: string): Promise<string> {
  try {
    const response = await anthropic.messages.create({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }],
    });
    return response.content[0].text;
  } catch (error) {
    console.error('Error calling Claude API:', error);
    return 'Error generating response';
  }
}

// Function to handle agent interactions
export const voterAgentInteraction = internalAction({
  args: {
    worldId: v.id('worlds'),
    agent1Id: agentId,
    agent2Id: agentId,
    player1Id: playerId,
    player2Id: playerId,
  },
  handler: async (ctx, args) => {
    // Get the agents from the database
    const agent1 = await ctx.runQuery(internal.voterSim.voterAgentQueries.getVoterAgent, {
      worldId: args.worldId,
      agentId: args.agent1Id,
    });

    const agent2 = await ctx.runQuery(internal.voterSim.voterAgentQueries.getVoterAgent, {
      worldId: args.worldId,
      agentId: args.agent2Id,
    });

    if (!agent1 || !agent2) {
      throw new Error('One or both agents not found');
    }

    // Randomly select an issue to discuss
    const issues = ['economy', 'healthcare', 'environment'];
    const issue = issues[Math.floor(Math.random() * issues.length)];

    // Generate a conversation between the agents using Claude
    const conversationPrompt = `
      ${agent1.name} and ${agent2.name} are discussing ${issue}.
      ${agent1.name}'s opinion on ${issue} is ${agent1.opinions[issue]} (on a scale of 0-1, where 0 is very conservative and 1 is very progressive).
      ${agent2.name}'s opinion on ${issue} is ${agent2.opinions[issue]} (on the same scale).

      ${agent1.name} is ${agent1.age} years old, has a ${agent1.income} income, and a ${agent1.education} education.
      ${agent2.name} is ${agent2.age} years old, has a ${agent2.income} income, and a ${agent2.education} education.

      Write a realistic, nuanced conversation between them about ${issue} policy. The conversation should reflect their different perspectives based on their opinions and backgrounds.
    `;

    const conversation = await callClaude(conversationPrompt);

    // For each agent, determine if their opinion changed based on the conversation
    const agent1UpdatePrompt = `
      Based on the following conversation about ${issue}:

      ${conversation}

      Did ${agent1.name}'s opinion on ${issue} change? ${agent1.name}'s original opinion was ${agent1.opinions[issue]} on a scale of 0-1.
      If their opinion changed, what is their new opinion value (as a number between 0 and 1)? If not, respond with "no change".
      Respond with ONLY a number between 0 and 1, or the exact phrase "no change".
    `;

    const agent2UpdatePrompt = `
      Based on the following conversation about ${issue}:

      ${conversation}

      Did ${agent2.name}'s opinion on ${issue} change? ${agent2.name}'s original opinion was ${agent2.opinions[issue]} on a scale of 0-1.
      If their opinion changed, what is their new opinion value (as a number between 0 and 1)? If not, respond with "no change".
      Respond with ONLY a number between 0 and 1, or the exact phrase "no change".
    `;

    const agent1Response = await callClaude(agent1UpdatePrompt);
    const agent2Response = await callClaude(agent2UpdatePrompt);

    // Parse responses and update opinions
    let agent1NewOpinion = agent1.opinions[issue];
    if (agent1Response !== 'no change') {
      const parsedValue = parseFloat(agent1Response);
      if (!isNaN(parsedValue) && parsedValue >= 0 && parsedValue <= 1) {
        agent1NewOpinion = parsedValue;
      }
    }

    let agent2NewOpinion = agent2.opinions[issue];
    if (agent2Response !== 'no change') {
      const parsedValue = parseFloat(agent2Response);
      if (!isNaN(parsedValue) && parsedValue >= 0 && parsedValue <= 1) {
        agent2NewOpinion = parsedValue;
      }
    }

    // Create memory entries for both agents
    const timestamp = Date.now();
    const agent1Memory = {
      summary: `Discussed ${issue} with ${agent2.name}: ${conversation.substring(0, 200)}...`,
      timestamp,
    };

    const agent2Memory = {
      summary: `Discussed ${issue} with ${agent1.name}: ${conversation.substring(0, 200)}...`,
      timestamp,
    };

    // Update the agents in the database
    await ctx.runMutation(internal.voterSim.voterAgentMutations.updateAgentAfterInteraction, {
      worldId: args.worldId,
      agentId: args.agent1Id,
      issue,
      newOpinion: agent1NewOpinion,
      memory: agent1Memory,
    });

    await ctx.runMutation(internal.voterSim.voterAgentMutations.updateAgentAfterInteraction, {
      worldId: args.worldId,
      agentId: args.agent2Id,
      issue,
      newOpinion: agent2NewOpinion,
      memory: agent2Memory,
    });

    return {
      issue,
      conversation,
      agent1: {
        id: args.agent1Id,
        oldOpinion: agent1.opinions[issue],
        newOpinion: agent1NewOpinion,
      },
      agent2: {
        id: args.agent2Id,
        oldOpinion: agent2.opinions[issue],
        newOpinion: agent2NewOpinion,
      },
    };
  },
});

// Function to handle agent reflection
export const voterAgentReflect = internalAction({
  args: {
    worldId: v.id('worlds'),
    agentId: agentId,
    playerId: playerId,
    memory: v.array(
      v.object({
        summary: v.string(),
        timestamp: v.number(),
      })
    ),
    opinions: v.object({
      economy: v.number(),
      healthcare: v.number(),
      environment: v.number(),
    }),
  },
  handler: async (ctx, args) => {
    // Get the agent from the database
    const agent = await ctx.runQuery(internal.voterSim.voterAgentQueries.getVoterAgent, {
      worldId: args.worldId,
      agentId: args.agentId,
    });

    if (!agent) {
      throw new Error('Agent not found');
    }

    // Create a prompt for reflection
    const reflectionPrompt = `
      ${agent.name}, reflect on your recent interactions:

      ${args.memory.map(m => `- ${m.summary}`).join('\n')}

      Your current opinions are:
      - Economy: ${args.opinions.economy} (on a scale of 0-1)
      - Healthcare: ${args.opinions.healthcare} (on a scale of 0-1)
      - Environment: ${args.opinions.environment} (on a scale of 0-1)

      How have these interactions influenced your opinions on these issues?

      Respond with updated opinion values in this exact format:
      economy: [number between 0-1]
      healthcare: [number between 0-1]
      environment: [number between 0-1]
    `;

    const reflectionResponse = await callClaude(reflectionPrompt);

    // Parse the response to extract updated opinions
    const updatedOpinions: Opinion = {
      economy: args.opinions.economy,
      healthcare: args.opinions.healthcare,
      environment: args.opinions.environment,
    };

    // Use regex to extract opinion values
    const economyMatch = reflectionResponse.match(/economy:\s*(\d+\.\d+)/i);
    const healthcareMatch = reflectionResponse.match(/healthcare:\s*(\d+\.\d+)/i);
    const environmentMatch = reflectionResponse.match(/environment:\s*(\d+\.\d+)/i);

    if (economyMatch) {
      const value = parseFloat(economyMatch[1]);
      if (!isNaN(value) && value >= 0 && value <= 1) {
        updatedOpinions.economy = value;
      }
    }

    if (healthcareMatch) {
      const value = parseFloat(healthcareMatch[1]);
      if (!isNaN(value) && value >= 0 && value <= 1) {
        updatedOpinions.healthcare = value;
      }
    }

    if (environmentMatch) {
      const value = parseFloat(environmentMatch[1]);
      if (!isNaN(value) && value >= 0 && value <= 1) {
        updatedOpinions.environment = value;
      }
    }

    // Update the agent in the database
    await ctx.runMutation(internal.voterSim.voterAgentMutations.updateAgentAfterReflection, {
      worldId: args.worldId,
      agentId: args.agentId,
      updatedOpinions,
    });

    return {
      agentId: args.agentId,
      oldOpinions: args.opinions,
      newOpinions: updatedOpinions,
      reflection: reflectionResponse,
    };
  },
});

// Function to handle agent voting
export const voterAgentVote = internalAction({
  args: {
    worldId: v.id('worlds'),
    agentId: agentId,
    playerId: playerId,
  },
  handler: async (ctx, args) => {
    // Get the agent from the database
    const agent = await ctx.runQuery(internal.voterSim.voterAgentQueries.getVoterAgent, {
      worldId: args.worldId,
      agentId: args.agentId,
    });

    if (!agent) {
      throw new Error('Agent not found');
    }

    // Create a prompt for voting
    const votingPrompt = `
      ${agent.name}, based on your opinions:
      - Economy: ${agent.opinions.economy} (on a scale of 0-1, where 0 is very conservative and 1 is very progressive)
      - Healthcare: ${agent.opinions.healthcare} (on the same scale)
      - Environment: ${agent.opinions.environment} (on the same scale)

      And considering your background:
      - Age: ${agent.age}
      - Income level: ${agent.income}
      - Education: ${agent.education}

      Who would you vote for: Candidate A (more conservative) or Candidate B (more progressive)?

      Respond with ONLY "Candidate A" or "Candidate B".
    `;

    const votingResponse = await callClaude(votingPrompt);

    // Parse the response to extract the vote
    let vote: 'Candidate A' | 'Candidate B' | undefined;

    if (votingResponse.includes('Candidate A')) {
      vote = 'Candidate A';
    } else if (votingResponse.includes('Candidate B')) {
      vote = 'Candidate B';
    }

    if (vote) {
      // Update the agent in the database
      await ctx.runMutation(internal.voterSim.voterAgentMutations.updateAgentVote, {
        worldId: args.worldId,
        agentId: args.agentId,
        vote,
      });
    }

    return {
      agentId: args.agentId,
      vote,
      response: votingResponse,
    };
  },
});
