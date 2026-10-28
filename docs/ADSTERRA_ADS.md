# Adsterra 广告接入规范

适用于游戏站（wiki）接入 Adsterra 横幅广告。当前已落地 6 站，统一使用同一套 7 位架构：`battleplan-wiki`（getbattleplan.org）、`ghostofyoteiwiki_com`、`moonfrost-wiki`、`sublustrum`、`enfosi-wiki`、`cloverrpgmagic.xyz`。

本文上半部分是规则正文，下半部分是可直接复制给 AI 的提示词定稿版（已按实跑代码修正）。

## 一、总体架构

每个广告位 = 一个独立的 `public/ads/<slot>.html` + 一个 React 组件渲染的 `<iframe>`。

- html 是独立 window：自己从 query 读 `key` 和 `invoke`，设置自己的 `atOptions`，`document.write` 注入 invoke 脚本。
- 不设全局 `window.atOptions`，不写队列加载。各 slot 天然隔离，互不串号。
- iframe 外层用 `flex` 居中，不加边框和背景，避免桌面端两侧出现横贯整屏的空白框。

## 二、Key 管理

- 所有 key 集中在 `src/config/ads.ts` 的 `ADS_CONFIG`，按 slot 命名。**不使用环境变量**：Adsterra key 是公开的，环境变量不带来保密收益，只多一个"部署漏配 = 广告静默消失"的故障点。
- `ADS_CONFIG` 用 `as const`，并导出 `export type AdSlot = keyof typeof ADS_CONFIG`。
- 手机放不下的位标 `desktopOnly: true`。
- invoke 主机写在同一个文件：`ADSTERRA_INVOKE_BASE`（banner）、`ADSTERRA_NATIVE_INVOKE_BASE`（native）。**不同账号的主机和路径不同**（banner `/22/{key}`，native `/21/{key}`），不要照抄别的站的域名。
- key 为空 → 组件 `return null`，不渲染、不报错。

## 三、组件 API

- `AdBanner({ slot, adKey?, eager? })` — prop 名用 `slot`，不要用 `type`。
- `StickyAdBanner({ adKey? })` — 需要 `"use client"`。
- `NativeBanner({ height? })`。
- 组件把 key 和 invoke 通过 query 传给 html：`/ads/${slot}.html?key=…&invoke=…`。**不要把 key 写死在 html 里**——那样 key 会同时存在于 `ads.ts` 和 html，轮换时必漏改。

## 四、atOptions 必含字段

`key`、`width`、`height`、`format: "iframe"`、`params: {}`。

`params` 为空对象，是厂商标签的一部分，无行为变化；6 个站已统一补齐。

## 五、位置与尺寸

- 文章详情页 7 位。首页加 2 位（728x90 + 300x250，放在折叠线以下：最近文章区块之后、`HomeModuleSections` 之前）。分类列表页不挂横幅（索引型薄页，加横幅会挤目录卡片，收益远小于互动信号损失）；法律页和 404 也不挂。
- 首页两个位放在 `src/app/[locale]/HomePageClient.tsx`，容器跟首页其它区块对齐：`mx-auto max-w-6xl px-4 sm:px-6 lg:px-8`。
- 分类列表页改挂 Social Bar（见第九节）：这些页原本一个广告位都没有，0 曝光 = 0 收入；Social Bar 一行脚本就能覆盖，且不改页面布局。
- 728x90 / 468x60 / 160x600 标 `desktopOnly`。
- `desktopOnly` 的断点 = 该位能放进正文列宽的最小视口。正文列 760px → `lg`（1024px）；正文列更宽（如 1080px）→ `md`（768px）。不要无脑用 `sm`（640px），否则 728x90 会被压扁。

## 六、Sticky 粘性广告

