# Complete PF2e Actor Import Payload

## Contents

1. Workflow and contract
2. Canonical payload schema
3. Chinese/English stat-block parsing
4. Core Actor fields
5. Strikes
6. Abilities
7. Spellcasting and inventory
8. Effects, auras, and Rule Elements
9. Inline roll automation
10. Conditions and UUIDs
11. Lossless/fairness rules
12. Validation

## 1. Workflow and contract

For a complete NPC/monster/hazard intended for direct Foundry creation or synchronization, emit JSON for `assets/fvtt-pf2e-unified-importer.js`.

The Skill performs semantic interpretation. The macro performs deterministic Foundry writes.

Do not make the Foundry macro guess Chinese terminology, encounter design intent, canonical spell names, or undocumented mechanics when ChatGPT can resolve them before import.

Use this root shape:

```json
{
  "schema": "pf2e-fvtt-actor",
  "version": 1,
  "actor": { }
}
```

`actor` intentionally mirrors the GLUniverse importer's intermediate NPC model closely. This keeps strict Markdown and direct JSON import conceptually aligned.

## 2. Canonical payload schema

```json
{
  "schema": "pf2e-fvtt-actor",
  "version": 1,
  "actor": {
    "name": "Creature Name",
    "kind": "npc",
    "level": 6,
    "rarity": "uncommon",
    "size": "med",
    "traits": ["undead", "incorporeal"],
    "description": "Public creature description.",
    "image": "",
    "token": {},
    "initiative": "perception",

    "perception": {
      "mod": 15,
      "details": "",
      "senses": [
        { "type": "darkvision" },
        { "type": "tremorsense", "range": 60, "acuity": "imprecise" }
      ]
    },

    "languages": {
      "value": ["common", "necril"],
      "details": ""
    },

    "skills": {
      "athletics": 14,
      "occultism": 13,
      "stealth": 16
    },

    "abilities": {
      "str": 2,
      "dex": 5,
      "con": 3,
      "int": 2,
      "wis": 3,
      "cha": 4
    },

    "ac": { "value": 24, "details": "" },
    "saves": {
      "fortitude": { "value": 13, "details": "" },
      "reflex": { "value": 17, "details": "" },
      "will": { "value": 15, "details": "" }
    },
    "allSaves": "",
    "hp": { "value": 95, "details": "" },

    "speed": {
      "value": 25,
      "otherSpeeds": [
        { "type": "fly", "value": 40 }
      ],
      "details": ""
    },

    "immunities": [
      { "type": "death-effects" }
    ],
    "weaknesses": [
      { "type": "vitality", "value": 5 }
    ],
    "resistances": [],

    "attacks": [],
    "actions": [],
    "spellcasting": [],
    "inventory": [],
    "effects": [],
    "notes": [],

    "hazard": {
      "stealth": { "value": 0, "details": "" },
      "hardness": 0,
      "complex": false,
      "disable": "",
      "routine": "",
      "reset": ""
    }
  }
}
```

For creatures use `kind: "npc"`. Use `kind: "hazard"` only when the source is actually a PF2e hazard.

## 3. Chinese/English stat-block parsing

Accept official-style English blocks, PF2SBC-like English blocks, translated Chinese blocks, or custom Chinese blocks if they express PF2e mechanics clearly.

Common Chinese core labels:

- `察觉` -> `perception.mod`
- `语言` -> `languages`
- `技能` -> `skills`
- `力量/敏捷/体质/智力/感知/魅力` -> `str/dex/con/int/wis/cha`
- `AC/防御等级` -> `ac`
- `强韧/反射/意志` -> `fortitude/reflex/will`
- `HP/生命值` -> `hp`
- `速度` -> `speed`
- `免疫/弱点/抗性` -> I/W/R arrays
- `近战/远程` -> `attacks`
- named action/reaction/free/passive blocks -> `actions`
- spell lines -> `spellcasting`
- `物品/装备` -> `inventory`

Normalize common enum values:

- rarity: `普通/common`, `非普通/uncommon`, `罕见/rare`, `独特/unique`
- size: `微型/tiny`, `小型/sm`, `中型/med`, `大型/lg`, `巨型/huge`, `超巨型/grg`
- action type: `动作/action`, `反应/reaction`, `自由动作/free`, `被动/passive`

