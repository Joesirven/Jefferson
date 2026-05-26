import { ObjectType, v } from 'convex/values';
import { GameId, parseGameId } from '../aiTown/ids';
import { agentId, playerId } from '../aiTown/ids';
import { Agent, SerializedAgent } from '../aiTown/agent';
import { Game } from '../aiTown/game';

// Define the opinion type
export const opinion = v.object({
  economy: v.number(),
  healthcare: v.number(),
  environment: v.number()
});
export type Opinion = ObjectType<typeof opinion>;

// Define the memory entry type
export const memoryEntry = v.object({
  summary: v.string(),
  timestamp: v.number()
});
export type MemoryEntry = ObjectType<typeof memoryEntry>;

// Define the serialized voter agent
export const serializedVoterAgent = {
  ...v.object({}), // Include all fields from SerializedAgent
  age: v.number(),
  income: v.union(v.literal('low'), v.literal('medium'), v.literal('high')),
  education: v.union(v.literal('high school'), v.literal('college'), v.literal('graduate')),
  opinions: opinion,
  memory: v.array(memoryEntry),
  interactionCount: v.number(),
  vote: v.optional(v.union(v.literal('Candidate A'), v.literal('Candidate B'))),
};
export type SerializedVoterAgent = ObjectType<typeof serializedVoterAgent>;

export class VoterAgent extends Agent {
  age: number;
  income: 'low' | 'medium' | 'high';
  education: 'high school' | 'college' | 'graduate';
  opinions: Opinion;
  memory: MemoryEntry[];
  interactionCount: number;
  vote?: 'Candidate A' | 'Candidate B';

  constructor(serialized: SerializedVoterAgent & SerializedAgent) {
    super(serialized);
    this.age = serialized.age;
    this.income = serialized.income;
    this.education = serialized.education;
    this.opinions = serialized.opinions;
    this.memory = serialized.memory;
    this.interactionCount = serialized.interactionCount;
    this.vote = serialized.vote;
  }

  // Override the tick method to include voter-specific behavior
  tick(game: Game, now: number) {
    // First run the parent tick method
    super.tick(game, now);

    // If we have 10 or more interactions, trigger a reflection
    if (this.interactionCount >= 10) {
      this.startOperation(game, now, 'voterAgentReflect', {
        worldId: game.worldId,
        agentId: this.id,
        playerId: this.playerId,
        memory: this.memory.slice(-10),
        opinions: this.opinions
      });

      // Reset the interaction count
      this.interactionCount = 0;
    }

    // After 50 simulation steps, trigger voting
    // This will need to be coordinated at the game level
  }

  // Override the serialize method to include voter-specific attributes
  serialize(): SerializedVoterAgent & SerializedAgent {
    return {
      ...super.serialize(),
      age: this.age,
      income: this.income,
      education: this.education,
      opinions: this.opinions,
      memory: this.memory,
      interactionCount: this.interactionCount,
      vote: this.vote
    };
  }

  // Static method to create a new voter agent
  static createVoterAgent(
    game: Game,
    now: number,
    playerId: GameId<'players'>,
  ): VoterAgent {
    // Create a base agent
    const baseAgent = new Agent({
      id: game.generateId('agents'),
      playerId,
      inProgressOperation: undefined,
    });

    // Add voter-specific attributes
    const voterAgent = new VoterAgent({
      ...baseAgent.serialize(),
      age: Math.floor(Math.random() * (80 - 18 + 1)) + 18,
      income: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
      education: ['high school', 'college', 'graduate'][Math.floor(Math.random() * 3)] as 'high school' | 'college' | 'graduate',
      opinions: {
        economy: Math.random(),
        healthcare: Math.random(),
        environment: Math.random()
      },
      memory: [],
      interactionCount: 0
    });

    return voterAgent;
  }
}
