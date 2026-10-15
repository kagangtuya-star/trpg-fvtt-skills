# PF2 Wiki item entry workflow

Read this reference when creating or updating PF2 item entries from CSV, XLSX, or manually supplied text.

An item consists of two pages:

- Display page: `{{物品数据|中文=物品名称}}`
- Data page: `Data:Items-<原文>.json`, using the site's BSON/JSON content model

## Choose the factual source

### CSV or XLSX supplied by the user

Treat supplied fields as the source of truth. When the input is complete, do not query Archives of Nethys (AON), replace file values with web results, or guess IDs, English names, sources, or prices.

Validate structure and formatting before any write:

- Required item fields: `中文`, `原文`, `ID`, `物品分类`, `稀有度`, `特征`, `用法`, `描述`.
- `ID` must be numeric. If it is missing, stop the affected write and report it; do not fill it from AON.
- A multi-level item must contain `类型数据`. Each type requires `类型`, `类型原文`, `等级`, `价格`, `来源`, and `系列`.
- Preserve missing optional fields using the existing data-page empty-value convention. Do not infer them from the web.
- If fields in the same file conflict, prefer the more explicit field only after reporting the conflict before writing.

Common main-table fields are:

`中文`, `原文`, `ID`, `物品分类`, `相关`, `稀有度`, `特征`, `用法`, `启动`, `描述`, `负载`, `制作需求`, `2e`, `许可`, `持续`, `弹药`, `图鉴`, `占手`, `类型数据`

Column aliases are acceptable, but map and report them before use. `类型数据` may be a JSON array in one cell or a separate sheet/table. Type entries use:

`类型`, `类型原文`, `等级`, `类型稀有度`, `价格`, `类型描述`, `PFS`, `来源`, `系列`, `类型制作需求`

If the file contains only part of the required data, list missing fields. Switch to external research only when the user explicitly authorizes another source.

### Manually supplied text

When only Chinese rules text is supplied, first inspect representative live pages and templates. Use AON or another user-authorized source only to fill missing ID, English name, source, level, price, or similar metadata. Do not overwrite the user's explicit translation or rules text.

## Normalize input

- Read worksheet names, headers, and row counts before deciding whether rows are individual items or whether the workbook separates item and type tables.
- Convert `ID` and levels to numbers. Do not carry Excel date formatting or display-only number formatting into JSON.
- Preserve prices in the Wiki's established form, such as `1,750 gp`.
- Preserve cell line breaks as `\n`. Convert empty cells to empty strings unless the field specifically uses `—` semantically.
- Split `特征` with ASCII commas. Preserve the order of `类型数据`.
- Strictly parse JSON strings in `类型数据`. On failure, stop that row instead of saving damaged JSON.
- Preserve spaces, hyphens, apostrophes, and capitalization in the original name used by `Data:Items-<原文>.json`.
- Keep established Wiki links and hover templates for rules terms, spells, and conditions when the live Wiki shows a corresponding convention.

## Candidate data object

Use the following as a structural example only. Values must come from the current input and verified live conventions.

```json
{
  "data_type": "物品",
  "ID": 5147,
  "中文": "全视之眼",
  "原文": "All-Seeing Eye",
  "物品分类": "咒心",
  "相关": "",
  "稀有度": "常见",
  "特征": "魔法,咒心",
  "用法": "附着于护甲或武器上",
  "启动": "",
  "描述": "规则正文（使用 \\n、[[链接]]、{{浮窗|法术|法术名}} 等现有写法）",
  "负载": "—",
  "制作需求": "",
  "2e": "",
  "许可": "",
  "持续": "",
  "弹药": "",
  "图鉴": "",
  "占手": "",
  "类型数据": [
    {
      "类型": "全视之眼",
      "类型原文": "All-Seeing Eye",
      "等级": 3,
      "类型稀有度": "常见",
      "价格": "50 gp",
      "类型描述": "",
      "PFS": "标准",
      "来源": "IM",
      "系列": "CR",
      "类型制作需求": ""
    }
  ]
}
```

## Validate and save

1. Batch-read the intended display and data titles. If either already exists, use the revision-guarded update workflow rather than creating an alternate title.
2. For an import, count affected pages. More than 10 pages triggers the scope-and-plan checkpoint in the main skill.
3. For multiple items, generate a local candidate manifest and difference summary. Do not silently skip a row that fails validation.
4. Create or update the data page first with a meaningful summary. Fetch it again and verify the BSON content model, stored JSON, and revision.
5. Prepare the display candidate exactly as:

   ```wikitext
   {{物品数据
   |中文=物品中文名
   }}
   ```

6. Parse the display candidate on the server. Confirm it does not report “未找到名称匹配的物品” and that title, level, types, prices, source, description, and activation render.
7. Only after successful data-page verification and display parsing, create or update the display page with a meaningful summary.
8. Fetch both pages after saving, compare the display page, and perform a representative server parse. If either revision changed during analysis, stop and recompute from the latest revision.

Do not broaden an item import into edits of templates, Lua modules, categories, or navigation pages. If the data lookup behaves unexpectedly, report it as a separate issue.
