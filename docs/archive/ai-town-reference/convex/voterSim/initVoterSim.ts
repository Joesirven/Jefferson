import { v } from 'convex/values';
import { action, mutation } from '../_generated/server';
import { Id } from '../_generated/dataModel';
import { internal } from '../_generated/api';
import { VoterAgent } from './voterAgent';
import { characters } from '../../data/characters';
import { Game } from '../aiTown/game';

// Function to initialize the voter simulation
export const initVoterSimulation = action({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    // Load the world
    const world = await ctx.runQuery(internal.aiTown.game.loadWorld, {
      worldId: args.worldId,
    });

    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Create a game instance
    const game = new Game(world);
    const now = Date.now();

    // Create 100 voter agents
    const voterAgents = [];
    const existingPlayers = game.world.players.size;
    const numAgentsToCreate = 100 - existingPlayers;

    if (numAgentsToCreate <= 0) {
      console.log('Already have enough agents in the world');
      return { success: true, message: 'Already have enough agents in the world' };
    }

    // Generate random names for our agents
    const firstNames = [
      'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth',
      'David', 'Susan', 'Richard', 'Jessica', 'Joseph', 'Sarah', 'Thomas', 'Karen', 'Charles', 'Nancy',
      'Christopher', 'Lisa', 'Daniel', 'Margaret', 'Matthew', 'Betty', 'Anthony', 'Sandra', 'Mark', 'Ashley',
      'Donald', 'Dorothy', 'Steven', 'Kimberly', 'Paul', 'Emily', 'Andrew', 'Donna', 'Joshua', 'Michelle',
      'Kenneth', 'Carol', 'Kevin', 'Amanda', 'Brian', 'Melissa', 'George', 'Deborah', 'Edward', 'Stephanie'
    ];

    const lastNames = [
      'Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor',
      'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson',
      'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez', 'King',
      'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter',
      'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins'
    ];

    // Create the agents
    for (let i = 0; i < numAgentsToCreate; i++) {
      // Generate a random name
      const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
      const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
      const name = `${firstName} ${lastName}`;

      // Select a random character from the available characters
      const characterKeys = Object.keys(characters);
      const character = characterKeys[Math.floor(Math.random() * characterKeys.length)];

      // Create a description
      const description = `A voter in the simulation.`;

      // Create a player for this agent
      const playerId = await ctx.runMutation(internal.aiTown.player.join, {
        worldId: args.worldId,
        name,
        character,
        description,
      });

      // Create a voter agent for this player
      const voterAgent = VoterAgent.createVoterAgent(game, now, playerId);
      voterAgents.push(voterAgent.serialize());
    }

    // Add the agents to the world
    await ctx.runMutation(internal.voterSim.addVoterAgents, {
      worldId: args.worldId,
      agents: voterAgents,
    });

    return {
      success: true,
      message: `Created ${numAgentsToCreate} voter agents`,
      agentsCreated: numAgentsToCreate,
    };
  },
});

// Mutation to add voter agents to the world
export const addVoterAgents = mutation({
  args: {
    worldId: v.id('worlds'),
    agents: v.array(v.any()),
  },
  handler: async (ctx, args) => {
    const world = await ctx.db.get(args.worldId);
    if (!world) {
      throw new Error(`World ${args.worldId} not found`);
    }

    // Add the agents to the world
    const updatedAgents = [...(world.agents || []), ...args.agents];

    await ctx.db.patch(args.worldId, {
      agents: updatedAgents,
    });

    return {
      success: true,
      agentsAdded: args.agents.length,
    };
  },
});

// Function to trigger voting for all agents
export const triggerVoting = action({
  args: {
    worldId: v.id('worlds'),
  },
  handler: async (ctx, args) => {
    // Get all agents in the world
    const agents = await ctx.runQuery(internal.voterSim.voterAgentQueries.getAllVoterAgents, {
      worldId: args.worldId,
    });

    // Trigger voting for each agent
    for (const agent of agents) {
      await ctx.runAction(internal.voterSim.voterAgentOperations.voterAgentVote, {
        worldId: args.worldId,
        agentId: agent.id,
        playerId: agent.playerId,
      });
    }

    // Get the voting results
    const results = await ctx.runQuery(internal.voterSim.voterAgentQueries.getVotingResults, {
      worldId: args.worldId,
    });

    return {
      success: true,
      message: 'Voting completed',
      results,
    };
  },
});
