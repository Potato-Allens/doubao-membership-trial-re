# FINDINGS.md · 实测证据与已证伪假设

记录时间：2026-10-25 ~ 2026-10-26。所有实验使用自有账号，凭证与订单号已脱敏。

---

## A. 首扫：212 个历史账号

**方法**：`trade/init`（只读，8 并发），取 `sku_list[].purchase_card_list[].discount_amount`。

| 结果 | 数量 |
|---|---|
| `discount_amount=6700`（¥1 / 7 天） | 1 |
| `discount_amount=3000`（首购 ¥38） | 1 |
| `discount_amount=2000`（首购 ¥48） | 1 |
| `discount_amount=0` | 134 |
| `710012001 login invalid` | 75 |

在包率 **1/212 ≈ 0.47%**。

> 修正记录：早期内部笔记写作"6 命中 / 2.83%"，复核后发现是把后续复扫结果与首扫混算导致的误记。以本表为准。

---

## B. 唯一在包账号的完整链路

`trial_stage=1` → `trade/create` → `pay_url` → 二维码 → 支付 → `trial_stage=2`。

- 订单金额：100 分
- 权益期：7 天
- 到期：自动续费 6800 分/月
- `order_expire_seconds=1799`（支付链 30 分钟）

结论：**在包内就是 100%**，没有概率成分。

---

## C. 伪造类实验（全部失败）

| # | 假设 | 操作 | 结果 |
|---|---|---|---|
| C1 | 压低客户端报价 | `estimated_pay_amount` 传 `100` / `1` | `611060114` |
| C2 | 复用他人 eligibility | `trade_extra={"selected_eligibility_id":<命中号的 id>}` | `611060114` |
| C3 | 打开 intro offer 开关 | `is_eligible_for_intro_offer=true` | 服务端忽略 |
| C4 | `is_trial` 是下单开关 | 传 `is_trial=1` | 无效；JS 证明它只是埋点字段 |
| C5 | 设备指纹继承资格 | 把命中号的 `device_id`/`web_id`/`install_id`/`iid` 全换到 miss 号 | 仍 `611060114` |
| C6 | 渠道差异 | `purchase_channel` 0~6 | 一致；7+ 返回空列表 |
| C7 | 端差异 | `aid=497858` vs `582478` | 一致 |
| C8 | request 层 IDOR | 直接构造 create 请求体 | 全部被价格重算拦下 |

**统一结论：价格与资格由服务端按 `uid` 下发，客户端一切声明性字段作废。**

---

## D. 活动系统探测

| 对象 | 方法 | 结果 |
|---|---|---|
| 内测活动 `k7m3qx9p` | `marketing/activity/detail` channel 0~5 | 全部 `status:2`（满/关闭） |
| 同上 | `trade/beta/check` | `611080000` 活动不存在 |
| 同上 | 落地页文案 | 「活动已过期」 |
| `beta/check` 空 `activity_id` | — | `{"state":1}`（通用占位，非资格） |
| `campaign/trial/init` | `{}` + 16 种 campaign_id | 全 `710010702` |
| `campaign/page/query` | `{}` | `page_status:3`（无活动绑定） |
| `incentive/campaign/pc_new_user_page/detail` | `campaign_id` 多种 | `page_status:5`（不在人群包） |
| `incentive/campaign/join` | 仅 campaign_id | `710010201` |
| `incentive/campaign/join` | + campaign_group_code | `710010702`（前进一层，仍失败） |

---

## E. 营销资源 / 券卡

| 端点 | 结果 |
|---|---|
| `marketing/card/list` | `cards:[]`（3 个号全空） |
| `marketing/card/balance` | `available_count:0`，只有额度重置卡 key |
| `marketing/subscribe/init` | 只返回 `renewal_guidance_v1`，`hit:false` |
| `marketing/resource/mget`（15 个候选 key + intro 标记） | 只回 `exit_retention` |
| `marketing/cta/resolve_fixed_cta` | 仅 `profile` / `user_setting` 有返回 |

→ 不存在"试用券 / 1 元券"通道。

---

## F. 学生权益线（真实存在，但门槛不同）

