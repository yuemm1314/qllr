// TeamSlot.vue <script setup>
import { computed } from 'vue';
import { useCharactersStore } from '@/stores/characters';
import type { TeamSlot } from '@/types/team';

const props = defineProps<{
  slot: TeamSlot;
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

// MAX 属性兜底
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
</script>
