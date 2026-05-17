<script setup lang="ts">
import { computed } from 'vue';
import { useCharactersStore } from '@/stores/characters';
import type { TeamSlot as TeamSlotType } from '@/types/team';

const props = defineProps<{
  slot: TeamSlotType;
  position: 'front' | 'back';
  index: number;
}>();

defineEmits<{
  (e: 'click'): void;
  (e: 'clear'): void;
}>();

const store = useCharactersStore();

const character = computed(() =>
  props.slot.characterName ? store.findByName(props.slot.characterName) : undefined
);

// === MAX 属性兜底（新增） ===
const maxHp = computed(() => character.value?.details?.maxStats?.hp);
const maxSp = computed(() => character.value?.details?.maxStats?.sp);

const hp = computed(() => props.slot.hp ?? maxHp.value);
const hpMax = computed(() => props.slot.hpMax ?? maxHp.value);
const sp = computed(() => props.slot.sp ?? maxSp.value);
const spMax = computed(() => props.slot.spMax ?? maxSp.value);

const hasHp = computed(() => hp.value != null && hpMax.value != null);
const hasSp = computed(() => sp.value != null && spMax.value != null);

const hpPct = computed(() =>
  hasHp.value ? Math.round((hp.value! / hpMax.value!) * 100) : 0
);
const spPct = computed(() =>
  hasSp.value ? Math.round((sp.value! / spMax.value!) * 100) : 0
);

// === 兼容旧 template 里可能引用的变量（如果存在请保留） ===
const level = computed(() => props.slot.level);
const awakening = computed(() => props.slot.awakening);
</script>

<template>
  <div
    class="slot"
    :class="[
      `jrpg-theme-${row}`,
      { filled: !!character, empty: !character },
    ]"
    @click="$emit('click')"
  >
    <!-- 左侧装饰条 -->
    <div class="side-bar"></div>

    <template v-if="character">
      <!-- 头像 -->
      <div class="portrait-wrap">
        <el-image :src="character.avatar" class="portrait" fit="contain" loading="lazy">
          <template #error>
            <div class="portrait-fallback">{{ character.name.slice(0, 2) }}</div>
          </template>
        </el-image>
      </div>

      <!-- 信息区 -->
      <div class="info">
        <!-- 第一行：姓名 + 星级 -->
        <div class="row-top">
          <span class="name">{{ character.name }}</span>
          <span v-if="hasAwakening" class="stars">
            {{ '★'.repeat(awakening) }}
          </span>
          <span v-else class="stars-empty">未配置</span>
        </div>

        <!-- 第二行：等级 + HP/SP 条 -->
        <div class="row-bottom">
          <div class="level-box">
            <span class="level-label">Lv</span>
            <span class="level-val" :class="{ none: slot.level === undefined }">
              {{ slot.level ?? '—' }}
            </span>
          </div>

          <div class="bars">
            <div class="bar-row">
              <span class="bar-label hp-label">HP</span>
              <div class="jrpg-bar" :class="{ inactive: !hasHp }">
                <div
                  v-if="hasHp"
                  class="jrpg-bar-fill hp"
                  :style="{ width: hpPct + '%' }"
                ></div>
              </div>
              <span class="bar-val">
                <template v-if="hasHp">{{ slot.hp ?? 0 }}/{{ slot.hpMax }}</template>
                <template v-else>—</template>
              </span>
            </div>
            <div class="bar-row">
              <span class="bar-label sp-label">SP</span>
              <div class="jrpg-bar" :class="{ inactive: !hasSp }">
                <div
                  v-if="hasSp"
                  class="jrpg-bar-fill sp"
                  :style="{ width: spPct + '%' }"
                ></div>
              </div>
              <span class="bar-val">
                <template v-if="hasSp">{{ slot.sp ?? 0 }}/{{ slot.spMax }}</template>
                <template v-else>—</template>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右上清空 -->
      <button class="clear-btn" @click.stop="$emit('clear')" title="移除角色">
        <el-icon><Close /></el-icon>
      </button>
    </template>

    <template v-else>
      <div class="empty-content">
        <el-icon class="empty-plus"><Plus /></el-icon>
        <span class="empty-label">{{ label || '空位' }}</span>
      </div>
    </template>
  </div>
</template>