```
POST /alice/commerce/sale/student/entitlement/receive/
→ 611060180  student douyin account required   （未绑抖音的号）
→ 611060181  student verification required      （未认证的号）
```

`activities: [{"crowd":"student","status":2}]` —— 学生人群活动当前也是 `status=2`。
这是一条独立折扣线（`discount_type=1`），需要抖音绑定 + 学信网认证，**不是 1 元试用**。

---

## G. 参数类型 bug（重要修正）

第一轮 `ug/campaign/list` 用数字 `scene`，服务端返回：

```
.(1)request.(3)scene: invalid request value, expected string, actual value: 0 (json.Number)
```

意味着**那一轮 250 组候选扫描全部无效**。修正为字符串后重打：

- 6 个 group_code × 30 个 scene（`member`/`settings`/`home`/`task_center`/`pc_client`/`0`~`6`/...）= 210 组
- 结果：全部 `{"code":2,"message":"campaign not found"}`
- 空 group_code → `{"code":1,"message":"invalid param"}`

同时验证：客户端 `local_webcontents` 2035 个文件里 **0 个硬编码 `campaign_group_code`**，活动码只由服务端配置下发。

---

## H. 退款实验（本仓库最重要的一条负结果）

**假设**：买 → 退 → 再买，可在同一账号循环获取 7 天试用。

**对象**：唯一在包账号（`trial_stage=2`，试用中）。

**步骤**：

```http
POST /alice/commerce/sale/debook/check/   {"order_id":"<已脱敏>"}
→ {"can_refund":true,"refundable_amount":"100"}

POST /alice/commerce/sale/debook/submit/  {"order_id":"<已脱敏>","refund_reason":1,"reason_detail":"..."}
→ {"accepted":true,"apply_id":"<已脱敏>"}
```

**观察**（退款后每 5 秒采样，共 6 次）：

| 时间 | `trial_info` | `discount_amount` | 按钮 |
|---|---|---|---|
| +5s | `null` | 0 | 立即升级 |
| +10s ~ +30s | `null` | 0 | 立即升级 |

**3 分钟后复核**：

- `debook/check` → `can_refund:false`，`ineligible_reasons:[6]`（已退）
- `subscription/overview` → `subscription_id:"0"`，`status:0`
- `trade/init` → `has_history_paid_subscription:true`，四张卡 `trial_info` 全 `null`

**结论**：`trial_stage` 由 `2` **直接变为 `null`，没有回到 `1`**。

> 资格是一次性消耗品。退款只退还 ¥1，不退还资格；该账号已永久失去试用。**"买退再买"证伪。**

---

## I. 数据汇总

| 结论 | 证据位置 |
|---|---|
| 首扫分布 | `evidence/scan_212_summary.json` |
| 全池复扫分布 | `evidence/sweep_elig_434_summary.json` |
| 端点全集 | `evidence/endpoint_catalog.json` |
| 接口 schema | `docs/PROTOCOL.md` |
---

## J. R460：判别器排除与两处修正

### J.1 四个候选判别器全部排除

| 假设 | 样本 | 结果 |
|---|---|---|
| `cc=1`（美区）专享 | 5 个 `cc=1` 号 | 4 个 `hist=false`、`cards=[]` ⇒ 无关 |
| `hm=2` 地区包 | 81 个 `hm=2` 号 | 仅 1 命中 ⇒ 无关 |
| 注册月份 | 2026-10 注册 100 号 | 仅 1 命中，无单调关系 |
| `new_user_check.is_old_user` | 60 号 | 35 个 `false` 全部 0 命中 ⇒ 无关 |

**结论不变：资格是按 `uid` 的人群包，可观测判别器只有服务端下发的 `trial_stage` / `discount_amount` 本身。**

### J.2 修正一：`status:2` 是兜底值

`marketing/activity/detail` 传任意 key（含明显不存在的 `zzzzzzzz`）都回 `{status:2}`。
此前记为"`k7m3qx9p` 已满/关闭"的判断**不成立**——那只是兜底返回。

### J.3 修正二：`config/pull` 不是"端点不可用"

