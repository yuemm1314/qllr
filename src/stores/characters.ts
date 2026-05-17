// src/stores/characters.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Character, CharacterDetailEntry } from '@/types/character';

// Vite 支持直接 import JSON
import listData from '@/data/wiki_character_list.json';
import detailsData from '@/data/wiki_character_details.json';
// 旧头像数据作为头像兜底（list 里也有 avatar 字段，但有少量 null）
import avatarsData from '@/data/wiki_avatars.json';

interface AvatarsFile {
  byName: Record<string, { avatar?: string; wikiPath?: string; wikiTitle?: string }>;
}

export const useCharactersStore = defineStore('characters', () => {
  const characters = ref<Character[]>([]);
  const loaded = ref(false);

  function load() {
    if (loaded.value) return;

    const avatarsMap = (avatarsData as AvatarsFile).byName || {};
    const detailsMap = (detailsData as { characters: Record<string, CharacterDetailEntry> })
      .characters || {};

    const list = (listData as any).characters as Character[];
    characters.value = list.map((c) => {
      const avatarFallback = avatarsMap[c.name]?.avatar;
      return {
        ...c,
        avatar: c.avatar || avatarFallback || null,
        details: detailsMap[c.name],
      };
    });
    loaded.value = true;
  }

  const total = computed(() => characters.value.length);
  const detailedCount = computed(
    () => characters.value.filter((c) => c.details).length
  );

  function findByName(name: string): Character | undefined {
    return characters.value.find((c) => c.name === name);
  }

  function findById(id: string): Character | undefined {
    return characters.value.find((c) => c.id === id);
  }

  return { characters, loaded, total, detailedCount, load, findByName, findById };
});
