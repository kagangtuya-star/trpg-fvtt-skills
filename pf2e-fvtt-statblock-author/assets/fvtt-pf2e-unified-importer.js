/**
 * PF2e Unified Statblock Importer Macro
 * Version 1.0.0
 *
 * Preferred workflow:
 *   1. Give a Chinese/English PF2e monster or hazard stat block to the
 *      pf2e-fvtt-statblock-author skill.
 *   2. The skill emits a compact `pf2e-fvtt-actor` JSON payload.
 *   3. Paste that JSON here to create a new Actor or fully sync a selected Actor.
 *
 * Also accepted:
 *   - legacy/small ability payloads with an `items` array;
 *   - GLUniverse strict Markdown when gluniverse-pf2e-statsblock-import is active.
 *
 * Sync safety:
 *   - core Actor fields are synchronized from the payload;
 *   - only Item documents previously created by THIS macro are deleted/rebuilt;
 *   - manually-created Items are never deleted by full sync.
 */

(async () => {
  const MACRO_ID = "pf2e-unified-statblock-importer";
  const SCHEMA_ID = "pf2e-fvtt-actor";
  const SCHEMA_VERSION = 1;
  const GL_IMPORTER_ID = "gluniverse-pf2e-statsblock-import";
  const IMPORT_FOLDER = "Imported NPCs";
  const SUPPORTED_ACTOR_TYPES = new Set(["npc", "hazard"]);
  const ABILITY_KEYS = ["str", "dex", "con", "int", "wis", "cha"];
  const INVENTORY_TYPES = new Set(["weapon", "armor", "shield", "consumable", "equipment", "backpack", "treasure"]);
  const currentBatchId = globalThis.foundry?.utils?.randomID?.() ?? `${Date.now()}`;
  const SIZE_MAP = {
    tiny: "tiny", small: "sm", sm: "sm", medium: "med", med: "med",
    large: "lg", lg: "lg", huge: "huge", gargantuan: "grg", grg: "grg"
  };

  if (game.system?.id !== "pf2e") {
    ui.notifications.error("PF2e Unified Importer: 当前世界不是 PF2e 系统。");
    return;
  }
  if (!game.user?.isGM) {
    ui.notifications.error("PF2e Unified Importer: 需要 GM 权限。");
    return;
  }

  const actors = Array.from(game.actors ?? [])
    .filter((actor) => SUPPORTED_ACTOR_TYPES.has(actor.type))
    .sort((a, b) => a.name.localeCompare(b.name));
  const controlled = globalThis.canvas?.tokens?.controlled ?? [];
  const controlledActor = controlled.length === 1 && SUPPORTED_ACTOR_TYPES.has(controlled[0].actor?.type)
    ? controlled[0].actor
    : null;

  const actorOptions = [
    `<option value="" ${controlledActor ? "" : "selected"}>— 创建新 Actor（完整怪物载荷）—</option>`,
    ...actors.map((actor) => `<option value="${escapeHtml(actor.id)}" ${actor.id === controlledActor?.id ? "selected" : ""}>${escapeHtml(actor.name)} [${actor.type}]</option>`)
  ].join("");

  const sample = JSON.stringify({
    schema: SCHEMA_ID,
    version: SCHEMA_VERSION,
    actor: {
      name: "示例幽影 Example Shadow",
      kind: "npc",
      level: 6,
      rarity: "uncommon",
      size: "med",
      traits: ["incorporeal", "undead"],
      description: "一只用于测试完整导入的数据块。",
      perception: { mod: 15, details: "", senses: [{ type: "darkvision" }] },
      languages: { value: ["common"], details: "" },
      skills: { stealth: 16, occultism: 13 },
      abilities: { str: 2, dex: 5, con: 3, int: 2, wis: 3, cha: 4 },
      ac: { value: 24, details: "" },
      saves: { fortitude: 13, reflex: 17, will: 15 },
      hp: { value: 95, details: "" },
      speed: { value: 25, otherSpeeds: [{ type: "fly", value: 40 }], details: "" },
      immunities: [], weaknesses: [], resistances: [],
      attacks: [{
        name: "幽影之触 Shadow Touch",
        type: "melee",
        bonus: 17,
        traits: ["agile", "magical"],
        damageRolls: [{ formula: "2d8+7", type: "void", category: null }],
        effects: [],
        description: ""
      }],
      actions: [{
        name: "幽影爆破 Shadow Burst",
        actionType: "action",
        actions: 2,
        category: "offensive",
        traits: ["divine", "void"],
        description: "对@Template[type:burst|distance:20]范围内所有生物造成@Damage[6d6[void]|options:area-damage]伤害（@Check[reflex|dc:24|basic|options:area-effect,inflicts:slowed]豁免）。失败获得迟缓 Slowed 1，持续1轮。"
      }],
      spellcasting: [], inventory: [], effects: [], notes: []
    }
  }, null, 2);

  const content = `
    <div style="display:grid;gap:.75rem;min-width:720px">
      <label style="display:grid;gap:.25rem">
        <strong>目标 Actor</strong>
        <select name="actorId">${actorOptions}</select>
      </label>
      <label style="display:grid;gap:.25rem">
        <strong>Skill 输出 / GLUniverse strict Markdown</strong>
        <textarea name="source" rows="26" spellcheck="false" style="font-family:monospace;resize:vertical">${escapeHtml(sample)}</textarea>
      </label>
      <label style="display:flex;align-items:center;gap:.4rem">
        <input type="checkbox" name="syncCore" checked>
        <span>同步 Actor 核心数据（等级、Traits、属性、AC/HP、豁免、技能、感官、I/W/R、速度等）</span>
      </label>
      <label style="display:flex;align-items:center;gap:.4rem">
        <input type="checkbox" name="syncItems" checked>
        <span>全量同步本宏管理的攻击、能力、法术、物品、Effect/Aura</span>
      </label>
      <p style="margin:0;opacity:.78">完整载荷：不选择目标时创建新 Actor；选择目标时同步。能力载荷：必须选择 NPC/Hazard。手工创建且没有本宏 flag 的 Item 不会被删除。</p>
    </div>`;

  let formData;
  try {
    formData = await promptInput(content);
  } catch (error) {
    console.error(`${MACRO_ID}: dialog error`, error);
    ui.notifications.error(`PF2e Unified Importer: ${error.message ?? error}`);
    return;
  }
  if (!formData) return;

  const values = formDataToObject(formData);
  const source = String(values.source ?? "").trim();
  if (!source) {
    ui.notifications.warn("PF2e Unified Importer: 没有输入数据。");
    return;
  }
  const syncCore = checkboxValue(values.syncCore);
  const syncItems = checkboxValue(values.syncItems);
  const targetActor = values.actorId ? game.actors.get(String(values.actorId)) : null;

  let parsed;
  try {
    parsed = await parseInput(source);
  } catch (error) {
    console.error(`${MACRO_ID}: parse error`, error);
    ui.notifications.error(`PF2e Unified Importer: 解析失败：${error.message ?? error}`);
    return;
  }

  try {
    if (parsed.kind === "abilities") {
      if (!targetActor || !SUPPORTED_ACTOR_TYPES.has(targetActor.type)) {
        throw new Error("能力载荷必须选择一个 NPC/Hazard Actor 作为目标。");
      }
      const result = await importAbilityPayload(targetActor, parsed.items);
      ui.notifications.info(`PF2e Unified Importer: ${targetActor.name} 已更新 ${result.updated} 个、创建 ${result.created} 个能力。`);
      return;
    }

    const npc = normalizeActorPayload(parsed.actor);
    validateActorPayload(npc);

    if (targetActor && !SUPPORTED_ACTOR_TYPES.has(targetActor.type)) {
      throw new Error("目标必须是 NPC 或 Hazard Actor。");
    }
    if (targetActor && targetActor.type !== resolveActorType(npc)) {
      throw new Error(`载荷类型为 ${resolveActorType(npc)}，不能同步到 ${targetActor.type} Actor。`);
    }

    let actor = targetActor;
    const creating = !actor;
    if (creating) {
      const folder = await getOrCreateFolder();
      const actorSource = await buildActorSource(npc, source, { forUpdate: false });
      actorSource.folder = folder?.id ?? null;
      actor = await Actor.create(actorSource, { renderSheet: false });
      if (!actor) throw new Error("Actor.create 未返回 Actor。");
    } else if (syncCore) {
      const actorSource = await buildActorSource(npc, source, { forUpdate: true, actor });
      await actor.update(actorSource);
    }

    let itemSummary = { deleted: 0, created: 0, unresolvedSpells: [] };
    if (syncItems || creating) {
      itemSummary = await syncManagedItems(actor, npc);
    }

    actor.sheet?.render?.(true);
    const unresolved = itemSummary.unresolvedSpells.length
      ? `；未匹配法术 ${itemSummary.unresolvedSpells.length} 个（已保留在施法条目说明中）`
      : "";
    ui.notifications.info(`PF2e Unified Importer: ${creating ? "已创建" : "已同步"} ${actor.name}；重建 ${itemSummary.created} 个受管 Item${unresolved}。`);
  } catch (error) {
    console.error(`${MACRO_ID}: import error`, error);
    ui.notifications.error(`PF2e Unified Importer: 导入失败：${error.message ?? error}`);
  }

  async function parseInput(text) {
    if (sourceLooksJson(text)) {
      const payload = JSON.parse(text);
      if (Array.isArray(payload)) return { kind: "abilities", items: payload.map(normalizeAbilityPayload) };
      if (payload?.schema === SCHEMA_ID || payload?.actor) {
        const version = Number(payload.version ?? 1);
        if (version > SCHEMA_VERSION) throw new Error(`载荷版本 ${version} 高于宏支持版本 ${SCHEMA_VERSION}。`);
        return { kind: "actor", actor: payload.actor ?? payload };
      }
      if (Array.isArray(payload?.items)) return { kind: "abilities", items: payload.items.map(normalizeAbilityPayload) };
      throw new Error("JSON 不是 pf2e-fvtt-actor 完整载荷，也不是能力 items 载荷。");
    }

    const module = game.modules.get(GL_IMPORTER_ID);
    const api = module?.active ? module.api : null;
    if (!api?.parse) {
      throw new Error("非 JSON 输入需要启用 GLUniverse PF2e Stat Block Importer；推荐先让 PF2e Skill 转换为 JSON。 ");
    }
    const result = api.parse(text);
    if (!result?.npc) throw new Error("GLUniverse parser 没有返回 npc 数据。");
    if (result.errors?.length) throw new Error(result.errors.join("；"));
    if (result.warnings?.length) console.warn(`${MACRO_ID}: GLUniverse warnings`, result.warnings);
    return { kind: "actor", actor: result.npc };
  }

  function sourceLooksJson(text) {
    const first = String(text).trimStart()[0];
    return first === "{" || first === "[";
  }

  function normalizeActorPayload(raw) {
    if (!raw || typeof raw !== "object") throw new Error("actor 必须是对象。");
    const name = String(raw.name ?? "").trim();
    if (!name) throw new Error("actor.name 不能为空。");

    const kind = resolveKind(raw.kind ?? raw.actorType ?? raw.type ?? "npc");
    const level = int(raw.level, 1);
    const size = SIZE_MAP[slugify(raw.size ?? "med")] ?? "med";
    const rarity = normalizeRarity(raw.rarity);
    const traits = list(raw.traits).map(slugify).filter(Boolean);
    const abilities = Object.fromEntries(ABILITY_KEYS.map((key) => [key, int(raw.abilities?.[key], 0)]));
    const savesRaw = raw.saves ?? {};

    return {
      name,
      kind,
      level,
      rarity,
      size,
      traits,
      description: String(raw.description ?? ""),
      image: String(raw.image ?? raw.img ?? "").trim(),
      token: raw.token && typeof raw.token === "object" ? structuredCloneSafe(raw.token) : {},
      initiative: String(raw.initiative ?? "perception"),
      perception: normalizePerception(raw.perception),
      languages: normalizeLanguages(raw.languages),
      skills: normalizeSkills(raw.skills),
      abilities,
      ac: normalizeValueDetails(raw.ac, 10),
      saves: {
        fortitude: normalizeSave(savesRaw.fortitude ?? savesRaw.fort),
        reflex: normalizeSave(savesRaw.reflex ?? savesRaw.ref),
        will: normalizeSave(savesRaw.will)
      },
      allSaves: String(raw.allSaves ?? ""),
      hp: normalizeValueDetails(raw.hp, 10),
      speed: normalizeSpeed(raw.speed),
      immunities: normalizeIwr(raw.immunities),
      weaknesses: normalizeIwr(raw.weaknesses),
      resistances: normalizeIwr(raw.resistances),
      attacks: listObjects(raw.attacks).map(normalizeAttack),
      actions: listObjects(raw.actions ?? raw.abilitiesList).map(normalizeAbilityPayload),
      spellcasting: listObjects(raw.spellcasting).map(normalizeSpellcasting),
      inventory: listObjects(raw.inventory).map(normalizeInventory),
      effects: listObjects(raw.effects).map(normalizeEffect),
      notes: list(raw.notes).map(String),
      hazard: normalizeHazard(raw.hazard)
    };
  }

  function validateActorPayload(npc) {
    if (!Number.isInteger(npc.level)) throw new Error("level 必须是整数。");
    if (!SUPPORTED_ACTOR_TYPES.has(resolveActorType(npc))) throw new Error("仅支持 npc/hazard。");
    warnUnknownSlugs("creature trait", npc.traits, Object.keys(CONFIG?.PF2E?.creatureTraits ?? {}));
    for (const attack of npc.attacks) {
      warnUnknownSlugs(`attack trait (${attack.name})`, attack.traits, Object.keys(CONFIG?.PF2E?.npcAttackTraits ?? {}));
      for (const roll of attack.damageRolls) {
        if (roll.type && CONFIG?.PF2E?.damageTypes && !(roll.type in CONFIG.PF2E.damageTypes)) {
          console.warn(`${MACRO_ID}: unknown damage type`, roll.type, attack.name);
        }
      }
    }
    for (const action of npc.actions) {
      warnUnknownSlugs(`action trait (${action.name})`, action.traits, Object.keys(CONFIG?.PF2E?.actionTraits ?? {}));
    }
  }

  function normalizePerception(value) {
    if (typeof value === "number" || typeof value === "string") return { mod: int(value, 0), details: "", senses: [] };
    const obj = value && typeof value === "object" ? value : {};
    return {
      mod: int(obj.mod ?? obj.value, 0),
      details: String(obj.details ?? ""),
      senses: listObjects(obj.senses).map((sense) => {
        const out = { type: slugify(sense.type ?? sense.name) };
        if (Number.isFinite(Number(sense.range))) out.range = Number(sense.range);
        if (sense.acuity) out.acuity = slugify(sense.acuity);
        return out;
      }).filter((sense) => sense.type)
    };
  }

  function normalizeLanguages(value) {
    if (Array.isArray(value)) return { value: value.map(slugify).filter(Boolean), details: "" };
    if (typeof value === "string") return { value: splitList(value).map(slugify).filter(Boolean), details: "" };
    const obj = value && typeof value === "object" ? value : {};
    return { value: list(obj.value).map(slugify).filter(Boolean), details: String(obj.details ?? "") };
  }

  function normalizeSkills(value) {
    const result = {};
    if (!value || typeof value !== "object") return result;
    for (const [key, raw] of Object.entries(value)) {
      const skill = normalizeSkillSlug(key);
      result[skill] = int(raw?.base ?? raw?.value ?? raw, 0);
    }
    return result;
  }

  function normalizeSave(value) {
    if (value && typeof value === "object") return { value: int(value.value ?? value.mod, 0), details: String(value.details ?? value.saveDetail ?? "") };
    return { value: int(value, 0), details: "" };
  }

  function normalizeValueDetails(value, fallback) {
    if (value && typeof value === "object") return { value: int(value.value ?? value.max, fallback), details: String(value.details ?? "") };
    return { value: int(value, fallback), details: "" };
  }

  function normalizeSpeed(value) {
    if (typeof value === "number" || typeof value === "string") return { value: int(value, 25), otherSpeeds: [], details: "" };
    const obj = value && typeof value === "object" ? value : {};
    return {
      value: int(obj.value, 25),
      otherSpeeds: listObjects(obj.otherSpeeds ?? obj.other).map((entry) => ({ type: slugify(entry.type), value: int(entry.value, 0) })).filter((entry) => entry.type && entry.value > 0),
      details: String(obj.details ?? "")
    };
  }

  function normalizeIwr(value) {
    if (!value) return [];
    if (typeof value === "string") return splitList(value).map((part) => {
      const match = part.match(/^(.*?)(?:\s+(\d+))?$/);
      return { type: slugify(match?.[1] ?? part), value: match?.[2] ? Number(match[2]) : undefined };
    }).filter((entry) => entry.type);
    return list(value).map((entry) => {
      if (typeof entry === "string") return { type: slugify(entry) };
      return { type: slugify(entry?.type ?? entry?.name), value: entry?.value == null ? undefined : int(entry.value, 0), exceptions: entry?.exceptions };
    }).filter((entry) => entry.type);
  }

  function normalizeAttack(raw, index) {
    const name = String(raw.name ?? `Attack ${index + 1}`).trim();
    const damageInput = raw.damageRolls ?? raw.damage ?? [];
    const damageRolls = Array.isArray(damageInput)
      ? damageInput.map(normalizeDamageRoll).filter(Boolean)
      : typeof damageInput === "object" && damageInput
        ? Object.values(damageInput).map((roll) => normalizeDamageRoll({ formula: roll.damage ?? roll.formula, type: roll.damageType ?? roll.type, category: roll.category })).filter(Boolean)
        : parseDamageText(String(damageInput));
    return {
      name,
      type: slugify(raw.type ?? raw.kind ?? "melee") === "ranged" ? "ranged" : "melee",
      bonus: int(raw.bonus ?? raw.attack ?? raw.modifier, 0),
      traits: list(raw.traits).map(slugify).filter(Boolean),
      effects: list(raw.effects ?? raw.attackEffects).map(slugify).filter(Boolean),
      damageRolls,
      range: raw.range == null ? null : int(raw.range?.increment ?? raw.range, 30),
      maxRange: raw.range?.max == null ? null : int(raw.range.max, 0),
      area: normalizeArea(raw.area),
      action: slugify(raw.action ?? "strike") || "strike",
      description: String(raw.description ?? ""),
      rules: Array.isArray(raw.rules) ? structuredCloneSafe(raw.rules) : []
    };
  }

  function normalizeDamageRoll(raw) {
    if (!raw) return null;
    if (typeof raw === "string") return parseDamageText(raw)[0] ?? null;
    const formula = String(raw.formula ?? raw.damage ?? "").replace(/\s+/g, "");
    if (!formula) return null;
    return { formula, type: slugify(raw.type ?? raw.damageType ?? "bludgeoning") || "bludgeoning", category: raw.category ? slugify(raw.category) : null };
  }

  function parseDamageText(text) {
    const result = [];
    for (const piece of String(text).replace(/\bplus\b/gi, ",").split(/[,;]/).map((p) => p.trim()).filter(Boolean)) {
      const match = piece.match(/(\d+d\d+(?:\s*[+\-]\s*\d+)?|\d+)\s+(?:(persistent|precision|splash)\s+)?([a-z-]+)(?:\s+damage)?/i);
      if (match) result.push({ formula: match[1].replace(/\s+/g, ""), category: match[2] ? slugify(match[2]) : null, type: slugify(match[3]) });
    }
    return result;
  }

  function normalizeArea(value) {
    if (!value) return null;
    if (typeof value === "string") {
      const match = value.match(/(\d+).*?(burst|cone|emanation|line)/i);
      return match ? { value: Number(match[1]), type: slugify(match[2]) } : null;
    }
    if (typeof value === "object" && value.type && value.value != null) return { type: slugify(value.type), value: int(value.value, 5) };
    return null;
  }

  function normalizeAbilityPayload(raw, index = 0) {
    if (!raw || typeof raw !== "object") throw new Error(`能力 ${index + 1} 不是对象。`);
    const name = String(raw.name ?? "").trim();
    if (!name) throw new Error(`能力 ${index + 1} 缺少 name。`);
    const actionType = normalizeActionType(raw.actionType ?? raw.type ?? "action");
    return {
      name,
      actionType,
      actions: actionType === "action" ? clampInt(raw.actions ?? 1, 1, 3) : null,
      category: normalizeCategory(raw.category),
      traits: list(raw.traits).map(slugify).filter(Boolean),
      frequency: raw.frequency ?? "",
      description: String(raw.description ?? ""),
      rules: Array.isArray(raw.rules) ? structuredCloneSafe(raw.rules) : [],
      img: typeof raw.img === "string" ? raw.img.trim() : ""
    };
  }

  function normalizeSpellcasting(raw, index) {
    const name = String(raw.name ?? `Spellcasting ${index + 1}`).trim();
    return {
      name,
      tradition: normalizeChoice(raw.tradition, ["arcane", "divine", "occult", "primal"], "arcane"),
      prepared: normalizeChoice(raw.prepared ?? raw.type, ["prepared", "spontaneous", "innate", "focus", "ritual"], "innate"),
      ability: normalizeChoice(String(raw.ability ?? "cha").slice(0, 3), ABILITY_KEYS, "cha"),
      dc: int(raw.dc ?? raw.spelldc, 0),
      attack: int(raw.attack ?? raw.spellattack, 0),
      slots: normalizeSlots(raw.slots),
      spells: listObjects(raw.spells).map(normalizeSpell),
      description: String(raw.description ?? ""),
      rules: Array.isArray(raw.rules) ? structuredCloneSafe(raw.rules) : []
    };
  }

  function normalizeSlots(value) {
    const out = {};
    if (!value || typeof value !== "object") return out;
    for (const [rank, count] of Object.entries(value)) {
      const n = Number(String(rank).replace(/^slot/i, ""));
      if (Number.isInteger(n) && n >= 0 && n <= 10) out[n] = Math.max(0, int(count?.max ?? count?.value ?? count, 0));
    }
    return out;
  }

  function normalizeSpell(raw, index) {
    if (typeof raw === "string") return { name: raw, rank: null, slots: null, frequency: "", uses: null, per: "day", signature: false, heightened: null, uuid: "" };
    return {
      name: String(raw?.name ?? `Spell ${index + 1}`).trim(),
      rank: raw?.rank == null && raw?.level == null ? null : clampInt(raw.rank ?? raw.level, 0, 10),
      slots: raw?.slots == null ? null : Math.max(1, int(raw.slots, 1)),
      frequency: String(raw?.frequency ?? ""),
      uses: raw?.uses == null ? null : Math.max(0, int(raw.uses, 0)),
      per: String(raw?.per ?? "day"),
      signature: !!raw?.signature,
      heightened: raw?.heightened == null ? null : clampInt(raw.heightened, 1, 10),
      uuid: String(raw?.uuid ?? "").trim()
    };
  }

  function normalizeInventory(raw, index) {
    const requested = slugify(raw.type ?? raw.category ?? "equipment");
    return {
      name: String(raw.name ?? `Item ${index + 1}`).trim(),
      type: INVENTORY_TYPES.has(requested) ? requested : "equipment",
      quantity: Math.max(1, int(raw.quantity, 1)),
      level: Math.max(0, int(raw.level, 0)),
      source: String(raw.source ?? raw.compendium ?? ""),
      uuid: String(raw.uuid ?? ""),
      traits: list(raw.traits).map(slugify).filter(Boolean),
      description: String(raw.description ?? ""),
      rules: Array.isArray(raw.rules) ? structuredCloneSafe(raw.rules) : []
    };
  }

  function normalizeEffect(raw, index) {
    return {
      name: String(raw.name ?? `Effect ${index + 1}`).trim(),
      level: Math.max(1, int(raw.level, 1)),
      traits: list(raw.traits).map(slugify).filter(Boolean),
      radius: raw.radius == null && raw.range == null ? null : int(raw.radius ?? raw.range, 0),
      duration: raw.duration ?? "unlimited",
      badge: raw.badge ?? null,
      description: String(raw.description ?? ""),
      rules: Array.isArray(raw.rules) ? structuredCloneSafe(raw.rules) : []
    };
  }

  function normalizeHazard(value) {
    const raw = value && typeof value === "object" ? value : {};
    return {
      stealth: normalizeValueDetails(raw.stealth, 0),
      hardness: Math.max(0, int(raw.hardness, 0)),
      complex: !!raw.complex,
      disable: String(raw.disable ?? ""),
      routine: String(raw.routine ?? ""),
      reset: String(raw.reset ?? "")
    };
  }

  async function buildActorSource(npc, originalSource, { forUpdate = false, actor = null } = {}) {
    const actorType = resolveActorType(npc);
    const art = !forUpdate || npc.image ? await findCreatureArt(npc.name) : null;
    const publicNotes = [npc.description, ...npc.notes].filter(Boolean).map(descriptionToHtml).join("\n");
    const flags = {
      [MACRO_ID]: {
        schema: SCHEMA_ID,
        version: SCHEMA_VERSION,
        lastImportedAt: new Date().toISOString(),
        source: originalSource
      }
    };

    let source;
    if (actorType === "hazard") {
      source = {
        name: npc.name,
        system: {
          traits: { value: filterKnownTraits(npc.traits, "creatureTraits").filter((t) => t !== "hazard"), rarity: npc.rarity, size: { value: npc.size } },
          attributes: {
            ac: { value: npc.ac.value, details: npc.ac.details },
            hp: { value: npc.hp.value, max: npc.hp.value, temp: 0, details: npc.hp.details, brokenThreshold: 0 },
            hardness: npc.hazard.hardness,
            stealth: { value: npc.hazard.stealth.value, details: npc.hazard.stealth.details },
            immunities: npc.immunities,
            weaknesses: npc.weaknesses,
            resistances: npc.resistances,
            emitsSound: false
          },
          saves: {
            fortitude: { value: npc.saves.fortitude.value },
            reflex: { value: npc.saves.reflex.value },
            will: { value: npc.saves.will.value }
          },
          details: {
            level: { value: npc.level },
            isComplex: !!npc.hazard.complex,
            description: publicNotes,
            disable: descriptionToHtml(npc.hazard.disable),
            routine: descriptionToHtml(npc.hazard.routine),
            reset: descriptionToHtml(npc.hazard.reset)
          }
        },
        flags
      };
    } else {
      source = {
        name: npc.name,
        system: {
          traits: { value: filterKnownTraits(npc.traits, "creatureTraits"), rarity: npc.rarity, size: { value: npc.size } },
          abilities: Object.fromEntries(ABILITY_KEYS.map((key) => [key, { mod: npc.abilities[key] ?? 0 }])),
          attributes: {
            ac: { value: npc.ac.value, details: npc.ac.details },
            allSaves: { value: npc.allSaves },
            hp: { value: npc.hp.value, max: npc.hp.value, temp: 0, details: npc.hp.details },
            speed: npc.speed,
            immunities: npc.immunities,
            weaknesses: npc.weaknesses,
            resistances: npc.resistances
          },
          perception: { mod: npc.perception.mod, details: npc.perception.details, senses: npc.perception.senses },
          saves: {
            fortitude: { value: npc.saves.fortitude.value, saveDetail: npc.saves.fortitude.details },
            reflex: { value: npc.saves.reflex.value, saveDetail: npc.saves.reflex.details },
            will: { value: npc.saves.will.value, saveDetail: npc.saves.will.details }
          },
          skills: buildSkills(npc.skills),
          details: {
            level: { value: npc.level },
            languages: npc.languages,
            publicNotes,
            privateNotes: `<section><h3>Imported Source</h3><pre>${escapeHtml(originalSource)}</pre></section>`
          },
          initiative: { statistic: normalizeSkillSlug(npc.initiative || "perception") }
        },
        flags
      };
    }

    if (!forUpdate) source.type = actorType;
    if (!forUpdate || npc.image) source.img = npc.image || art?.img || `systems/pf2e/icons/default-icons/${actorType}.svg`;

    const token = buildPrototypeToken(npc, actorType, art, actor);
    source.prototypeToken = token;
    return source;
  }

  function buildPrototypeToken(npc, actorType, art, actor) {
    const scale = { tiny: 0.5, sm: 1, med: 1, lg: 2, huge: 3, grg: 4 };
    const dimension = scale[npc.size] ?? 1;
    const current = actor?.prototypeToken?.toObject?.() ?? {};
    const token = {
      ...current,
      width: dimension,
      height: dimension,
      actorLink: false,
      disposition: actorType === "hazard" ? CONST.TOKEN_DISPOSITIONS.NEUTRAL : CONST.TOKEN_DISPOSITIONS.HOSTILE,
      displayName: CONST.TOKEN_DISPLAY_MODES.OWNER_HOVER,
      displayBars: CONST.TOKEN_DISPLAY_MODES.OWNER,
      sight: { ...(current.sight ?? {}), enabled: actorType !== "hazard" },
      flags: foundry.utils.mergeObject(current.flags ?? {}, { pf2e: { linkToActorSize: true, autoscale: true } }, { inplace: false })
    };
    const requested = npc.token ?? {};
    if (art?.tokenSrc) token.texture = { ...(token.texture ?? {}), src: art.tokenSrc };
    if (requested.img || requested.texture?.src) token.texture = { ...(token.texture ?? {}), src: requested.img ?? requested.texture.src };
    if (requested.nameDisplay != null) token.displayName = requested.nameDisplay;
    if (requested.disposition != null) token.disposition = requested.disposition;
    return token;
  }

  async function syncManagedItems(actor, npc) {
    const managed = actor.items.filter((item) => item.getFlag(MACRO_ID, "managed"));
    const ids = managed.map((item) => item.id);
    if (ids.length) await actor.deleteEmbeddedDocuments("Item", ids);

    const sources = [
      ...npc.attacks.map(buildMeleeItemSource),
      ...npc.actions.map(buildActionItemSource),
      ...(await Promise.all(npc.inventory.map(buildInventoryItemSource))),
      ...npc.effects.map(buildEffectItemSource)
    ].filter(Boolean);

    let created = 0;
    if (sources.length) {
      const docs = await actor.createEmbeddedDocuments("Item", sources);
      created += docs.length;
    }
    const unresolvedSpells = await importSpellcasting(actor, npc.spellcasting);
    created = actor.items.filter((item) => item.getFlag(MACRO_ID, "batch") === currentBatchId).length;
    return { deleted: ids.length, created, unresolvedSpells };
  }

  function managedItem(source) {
    const clone = structuredCloneSafe(source);
    clone.flags ??= {};
    clone.flags[MACRO_ID] = { managed: true, batch: currentBatchId };
    return clone;
  }

  function buildMeleeItemSource(attack) {
    const damageRolls = {};
    attack.damageRolls.forEach((roll, index) => {
      damageRolls[index === 0 ? "main" : `extra${index}`] = { damage: roll.formula, damageType: roll.type || "bludgeoning", category: roll.category || null };
    });
    return managedItem({
      name: attack.name,
      type: "melee",
      img: attack.type === "ranged" ? "systems/pf2e/icons/default-icons/ranged.svg" : "systems/pf2e/icons/default-icons/melee.svg",
      system: {
        description: { value: descriptionToHtml(attack.description) },
        rules: attack.rules,
        slug: slugifyLatin(attack.name) || null,
        traits: { value: filterKnownTraits(attack.traits, "npcAttackTraits"), otherTags: [] },
        action: attack.action || "strike",
        bonus: { value: attack.bonus },
        attackEffects: { value: attack.effects },
        damageRolls,
        range: attack.type === "ranged" ? { increment: attack.range ?? 30, max: attack.maxRange ?? null } : null,
        area: attack.area,
        subjectToMAP: true
      }
    });
  }

  function buildActionItemSource(action) {
    const system = {
      description: { value: descriptionToHtml(action.description) },
      rules: action.rules,
      slug: slugifyLatin(action.name) || null,
      traits: { value: filterKnownTraits(action.traits, "actionTraits"), otherTags: [] },
      actionType: { value: action.actionType },
      actions: { value: action.actionType === "action" ? action.actions : null },
      category: action.category
    };
    const frequency = normalizeFrequency(action.frequency);
    if (frequency) system.frequency = frequency;
    return managedItem({ name: action.name, type: "action", img: action.img || actionIcon(action.actionType, action.actions), system });
  }

  async function buildInventoryItemSource(item) {
    const matched = await resolveCompendiumItem(item, { type: item.type });
    if (!matched) {
      console.warn(`${MACRO_ID}: inventory item not found; using equipment fallback`, item.name);
      return managedItem({
        name: item.name,
        type: "equipment",
        img: "systems/pf2e/icons/default-icons/equipment.svg",
        system: {
          description: { value: descriptionToHtml([item.description, `原请求类型：${item.type}`].filter(Boolean).join("\n")) },
          rules: item.rules,
          level: { value: item.level },
          quantity: item.quantity,
          traits: { value: [], rarity: "common", otherTags: [] }
        }
      });
    }
    const source = matched.toObject ? matched.toObject() : structuredCloneSafe(matched);
    delete source._id;
    source.name = item.name || source.name;
    source.system ??= {};
    source.system.quantity = item.quantity;
    if (item.rules.length) source.system.rules = item.rules;
    if (item.description) source.system.description = { value: descriptionToHtml(item.description) };
    return managedItem(source);
  }

  function buildEffectItemSource(effect) {
    const rules = structuredCloneSafe(effect.rules);
    if (effect.radius && !rules.some((rule) => rule?.key === "Aura")) {
      rules.unshift({ key: "Aura", radius: effect.radius, traits: effect.traits.filter((t) => t !== "aura"), effects: [] });
    }
    return managedItem({
      name: effect.name,
      type: "effect",
      img: "systems/pf2e/icons/default-icons/effect.svg",
      system: {
        description: { value: descriptionToHtml(effect.description) },
        rules,
        slug: slugifyLatin(effect.name) || null,
        level: { value: effect.level },
        traits: { value: effect.traits, otherTags: [] },
        duration: normalizeDuration(effect.duration),
        badge: normalizeBadge(effect.badge),
        tokenIcon: { show: true },
        unidentified: false,
        start: { value: 0, initiative: null },
        fromSpell: false
      }
    });
  }

  async function importSpellcasting(actor, entries) {
    const unresolved = [];
    for (const entry of entries) {
      const resolved = [];
      const missing = [];
      for (const spell of entry.spells) {
        const document = await resolveSpell(spell);
        if (document) resolved.push({ spell, document });
        else missing.push(spell);
      }
      unresolved.push(...missing.map((spell) => spell.name));

      const missingText = missing.length
        ? `\n\n【未匹配到当前 PF2e Compendium 的法术】\n${missing.map((spell) => `${spell.rank == null ? "?" : spell.rank}环：${spell.name}`).join("\n")}`
        : "";
      const entrySource = buildSpellcastingEntrySource(entry, `${entry.description}${missingText}`);
      const [entryDoc] = await actor.createEmbeddedDocuments("Item", [entrySource]);
      if (!entryDoc) continue;

      const spellSources = resolved.map(({ spell, document }) => {
        const source = document.toObject();
        delete source._id;
        source.system ??= {};
        source.system.location = buildSpellLocation(spell, entryDoc.id);
        if (Number.isInteger(spell.rank)) source.system.level = { value: spell.rank };
        source.flags ??= {};
        source.flags[MACRO_ID] = { managed: true, batch: currentBatchId, parentEntry: entryDoc.id };
        return source;
      });
      const createdSpells = spellSources.length ? await actor.createEmbeddedDocuments("Item", spellSources) : [];
      if (entry.prepared === "prepared" && createdSpells.length) {
        const slots = buildSpellSlots(entry);
        for (let i = 0; i < createdSpells.length; i++) {
          const spellData = resolved[i]?.spell;
          const doc = createdSpells[i];
          if (!spellData || !doc || !Number.isInteger(spellData.rank)) continue;
          const slot = slots[`slot${spellData.rank}`];
          if (!slot) continue;
          const copies = Math.max(1, spellData.slots ?? 1);
          for (let c = 0; c < copies; c++) slot.prepared.push({ id: doc.id, expended: false });
        }
        await entryDoc.update({ "system.slots": slots });
      }
    }
    return unresolved;
  }

  function buildSpellcastingEntrySource(entry, description) {
    return managedItem({
      name: entry.name,
      type: "spellcastingEntry",
      img: "systems/pf2e/icons/default-icons/spellcastingEntry.svg",
      system: {
        description: { value: descriptionToHtml(description) },
        rules: entry.rules,
        slug: slugifyLatin(entry.name) || null,
        ability: { value: entry.ability },
        tradition: { value: entry.tradition },
        prepared: { value: entry.prepared, flexible: false },
        spelldc: { value: entry.attack, dc: entry.dc },
        showSlotlessLevels: { value: true },
        proficiency: { value: 1 },
        slots: buildSpellSlots(entry),
        autoHeightenLevel: { value: null },
        traits: { otherTags: [] }
      }
    });
  }

  function buildSpellSlots(entry) {
    const slots = Object.fromEntries(Array.from({ length: 11 }, (_v, rank) => [`slot${rank}`, { prepared: [], value: 0, max: 0 }]));
    for (const [rank, count] of Object.entries(entry.slots)) {
      const slot = slots[`slot${rank}`];
      if (slot) slot.value = slot.max = Math.max(0, int(count, 0));
    }
    for (const spell of entry.spells) {
      if (!Number.isInteger(spell.rank)) continue;
      const slot = slots[`slot${spell.rank}`];
      if (!slot) continue;
      const copies = spell.slots ?? (entry.prepared === "prepared" ? 1 : 0);
      if (copies) slot.value = slot.max = Math.max(slot.max, copies);
    }
    return slots;
  }

  function buildSpellLocation(spell, entryId) {
    const location = { value: entryId };
    if (spell.signature) location.signature = true;
    if (spell.heightened) location.heightenedLevel = spell.heightened;
    const freq = slugify(spell.frequency);
    if (["at-will", "atwill", "constant"].includes(freq)) location.uses = { value: -1, max: -1, per: "day" };
    else if (spell.uses != null) location.uses = { value: spell.uses, max: spell.uses, per: normalizeFrequencyPer(spell.per) };
    return location;
  }

  async function resolveSpell(spell) {
    if (spell.uuid && globalThis.fromUuid) {
      try {
        const doc = await fromUuid(spell.uuid);
        if (doc?.type === "spell") return doc;
      } catch (error) {
        console.warn(`${MACRO_ID}: bad spell uuid`, spell.uuid, error);
      }
    }
    return resolveCompendiumDocument(spell.name, { type: "spell", packHint: "pf2e.spells-srd" });
  }

  async function resolveCompendiumItem(item, { type = null } = {}) {
    if (item.uuid && globalThis.fromUuid) {
      try {
        const doc = await fromUuid(item.uuid);
        if (doc && (!type || doc.type === type)) return doc;
      } catch (error) {
        console.warn(`${MACRO_ID}: bad item uuid`, item.uuid, error);
      }
    }
    return resolveCompendiumDocument(item.name, { type, packHint: item.source });
  }

  const indexCache = new Map();
  async function resolveCompendiumDocument(name, { type = null, packHint = "" } = {}) {
    const target = matchNormalize(name);
    if (!target) return null;
    const packs = game.packs.filter((pack) => pack.documentName === "Item" && (!packHint || pack.collection === packHint || pack.metadata?.id === packHint || pack.collection.includes(packHint) || pack.metadata?.packageName === "pf2e"));
    const pf2ePacks = packs.length ? packs : game.packs.filter((pack) => pack.documentName === "Item" && pack.metadata?.packageName === "pf2e");
    let fuzzy = null;
    for (const pack of pf2ePacks) {
      let index = indexCache.get(pack.collection);
      if (!index) {
        index = await pack.getIndex({ fields: ["name", "type", "system.slug"] });
        indexCache.set(pack.collection, index);
      }
      for (const candidate of index) {
        if (type && candidate.type !== type) continue;
        const candName = matchNormalize(candidate.name);
        if (!candName) continue;
        if (candName === target || slugifyLatin(candidate.system?.slug) === slugifyLatin(name)) return pack.getDocument(candidate._id);
        if ((candName.startsWith(`${target} `) || target.startsWith(`${candName} `)) && (!fuzzy || candName.length < fuzzy.name.length)) fuzzy = { pack, id: candidate._id, name: candName };
      }
    }
    return fuzzy ? fuzzy.pack.getDocument(fuzzy.id) : null;
  }

  const actorIndexCache = new Map();
  async function findCreatureArt(name) {
    const target = matchNormalize(name);
    if (!target) return null;
    const packs = game.packs.filter((pack) => pack.documentName === "Actor" && pack.metadata?.packageName === "pf2e");
    for (const pack of packs) {
      let index = actorIndexCache.get(pack.collection);
      if (!index) {
        index = await pack.getIndex({ fields: ["name", "img", "prototypeToken.texture.src"] });
        actorIndexCache.set(pack.collection, index);
      }
      const entry = index.find((candidate) => matchNormalize(candidate.name) === target);
      if (!entry) continue;
      const usable = (path) => path && !String(path).includes("default-icons") && !String(path).includes("mystery-man") ? path : null;
      const img = usable(entry.img);
      const tokenSrc = usable(entry.prototypeToken?.texture?.src);
      if (img || tokenSrc) return { img, tokenSrc };
    }
    return null;
  }

  async function importAbilityPayload(actor, items) {
    const updates = [];
    const creates = [];
    for (const action of items) {
      const source = buildActionItemSource(action);
      // Ability-only payloads update same-name Action items, including hand-made ones,
      // because this is an explicit targeted operation rather than full-sync cleanup.
      const existing = actor.items.find((item) => item.type === "action" && normalizeName(item.name) === normalizeName(source.name));
      if (existing) updates.push({ _id: existing.id, ...source });
      else creates.push(source);
    }
    if (updates.length) await actor.updateEmbeddedDocuments("Item", updates);
    if (creates.length) await actor.createEmbeddedDocuments("Item", creates);
    return { updated: updates.length, created: creates.length };
  }

  function descriptionToHtml(text) {
    if (!text) return "";
    let normalized = String(text)
      .replace(/\r\n?/g, "\n")
      .replace(/\\r\\n/g, "\n")
      .replace(/\\n/g, "\n");
    normalized = enrichPf2eText(normalized);

    const lines = normalized.split("\n");
    const html = [];
    let paragraph = [];
    const flush = () => {
      if (!paragraph.length) return;
      html.push(`<p>${paragraph.map((line) => escapeHtml(line)).join("<br>")}</p>`);
      paragraph = [];
    };
    for (const rawLine of lines) {
      const line = rawLine.trimEnd();
      if (!line.trim()) { flush(); continue; }
      const heading = line.trim().match(/^【(.+?)】$/);
      if (heading) { flush(); html.push(`<h3>${escapeHtml(heading[1])}</h3>`); continue; }
      paragraph.push(line);
    }
    flush();
    return html.join("\n");
  }

  function enrichPf2eText(source) {
    const { text: protectedText, restore } = protectFoundrySyntax(String(source ?? ""));
    let text = protectedText;
    text = enrichTextChecks(text);
    text = enrichTextDamage(text);
    text = enrichTextTemplates(text);
    text = enrichExplicitDiceRolls(text);
    text = linkConditionsUsingLivePf2e(text);
    return restore(text);
  }

  function protectFoundrySyntax(source) {
    const protectedValues = [];
    let out = "";
    for (let i = 0; i < source.length;) {
      const directive = ["@Check[", "@Damage[", "@Template[", "@UUID["].find((prefix) => source.startsWith(prefix, i));
      if (directive) {
        const start = i;
        const open = i + directive.length - 1;
        let depth = 0;
        let end = -1;
        for (let j = open; j < source.length; j++) {
          if (source[j] === "[") depth++;
          else if (source[j] === "]") {
            depth--;
            if (depth === 0) { end = j + 1; break; }
          }
        }
        if (end > 0 && source[end] === "{") {
          const close = source.indexOf("}", end + 1);
          if (close >= 0) end = close + 1;
        }
        if (end > 0) {
          const token = `\uE000${protectedValues.length}\uE001`;
          protectedValues.push(source.slice(start, end));
          out += token;
          i = end;
          continue;
        }
      }
      if (source.startsWith("[[", i)) {
        let end = source.indexOf("]]", i + 2);
        if (end >= 0) {
          end += 2;
          if (source[end] === "{") {
            const close = source.indexOf("}", end + 1);
            if (close >= 0) end = close + 1;
          }
          const token = `\uE000${protectedValues.length}\uE001`;
          protectedValues.push(source.slice(i, end));
          out += token;
          i = end;
          continue;
        }
      }
      out += source[i++];
    }
    return {
      text: out,
      restore: (value) => String(value).replace(/\uE000(\d+)\uE001/g, (_m, id) => protectedValues[Number(id)] ?? _m)
    };
  }

  function enrichTextChecks(text) {
    const aliases = [
      ["fortitude", "强韧|Fortitude|Fort"], ["reflex", "反射|Reflex|Ref"], ["will", "意志|Will"],
      ["perception", "察觉|Perception"], ["acrobatics", "特技|杂技|Acrobatics"], ["arcana", "奥秘|Arcana"],
      ["athletics", "运动|Athletics"], ["crafting", "制造|Crafting"], ["deception", "欺骗|Deception"],
      ["diplomacy", "交涉|外交|Diplomacy"], ["intimidation", "威吓|Intimidation"], ["medicine", "医药|医学|Medicine"],
      ["nature", "自然|Nature"], ["occultism", "神秘|Occultism"], ["performance", "表演|Performance"],
      ["religion", "宗教|Religion"], ["society", "社会|Society"], ["stealth", "隐匿|Stealth"],
      ["survival", "生存|Survival"], ["thievery", "盗窃|Thievery"], ["flat", "平检|纯检定|flat check"]
    ];
    for (const [slug, pattern] of aliases) {
      const re1 = new RegExp(`DC\\s*(\\d+)\\s*(?:点)?\\s*(${pattern})(基本)?(?:豁免|检定)?`, "gi");
      text = text.replace(re1, (_m, dc, _label, basic) => `@Check[${slug}|dc:${dc}${basic ? "|basic" : ""}]`);
      const re2 = new RegExp(`(${pattern})\\s*(?:豁免|检定)?\\s*DC\\s*(\\d+)(?:\\s*(基本))?`, "gi");
      text = text.replace(re2, (_m, _label, dc, basic) => `@Check[${slug}|dc:${dc}${basic ? "|basic" : ""}]`);
    }
    return text;
  }

  function enrichTextDamage(text) {
    const typeMap = {
      "强酸": "acid", "acid": "acid", "流血": "bleed", "bleed": "bleed", "钝击": "bludgeoning", "bludgeoning": "bludgeoning",
      "寒冷": "cold", "cold": "cold", "电击": "electricity", "电力": "electricity", "electricity": "electricity",
      "火焰": "fire", "fire": "fire", "力场": "force", "force": "force", "心灵": "mental", "mental": "mental",
      "穿刺": "piercing", "piercing": "piercing", "毒素": "poison", "poison": "poison", "挥砍": "slashing", "slashing": "slashing",
      "音波": "sonic", "sonic": "sonic", "灵魂": "spirit", "spirit": "spirit", "活力": "vitality", "vitality": "vitality",
      "虚能": "void", "void": "void"
    };
    const typePattern = Object.keys(typeMap).sort((a, b) => b.length - a.length).map(escapeRegExp).join("|");
    const cn = new RegExp(`(\\d+d\\d+(?:\\s*[+\\-]\\s*\\d+)?|\\d+)\\s*(持续|精准|溅射)?\\s*(${typePattern})\\s*(?:伤害|damage)`, "gi");
    text = text.replace(cn, (_m, formula, category, type) => {
      const cat = category === "持续" ? "persistent," : category === "精准" ? "precision," : category === "溅射" ? "splash," : "";
      return `@Damage[${formula.replace(/\s+/g, "")}[${cat}${typeMap[String(type).toLowerCase()] ?? typeMap[type]}]]`;
    });
    const en = new RegExp(`(\\d+d\\d+(?:\\s*[+\\-]\\s*\\d+)?|\\d+)\\s+(persistent\\s+|precision\\s+|splash\\s+)?(${typePattern})\\s+damage`, "gi");
    text = text.replace(en, (_m, formula, category, type) => {
      const cat = category ? `${slugify(category)},` : "";
      return `@Damage[${formula.replace(/\s+/g, "")}[${cat}${typeMap[String(type).toLowerCase()] ?? typeMap[type]}]]`;
    });
    return text;
  }

  function enrichTextTemplates(text) {
    const cnTypes = { "爆发": "burst", "锥形": "cone", "散发": "emanation", "线形": "line" };
    text = text.replace(/(\d+)\s*尺(?:长\s*(\d+)\s*尺宽)?\s*(爆发|锥形|散发|线形)/g, (_m, distance, width, shape) => `@Template[type:${cnTypes[shape]}|distance:${distance}${width ? `|width:${width}` : ""}]`);
    text = text.replace(/(\d+)\s*(?:-?foot|feet|ft\.?)\s*(burst|cone|emanation|line)/gi, (_m, distance, shape) => `@Template[type:${slugify(shape)}|distance:${distance}]`);
    return text;
  }

  function enrichExplicitDiceRolls(text) {
    text = text.replace(/GM\s*(?:掷骰|roll)\s*([0-9d+\-*/() ]+)/gi, (_m, formula) => `[[/gmr ${formula.trim()}]]`);
    text = text.replace(/(?:掷骰|roll)\s*([0-9d+\-*/() ]+)/gi, (_m, formula) => `[[/r ${formula.trim()}]]`);
    return text;
  }

  function linkConditionsUsingLivePf2e(text) {
    const manager = game.pf2e?.ConditionManager;
    if (!manager || typeof manager.getCondition !== "function") return text;
    const slugs = Array.isArray(manager.conditionsSlugs) ? [...manager.conditionsSlugs] : Object.keys(CONFIG?.PF2E?.conditionTypes ?? {});
    let output = text;
    for (const slug of slugs.sort((a, b) => b.length - a.length)) {
      let condition;
      try { condition = manager.getCondition(slug); } catch (_error) { continue; }
      const uuid = condition?._stats?.compendiumSource ?? condition?.uuid;
      if (!uuid) continue;
      const label = titleCaseSlug(slug);
      const pattern = new RegExp(`\\b${escapeRegExp(label).replace(/\\-/g, "[- ]")}\\b`, "g");
      output = output.replace(pattern, (match) => `@UUID[${uuid}]{${match}}`);
    }
    return output;
  }

  function normalizeFrequency(value) {
    if (!value) return null;
    if (typeof value === "object") {
      const max = Math.max(1, int(value.max ?? value.value, 1));
      const out = { max, per: normalizeFrequencyPer(value.per ?? "day") };
      if (value.value != null) out.value = clampInt(value.value, 0, max);
      return out;
    }
    const text = String(value).trim();
    const max = Math.max(1, int(text.match(/\d+/)?.[0], 1));
    const unit = text.match(/per\s+(.+)$/i)?.[1]?.trim() ?? text.match(/\/\s*([^\s]+)/)?.[1] ?? (/每轮/.test(text) ? "round" : /每天/.test(text) ? "day" : /每小时/.test(text) ? "hour" : /每分钟/.test(text) ? "minute" : "day");
    return { max, per: normalizeFrequencyPer(unit) };
  }

  function normalizeFrequencyPer(value) {
    const raw = String(value ?? "day").trim();
    const choices = CONFIG?.PF2E?.frequencies ?? {};
    if (raw in choices) return raw;
    const lower = raw.toLowerCase();
    const aliases = {
      round: ["round", "PT6S"], minute: ["PT1M", "minute"], hour: ["PT1H", "hour"], day: ["day", "P1D"], week: ["P1W", "week"], month: ["P1M", "month"], year: ["P1Y", "year"],
      "轮": ["round", "PT6S"], "分钟": ["PT1M", "minute"], "小时": ["PT1H", "hour"], "天": ["day", "P1D"]
    };
    for (const candidate of aliases[lower] ?? aliases[raw] ?? []) if (candidate in choices) return candidate;
    const caseMatch = Object.keys(choices).find((key) => key.toLowerCase() === lower);
    return caseMatch ?? (Object.keys(choices).includes("day") ? "day" : Object.keys(choices)[0] ?? raw);
  }

  function normalizeDuration(value) {
    if (value && typeof value === "object") return structuredCloneSafe(value);
    const text = String(value ?? "unlimited").trim();
    const slug = slugify(text);
    if (["unlimited", "无限", "permanent", "永久"].includes(slug) || /^(无限|永久)$/.test(text)) return { value: -1, unit: "unlimited", expiry: null, sustained: false };
    const match = text.match(/(\d+)\s*(rounds?|轮|minutes?|分钟|hours?|小时|days?|天)/i);
    if (!match) return { value: -1, unit: "unlimited", expiry: null, sustained: false };
    const unitRaw = match[2].toLowerCase();
    const unit = /round|轮/.test(unitRaw) ? "rounds" : /minute|分钟/.test(unitRaw) ? "minutes" : /hour|小时/.test(unitRaw) ? "hours" : "days";
    return { value: Number(match[1]), unit, expiry: "turn-start", sustained: false };
  }

  function normalizeBadge(value) {
    if (!value) return null;
    if (typeof value === "object") return structuredCloneSafe(value);
    const number = Number(value);
    return Number.isFinite(number) ? { type: "counter", value: number, min: 1, max: null, labels: null, loop: false } : null;
  }

  function actionIcon(type, actions) {
    if (type === "reaction") return "systems/pf2e/icons/actions/Reaction.webp";
    if (type === "free") return "systems/pf2e/icons/actions/FreeAction.webp";
    if (type === "passive") return "systems/pf2e/icons/actions/Passive.webp";
    return ({ 1: "systems/pf2e/icons/actions/OneAction.webp", 2: "systems/pf2e/icons/actions/TwoActions.webp", 3: "systems/pf2e/icons/actions/ThreeActions.webp" })[actions ?? 1];
  }

  function buildSkills(skills) {
    const configSkills = CONFIG?.PF2E?.skills ?? {};
    const result = {};
    for (const [name, value] of Object.entries(skills)) {
      const slug = normalizeSkillSlug(name);
      result[slug] = { base: int(value, 0) };
    }
    return result;
  }

  function normalizeSkillSlug(name) {
    const raw = slugify(name);
    const aliases = { acrobatics: "acrobatics", arcana: "arcana", athletics: "athletics", crafting: "crafting", deception: "deception", diplomacy: "diplomacy", intimidation: "intimidation", medicine: "medicine", nature: "nature", occultism: "occultism", performance: "performance", religion: "religion", society: "society", stealth: "stealth", survival: "survival", thievery: "thievery", perception: "perception" };
    return aliases[raw] ?? raw;
  }

  function filterKnownTraits(values, configKey) {
    const choices = CONFIG?.PF2E?.[configKey] ?? {};
    if (!Object.keys(choices).length) return values;
    const known = values.filter((value) => value in choices);
    const unknown = values.filter((value) => !(value in choices));
    if (unknown.length) console.warn(`${MACRO_ID}: ignored unknown ${configKey}`, unknown);
    return known;
  }

  function warnUnknownSlugs(label, values, known) {
    if (!known.length) return;
    const set = new Set(known);
    const unknown = values.filter((value) => !set.has(value));
    if (unknown.length) console.warn(`${MACRO_ID}: unknown ${label}`, unknown);
  }

  async function getOrCreateFolder() {
    const existing = game.folders.find((folder) => folder.type === "Actor" && folder.name === IMPORT_FOLDER);
    return existing ?? Folder.create({ name: IMPORT_FOLDER, type: "Actor" });
  }

  function resolveActorType(npc) {
    return npc.kind === "hazard" ? "hazard" : "npc";
  }

  function resolveKind(value) {
    return slugify(value) === "hazard" ? "hazard" : "npc";
  }

  function normalizeActionType(value) {
    const slug = slugify(value);
    if (slug.includes("reaction") || slug === "反应") return "reaction";
    if (slug.includes("free") || slug === "自由动作") return "free";
    if (slug.includes("passive") || slug === "被动") return "passive";
    return "action";
  }

  function normalizeCategory(value) {
    const slug = slugify(value ?? "offensive") || "offensive";
    const choices = CONFIG?.PF2E?.actionCategories ?? {};
    return !Object.keys(choices).length || slug in choices ? slug : ("offensive" in choices ? "offensive" : null);
  }

  function normalizeRarity(value) {
    const slug = slugify(value ?? "common");
    const aliases = { common: "common", uncommon: "uncommon", rare: "rare", unique: "unique", "普通": "common", "非普通": "uncommon", "罕见": "rare", "独特": "unique" };
    return aliases[slug] ?? aliases[String(value ?? "").trim()] ?? "common";
  }

  function normalizeChoice(value, allowed, fallback) {
    const slug = slugify(value);
    return allowed.includes(slug) ? slug : fallback;
  }

  function matchNormalize(value) {
    return String(value ?? "").toLowerCase().replace(/\([^)]*\)/g, " ").replace(/['’]/g, "").replace(/^the\s+/, "").replace(/[^a-z0-9\u4e00-\u9fff]+/g, " ").trim();
  }

  function titleCaseSlug(value) {
    return String(value).split("-").map((part) => part ? part[0].toUpperCase() + part.slice(1) : part).join("-");
  }

  function normalizeName(value) {
    return String(value ?? "").trim().toLocaleLowerCase();
  }

  function slugify(value) {
    return String(value ?? "").trim().toLowerCase().replace(/['’]/g, "").replace(/[^a-z0-9\u4e00-\u9fff]+/g, "-").replace(/^-|-$/g, "");
  }

  function slugifyLatin(value) {
    return String(value ?? "").trim().toLowerCase().replace(/['’]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  function splitList(value) {
    return String(value ?? "").split(/[,;，；]/).map((part) => part.trim()).filter(Boolean);
  }

  function list(value) {
    if (Array.isArray(value)) return value;
    if (value == null || value === "") return [];
    return typeof value === "string" ? splitList(value) : [value];
  }

  function listObjects(value) {
    return Array.isArray(value) ? value.filter((item) => item && typeof item === "object") : [];
  }

  function int(value, fallback = 0) {
    const match = String(value ?? "").match(/[-+]?\d+/);
    return match ? Number(match[0]) : fallback;
  }

  function clampInt(value, min, max) {
    return Math.min(max, Math.max(min, int(value, min)));
  }

  function checkboxValue(value) {
    return value === true || value === "on" || value === "true" || value === "1";
  }

  function structuredCloneSafe(value) {
    if (globalThis.structuredClone) return structuredClone(value);
    return JSON.parse(JSON.stringify(value));
  }

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>\"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[ch]);
  }

  function formDataToObject(formData) {
    if (!formData) return {};
    if (formData.object && typeof formData.object === "object") return formData.object;
    if (typeof formData.entries === "function") return Object.fromEntries(formData.entries());
    return formData;
  }

  async function promptInput(dialogContent) {
    const DialogV2 = globalThis.foundry?.applications?.api?.DialogV2;
    if (DialogV2?.input) {
      return DialogV2.input({
        window: { title: "PF2e Unified Statblock Importer" },
        content: dialogContent,
        rejectClose: false,
        modal: true,
        ok: { label: "导入 / 同步" }
      });
    }
    if (globalThis.Dialog) {
      return new Promise((resolve) => {
        let settled = false;
        const finish = (value) => { if (!settled) { settled = true; resolve(value); } };
        new Dialog({
          title: "PF2e Unified Statblock Importer",
          content: `<form>${dialogContent}</form>`,
          buttons: {
            import: {
              label: "导入 / 同步",
              callback: (html) => {
                const root = html?.[0] ?? html;
                const form = root?.querySelector?.("form") ?? root;
                finish(form ? new FormData(form) : null);
              }
            },
            cancel: { label: "取消", callback: () => finish(null) }
          },
          default: "import",
          close: () => finish(null)
        }).render(true);
      });
    }
    throw new Error("当前 Foundry 版本没有 DialogV2 或 legacy Dialog API。");
  }
})();