- `sticky top-[<头部高度+16px>] z-20 py-2`。clover 头部是 `sticky top-0 min-h-[72px]` → `top-[88px]`；battleplan 用 `top-20`。
- **不要加 `border-y` 这类横贯整屏的分隔线**——桌面端会在 320 横幅两侧拉出一条贯穿全屏的框。
- 内层 `mx-auto max-w-[<正文列宽>]` 限宽居中（clover `max-w-[760px]`），把 320 横幅锁进内容宽度，桌面端两侧不会露出横贯空白框。
- 不加 `md:hidden`：桌面端和移动端都要显示。
- 用 `eager` 加载，避免首屏 sticky 位空白。

## 七、关闭按钮

- `useState` 记 `dismissed`，点关闭后置 true，组件 `return null`。
- 广告右上角叠 lucide-react 的 `X`（`absolute` 定位）。父容器 `relative inline-block pr-0 sm:pr-10`：手机端不预留 40px（否则 320 横幅右侧空一块），`sm` 以上才给按钮留位。
- `aria-label` 用站点语言：中文站 `关闭广告`，英文站 `Close ad`。

## 八、Native Banner（可选）

- 不用 `atOptions`；用 `<div id="container-{key}"></div>` + async invoke 脚本，**container id 必须等于 key**。
- 主机路径与 banner 不同（`/21` vs `/22`），单独一个 base 常量。

## 九、Social Bar（可选）

- Social Bar 不是横幅位：没有 iframe、没有宽高，是一行 `<script data-cfasync="false" src="https://bauval.org/14/<key>"></script>`，形态由 Adsterra 决定（页内推送、图标通知、自定义挂件、插屏）。主机路径是 `/14/`（横幅 `/22/`、native `/21/`）。
- 用途是给"一个广告位都没有的页面"补曝光。已经挂了横幅的页面不要再叠。
- 挂载范围：**只挂分类列表页**（`CONTENT_TYPES` 里的页，即 `[locale]/[...slug]/page.tsx` 中 `slug.length === 1` 的分支）。文章页、首页、法律页、404 都不挂。
- key 与主机写在 `src/config/ads.ts`（`ADSTERRA_SOCIAL_BAR_KEY` / `ADSTERRA_SOCIAL_BAR_SRC`），组件放 `src/components/ads/social-bar.tsx`，用 `next/script` 且 `strategy="afterInteractive"`。
- 直接挂在分类列表页的分支里（该分支已被 `CONTENT_TYPES.includes(contentType)` 守卫），不要另写 `usePathname()` 客户端组件做路由判断。
- **Popunder 不加**：它会在后台新开标签页，体验和排名信号最差。

## 十、范围

只新增/修改广告相关文件，不动其它广告位和无关代码。

## 十一、验收清单

1. `npm run build` 通过。
2. 本地 `next start` 抽查文章页 HTML：7 个 `/ads/*.html?key=…&invoke=…` 全部存在且 key 正确。
3. 移动端 390x844：`document.documentElement.scrollWidth === clientWidth`（无横向滚动），宽位 `display:none`。
4. 桌面 1440x900：7 位全部可见、尺寸正确，native 宽度 = 728（或站点设定值）；首页两个位（728x90 + 300x250）在桌面可见、手机只剩 300x250。
5. 分类列表页 HTML 里有 `/14/` 的 Social Bar 脚本；文章页、首页、法律页、404 里没有。
6. 关闭按钮点击后，按钮和广告都消失。
7. 线上部署后再验一遍同样 4 项。
8. **注意**：本机 IP 被 Cloudflare 拦截（`bauval.org` 与 `highrevenueformat.com` 均返回 403），广告创意是否填充**无法在本机判定**——已在 6 个站实测同样 403（含早已上线的站点），属环境限制而非代码问题。创意填充需用正常网络或广告后台查看。

## 十二、可直接复制的提示词（定稿版）

### A. 接入 banner 横幅广告