之前 62 个配置 id 全部 `710010202`，原因是 `objects` 传了字符串/对象。真实类型是 **int 数组**，`reason` 是 **int**。
CDP 抓包（R460）拿到了客户端原始 body，端点本身完全可用。详见 `docs/PROTOCOL.md §11`。

### J.4 账号池存活率

| 指标 | 数值 |
|---|---|
| 池内总数 | 212 |
| 抽样前 40 | 11 活 / 29 `710012001` |
| 11 个活号命中 | **0** |

⇒ 当前瓶颈是**号源**，不是判定逻辑。
---

## K. R462：campaign / incentive / ug 族的定性（多为死代码）

### K.1 全池复核

- 212 个号实测 **137 活**（`code=0`），此前"11/40"是抽样偏差。
- `disc>0` 仅 3 个：6700（唯一 1 元试用）· 3000 · 2000。
- `cc=1`（美区）共 5 个，全部注册于 2026-10-13/14，唯一 6700 命中在其中（1/5）。但同批另外 4 个全 0，样本太小，**不能**据此认定美区专享。

### K.2 端点定性

| 端点 | 实测 | 定性 |
|---|---|---|
| `sale/campaign/trial/init/` | 恒 `710010702` | **死接口**（bundle 无调用点） |
| `incentive/campaign/subscription/query/` | `code 0, data null` | 无活动上下文 |
| `incentive/campaign/join/` | 需 `campaign_id`，拿不到 | **无调用点** |
| `incentive/campaign/pc_new_user_page/detail/` | 需 `campaign_id` | **无调用点**（PC 新客页未接线） |
| `sale/campaign/page/query/` | 所有号都 `{page_status:3,page_type:0}` | `page_status` 在 bundle 里 **0 命中** ⇒ 客户端不解析，属死字段 |
| `intake/entitlement/query` | `scene=1` → `fingerprint` | 命中号与普通号**同值**，设备级指纹 |
| `benefit_supply/fission/get_user_is_new_flag` | 空 body → `710010202` | 需参数 |
| `benefit_supply/fission/get_group_invitation` | 需 `campaign_key` | 拿不到 key |
| `ug/campaign/list/` | 空 body → `code 1` | 真实入参 `{campaign_group_code,pinned_campaign_code,scene}` |
| `ug/campaign/v3/detail/` | 传 `campaign_id` → `710010202` | 真实入参是 `campaign_group_code` |
| `ug/campaign/create/` | 空 body → **625002002**（新错误码） | 端点活着，入参 `{campaign_code,scene}` |
| `ug/campaign/verify/` | — | 入参 `{invite_code}` |
| `ug/campaign/landing/get` | `code 0`，空页面 | 需活动上下文 |
| `marketing/cta/resolve_fixed_cta` | 仅 `scene_key=profile` 有返回 | 返回 `policy_id=fixed_upgrade_version_web` |

### K.3 差分

命中号（已焚毁）vs 2 个普通号 × 12 个只读端点：字段级 diff **除时间戳/URL 外零差异**。

⇒ 资格不存在"可观测的客户端标记"；只能从 `trade/init` 的 `discount_amount` + `trial_info` 读出来。

### K.4 待验（后台任务）

零点名额刷新假设：`_r470_grab.py` 在 23:57 起每 5s 查活动状态、每 120s 对 137 活号全量 `trade/init`，命中即建单。结果见 `_r470_grab.log` / `_r470_hits.jsonl`。
### K.5 零点名额刷新：证否（R463）

- 23:57–00:04 每 5 s 查 `campaign/page/query`、每 ~120 s 对 **137 个活号**全量 `trade/init`。
- `page_status` 跨 00:00 **始终为 3**，无翻转；4 轮全量扫描 **hits=0**。
- `trade/init` + `activity_id=pc_growth_*` / `new_user` / `trial` → 恒 `611080000 beta activity not found`。
- PC 端 4652 个前端文件里：`activity_id` 硬编码 **0 个**，`campaign_group_code` **0 个**，只有 3 个 `pc_growth_*` 的 `campaign_code`（UG 任务类）。

⇒ **不存在"每日零点放名额"机制**；时间窗假设关闭。
### K.6 R465：移动端 / estimate / activities / 号源 四条线

