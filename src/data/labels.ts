// src/data/labels.ts
import type { WeaponKey, ElementKey, InfluenceKey } from '@/types/character';

export const WEAPON_LABEL: Record<WeaponKey, string> = {
  sword: '剑', spear: '枪', dagger: '短剑', axe: '斧',
  bow: '弓', staff: '杖', book: '书', fan: '扇',
};

export const ELEMENT_LABEL: Record<ElementKey, string> = {
  fire: '火', ice: '冰', thunder: '雷',
  wind: '风', light: '光', dark: '暗',
};

export const ELEMENT_COLOR: Record<ElementKey, string> = {
  fire: '#e85d3c', ice: '#5ec1e8', thunder: '#e8c93c',
  wind: '#6fdc8c', light: '#f0e6a8', dark: '#a070d8',
};

export const INFLUENCE_LABEL: Record<InfluenceKey, string> = {
  wealth: '富', power: '权', fame: '名望',
  possession: '拥有', dominance: '支配', recognition: '认可',
};

export const STAT_LABEL = {
  hp: 'HP', sp: 'SP',
  patk: '物攻', pdef: '物防',
  eatk: '属攻', edef: '属防',
  crit: '会心', spd: '速度',
} as const;
