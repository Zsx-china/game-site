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

- 文章详情页 6 位（6 个横幅）。**首页默认加 6 位**：顶部 sticky 320×50（通栏带下边框，跟文章页同一个位，可关闭）+ native 卡片 + 桌面 728×90（native 卡片之后）+ 桌面 468×60（内容模块之后）+ 桌面 728×90（页尾再来一条）+ 手机专属 300×250。参考站（enfosi.online）首页就是这样：桌面位在 `src/config/ads.ts` 标 `desktopOnly`（手机自动隐藏），手机位用 `md:hidden` 单独挂，一个桌面位旁边配一个手机位。页尾那条桌面 728×90 复用同一个单元——Adsterra 面板不允许同一站再发第二个同尺寸横幅单元，参考站也是同一个位在首页用两次。新站建站时就要加，不是可选项。**手机另加 3 条**（都不和桌面位相邻）：native 卡片之后的 300×250、`HomeModuleSections` 之后的 320×50、页尾 320×50 —— 合计手机 4 位（含顶部 sticky）。参考站手机首页有 6 条，我们取 4 条，避免广告块连成一片。分类列表页两套并列：桌面 728×90 ×2（标题下、页尾，复用同一单元）+ 中段 300×250（第六条卡片之后，占满整行）；手机 320×50 ×2（同样位置）+ 中段 300×250；再叠 Social Bar。法律页和 404 不挂。
- 首页这些位都放在 `src/app/[locale]/HomePageClient.tsx`：sticky 320×50 放在组件最上面（`return <div className="min-w-0 bg-background">` 之后、hero 之前）；native 卡片紧跟"最近文章"区块，其后依次是桌面 728×90 和手机 300×250，都在 `HomeModuleSections` 之前；桌面 468×60 放在 `HomeModuleSections` 之后；页尾（最后的 CTA 区块之后）再放一条桌面 728×90。手机位：`md:hidden` 的 320×50 放在 `HomeModuleSections` 之后（在桌面 468 之前，否则手机上没有它挡着，两条手机位会贴在一起）、页尾再接一条 `md:hidden` 320×50。容器跟首页其它区块对齐：`mx-auto max-w-6xl px-4 sm:px-6 lg:px-8`。
- 首页的 Native Banner 卡片 `<NativeBanner />`（见第九节）放在"最近文章"区块之后——参考站就是 native 卡片紧跟"最新文章"区块。文章页默认不挂 native。
- 分类列表页 = 桌面 728×90 ×2 + 中段 300×250 + 手机 320×50 ×2 + Social Bar（见第十节）。参考站列表页就是这个结构（桌面三条、手机三条），中段 300×250 用 `sm:col-span-2 lg:col-span-3` 占满整行，卡片网格不会被切断。wrapper 用 `hidden lg:flex`（桌面位）和 `flex lg:hidden`（手机位），互不干扰。
- 728x90 / 468x60 / 160x600 标 `desktopOnly`。
- `desktopOnly` 的断点 = 该位能放进正文列宽的最小视口。正文列 864px → `lg`（1024px）；正文列更宽（如 1080px）→ `md`（768px）。不要无脑用 `sm`（640px），否则 728x90 会被压扁。

- Clover 文章页：正文和相关文章之后，页尾横幅顺序为 **728×90 → 300×250 → 468×60**，文章顶部不再放 728×90。左右两条空带都放竖版位（左 160×600、右 160×300，见第六节），桌面目录改为正文上方的内联卡片（`SidebarTOC`，`mt-8 hidden lg:block`）。手机：正文第一个 H2 之后插一条 300×250（`article-body.tsx` 里的 `h2` 组件数到第 2 个 H2 时在前面渲染 `lg:hidden` 的 `<AdBanner slot="banner-300x250" />`，正文不足 2 个 H2 的文章自动不插），页尾再在 468×60 之后加一条 `lg:hidden` 320×50。
- Clover 文章粘性条放在限宽 `<main>` 外、导航下方，整条覆盖视口宽度。注意：参考站文章页的粘性条自然位置在标题区之后，Clover 当前在标题区之前；二者滚动后都吸顶，但初始位置尚未完全对齐。

## 六、单栏页的空带广告位

