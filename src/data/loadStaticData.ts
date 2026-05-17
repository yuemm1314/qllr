/**
 * 静态数据源实现：从 src/data/ 下的 JSON 文件加载。
 *
 * Vite 会把 JSON 直接打包进 bundle，零运行时网络开销。
 * 如果文件不存在，会抛错并提示用户运行下载命令。
 */

import type { Character } from '@/types/character'
import type { DataSource } from './dataSource'

// ⚠️ 这两个 import 在你下载完 JSON 文件之前会报红，是正常的
// 下载命令见 README.md "准备数据" 一节
import avatarsRaw from './wiki_avatars.json'
import skillsRaw from './wiki_active_skills_zh.json'

interface AvatarEntry {
  avatar: string
  wikiPath: string
  wikiTitle: string
}

interface SkillEntry {
  activeSkillsZh: string[]
  wikiUrl: string
  wikiTitle: string
  count: number
}

interface AvatarFile {
  schema: string
  fetchedAt: string
  count: number
  byName: Record<string, AvatarEntry>
}

interface SkillFile {
  schema: string
  fetchedAt: string
  characterCount: number
  byCharacter: Record<string, SkillEntry>
}

export class StaticDataSource implements DataSource {
  private cache: Character[] | null = null

  async loadCharacters(): Promise<Character[]> {
    if (this.cache) return this.cache

    const avatarFile = avatarsRaw as unknown as AvatarFile
    const skillFile = skillsRaw as unknown as SkillFile

    const result: Character[] = []
    for (const [name, avatar] of Object.entries(avatarFile.byName)) {
      const skills = skillFile.byCharacter[name]
      result.push({
        id: name,
        name,
        avatar: avatar.avatar,
        wikiPath: avatar.wikiPath,
        activeSkills: skills?.activeSkillsZh ?? [],
        // 以下字段当前数据集没有，留空待补
        job: undefined,
        weapon: undefined,
        element: undefined,
        rarity: undefined,
        tags: [],
      })
    }

    // 按名字稳定排序，便于 UI 浏览
    result.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'))

    this.cache = result
    return result
  }

  describe(): string {
    const file = avatarsRaw as unknown as AvatarFile
    return `Wiki 离线数据（共 ${file.count} 个角色）`
  }

  async lastUpdatedAt(): Promise<string | null> {
    const file = avatarsRaw as unknown as AvatarFile
    return file.fetchedAt ?? null
  }
}