For actions, interpret glyphs and text consistently:

- `◆`, `[one-action]`, `1动作` -> `action`, `actions: 1`
- `◆◆`, `[two-actions]`, `2动作` -> `action`, `actions: 2`
- `◆◆◆`, `[three-actions]`, `3动作` -> `action`, `actions: 3`
- reaction glyph/text -> `reaction`
- free-action glyph/text -> `free`
- no action cost and clearly always-on -> `passive`

Translate well-known PF2e trait names to canonical English slugs when confident. Do not invent a trait slug from an uncertain Chinese term. Preserve uncertain source terminology in `description` or `notes` instead.

## 4. Core Actor fields

Populate every explicit source field. Do not omit a core statistic merely because it is not relevant to an ability.

Skills use PF2e canonical slugs when known:

- Acrobatics -> `acrobatics`; Chinese `特技/杂技`
- Arcana -> `arcana`; `奥秘`
- Athletics -> `athletics`; `运动`
- Crafting -> `crafting`; `制造`
- Deception -> `deception`; `欺骗`
- Diplomacy -> `diplomacy`; `交涉/外交`
- Intimidation -> `intimidation`; `威吓`
- Medicine -> `medicine`; `医药/医学`
- Nature -> `nature`; `自然`
- Occultism -> `occultism`; `神秘`
- Performance -> `performance`; `表演`
- Religion -> `religion`; `宗教`
- Society -> `society`; `社会`
- Stealth -> `stealth`; `隐匿`
- Survival -> `survival`; `生存`
- Thievery -> `thievery`; `盗窃`

For senses use canonical English types such as `darkvision`, `low-light-vision`, `tremorsense`, `scent`, and include range/acuity only if stated.

For I/W/R use current PF2e-style English slugs when confidently known. Do not fabricate compendium UUIDs or Rule Elements to represent I/W/R; the macro writes structured Actor arrays directly.

## 5. Strikes

Each Strike is structured data, not only prose:

```json
{
  "name": "幽影之触 Shadow Touch",
  "type": "melee",
  "bonus": 17,
  "traits": ["agile", "magical"],
  "effects": [],
  "damageRolls": [
    { "formula": "2d8+7", "type": "void", "category": null }
  ],
  "range": null,
  "maxRange": null,
  "area": null,
  "action": "strike",
  "description": "",
  "rules": []
}
```

For ranged attacks use `type: "ranged"` and `range` as the range increment.

Canonical damage types include `acid`, `bleed`, `bludgeoning`, `cold`, `electricity`, `fire`, `force`, `mental`, `piercing`, `poison`, `slashing`, `sonic`, `spirit`, `vitality`, and `void`.

Use `category: "persistent"`, `"precision"`, or `"splash"` only when the source explicitly indicates that category.

## 6. Abilities

Each creature ability becomes an owned PF2e Action Item:

```json
{
  "name": "预告式熵灾 Entropic Omen",
  "actionType": "free",
  "actions": null,
  "category": "offensive",
  "traits": ["mythic", "divine", "void"],
  "frequency": "1 per round",
  "description": "...",
  "rules": []
}
```

For long multi-mode abilities keep the whole mechanic in one `description`. Use internal plain markers such as `【坍缩之兆 Collapse Omen】`; the macro renders these as HTML headings. Do not split one logical ability into multiple items merely because it has submodes.

`rules` is optional. Only emit PF2e Rule Elements when the user supplied them or correctness is verified. Never invent a Rule Element just to make prose more automated.

## 7. Spellcasting and inventory

Spellcasting entry:

```json
{
  "name": "Occult Innate Spells",
  "tradition": "occult",
  "prepared": "innate",
  "ability": "cha",
  "dc": 32,
  "attack": 24,
  "slots": { "5": 2, "4": 3 },
  "spells": [
    { "name": "Shadow Blast", "rank": 5, "uses": 1, "per": "day" },
    { "name": "Darkness", "rank": 4, "frequency": "at-will" }
  ],
  "description": "",
  "rules": []
}
```

Prefer canonical English spell names when the source provides them or the identification is highly confident, because the Foundry macro resolves spells from live PF2e compendia by name/slug. If only a Chinese spell name is available and the canonical English name is uncertain, keep the Chinese name and do not guess a UUID. The macro preserves unresolved spell names in the spellcasting entry description and warns the GM instead of silently dropping them.