<style scoped>
.slot {
  position: relative;
  display: flex;
  align-items: stretch;
  height: 78px;
  background:
    linear-gradient(180deg, rgba(255, 220, 150, 0.03), transparent 50%),
    var(--jrpg-bg-card);
  border: 1px solid var(--jrpg-border-gold);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  box-shadow: var(--jrpg-shadow-card);
}
.slot:hover {
  border-color: var(--jrpg-border-gold-bright);
  background:
    linear-gradient(180deg, rgba(255, 220, 150, 0.08), transparent 50%),
    var(--jrpg-bg-card-hover);
  transform: translateY(-1px);
}
.slot.empty {
  border-style: dashed;
  background: var(--jrpg-bg-slot);
}
.slot.empty:hover {
  border-style: solid;
}

.side-bar {
  width: 4px;
  background: linear-gradient(180deg, var(--row-color), var(--row-color-dim));
  box-shadow: 0 0 6px var(--row-color);
}
.slot.empty .side-bar {
  background: var(--jrpg-border);
  box-shadow: none;
  opacity: 0.4;
}

/* 头像：用 contain 不被裁切，背景填补留白 */
.portrait-wrap {
  width: 64px;
  height: 100%;
  padding: 4px;
  flex-shrink: 0;
}
.portrait {
  width: 100%;
  height: 100%;
  border-radius: 3px;
  border: 1px solid var(--jrpg-border);
  background:
    radial-gradient(circle at center, #3a2a18, var(--jrpg-bg-deep));
}
.portrait-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--jrpg-bg-deep);
  color: var(--jrpg-text-muted);
  font-size: 11px;
  border-radius: 3px;
}

/* 信息两行 */
.info {
  flex: 1;
  min-width: 0;
  padding: 6px 10px 6px 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.name {
  font-family: 'Noto Serif SC', 'STSong', serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--jrpg-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.6);
}
.stars {
  font-size: 11px;
  color: var(--jrpg-text-gold);
  text-shadow: 0 0 4px rgba(241, 198, 82, 0.5);
  flex-shrink: 0;
  letter-spacing: 1px;
}
.stars-empty {
  font-size: 10px;
  color: var(--jrpg-text-muted);
  flex-shrink: 0;
  font-style: italic;
}

.row-bottom {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 等级框 */
.level-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  min-width: 32px;
  padding: 2px 4px;
  border-right: 1px solid var(--jrpg-border);
  line-height: 1;
}
.level-label {
  font-size: 9px;
  color: var(--jrpg-text-muted);
  font-family: 'Cinzel', monospace;
  letter-spacing: 0.5px;
}
.level-val {
  font-size: 16px;
  font-weight: 700;
  color: var(--jrpg-text-gold);
  font-family: 'Cinzel', 'Noto Serif SC', serif;
  margin-top: 1px;
}
.level-val.none {
  color: var(--jrpg-text-muted);
  font-size: 14px;
}

/* 双条 */
.bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
}
.bar-label {
  width: 16px;
  flex-shrink: 0;
  font-family: 'Cinzel', monospace;
  font-weight: 600;
  font-size: 10px;
}
.hp-label {
  color: var(--jrpg-hp);
}
.sp-label {
  color: var(--jrpg-sp);
}
.bar-val {
  font-size: 10px;
  color: var(--jrpg-text-soft);
  min-width: 70px;
  text-align: right;
  font-family: 'Cinzel', monospace;
  flex-shrink: 0;
}
.jrpg-bar {
  flex: 1;
  min-width: 0;
}
.jrpg-bar.inactive {
  background:
    repeating-linear-gradient(
      45deg,
      rgba(0, 0, 0, 0.5),
      rgba(0, 0, 0, 0.5) 4px,
      rgba(40, 30, 20, 0.5) 4px,
      rgba(40, 30, 20, 0.5) 8px
    );
}

/* 清空按钮 */
.clear-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid var(--jrpg-border);
  color: var(--jrpg-text-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
  font-size: 12px;
  padding: 0;
  z-index: 2;
}
.slot:hover .clear-btn {
  opacity: 1;
}
.clear-btn:hover {
  background: var(--jrpg-front);
  border-color: var(--jrpg-front);
  color: #fff;
}

/* 空位 */
.empty-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.empty-plus {
  font-size: 24px;
  color: var(--jrpg-text-muted);
}
.empty-label {
  font-size: 11px;
  color: var(--jrpg-text-muted);
  letter-spacing: 1px;
}
</style>
