Title: 一个 else if 引发的血案 —— 记一次高考志愿小程序的 bug 修复
Date: 2026-06-27 23:30
Category: 项目
Tags: 微信小程序, 高考, 云开发, 调试, bug修复
Slug: ledao-volunteer-v2.1.1
Author: ZeroToDev
Summary: 修复了三个叠加 bug：综合科类分类逻辑缺陷导致旧高考省份分数全空、preloadData 响应超 1MB、seedAll 云函数部署失败。核心教训：else if 和两个独立 if，差一个字符，差一整个省份的数据。

## 起因

用户反馈：生源地选陕西后，高校录取线里几乎全部学校都没有物理类分数。专业查询选「首选物理」，只出来一个上海海事大学。

诡异的是，v2.1 昨天刚修过"科类匹配修复"。

## 调查

我打开 `seedAll/provinces/陕西.json`，搜 `首选物理` —— 0 个匹配。搜 `首选历史` —— 179 个。搜 `综合` —— 遍地都是。

原来陕西等省份至今仍用旧高考的「综合」科类（不分物理/历史），数据里压根没有 `首选物理` 这个 key。那为什么综合数据没显示出来？

翻到 `queryScores/index.js` 的科类分类逻辑：

```javascript
// v2.1 的代码（昨天刚改的）
for (const [cat, score] of Object.entries(item.s)) {
    if (cat === '首选历史' || cat === '综合' || cat.includes('历史') || cat.includes('文科')) {
        → historyScore   // 综合钉死在历史
    } else if (cat === '首选物理' || cat.includes('物理') || cat.includes('理科')) {
        → physicsScore   // 永远收不到综合
    }
}
```

看到了吗？第 118 行，`综合` 在 `if` 的第一个分支里。第 121 行是 `else if`。`综合` 进了历史就出不来了，物理类永远为空。

**一个 `else`，六个省的数据消失。**

## 修复

```javascript
// v2.1.1：改成两个独立 if
for (const [cat, score] of Object.entries(item.s)) {
    if (cat === '首选历史' || cat === '综合' || cat.includes('历史') || cat.includes('文科')) {
        → historyScore   // 综合也能进历史
    }
    if (cat === '首选物理' || cat === '综合' || cat.includes('物理') || cat.includes('理科')) {
        → physicsScore   // 综合也能进物理
    }
}
```

`else` 删掉，两个 `if` 各走各的。`综合` 同时出现在两边，旧高考省份不再空数据。

但这只是第一个 bug。

## 连锁反应

改完代码后发现还有两个问题：

**数据源本身也有缺失。** `seedAll` 目录下 6 个省份（上海、北京、天津、安徽、山西、陕西）的 JSON 文件压根没有 `首选物理` 字段，连那 1 条记录都没了。这些文件是另一套数据管道产出的，比 `seedData` 少了大量记录。直接把 `seedData` 的正确版本复制过去。

**preloadData 云函数炸了。** 我在云函数里把 `综合` 数据全量合并到 `首选物理` 和 `首选历史` 的 browseByCat 索引中，同一份数据在 JSON 响应里出现三次。陕西这种综合量大省直接飙过 1MB 上限，报 `response size exceeded`。

解法：云函数不合并，改由前端 `major.js` 在读取缓存时自行回落：

```javascript
let catData = cache.browseByCat[this.data.selectedCategory]
if ((!catData || Object.keys(catData).length === 0) && this.data.selectedCategory !== '综合') {
    catData = cache.browseByCat['综合']  // 前端回落，数据不丢，传输不翻倍
}
```

**seedAll 云函数完全不工作。** `getProvinceFiles()` 在 v2.1 重构时被误删；链式 `cloud.callFunction` 自调用在云环境里网络超时；Node 版本不支持 `Promise.allSettled`；还有个 15MB 的 `admission_data.json.gz` 加载了但从来不用的死代码。全部重写了一遍。

## 涉及文件

| 文件 | 改动 |
|------|------|
| `queryScores/index.js` | else if → 两个独立 if |
| `preloadData/index.js` | 同上 + 撤回 browseByCat 合并 |
| `queryMajors/index.js` | browse 回落综合 + search 不过滤综合 |
| `pages/score/score.js` | 前端同步修复 |
| `pages/major/major.js` | 读缓存时空→回落综合 |
| `seedAll/index.js` | 重写（polyfill、去链式、恢复函数） |
| `seedAll/provinces/*.json` (6个) | 从 seedData 复制修复 |
| `seedMajorIndex/chunks/*.json` (151个) | 重建索引，1,801,972 条 |

## 教训

1. **`if/else if` vs 两个 `if`** —— 当数据分类不是互斥的，不要用 `else if`。旧高考的「综合」既不是物理也不是历史的子集，它是两者共有。
2. **不要在云函数里复制数据** —— 把 `综合` 合并到三个 browseByCat 里看起来方便了前端，实际把响应撑爆了。让前端做回落，传输只传一份。
3. **死代码不只是难看** —— 15MB 的 `.gz` 文件加载但从不使用，直接把云函数包体积撑大、部署失败。删掉。

---

*代码已开源在 [GitHub](https://github.com/zerotodev2026/ledao-volunteer) 和 [Gitee](https://gitee.com/from-scratch-to-development/ledao-volunteer)。*
