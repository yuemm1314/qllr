export interface RankingEntry {
  characterName: string;
  skillName: string;
  skillType: 'active' | 'ultimate';
  weapons: string[];
  elements: string[];
  power: number;
  hits: number;
  baseMultiplier: number;
  buffMultiplier: number;
  finalMultiplier: number;
  buffNotes: string[];
  turnCost: number;
  requiresTrigger: boolean;
  cost: string;
  effect: string;
  bpEffect: string;
}

export interface SkillRankingsFile {
  schema: string;
  generatedAt: string;
  totalEntries: number;
  rules: Record<string, string>;
  rankings: Record<string, RankingEntry[]>;
}
