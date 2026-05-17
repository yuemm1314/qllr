/**
 * Boss 笔记相关类型。第一阶段只做最小可用版本：名字 + 弱点 + 备注。
 * 第二阶段会扩展为完整的"机制/阶段/HP/护盾值"模型。
 */

import type { ElementType, WeaponType } from './character'

export interface BossNote {
  id: string
  name: string
  /** 弱点武器 */
  weakWeapons: WeaponType[]
  /** 弱点元素 */
  weakElements: ElementType[]
  /** 护盾值（可选） */
  shield?: number
  /** 机制描述（自由文本） */
  mechanics?: string
  /** 个人攻略笔记 */
  notes?: string
  /** 关联的阵容 ID 列表 */
  relatedTeamIds: string[]
  createdAt: number
  updatedAt: number
}

export function createEmptyBossNote(name = '新 Boss'): BossNote {
  const now = Date.now()
  return {
    id: crypto.randomUUID(),
    name,
    weakWeapons: [],
    weakElements: [],
    relatedTeamIds: [],
    createdAt: now,
    updatedAt: now,
  }
}