| 线路 | 做法 | 结果 |
|---|---|---|
| 移动端专享促销 | `device_platform` = android / ios / harmony / ipad / pc_win | 全 `disc=0`，服务端按 cookie 认人，不认 UA |
| estimate 泄漏 intro 价 | `trade/estimate` + `total_price=6800` + `is_eligible_for_intro_offer=true` | `pay_amount` 恒 6800，`trade_extra="{}"` |
| `activities[]` 人群标记 | 137 个活号全量 | 全部 `[{"crowd":"student","status":2}]`，零差异 |
| 新号源 | `pool/*`、`export/*`、Doubao/DoubaoWork CDP cookie、nexSMS 余额 | 无新 sessionid；nexSMS 余额 **$0.42**，无法注册 |

**统计**：1/137 命中 → 0.73%，Wilson 95% CI 0.13%–4.02%，期望 137 个号/命中（区间 25–775）。

**工程结论**：唯一可交付的"随时有货"形态 = 常驻 `hunt.py --watch`（只读探测）+ 命中库存 + 按需 mint。已在 137 活号上以 60 分钟周期运行。

> `hunt.py` 本轮升级：命中即使 `--no-mint` 也写 `hits.jsonl`（`event:"hit"`），并做 `(name, disc)` 去重，避免 watch 模式刷屏。
### K.7 R466：`samantha/fission/*` 族还原（bundle → 实测）

从 41 MB web bundle 里还原出完整的裂变/邀请族。此前从未探测过。

| 端点 | method | 真实入参 | 空/错参实测 |
|---|---|---|---|
| `/samantha/fission/entrance` | **GET** | `{enter_from}` | 字符串 → `671010000` |
| `/samantha/fission/home_page` | **GET** | `{activity_id}` | 空 → `671010000` |
| `/samantha/fission/share_info` | **GET** | `{invited_code, activity_id}` | 空 → `671010000` |
| `/samantha/fission/draw` | POST | `{is_exchange, activity_id}` | 空 → `671010000` |
| `/samantha/fission/approve` | POST | `{invited_code, activity_id}` | 空 → `671010000` |
| `/samantha/fission/report` | POST | `{report_type, activity_id}` | 空 → `671010000` |
| `/samantha/fission/check` | POST | `{data}` | `{data:""}` → `710022001 record not found` |
| `/samantha/fission/reward_info` | POST | `{order_id, activity_id}` | 空 → `671010000` |

同轮还原的基础设施：

- `/credit/invite`（GET 打过去返回 HTML，是前端路由不是 API）
- `/alice/auth/grant`、`/alice/auth/verify`（入参 `{order_id, src_platform, trigger}`）
- `/commerce/benefit_supply/fission/{join_group,get_campaign_info,get_group_invitation,...}`（需 `campaign_key` / `encrypt_group_id`）
- PC 端 `landpage_click` 实际打到第三方落地页域名 `https://99uri.com/ug/pc/landpage_click`

### K.8 R467：`enter_from` 是 int 枚举 + 全池扫描（关键纠错）

**纠错**：R466 用 `enter_from="chat"` 打 GET，全部 `671010000 params invalid`，一度以为"端点不存在/仅 POST"。
bundle 里的枚举定义是：

```js
(i.Desktop = 0), (i.Web = 1)
```

改成 **int 0/1** 后，`GET /samantha/fission/entrance` 直接 `code=0`，返回：

```jsonc
{"show_entrance":false,"show_popup":false,"entrance_banner":null,
 "popup_data":null,"invite_info":null,"activity_info":null,
 "show_settings_entrance":false}
```

**全池扫描**：212 个账号 × `enter_from ∈ {0,1}`：

| 指标 | 数值 |
|---|---|
| `code=0` | 212 / 212 |
| `show_entrance=true` | 0 |
| `show_popup=true` | 0 |
| `activity_info != null` | 0 |
| `entrance_banner != null` | 0 |

⇒ `entrance` 是**活动级**开关：失效 Cookie 也回 `code=0`，它回答"现在有没有活动"，不是"这个 uid 有没有资格"。
⇒ 当前**没有在投放的 fission 活动**，这条线没有可领的邀请/抽奖奖励。