1. 在 `public/ads/` 下为每个广告位各建一个 html（如 `banner-320x50.html`、`banner-300x250.html`），文件里从 query 读 `key` 和 `invoke`，设置自己的 `atOptions`（含 `key`、宽、高、`format: "iframe"`、`params: {}`），并用 `document.write` 注入 invoke 脚本。
2. 在 `src/config/ads.ts` 集中登记所有 slot 的 key、宽高、`desktopOnly` 标记，以及 invoke 主机常量。key 不写死在 html，也不放环境变量。
3. 做一个广告组件，渲染 `<iframe>`，src 指向对应 html，width/height 用该位尺寸，带 `scrolling="no"`、`style={{ border: "none", maxWidth: "100%" }}`，外层 `flex` 居中，不加边框和背景。
4. 组件 prop 用 `slot`，不要用 `type`。
5. key 为空时 `return null`，不渲染也不报错。
6. 不用全局 `window.atOptions`，不写队列加载；每个位靠自己的 html（独立 window）天然隔离。
7. 只新增广告相关文件，不改其它无关代码。

### B. Sticky 粘性广告

1. 用 `sticky top-[<头部高度+16px>] z-20 py-2` 让它滚动时粘在视口顶部；不要加 `border-y` 这类横贯整屏的分隔线。
2. 用 `<AdBanner slot="banner-320x50" adKey={…} eager />` 渲染 320×50（移动端和桌面端都显示），adKey 默认取 `ADS_CONFIG`。
3. 关键：给广告外层套 `mx-auto max-w-[<正文列宽>]` 容器限宽居中，把 320 横幅锁进内容宽度内，桌面端两侧不会出现横贯整屏的空白/透明框。
4. 不要加 `md:hidden`。
5. adKey 为空时 `return null`，不报错。
6. 只改这一个位置，不动其它广告位和无关代码。

### C. 关闭按钮

1. 用 `useState` 记一个 `dismissed` 状态，点关闭按钮后设为 true，组件 `return null` 不再渲染。
2. 在广告右上角叠一个 ✕ 按钮（lucide-react 的 `X` 图标，`absolute` 定位），父容器加 `relative inline-block pr-0 sm:pr-10` 给按钮留位（手机端不占位）。
3. 把广告外层用 `mx-auto max-w-[<正文列宽>]` 限宽居中，避免桌面端 320 横幅两侧露出横贯整屏的空白框。
4. `aria-label` 用站点语言。
5. 只改这一个广告位，adKey 为空时同样 `return null`，不动其它广告和无关代码。

### D. 首页广告位

1. 在首页组件（`src/app/[locale]/HomePageClient.tsx`）里，紧跟"最近文章"区块之后、`HomeModuleSections` 之前插入一个 `<section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">`，里面放 `<AdBanner slot="banner-728x90" />` 和 `<AdBanner slot="banner-300x250" />`。
2. 位置在折叠线以下，不要放首屏上方。
3. 728x90 是 `desktopOnly`，手机自动隐藏；300x250 两端都显示。
4. 分类列表页、法律页和 404 不挂横幅广告位（分类列表页挂 Social Bar，见 E）。
5. 只改首页这一个文件和广告相关文件，不动其它无关代码。

### E. Social Bar（分类列表页）

1. 在 `src/config/ads.ts` 加 `ADSTERRA_SOCIAL_BAR_KEY` 和 `ADSTERRA_SOCIAL_BAR_SRC = \`https://bauval.org/14/${ADSTERRA_SOCIAL_BAR_KEY}\``。
2. 新建 `src/components/ads/social-bar.tsx`：返回 `<Script src={ADSTERRA_SOCIAL_BAR_SRC} data-cfasync="false" strategy="afterInteractive" />`，用 `next/script`，不要 iframe、不要宽高。
3. 只在分类列表页挂：在 `src/app/[locale]/[...slug]/page.tsx` 的 `slug.length === 1` 分支（列表页渲染函数）末尾渲染 `<SocialBar />`。该分支已被 `CONTENT_TYPES.includes(contentType)` 守卫，所以不可能出现在文章页。
4. 文章页、首页、法律页、404 一律不挂。
5. 不加 Popunder。
6. 只改广告相关文件，不动其它无关代码。
