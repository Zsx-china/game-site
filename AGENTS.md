## 新站资料采集默认流程

建立或换皮游戏站时，先读取 `docs/NEW_SITE_WORKFLOW.md`，按“SEOScout 资料采集 → 基础配置 → SEO 与法律页 → 多语言与导航 → 首页模块 → 文章与导航 → 上线前验收”执行。默认使用逐部分确认的标准模式；用户提出“抢排名”“一个上午上线”或明确要求快速首发时，使用该文档的快速首发模式和三道确认门。两种模式都必须先通过第零阶段验收，再修改站点业务文件。

用户已确认：以后建立新站，默认沿用本次验证的远端 SEOScout + 青果代理采集方式。

- 先用 `tools/seoscout_preflight.py` 校验关键词数量和项目名，再在已配置的 VPS `/root/seoscout` 依次执行 `seoscout search`、核验 `search_results.json`、执行 `seoscout collect`；使用青果标准代理并启用 `USE_PROXY_FOR_EXTRACT=true`，沿用现有私密配置保存凭据。
- 青果标准代理已验证新连接可获得不同出口 IP。采集失败时通过新连接重试；此流程直接运行 SEOScout，拨号脚本仅在用户选择拨号换 IP 时使用。
- 断点续采保留已有字幕和网页，只补采所选来源中缺失的内容。按保存结果核验完成情况，部分失败也可能返回退出码 0。
- YouTube 出现 `RequestBlocked` / `IpBlocked` 时重试代理连接；出现 `TranscriptsDisabled` / `NoTranscriptFound` 或重试后仍被封锁时，记录并跳过。用户已确认永不进行音频下载或语音转写。
- 汇报实际保存的来源数量和未成功来源；新站使用自己的项目名与关键词文件。

## 新站文章生成默认流程

用户已确认：远端 VPS 只负责 SEOScout 搜索和采集；文章生成与翻译默认在本地运行 SEOScout，避免 VPS 的 PPPoE 周期性断线。生成前读取 `docs/SEOSCOUT_GENERATION_WORKFLOW.md`。

- 从 VPS 同步对应项目的关键词、`out/collected/` 和必要配置到本地临时工作目录；私密凭据仅保存在本地私密环境配置，不写入仓库或日志。
- 本地按“真实提示词预检 → 精确生成 1 篇 → 串行生成 2 篇 → 每批 1–2 篇续跑”执行；成功文章立即保留，重跑只补缺失项。
- 模型与端点以提供商当前 `/models` 和官方文档为准；先验证再写入私密 `.env`，不在工作流中缓存易过期的默认模型。
- 生成与翻译分别执行；每个步骤结束后按实际文件核验数量、分类、metadata、占位符和失败项，不以退出码 0 作为完成依据。
- 用户明确要求某次任务继续在远端执行时，才改用远端生成。

## 广告接入

游戏站接入 Adsterra 广告统一按 `docs/ADSTERRA_ADS.md` 执行（7 位架构：key 集中在 `src/config/ads.ts`、html 走 query 传 key+invoke、sticky 320×50 可关闭、宽位 `desktopOnly`）；已落地 6 站，改动前先核对该文档。**新站默认就要加首页广告位**：首页 = 顶部 sticky 320×50 + native 卡片 + 手机专属 300×250（桌面不加 728x90/300x250），分类列表页挂 Social Bar。

## 环境事实补充

- GitHub CLI 在 Windows 侧：`/mnt/c/Program Files/GitHub CLI/gh.exe`（账号 Zsx-china，WSL PATH 无 gh）；git 推送需 `git -c http.proxy= -c https.proxy=` 绕过失效的代理配置。
- tabbit 浏览器自动化：`/mnt/c/Users/34420/AppData/Local/Tabbit/LocalAgent/bin/tabbit-cli.exe`。
- 游戏站中性模板（保留 5 语言 i18n、GA、SEO 框架）位于私有仓库 <https://github.com/Zsx-china/game-site-template>，本地目录为 `/mnt/c/Users/34420/business/game-sites/game-site-template/`。复制新站时执行 `docs/NEW_SITE_WORKFLOW.md` 的“旧品牌快速门禁”：零命中跳过清理，发现残留才处理；上线前仍核对当前项目配置、占位值、图片和链接。生产验收优先运行 `npm run site:check`。