单栏文章页（`main max-w-[1200px]` + 正文列 `max-w-[864px]`）的两条侧轨用整页 `fixed` 定位，空带宽度按**视口**算：1440 视口两侧各约 280px，1280 视口各约 200px，放 160px 宽竖版 + 32px 间距都够，再宽的尺寸塞不进去。**左右都不是空的**：左边放 160x600，右边放 160x300。

- 160x600 放进左侧空带：`min-[1280px]:fixed min-[1280px]:top-20 min-[1280px]:left-[calc(50%-624px)] min-[1280px]:z-10 min-[1280px]:w-[160px]`，只在 `min-[1280px]` 起变成悬浮。**用 `fixed` 直接悬浮、不要用 `absolute` + `sticky`**——`fixed` 相对视口定位，滚到页尾也一直挂着（参考站就是这样）；`sticky` 只跟着正文容器走，到正文末尾就停。偏移量算法：正文列 864px 居中 ⇒ 半宽 432，加 32px 间距、加 160px 广告宽 = `calc(50%-624px)`。前提是正文列真的居中（无左侧栏、右侧空带没有浮动目录），否则 50% 算不准。
- 160x300 放进右侧空带：同一套写法镜像过去——`min-[1280px]:fixed min-[1280px]:top-20 min-[1280px]:left-[calc(50%+464px)] min-[1280px]:z-10 min-[1280px]:w-[160px]`（432 + 32 = 464）。两条侧轨都在 `z-10`，粘性通栏 `z-20`、站点头部 `z-50`，层级不能反。
- **一个空带只放一个位**。600 + 300 叠起来 = 924px > 900px 视口高，粘住时下面那个会永远露不全；也**不要**把 160x300 同时留在正文流里——同一个单元在 DOM 里只能有一份。
- **每个位在 DOM 里只能有一份**。不要用"桌面显示一份、隐藏再放一份"的做法——`display:none` 的 iframe 照样发请求，同一个广告位每页请求两次。桌面/移动用同一份 + 响应式定位（`min-[1280px]:fixed` / 不加前缀时保持常规流里的居中块，窄屏照样有 160x300 曝光）。
- 300x250（300px 宽）塞不进 204px 空带，只能留在正文流里。
- 参考做法：enfosi.online 的文章页是两条 `fixed top-20 w-40 z-10 hidden xl:block` 的侧轨（左侧 160x600、右侧 160x300，与正文留 31px），正文列 864px。clover 正文列同为 864px，两条空带照样放得下，所以左右都用；写法同样是整页 `fixed top-20`，只是横向用 `calc(50%±…)` 跟着居中的正文列走（参考站是贴视口边）。
- **右侧空带的前提：把浮动目录挪走**。220px 浮动目录 (`article-toc.tsx`) + 32px 间距 + 160px 广告 + 24px 间距 = 436px 右侧空带，1440 视口下只有约 333px，**放不下**（要 ≥1632px 才够）。所以先按第十四节把目录改成正文上方的内联卡片（`SidebarTOC`），右侧空带才空出来；代价是目录不再跟随滚动、也不再高亮当前章节。不要为了腾位置删掉目录——`MobileTOC` 只管手机，桌面端删了就没有目录了。

## 七、Sticky 粘性广告

- `sticky top-[<头部高度+16px>] z-20 border-b border-border py-2`，内层再套 `flex justify-center` 让 320 横幅在视口里居中——整条通栏 + 一条细下边框（参考站 enfosi.online 就是这个形状）。clover 头部是 `sticky top-0 min-h-[72px]` → `top-[88px]`。
- **只用 `border-b`（一条下边框）；不要 `border-y`（上下两条），不要加背景色或外框**——横贯整屏的框会在 320 横幅两侧拉出一条贯穿全屏的空条。
- 不加 `md:hidden`：桌面端和移动端都要显示。
- 用 `eager` 加载，避免首屏 sticky 位空白。

## 八、关闭按钮

- `useState` 记 `dismissed`，点关闭后置 true，组件 `return null`。
- 广告右上角叠 lucide-react 的 `X`（`absolute` 定位）。父容器 `relative inline-block pr-0 sm:pr-10`：手机端不预留 40px（否则 320 横幅右侧空一块），`sm` 以上才给按钮留位。
- `aria-label` 用站点语言：中文站 `关闭广告`，英文站 `Close ad`。