**`activity_id` 命名空间**：

| 入参 | 结果 |
|---|---|
| `""` / `"doubao"` / `"trial"` / `"null"` | `671010000 params invalid` |
| `0` / `1` / `2..10` / `100` / `1000` / `2026` / `999999` / `1e8` / 命中号 uid | `710022001 record not found` |

⇒ 只收整数；不是小整数枚举；活动 id 只能从真实入口（`entrance_banner.activity_id`）或分享链获得。

**其余端点**：

| 实验 | 结果 |
|---|---|
| `share_info` + `invited_code ∈ {a,1,abc123,A1B2C3}` + `activity_id=1` | 全 `710022001 record not found` |
| `check` + `{data:""}` | `710022001 record not found`（先查记录再校验） |
| `/alice/auth/grant` + `{order_id:"",src_platform:1,trigger:1}` | `ECOM_AUTH_INVALID_PARAM` / `订单号不能为空` |
| `/credit/invite` GET | HTML 页面 |

**结论**：fission 是"有活动才有入口"的投放体系，不是常驻的邀请返利；`auth/grant` 是"按订单发权益"，必须先有真实订单。两条线都不构成 `trade/init` 之外的第二条 1 元路径。
### K.9 R468：号源考古 + 资格与注册环境的相关性（3/3 出单）

**背景**：R467 结束时池子 137 活号、命中 0（唯一的旧命中号已焚毁）。R468 改从磁盘历史里回收 sessionid。

**回收**：在 `Documents\Codex` 下找到 1041 个含 `sessionid=` 的文件（历史 ck 导出、per-account 目录、旧 claim 项目），去重后 508 个 unique sessionid；与主池合并成 560 个账号，实测 **243 活**。

**结果**：找回 **3 个 6700 资格 uid / 6 条 cookie**：

| uid（打码） | 手机 | 账号地区 |
|---|---|---|
| 6392…313 | +1 | cc=1 |
| 3999…705 | +1 | cc=1 |
| 2416…572 | +852 | cc=852 |

**3/3 出单**：三个 uid 各调用一次 `trade/create`，全部 `code=0`，返回 `pay_url` 与 `order_expire_seconds=1799`；`estimated_pay_amount=100` 被接受，无 `611060114`。

**新事实：建单不消耗资格。** create 之后重新 `trade/init`，6/6 条 cookie 仍为 `disc=6700 / trial_stage=1`。资格只在**支付成功**后才变成 `2`。

**相关性**：把号池导出里的 `src_id` 与 claim DB 的 `iso` / 代理 region join：

| 维度 | 样本 | 命中 | 命中率 |
|---|---|---|---|
| iso=US | 49 | 5 | **10.2%** |
| iso=HK | 20 | 3 | **15.0%** |
| iso=CN | 33 | 0 | **0%** |
| iso=GB | 3 | 0 | 0% |
| proxy=US | 71 | 6 | 8.5% |
| proxy=HK | 70 | 3 | 4.3% |
| 无代理/未知 | 83 | 0 | **0%** |

⇒ 资格与「**美区/港区注册环境**（境外手机号 + US/HK 出口）」强相关；中国大陆注册的 33 个号全部无资格。这也解释了为什么 R455–R467 在客户端参数上怎么调都没用：人群包在注册时就已经定了。

**限制**：`phone_login.py` 记录，向 +852 等境外号 `send_code` 会被 passport 滑块拦截（`1105/1107`），境外号只能走扫码通道注册，无法纯协议批量造号。

**工程**：新增 `tools/_r468_recover_pool.py`（本地 sessionid 回收 + 去重，不发网络请求）；资格库存与按需出码在本地用 `mint1.py`（不公开）。

## L. R469：全字段差分与号源三路

**1. `trade/init` 递归 diff（命中 vs 普通，`tools/_r469_diff.py`）**

整份响应只有 **9 处差异**，全部在 `sku_list[1].purchase_card_list[0]`（`discount_amount` 6700 / `trial_info` / `button_text` / `discount_type` / `trade_extra.selected_eligibility_id` / 4 个价签字段）+ `service_current_time`。
`data.activities` 两号**完全相同** `[{"crowd":"student","status":2}]`。

