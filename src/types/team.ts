import type { Character } from './character'

/**
 * 阵容槽位 — 一个位置上的角色及其个人配置
 *
 * 注：Wiki 没有角色等级/觉醒数据，这些是"用户在自己存档里"的状态，
 * 所以放在 slot 里而不是 Character 里。
 */
export interface TeamSlot {
  characterId: string | null
  note?: string
  /** 等级 */
  level?: number
  /** 觉醒 0-5 */
  awakening?: number
  /** 体力当前/最大（用户手填） */
  hp?: number
  hpMax?: number
  /** 精力当前/最大 */
  sp?: number
  spMax?: number
}

export interface Team {
  id: string
  name: string
  front: [TeamSlot, TeamSlot, TeamSlot, TeamSlot]
  back: [TeamSlot, TeamSlot, TeamSlot, TeamSlot]
  tags: string[]
  bossId?: string
  description?: string
  createdAt: number
  updatedAt: number
}

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

export interface ResolvedTeamSlot {
  slot: TeamSlot
  character: Character | null
}