If the source supplies a verified exact UUID, put it in `spell.uuid`. Never synthesize a UUID from a slug.

Inventory item:

```json
{
  "name": "Greater Striking Longsword",
  "type": "weapon",
  "quantity": 1,
  "level": 8,
  "source": "pf2e.equipment-srd",
  "uuid": "",
  "traits": [],
  "description": "",
  "rules": []
}
```

Prefer a canonical compendium name/verified UUID. If an item cannot be resolved, the macro creates a safe equipment fallback carrying its source text rather than failing the whole Actor import.

## 8. Effects, auras, and Rule Elements

Use `effects` only for actual owned Effect/Aura documents that should exist on the Actor.

```json
{
  "name": "Entropy's Shadow",
  "level": 12,
  "traits": ["aura", "void"],
  "radius": 20,
  "duration": "unlimited",
  "badge": null,
  "description": "...",
  "rules": [
    { "key": "Aura", "radius": 20, "traits": ["void"], "effects": [] }
  ]
}
```

If `radius` is supplied and no Aura Rule Element exists, the macro can construct a minimal Aura rule. For complex aura automation, prefer an explicit verified Rule Element.

## 9. Inline roll automation

Descriptions must explicitly use PF2e enrich syntax whenever the source expresses a roll, save, damage, or measured area.

Preferred forms:

```text
@Check[fortitude|dc:32]
@Check[reflex|dc:32|basic|options:area-effect]
@Check[will|dc:32|options:area-effect,damaging-effect]
@Check[athletics|dc:32]
@Check[flat|dc:5]
@Damage[6d6[void]]
@Damage[6d6[void]|options:area-damage]
@Damage[5d6[cold],3d6[void]|options:area-damage]
@Template[type:burst|distance:20]
@Template[type:cone|distance:30]
@Template[type:line|distance:60|width:10]
[[/gmr 1d20+22 #Counteract Omen]]{反制 +22}
```

When converting natural-language rolls:

- `DC 32 强韧基本豁免` -> `@Check[fortitude|dc:32|basic]`
- `DC 32 运动检定` -> `@Check[athletics|dc:32]`
- `DC 5 平检` -> `@Check[flat|dc:5]`
- `6d6虚能伤害` -> `@Damage[6d6[void]]`
- `1d6持续火焰伤害` -> `@Damage[1d6[persistent,fire]]`
- `20尺爆发` -> `@Template[type:burst|distance:20]` when it actually describes an area template

Do not convert every occurrence of a distance into a template. Only create a template for a genuine measured effect area.

Use `options:area-damage` for damage originating from an area and `options:area-effect` on checks caused by an area. `basic` already provides the damaging-effect roll option.

## 10. Conditions and UUIDs

Never invent condition compendium UUIDs.

For Chinese descriptions emit the Chinese condition plus canonical capitalized English PF2e name:

```text
失败：获得迟缓 Slowed 1，持续1轮。
```

The Foundry macro resolves the English condition against the live PF2e `ConditionManager` and inserts a verified `@UUID` if available.

Do not output guessed forms like:

```text
@UUID[Compendium.pf2e.conditionitems.Item.Slowed]
```

## 11. Lossless/fairness rules

- Preserve the original mechanic. Do not silently rebalance while converting format.
- Preserve unusual custom mechanics as prose if the PF2e document schema has no exact structured field.
- Put source material that cannot safely map to a core field in `description` or `notes` rather than discarding it.
- Do not infer a spell, item, trait, condition, UUID, or Rule Element from a weak guess.
- If a source field is ambiguous, choose the conservative representation and mention the ambiguity outside the JSON if needed.
- Keep names bilingual when the source is bilingual. For compendium-resolved spells/items, prefer canonical English names in the structured lookup field.

## 12. Validation

For complete Actor JSON:

1. Save the exact final JSON as UTF-8.
2. Run `python scripts/validate_actor_payload.py <payload.json>`.
3. Fix every `ERROR`.
4. Review every `WARN`.
5. Return the exact validated JSON without changing it afterward.

The Foundry runtime remains authoritative for live PF2e trait lists, condition UUIDs, frequency enums, compendium documents, and schema migrations.
