import { v } from 'convex/values';
import { internalQuery } from '../_generated/server';
import { Id } from '../_generated/dataModel';
import { GameId, agentId, playerId } from '../aiTown/ids';

// Query to get a voter agent by ID
export const getVoterAgent = internalQuery({
  args: {
    worldId: v.id('worlds'),
    agentId: agentId,
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Find the agent in the world's agents array
    const agent = world.agents.find(a => a.id === args.agentId);
    if (!agent) {
      return null;
    }

    // Find the player associated with this agent
    const player = world.players.find(p => p.id === agent.playerId);
    if (!player) {
      return null;
    }

    // Return the agent with player information
    return {
      ...agent,
      name: player.name,
    };
  },
});

// Query to get all voter agents in a world
export const getAllVoterAgents = internalQuery({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Map agents to include player information
    const agents = world.agents.map(agent => {
      const player = world.players.find(p => p.id === agent.playerId);
      if (!player) {
        return null;
      }
      return {
        ...agent,
        name: player.name,
      };
    }).filter(Boolean); // Remove null entries

    return agents;
  },
});

// Query to get voting results
export const getVotingResults = internalQuery({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Count votes for each candidate
    let candidateACount = 0;
    let candidateBCount = 0;
    let undecidedCount = 0;

    world.agents.forEach(agent => {
      if (agent.vote === 'Candidate A') {
        candidateACount++;
      } else if (agent.vote === 'Candidate B') {
        candidateBCount++;
      } else {
        undecidedCount++;
      }
    });

    // Group agents by demographic factors
    const byAge: Record<string, { A: number, B: number }> = {
      '18-30': { A: 0, B: 0 },
      '31-50': { A: 0, B: 0 },
      '51-80': { A: 0, B: 0 },
    };

    const byIncome: Record<string, { A: number, B: number }> = {
      'low': { A: 0, B: 0 },
      'medium': { A: 0, B: 0 },
      'high': { A: 0, B: 0 },
    };

    const byEducation: Record<string, { A: number, B: number }> = {
      'high school': { A: 0, B: 0 },
      'college': { A: 0, B: 0 },
      'graduate': { A: 0, B: 0 },
    };

    world.agents.forEach(agent => {
      if (!agent.vote) return;

      // Age grouping
      let ageGroup;
      if (agent.age <= 30) ageGroup = '18-30';
      else if (agent.age <= 50) ageGroup = '31-50';
      else ageGroup = '51-80';

      if (agent.vote === 'Candidate A') {
        byAge[ageGroup].A++;
        byIncome[agent.income].A++;
        byEducation[agent.education].A++;
      } else if (agent.vote === 'Candidate B') {
        byAge[ageGroup].B++;
        byIncome[agent.income].B++;
        byEducation[agent.education].B++;
      }
    });

    return {
      totalVotes: candidateACount + candidateBCount,
      undecided: undecidedCount,
      results: {
        'Candidate A': candidateACount,
        'Candidate B': candidateBCount,
      },
      demographics: {
        byAge,
        byIncome,
        byEducation,
      }
    };
  },
});
