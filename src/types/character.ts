
---

## TypeScript 类型定义

### 文件: `src/types/character.ts`

```ts
/**
 * 角色相关的类型定义。
 *
 * 设计原则：
 * 1. 一个角色（Character）= Wiki 上一个独立条目（例如"提米诺斯Ex" 和 "提米诺斯" 是两个 Character）
 * 2. 静态字段（从 Wiki 来的）和用户字段（你自己练的角色配置）分开
 * 3. 留足扩展位：未来要加属性、武器、星级，直接补字段即可，旧数据兼容
 */

/** 武器类型 */
export type WeaponType = '剑' | '枪' | '短剑' | '斧' | '弓' | '杖' | '扇' | '书' | '未知'

/** 元素属性 */
export type ElementType = '火' | '冰' | '雷' | '风' | '光' | '暗' | '无' | '未知'

/** 职业（八职业 + 后续扩展） */
export type JobType =
  | '剑士' | '战士' | '盗贼' | '商人'
  | '猎人' | '药师' | '舞娘' | '神官'
  | '学者' | '其他'

/**
 * 角色基础信息（静态，来自 Wiki）
 *
 * 注意：当前 Wiki JSON 里大量字段缺失（job / weapon / element / rarity），
 * 我们先把字段留好，未来爬虫补全时直接填入即可，前端 UI 已经按字段在显示。
 */
export interface Character {
  /** 唯一 ID，使用 Wiki 名称（中文）作为 ID 保证稳定 */
  id: string
  /** 显示名称 */
  name: string
  /** 头像 URL（Wiki CDN 直链） */
  avatar: string
  /** Wiki 详情页路径，例如 "/octopathsp/提米诺斯Ex" */
  wikiPath?: string
  /** 主动技能名列表（中文） */
  activeSkills: string[]

  // 以下字段当前爬虫未抓取，留作扩展位
  job?: JobType
  weapon?: WeaponType
  subWeapon?: WeaponType
  element?: ElementType
  /** 星级：3 / 4 / 5 */
  rarity?: 3 | 4 | 5
  /** 标签（"破盾"/"输出"/"奶妈"/"辅助" 等，可自由扩展） */
  tags?: string[]
}

/**
 * 用户对某个角色的"个人配置"（与游戏存档对应）
 * 阵容保存时只引用 characterId，不复制整个角色信息
 */
export interface CharacterOwned {
  characterId: string
  /** 是否拥有（未拥有的角色也可以加入"理论阵容") */
  owned: boolean
  /** 等级 */
  level?: number
  /** 觉醒等级 0~5 */
  awakening?: number
  /** 突破 */
  ascension?: number
  /** 备注 */
  note?: string
}