## 九、Native Banner（可选）

- **不要用 iframe 装 native**。native 广告的卖点是图文并排的推荐卡，塞进固定高度的 iframe 会把它压成一条横幅，形态和点击率都吃亏。
- 做法：页面里放一个空的 `<div id="container-{key}"></div>`（**container id 必须等于 key**），再用 `next/script` 注入 `https://bauval.org/21/{key}`（`async` + `data-cfasync="false"` + `strategy="afterInteractive"`）。广告脚本自己往这个空 div 里渲染卡片。
- 卡片外壳由站点自己套：`min-h-[120px] overflow-hidden rounded-2xl`，外层 `w-full max-w-4xl`，整体外面再包一层 `my-8 flex w-full justify-center`。**高度用 `min-h` 不写死**（卡片高度由广告方决定）。外壳**不要加 `border` 或 `bg`**——广告自己会画背景，多一层框会在广告没填充时变成一个空盒子。
- 主机路径与 banner 不同（`/21` vs `/22`），单独一个 base 常量 `ADSTERRA_NATIVE_INVOKE_BASE`。
- key 和 base 写在 `src/config/ads.ts`；组件 `src/components/ads/native-banner.tsx` 里用 `ADS_CONFIG["native-banner"].key`。
- **不需要 `public/ads/native-banner.html`**（那是旧 iframe 方案的文件，改造时删掉）。
- 位置：**首页，折叠线以下，紧跟"最近文章"区块**（参考站就是这样）。文章页默认不挂 native——要挂就在正文广告栈里加回一行 `<NativeBanner />`（同时加回 import）。

## 十、Social Bar（可选）

- Social Bar 不是横幅位：没有 iframe、没有宽高，是一行 `<script data-cfasync="false" src="https://bauval.org/14/<key>"></script>`，形态由 Adsterra 决定（页内推送、图标通知、自定义挂件、插屏）。主机路径是 `/14/`（横幅 `/22/`、native `/21/`）。
- 用途是给"一个广告位都没有的页面"补曝光。已经挂了横幅的页面不要再叠。
- 挂载范围：**只挂分类列表页**（`CONTENT_TYPES` 里的页，即 `[locale]/[...slug]/page.tsx` 中 `slug.length === 1` 的分支）。文章页、首页、法律页、404 都不挂。这些页同时挂桌面 728×90 ×2 + 手机 320×50 ×2 + 中段 300×250（见第五节），三种格式并存。
- key 与主机写在 `src/config/ads.ts`（`ADSTERRA_SOCIAL_BAR_KEY` / `ADSTERRA_SOCIAL_BAR_SRC`），组件放 `src/components/ads/social-bar.tsx`，用 `next/script` 且 `strategy="afterInteractive"`。
- 直接挂在分类列表页的分支里（该分支已被 `CONTENT_TYPES.includes(contentType)` 守卫），不要另写 `usePathname()` 客户端组件做路由判断。
- **Popunder 不加**：它会在后台新开标签页，体验和排名信号最差。

## 十一、范围

只新增/修改广告相关文件，不动其它广告位和无关代码。

## 十二、验收清单

