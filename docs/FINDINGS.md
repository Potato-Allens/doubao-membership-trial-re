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