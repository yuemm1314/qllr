/**
 * 数据源抽象层（重要！）
 * ============================================
 * 这一层的目的是把"数据从哪儿来"与"前端怎么用"解耦。
 *
 * 当前实现：从打包进来的静态 JSON 文件加载（StaticDataSource）。
 * 未来可以无缝切换到：
 *   - IndexedDB（用户离线 + 大量数据）
 *   - 远程 API（如果你以后想搭服务器同步多端）
 *   - WebSocket 实时推送
 *
 * 切换时：只需要新写一个实现 DataSource 接口的类，在 index.ts 里换掉即可，
 *        其他业务代码（stores / views）一行不用改。
 */

import type { Character } from '@/types/character'

export interface DataSource {
  /** 加载所有角色（含技能） */
  loadCharacters(): Promise<Character[]>
  /** 数据来源描述（用于 UI 展示，比如"来自 Wiki 离线包 / 来自远程 API"） */
  describe(): string
  /** 数据最后更新时间（ISO 字符串），UI 可显示"x 天前更新" */
  lastUpdatedAt(): Promise<string | null>
}