1. `npm run build` 通过。
2. 本地 `next start` 抽查文章页 HTML：6 个横幅 `/ads/*.html?key=…&invoke=…` 全部存在且 key 正确；文章页没有 native（native 在首页，是 `<div id="container-<key>">` + `/21/` 脚本，不是 iframe）。
3. 移动端 390x844：`document.documentElement.scrollWidth === clientWidth`（无横向滚动），宽位 `display:none`。
4. 桌面 1440x900：文章页横幅位全部可见、尺寸正确，页尾顺序为相关文章之后 **728×90 → 300×250 → 468×60**（文章顶部没有 728×90），粘性条整条覆盖视口宽（`x=0`、宽度 = `clientWidth`）；首页显示 sticky 320×50（通栏、带下边框）+ native 卡片 + 桌面 728×90（native 之后）+ 桌面 468×60 + 页尾桌面 728×90（手机专属 300×250 在桌面不出现），native 卡片容器存在（高度由广告方决定，最小 120px）；手机首页显示 4 条：sticky 320×50 + 300×250（native 之后）+ 320×50（模块之后）+ 320×50（页尾），桌面位不出现；手机文章页显示 sticky 320×50 + 中段 300×250 + 页尾 300×250 + 页尾 320×50。
5. 分类列表页 HTML 里有 `/14/` 的 Social Bar 脚本，并且恰好两个 `banner-728x90`、两个 `banner-320x50`、一个 `banner-300x250` iframe（同一单元两份 DOM 属预期）；桌面只显示 728×90 与 300×250，手机只显示 320×50 与 300×250；文章页、首页、法律页、404 里没有 Social Bar 脚本。
6. 关闭按钮点击后，按钮和广告都消失。
7. 竖版位放进空带后：文章页的**广告 iframe 数量仍等于广告位数量**（不能出现同一广告位两份 DOM）；1440 下左侧位右边缘 = 正文列左边缘 − 32px、右侧位左边缘 = 正文列右边缘 + 32px；两条侧轨是 `fixed`：滚到正文中段和滚到页面最底部时 `y` 都不变（1440 实测都停在 80）；桌面目录是正文上方的内联卡片，右侧空带里不再有浮动目录；各宽度 `scrollWidth === clientWidth`（1280 是最窄的必验宽度）。
8. 线上部署后再验一遍同样 4 项。
9. **注意**：本机 IP 被 Cloudflare 拦截（`bauval.org` 与 `highrevenueformat.com` 均返回 403），广告创意是否填充**无法在本机判定**——已在 6 个站实测同样 403（含早已上线的站点），属环境限制而非代码问题。创意填充需用正常网络或广告后台查看。

## 十三、可直接复制的提示词（定稿版）

### A. 接入 banner 横幅广告

1. 在 `public/ads/` 下为每个广告位各建一个 html（如 `banner-320x50.html`、`banner-300x250.html`），文件里从 query 读 `key` 和 `invoke`，设置自己的 `atOptions`（含 `key`、宽、高、`format: "iframe"`、`params: {}`），并用 `document.write` 注入 invoke 脚本。
2. 在 `src/config/ads.ts` 集中登记所有 slot 的 key、宽高、`desktopOnly` 标记，以及 invoke 主机常量。key 不写死在 html，也不放环境变量。
3. 做一个广告组件，渲染 `<iframe>`，src 指向对应 html，width/height 用该位尺寸，带 `scrolling="no"`、`style={{ border: "none", maxWidth: "100%" }}`，外层 `flex` 居中，不加边框和背景。
4. 组件 prop 用 `slot`，不要用 `type`。
5. key 为空时 `return null`，不渲染也不报错。
6. 不用全局 `window.atOptions`，不写队列加载；每个位靠自己的 html（独立 window）天然隔离。
7. 只新增广告相关文件，不改其它无关代码。
8. native 广告位不用 html 文件，单独按 G 段做。
9. 文章页的页尾横幅放在相关文章之后，顺序为 728×90 → 300×250 → 468×60；验收时检查 DOM 顺序和实际显示位置。

### B. Sticky 粘性广告

1. 用 `sticky top-[<头部高度+16px>] z-20 border-b border-border py-2` 让它滚动时粘在视口顶部，整条通栏 + 一条细下边框（参考站 enfosi.online 的做法）；不要用 `border-y`，不要加背景色或外框。
2. 用 `<AdBanner slot="banner-320x50" adKey={…} eager />` 渲染 320×50（移动端和桌面端都显示），adKey 默认取 `ADS_CONFIG`。
3. 关键：外层通栏，里面再套一层 `flex justify-center` 让 320 横幅在视口里居中（不要再用 `mx-auto max-w-[<正文列宽>]` 限宽，那是旧写法）。Clover 当前将文章粘性条作为限宽 `<main>` 前的同级元素；不要把这一初始位置误记为参考站标题区之后的位置。
4. 不要加 `md:hidden`。
5. adKey 为空时 `return null`，不报错。
6. 只改这一个位置，不动其它广告位和无关代码。

### C. 关闭按钮

