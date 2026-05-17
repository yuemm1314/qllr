// src/types/character.ts

export type WeaponKey =
  | 'sword' | 'spear' | 'dagger' | 'axe' | 'bow' | 'staff' | 'book' | 'fan';

export type ElementKey =
  | 'fire' | 'ice' | 'thunder' | 'wind' | 'light' | 'dark';

export type InfluenceKey =
  | 'wealth' | 'power' | 'fame' | 'possession' | 'dominance' | 'recognition';

/** 来自 wiki_character_list.json 的基础信息 */
export interface CharacterListEntry {
  name: string;
  wikiPath: string | null;
  wikiUrl: string | null;
  avatar: string | null;
  job: string;
  rarity: number | null;
  influence: InfluenceKey | null;
  influenceText: string | null;
  gacha: string;
  cnReleaseDate: string | null;
  jpReleaseDate: string | null;
  weakness: {
    weapons: WeaponKey[];
    elements: ElementKey[];
  };
}

/** 角色 MAX 属性（6 星 120 级满觉） */
export interface MaxStats {
  hp?: number;
  sp?: number;
  patk?: number;
  pdef?: number;
  eatk?: number;
  edef?: number;
  crit?: number;
  spd?: number;
}

export interface SkillDetail {
  name: string;
  cost: string;
  tags: string[];
  effect: string;
  bpEffect: string;
  enhanceEffect: string;
  enhanceCondition: string;
}

/** 来自 wiki_character_details.json 的详情 */
export interface CharacterDetailEntry {
  name: string;
  wikiUrl: string;
  fetchedAt: string;
  basicInfo: Record<string, string>;
  maxStats: MaxStats;
  skills: {
    active: SkillDetail[];
    passive: SkillDetail[];
    ultimate: SkillDetail[];
  };
}

/** 合并后的角色对象（前端实际使用） */
export interface Character extends CharacterListEntry {
  details?: CharacterDetailEntry;
}
