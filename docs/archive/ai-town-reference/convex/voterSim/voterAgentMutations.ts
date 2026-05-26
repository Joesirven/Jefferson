import { v } from 'convex/values';
import { internalMutation } from '../_generated/server';
import { Id } from '../_generated/dataModel';
import { GameId, agentId } from '../aiTown/ids';
import { Opinion } from './voterAgent';
import { MemoryEntry } from './voterAgent';

// Mutation to update an agent after an interaction
export const updateAgentAfterInteraction = internalMutation({
  args: {
    worldId: v.id('worlds'),
    agentId: agentId,
    issue: v.string(),
    newOpinion: v.number(),
    memory: v.object({
      summary: v.string(),
      timestamp: v.number(),
    }),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Find the agent in the world's agents array
    const agentIndex = world.agents.findIndex(a => a.id === args.agentId);
    if (agentIndex === -1) {
      throw new Error(`Agent ${args.agentId} not found in world ${args.worldId}`);
    }

    // Create a copy of the agents array
    const updatedAgents = [...world.agents];
    const agent = { ...updatedAgents[agentIndex] };

    // Update the agent's opinion on the issue
    agent.opinions = {
      ...agent.opinions,
      [args.issue]: args.newOpinion,
    };

    // Add the memory entry
    agent.memory = [...(agent.memory || []), args.memory];

    // Increment the interaction count
    agent.interactionCount = (agent.interactionCount || 0) + 1;

    // Replace the agent in the array
    updatedAgents[agentIndex] = agent;

    // Update the world
    await ctx.db.patch(args.worldId, {
      agents: updatedAgents,
    });

    return agent;
  },
});

// Mutation to update an agent after reflection
export const updateAgentAfterReflection = internalMutation({
  args: {
    worldId: v.id('worlds'),
    agentId: agentId,
    updatedOpinions: v.object({
      economy: v.number(),
      healthcare: v.number(),
      environment: v.number(),
    }),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Find the agent in the world's agents array
    const agentIndex = world.agents.findIndex(a => a.id === args.agentId);
    if (agentIndex === -1) {
      throw new Error(`Agent ${args.agentId} not found in world ${args.worldId}`);
    }

    // Create a copy of the agents array
    const updatedAgents = [...world.agents];
    const agent = { ...updatedAgents[agentIndex] };

    // Update the agent's opinions
    agent.opinions = args.updatedOpinions;

    // Reset the interaction count
    agent.interactionCount = 0;

    // Replace the agent in the array
    updatedAgents[agentIndex] = agent;

    // Update the world
    await ctx.db.patch(args.worldId, {
      agents: updatedAgents,
    });

    return agent;
  },
});

// Mutation to update an agent's vote
export const updateAgentVote = internalMutation({
  args: {
    worldId: v.id('worlds'),
    agentId: agentId,
    vote: v.union(v.literal('Candidate A'), v.literal('Candidate B')),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Find the agent in the world's agents array
    const agentIndex = world.agents.findIndex(a => a.id === args.agentId);
    if (agentIndex === -1) {
      throw new Error(`Agent ${args.agentId} not found in world ${args.worldId}`);
    }

    // Create a copy of the agents array
    const updatedAgents = [...world.agents];
    const agent = { ...updatedAgents[agentIndex] };

    // Update the agent's vote
    agent.vote = args.vote;

    // Replace the agent in the array
    updatedAgents[agentIndex] = agent;

    // Update the world
    await ctx.db.patch(args.worldId, {
      agents: updatedAgents,
    });

    return agent;
  },
});