1. 用 `useState` 记一个 `dismissed` 状态，点关闭按钮后设为 true，组件 `return null` 不再渲染。
2. 在广告右上角叠一个 ✕ 按钮（lucide-react 的 `X` 图标，`absolute` 定位），父容器加 `relative inline-block pr-0 sm:pr-10` 给按钮留位（手机端不占位）。
3. 关闭按钮所在的 `relative inline-block` 放在 sticky 的 `flex justify-center` 里面即可，不用再加限宽容器。
4. `aria-label` 用站点语言。
5. 只改这一个广告位，adKey 为空时同样 `return null`，不动其它广告和无关代码。

### D. 首页广告位（默认加，新站必做）

1. 在首页组件（`src/app/[locale]/HomePageClient.tsx`）里，紧跟"最近文章"区块之后、`HomeModuleSections` 之前插入一个 `<section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">`，里面放 `<NativeBanner />`（native 卡片）。
2. 紧跟 native 卡片插桌面横幅 728×90：`<section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8"><AdBanner slot="banner-728x90" /></section>`（728x90 在 `src/config/ads.ts` 标了 `desktopOnly`，桌面显示、手机自动隐藏）。
3. 再插一个手机专属横幅：`<section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 md:hidden"><AdBanner slot="banner-300x250" /></section>`（`md:hidden` = 桌面隐藏，只在手机显示）。
4. `HomeModuleSections` 之后再插桌面横幅 468×60：`<section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8"><AdBanner slot="banner-468x60" /></section>`（参考站就是把这个位放在两个内容模块之间）。
5. 页尾（最后的 CTA 区块之后）再放一条桌面 728×90：`<section className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8"><AdBanner slot="banner-728x90" /></section>`。参考站页尾也有一条；Adsterra 面板不允许同一站再发第二个同尺寸横幅单元，所以这里复用 728x90 单元——同一页出现两次同一单元是参考站的做法；如果后台显示这条位填充率低就删掉它。
6. 首页顶部再加 sticky 320×50：import `StickyAdBanner`（`@/components/ads/sticky-ad-banner`），在 `return <div className="min-w-0 bg-background">` 之后、hero 之前写一行 `<StickyAdBanner />`（跟文章页同一个位，可关闭，通栏带下边框，见 B 段）。
7. 桌面位和手机位成对安排（参考站每个桌面位旁边都有一个手机位）。同一个广告单元不要在不同位置重复挂（`display:none` 的 iframe 一样会请求广告，重复挂等于重复请求同一广告位）；页尾那条 728×90 是唯一例外。
8. 这些位都在折叠线以下，不要放首屏上方。
9. 首页这几个位**新站默认就加**，不用等用户特别要求；只有用户明确说"首页别挂广告"才去掉。
10. 分类列表页：标题下和页尾各一条 728×90（桌面，`hidden lg:flex`）+ 同样位置各一条 320×50（手机，`flex lg:hidden`）+ 第六条卡片之后一条 300×250（`sm:col-span-2 lg:col-span-3` 占满整行），并叠加 Social Bar（见 E）；法律页和 404 不挂任何广告位。
11. 只改首页这一个文件和广告相关文件，不动其它无关代码。

### E. Social Bar（分类列表页）

1. 在 `src/config/ads.ts` 加 `ADSTERRA_SOCIAL_BAR_KEY` 和 `ADSTERRA_SOCIAL_BAR_SRC = \`https://bauval.org/14/${ADSTERRA_SOCIAL_BAR_KEY}\``。
2. 新建 `src/components/ads/social-bar.tsx`：返回 `<Script src={ADSTERRA_SOCIAL_BAR_SRC} data-cfasync="false" strategy="afterInteractive" />`，用 `next/script`，不要 iframe、不要宽高。
3. 只在分类列表页挂：在 `src/app/[locale]/[...slug]/page.tsx` 的 `slug.length === 1` 分支（列表页渲染函数）末尾渲染 `<SocialBar />`。该分支已被 `CONTENT_TYPES.includes(contentType)` 守卫，所以不可能出现在文章页。
4. 文章页、首页、法律页、404 一律不挂。
5. 不加 Popunder。
6. 只改广告相关文件，不动其它无关代码。

