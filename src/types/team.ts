/**
 * 阵容（编队）相关的类型定义。
 *
 * 一个 Team 表示一套 8 人编队：4 前卫 + 4 后卫。
 * 每个槽位可以为空（null），表示这个位置还没安排角色。
 */

import type { Character } from './character'

/** 阵容槽位（一个位置） */
export interface TeamSlot {
  /** 引用的角色 ID（null 表示空位） */
  characterId: string | null
  /** 该角色在此阵容中的临时备注（如"开局换前"、"破盾位"） */
  note?: string
}

/** 一套完整阵容 */
export interface Team {
  /** UUID */
  id: string
  /** 阵容名称（例如 "打萨赞托斯-3 回合"） */
  name: string
  /** 4 个前卫位 */
  front: [TeamSlot, TeamSlot, TeamSlot, TeamSlot]
  /** 4 个后卫位 */
  back: [TeamSlot, TeamSlot, TeamSlot, TeamSlot]
  /** 阵容标签（"周本"/"试炼"/"主线" 等） */
  tags: string[]
  /** 关联的 Boss ID（可选） */
  bossId?: string
  /** 富文本备注（攻略思路、技能时序等） */
  description?: string
  /** 创建/更新时间 */
  createdAt: number
  updatedAt: number
}

/** 创建一个空阵容的工厂函数 */
export function createEmptyTeam(name = '新阵容'): Team {
  const emptySlot = (): TeamSlot => ({ characterId: null })
  const now = Date.now()
  return {
    id: crypto.randomUUID(),
    name,
    front: [emptySlot(), emptySlot(), emptySlot(), emptySlot()],
    back: [emptySlot(), emptySlot(), emptySlot(), emptySlot()],
    tags: [],
    description: '',
    createdAt: now,
    updatedAt: now,
  }
}

/** 解析后的阵容（slot 里附带 Character 对象，UI 显示用） */
export interface ResolvedTeamSlot {
  slot: TeamSlot
  character: Character | null
}
