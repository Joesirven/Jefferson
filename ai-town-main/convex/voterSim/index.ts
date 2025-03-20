// Export all voter simulation functions
export * as voterAgent from './voterAgent';
export * as voterAgentOperations from './voterAgentOperations';
export * as voterAgentQueries from './voterAgentQueries';
export * as voterAgentMutations from './voterAgentMutations';
export * as initVoterSim from './initVoterSim';
export * as simulationSteps from './simulationSteps';

// Export a public API for the frontend
import { query } from '../_generated/server';
import { v } from 'convex/values';
import { internal } from '../_generated/api';

// Query to get the current voting results
export const getVotingResults = query({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    return await ctx.runQuery(internal.voterSim.voterAgentQueries.getVotingResults, {
      worldId: args.worldId,
    });
  },
});

// Query to get all voter agents
export const getAllVoterAgents = query({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    return await ctx.runQuery(internal.voterSim.voterAgentQueries.getAllVoterAgents, {
      worldId: args.worldId,
    });
  },
});