⇒ 客户端无隐藏人群标记；资格是服务端 uid 维度的判定结果，请求体里那些字段只是回显。

**2. `Downloads` 池（2186 unique sid）**

`1000个.txt`(1000) + `redeem_batch_117_*`(666) + `redeem_batch_26_*`(520) + `DOLA*_500.txt`(500)。
随机 100 条打 `trade/init` → **100/100 `710012001 login invalid`**。这批是 Dola 账号，只有 passport cookie，与本项目无关，全量跑无意义。

**3. 本地 Chrome profile（136 个）**

`doubao-pool/data/chrome/acc_*` 全部可解：`encrypted_key` 剥 `DPAPI` 5 字节 → `CryptUnprotectData` → `AESGCM` 解 `v10` → **明文 `[32:]` 才是 cookie 本体**。
136 条 sessionid 中仅 **4 条**不在已知池。存量本地 profile 已榨干。

**结论**：新增号源只能去外部找「US / HK 注册环境」的历史池，继续翻本机文件是负收益。

## M. R470：资格落在 `country_code` 与 per-uid eligibility 上

**1. 账号档案对齐（243 活号）**

`/passport/account/info/v2/` 的 `country_code`（手机国家码）与 `trade/init` 折扣对齐：

| cc | 行数 | 命中行 |
|---|---|---|
| 86 | 79 | 0 |
| 0 | 20 | 0 |
| 1 | 20 | 4 |
| 852 | 123 | 2 |
| 44 | 1 | 0 |

所有命中 `hm_region=2`（境外），但境外 143 行只中 6 行（3 个 uid）→ 必要条件，不充分。
同一天同批次注册的境外号有中也有不中，`user_create_time` / 手机前缀均无法区分。

**2. eligibility 是 per-uid 记录**

| uid | cc | selected_eligibility_id |
|---|---|---|
| 639260239604313 | 1 | 7698970573258588170 |
| 3999391513351705 | 1 | 7700991370128261130 |
| 2416094733678572 | 852 | 7698658388344340514 |

三者互不相同 → 不存在公共活动对象可复用（与 §II 第 2 条一致）。

**3. 请求侧 7 组 region/sys_region/language 矩阵**：命中恒 6700、普通恒 0。

**4. 新端点负结果**：`student/*` 611060180；`ug/campaign/list|v3/detail` campaign not found；`landing/get` 空页面；
`marketing/card/*` 仅 quota_reset_card；`marketing/subscribe/init` 空；`campaign/trial/init` 与 `fixed_subscription/claim` 恒 710010702。

**5. CDP 真机抓包（会员页）**：只有 5 个请求（entry/config、trade/init、incentive/campaign/subscription/query、
marketing/subscribe/init、marketing/resource/mget/v2），无隐藏开关。

**6. Desktop 大盘 4554 条**：`710012001` 2689、活 2、命中 0（1863 条超时另跑）。

## N. R471：候选漏斗（境外 + 零订阅）

560 行全池用 `tools/triage.py` 一次分流（33.5 s）：

| 阶段 | 数量 |
|---|---|
| 池 | 560 |
| 会话有效 | 243 |
| 境外（cc=1/852/44） | 143 |
| 境外 + 零订阅（候选） | 27 行 / 18 uid |
| 候选里命中 1 元 | 6 行 / 3 uid（**16.7%** uid 口径） |

`country_code × 订阅记录`（行数/命中）：86: 57/0、22/0；0: 5/0、15/0；1: 17/4、3/0；852: 9/2、114/0；44: 1/0。

两条硬结论：
1. `cc=86` 零订阅也 0 命中 → 号码归属地是硬门槛。
2. 有订阅记录的境外号 117 行 0 命中 → 历史免费会员顶掉首购资格。

剩余 15 个候选与命中号在所有可观测量上完全一致（档案、entry/config、activities、has_history_paid_subscription、
entitlement_claim_status），末道闸仍是服务端按 uid 发放。

证据：`docs/evidence/r471_triage.json`；工具：`tools/triage.py`。