### F. 单栏页竖版位放进空带（左右各一条）

1. 单栏文章页（`main max-w-[1200px]` + 正文列 `max-w-[864px]`）两侧各约 280px（1440 视口，按视口算）。左边放 160x600，右边放 160x300。
2. 先把桌面浮动目录挪走：右侧空带原本被 `article-toc.tsx` 的 220px 浮动目录占着；目录 + 32px 间距 + 160px 广告 + 24px 间距 ≈ 436px，1440 视口只有约 333px，放不下（要 ≥1632px 才够）。改成正文上方的内联卡片：删掉 `ArticleTOC` 的 import 和用法，在标题区正文列里加 `<div className="mt-8 hidden lg:block"><SidebarTOC headings={item.headings} label={messages.shared.tableOfContents} currentPathname={localizeHref(pathname, locale)} /></div>`。代价是目录不再跟随滚动、也不高亮当前章节——可以接受，但别为了腾位置直接删目录（`MobileTOC` 只管手机，桌面删了就没有目录了）。
3. 把 160x600 改成左侧悬浮轨：`<div className="mt-10 flex justify-center min-[1280px]:fixed min-[1280px]:top-20 min-[1280px]:left-[calc(50%-624px)] min-[1280px]:z-10 min-[1280px]:mt-0 min-[1280px]:w-[160px]"><AdBanner slot="banner-160x600" /></div>`。
4. 160x300 镜像到右侧：同一套 class，把 `left-[calc(50%-624px)]` 换成 `left-[calc(50%+464px)]`，里面放 `<AdBanner slot="banner-160x300" />`。顺手删掉原来正文下方那条 160x300 横排容器。
5. 数字怎么来：正文列 864px 居中 ⇒ 半宽 432；左轨左边缘 = 50% − 432 − 32 − 160 = `50%-624px`，右轨左边缘 = 50% + 432 + 32 = `50%+464px`。正文列宽度或间距一变，这两个数要跟着改。
6. 同一份 DOM 兼顾窄屏：`min-[1280px]:fixed` 之前的断点下它就是普通居中块，落在正文流里。不要再额外复制一份——`display:none` 的 iframe 照样发请求，一个广告位会被请求两次。
7. 用 `fixed` 不要用 `absolute` + `sticky`：`sticky` 只跟着正文容器走、到正文末尾就停下；`fixed` 相对视口，滚到页尾也在（和参考站一致）。
7. 一条空带只放一个位（600 + 300 = 924px > 900px 视口高，下面那个会永远露不全）；300x250（300px 宽）塞不进 204px 空带，仍放正文流里。

### G. Native Banner 卡片（不套 iframe）

1. 在 `src/config/ads.ts` 里保留 native 的 key，并导出 `ADSTERRA_NATIVE_INVOKE_BASE = "https://bauval.org/21"`（banner 是 `/22`，两个主机不一样）。
2. 新建 `src/components/ads/native-banner.tsx`：`const key = ADS_CONFIG["native-banner"].key; if (!key) return null;`，渲染一个空 div `<div id={`container-${key}`} />`，外面套卡片壳 `min-h-[120px] overflow-hidden rounded-2xl`（**不要加 `border`/`bg`**，广告没填充时会变成空盒子），再包一层 `w-full max-w-4xl`，整体外面再包 `my-8 flex w-full justify-center`；同一个组件里用 `next/script` 注入 `<Script src={`${ADSTERRA_NATIVE_INVOKE_BASE}/${key}`} async data-cfasync="false" strategy="afterInteractive" />`。
3. **container id 必须等于 key**，否则脚本找不到坑位、什么都不会渲染。
4. 高度写 `min-h`，不要写死 90px——卡片高度由广告方决定；也不要用 iframe 罩着，否则 native 被压成横幅条。
5. 旧的 `public/ads/native-banner.html`（iframe 方案）删掉，不用再建。
6. 挂载点：**首页，折叠线以下，紧跟"最近文章"区块**（跟参考站一致）。文章页默认不挂；要挂就在正文广告栈加回一行 `<NativeBanner />` 并补上 import。
7. 只改广告相关文件，不动其它无关代码。
