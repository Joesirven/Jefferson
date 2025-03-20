import { v } from 'convex/values';
import { action, mutation, internalAction } from '../_generated/server';
import { Id } from '../_generated/dataModel';
import { internal } from '../_generated/api';
import { GameId, agentId } from '../aiTown/ids';

// Global counter for simulation steps
let simulationStep = 0;
const TOTAL_SIMULATION_STEPS = 50;

// Function to run a single simulation step
export const runSimulationStep = action({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    // Increment the simulation step
    simulationStep++;
    console.log(`Running simulation step ${simulationStep}/${TOTAL_SIMULATION_STEPS}`);

    // Get all agents in the world
    const agents = await ctx.runQuery(internal.voterSim.voterAgentQueries.getAllVoterAgents, {
      worldId: args.worldId,
    });

    if (agents.length < 2) {
      throw new Error('Not enough agents in the world to run a simulation step');
    }

    // If we've reached the final step, trigger voting
    if (simulationStep >= TOTAL_SIMULATION_STEPS) {
      return await ctx.runAction(internal.voterSim.initVoterSim.triggerVoting, {
        worldId: args.worldId,
      });
    }

    // Otherwise, trigger interactions between random pairs of agents
    const interactionResults = [];

    // Create a copy of the agents array to shuffle
    const shuffledAgents = [...agents];

    // Fisher-Yates shuffle algorithm
    for (let i = shuffledAgents.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffledAgents[i], shuffledAgents[j]] = [shuffledAgents[j], shuffledAgents[i]];
    }

    // Pair up agents and trigger interactions
    for (let i = 0; i < shuffledAgents.length - 1; i += 2) {
      const agent1 = shuffledAgents[i];
      const agent2 = shuffledAgents[i + 1];

      try {
        const result = await ctx.runAction(internal.voterSim.voterAgentOperations.voterAgentInteraction, {
          worldId: args.worldId,
          agent1Id: agent1.id,
          agent2Id: agent2.id,
          player1Id: agent1.playerId,
          player2Id: agent2.playerId,
        });

        interactionResults.push(result);
      } catch (error) {
        console.error(`Error in interaction between ${agent1.id} and ${agent2.id}:`, error);
      }
    }

    return {
      success: true,
      step: simulationStep,
      totalSteps: TOTAL_SIMULATION_STEPS,
      interactionsTriggered: interactionResults.length,
      interactionResults,
    };
  },
});

// Function to run the entire simulation
export const runFullSimulation = action({
  args: {
    worldId: v.id('worlds'),
    stepsToRun: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    // Reset the simulation step counter
    simulationStep = 0;

    // Determine how many steps to run
    const stepsToRun = args.stepsToRun || TOTAL_SIMULATION_STEPS;

    // Initialize the simulation if needed
    await ctx.runAction(internal.voterSim.initVoterSim.initVoterSimulation, {
      worldId: args.worldId,
    });

    // Run the simulation steps
    const results = [];
    for (let i = 0; i < stepsToRun; i++) {
      const result = await ctx.runAction(internal.voterSim.simulationSteps.runSimulationStep, {
        worldId: args.worldId,
      });
      results.push(result);

      // If the last step triggered voting, we're done
      if (result.step >= TOTAL_SIMULATION_STEPS) {
        break;
      }
    }

    // Get the final voting results
    const votingResults = await ctx.runQuery(internal.voterSim.voterAgentQueries.getVotingResults, {
      worldId: args.worldId,
    });

    return {
      success: true,
      stepsRun: results.length,
      finalStep: simulationStep,
      votingResults,
    };
  },
});

// Function to reset the simulation
export const resetSimulation = action({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    // Reset the simulation step counter
    simulationStep = 0;

    // Clear all agents from the world
    await ctx.runMutation(internal.voterSim.simulationSteps.clearAgents, {
      worldId: args.worldId,
    });

    return {
      success: true,
      message: 'Simulation reset',
    };
  },
});

// Mutation to clear all agents from the world
export const clearAgents = mutation({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Get all players associated with agents
    const agentPlayerIds = world.agents?.map(agent => agent.playerId) || [];

    // Remove all agents
    await ctx.db.patch(args.worldId, {
      agents: [],
    });

    // Remove all players associated with agents
    for (const playerId of agentPlayerIds) {
      // Find the player in the world's players array
      const playerIndex = world.players.findIndex(p => p.id === playerId);
      if (playerIndex !== -1) {
        // Create a copy of the players array
        const updatedPlayers = [...world.players];
        // Remove the player
        updatedPlayers.splice(playerIndex, 1);
        // Update the world
        await ctx.db.patch(args.worldId, {
          players: updatedPlayers,
        });
      }
    }

    return {
      success: true,
      agentsRemoved: world.agents?.length || 0,
    };
  },
});
