# PROTOCOL.md · 接口全集与请求 schema

> 所有端点均需在 query 上带 **AGW 公共参数**（见文末）。body 为 JSON。
> 标注 `[只读]` 的端点不产生写操作，可安全用于批量探测。

---

## 0. 公共参数（scope）

```
version_code=20800
language=zh
device_platform=web
doubao_device_platform=web
aid=497858              # 工作版（飞书）用 582478
real_aid=497858
pkg_type=release_version
pc_version=0.1.0
doubao_pc_version=0.1.0
region=CN
sys_region=CN
samantha_web=1
web_platform=desktop
use-olympus-account=1
```

请求头：`content-type: application/json`、`agw-js-conv: str`、`origin: https://www.doubao.com`、`referer: https://www.doubao.com/member/subscription`。

---

## 1. 交易（6）

### `POST /alice/commerce/sale/trade/init/` [只读]

```json
{"scene_key": "default_member_link", "default_sku_key": "doubao_personal_std",
 "purchase_channel": 2, "activity_id": "", "feature_key": "",
 "is_eligible_for_intro_offer": false}
```

可选 `scene_key`：`default_member_link`（默认）、`default_cloud_driver_link`、`profile`、`user_setting`。
返回：`activities`、`default_sku_key`、`entitlement_claim_status`、`has_history_paid_subscription`、`page_display_type`、`service_current_time`、`show_consumption`、`sku_list[]`、`sub_type`。

`sku_list[].purchase_card_list[]` 字段：`card_id`、`discount_amount`、`discount_total_price`、`trial_info`、`button_text`、`period_type`、`subscription_type`、`action`。

### `POST /alice/commerce/sale/trade/estimate/`

必填 `sku_key`、`card_id`、`total_price`。价格与服务端不符即 `611060114`，噪声大，**筛号不要用它**。

### `POST /alice/commerce/sale/trade/create/`

```json
{"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
 "estimated_pay_amount":"100","purchase_channel":2,"activity_id":"",
 "upgrade_mode":0,"is_eligible_for_intro_offer":true,"entry_method":"copy_link",
 "timezone":-480,"is_gift_deferred":false,"start_time":1793000000000,
 "trade_extra":"{\"selected_eligibility_id\":123}"}
```

返回 `data.payment_credential.pay_url`、`data.order_id`、`data.subscription_id`。

### `POST /alice/commerce/sale/trade/result/`

```json
{"order_id": "...", "subscription_id": "..."}
```

### `POST /alice/commerce/sale/trade/refresh_qrcode[/]`

```json
{"order_id": "...", "subscription_id": "..."}
```

### `POST /alice/commerce/sale/trade/beta/check/`

```json
{"activity_id": ""}
```

`""` → `{"state":1}`；不存在的 id → `611080000`。

---

## 2. 订阅（8）

| 端点 | body | 说明 |
|---|---|---|
| `subscription/status/` | `{"required_fields":[],"product_lines":[]}` | `has_subscribed` / `is_subscribing` |
| `subscription/overview/` | `{}` | 当前订阅、到期时间、权益组 |
| `subscription/list/` | `{"product_lines":[]}` | 历史订阅 |
| `subscription/detail/` | `{"subscription_id":"..."}` | 单条详情 |
| `subscription/cancel/` | `{"subscription_id":"..."}` | 取消自动续费（权益保留到 end_time） |
| `subscription/entry/config[/]` | `{}` | 会员入口配置（`show_pc_campaign`、跳转链接、`subs_status`） |
| `subscription/benefit_package/` | `{}` | 权益清单 |
| `subscription/quota/summary/` | `{}` | 额度汇总 |

`entry/config` 返回的跳转链接包含：`default_sku_key`、`doubao_user_id`、`enter_method`、`feature_key`、`period_type`、`scene_key`、`subs_purchase_id`（客户端生成的 UUID）、`subscription_type`。

---

## 3. 活动 / 营销（18）

| 端点 | body | 说明 |
|---|---|---|
| `campaign/trial/init/` | `{}` | 「领取 7 天试用」弹窗；无名额 → `710010702` |
| `campaign/page/query/` | `{}` | `{"page_status":3,"page_type":0}`；非 3 表示有活动 |
| `campaign/fixed_subscription/claim/` | `{"AgwCommonParam":{}}` | 领固定订阅；未命中 → `710010702` |
| `marketing/activity/detail/` | `{"activity_key":"...","channel":0}` | `status:2` = 已满/关闭 |
| `marketing/subscribe/init/` | `{"payload":"<json string>","request_id":"<uuid>"}` | 营销活动注册表；实测只回 `renewal_guidance_v1`（`hit:false`） |
| `marketing/resource/mget/` | `{"resource_keys":["..."],"is_eligible_for_intro_offer":true}` | 资源位；实测只回 `exit_retention` |
| `marketing/resource/mget/v2/` | 同上 | v2 |
| `marketing/card/list/` | `{"with_limit_status":true}` | 用户券卡；实测 `cards:[]` |
| `marketing/card/use/` | `{"card_key","card_id","use_request_id","trigger_scene"}` | 用卡 |
| `marketing/card/balance/` | `{"card_key","card_keys"}` | 仅 `pc_quota_reset_card` / `quota_reset_card` |
| `marketing/gift/detail/` | `{"gift_id":"..."}` | 礼包详情 |
| `marketing/gift/redeem/` | `{"gift_code":"..."}` | 兑换 |
| `marketing/cta/resolve_fixed_cta` | `{"scene_key","sku_key"}` | 仅 `profile` / `user_setting` 有返回 |
| `marketing/reward/renewal/status/` | `{"order_id","with_reward_details"}` | 续费奖励状态 |
| `marketing/resource/frequency/report/` | `{"frequency_report_extra":"..."}` | 频控上报 |
| `incentive/campaign/join/` | `{"campaign_id","campaign_group_code"}` | 报名；单传 campaign_id → `710010201` |
| `incentive/campaign/subscription/query/` | `{}` | 返回 `data:null` |
| `incentive/campaign/pc_new_user_page/detail/` | `{"campaign_id":"..."}` | `page_status:5` = 不在人群包 |

---

## 4. 退款（3）

```http
POST /alice/commerce/sale/debook/check/     {"order_id":"..."}
POST /alice/commerce/sale/debook/reasons/   {}
POST /alice/commerce/sale/debook/submit/    {"order_id","refund_reason","reason_detail"}
```

`check` 返回 `can_refund` / `refundable_amount` / `ineligible_reasons`。
退款原因：`1` 买错了 / `2` 忘记取消 / `3` 不满意 / `4` 重复扣费 / `101` 其他。
`submit` 返回 `{"accepted":true,"apply_id":"..."}`。

> 实测：退款成功后 `trial_stage` 从 `2` 变 `null`，**不回到 `1`**。资格不回收也不重置。

---

## 5. 学生权益（3）

| 端点 | body | 返回 |
|---|---|---|
| `student/verify_info/` | `{"use_douyin_open_id_cache":true}` | 认证状态 |
| `student/verify_url/` | `{}` | 认证跳转链接 |
| `student/entitlement/receive/` | `{}` | `611060180` 需绑抖音 / `611060181` 需学信网 |

---

## 6. 订单 / 发票（10）

`order/list/`、`order/detail/`、`invoice/apply/{detail,last/detail,list,submit}`、`invoice/can_invoice_orders/query/`、`invoice/{download,resend/email}`、`invoice/title/{create,delete,detail,list,update}`、`invoice/enterprise_info/query/`。

---

## 7. 权益 / 用量（3）

`intake/entitlement/query`（需完整参数，否则 `710010202`）、`entitlement/usage_detail/`、`usage/timeline/`。

---

## 8. UG 活动（13）

```http
POST /alice/ug/campaign/list/            {"campaign_group_code":"<str>","scene":"<STRING>","pinned_campaign_code":""}
POST /alice/ug/campaign/v3/detail/       {"campaign_group_code":"<str>"}
POST /alice/ug/campaign/item/reward/claim/ {"task_id","campaign_group_code","campaign_item_code"}
POST /alice/ug/campaign/landing/get      {"scene":"..."}
POST /alice/ug/campaign/landing/checkin  {"scene":"...","biz_params":{}}      # biz_params 必须是 map
POST /alice/ug/campaign/landing/report   {"event_type","biz_event_name","biz_params"}
POST /alice/ug/campaign/verify/          {"invite_code"}
POST /alice/ug/campaign/quota/records/   {}
POST /alice/ug/campaign/school/season/detail/ {"school_season_campaign_code"}
POST /alice/ug/campaign/student/verify_info/  {"use_douyin_open_id_cache":true}
POST /alice/ug/campaign/student/verify_url/   {}
POST /alice/ug/event/report              {"code","scene","campaign_item_code","message_id","params"}
```

### ⚠️ 参数类型陷阱

| 字段 | 正确类型 | 传错的报错 |
|---|---|---|
| `ug/campaign/list.scene` | string | `expected string, actual value: 0 (json.Number)` |
| `ug/campaign/landing/checkin.biz_params` | map | `expected map, actual value: (string)` |
| `marketing/subscribe/init.payload` | string（JSON 文本） | 传对象 → 参数错 |

`scene` 一旦传成数字，整轮扫描全部无效——这是本项目踩过最贵的坑。

---

## 9. 全量清单

67 个端点见 [`evidence/endpoint_catalog.json`](evidence/endpoint_catalog.json)。

---

## 10. 前端调用链（JS 层还原）

- `AGWTradeInit` → `trade/init`：只传 `scene_key/default_sku_key/purchase_channel/activity_id/feature_key/is_eligible_for_intro_offer`
- `AGWTradeCreate` → `trade/create`：字段与 §1 完全一致
- `estimated_pay_amount: String(e)` —— `e` 来自 init 返回的卡面，客户端只是"回传报价"
- `is_trial` **只出现在埋点事件里**（`+(card.trial_info.trial_stage === Trialing)`），不是下单参数
- 会员页路由 `/member/campaign` 懒加载 chunk `303/9511/5893/9880/6777/9184`
- PC 客户端 `local_webcontents` 2035 个 js/json/html 中，`campaign_group_code` 全部是变量引用，**0 个硬编码活动码**
---

## 11. PC 端配置下发（R460 · CDP 抓包还原）

> 来源：CDP `Network.requestWillBeSent`（端口 9224，`suppress_origin=True`）+ `Page.reload`。`config/pull` 只在首屏加载时发一次。

### 11.1 `user/config/pull`

```http
POST /alice/user/config/pull?version_code=20800&...&aid=582478&doubao_device_platform=desktop
Content-Type: application/json

{"objects":[114,111],"reason":2}
```

字段类型（**这是本轮最贵的坑**）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `objects` | `int[]` | 配置对象 id 数组；客户端分 4 包拉取，最大一包 62 个 id |
| `reason` | `int` | 拉取原因；`1` = 常规，`2` = 首屏 |

传字符串/对象 → 统一 `710010202`，会被误判为"端点不可用"。

抓到的四包：

```jsonc
{"objects":[114,111],"reason":2}
{"objects":[150],"reason":1}
{"objects":[300,301,302,379,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,376],"reason":1}
{"objects":[145,146],"reason":1}
```

### 11.2 `biz/activity/get_pop_window`

```http
POST /biz/activity/get_pop_window?aid=582478&doubao_device_platform=desktop
{"pc_os":"Windows","scene":8,"surface":3,"ug_campaign_info":{}}
```

- `scene` / `surface` 均为 **int**；类型错时静默返回空列表（不报参数错）。
- 全扫 `scene 0~20 × surface 0~5`（126 组）：非空 30 组，全部是推荐词类弹窗（`SugNewHotspot` / `PersonalityWcb` / `SugNewKeyword` / `SugCreationText*`），**不存在会员/试用类弹窗**。

### 11.3 `benefit_supply` 族（**不带 `/alice` 前缀**）

| 端点 | 返回 |
|---|---|
| `benefit_supply/ping` | `{}` |
| `benefit_supply/fission/get_user_is_new_flag` | `{is_new_user:false}` |
| `benefit_supply/fission/get_campaign_info` | `611100000 campaign not found` |
| `benefit_supply/credit/get_credit_num_optional_tasks` | 积分 0 + 2 个可选任务（每日登录 App / 每日登录豆包电脑端） |
| `benefit_supply/credit/user_activity` | `data:null` |
| `benefit_supply/credit/get_credit_tip` | `data:null` |

### 11.4 `intake/entitlement/*`

| 端点 | 要点 |
|---|---|
| `intake/entitlement/query` | `scene` 必须 **int**；`scene=1` 返回 `{"fingerprint":"927f9d76…"}`，其余 1~40 全 `710010202` |
| `intake/entitlement/changed_callback/` | `{callback_scene}` → `code 0, data {}`（内部回调，无外部副作用观测到） |
| `sale/approval/event_callback[/_ppe]` | `code 0`（需 challenge/token/type/ts/uuid/event） |
| `sale/pipo_pay/*_callback/` | **404**，不可达 |

### 11.5 一个必须记住的反例

`marketing/activity/detail` 对**任意** `activity_key`（`zzzzzzzz` / `test` / `q923dmsa` / `k7m3qx9p`）都返回 `{status:2}`。
⇒ `status:2` 是**兜底返回值**，不能解读为"活动已售罄/已关闭"。此前基于该字段的判断作废。
---

## 12. campaign / incentive / ug 族的真实入参（bundle 还原）

web bundle（41 MB）里这些 API 的封装函数如下，**参数名以本表为准**：

| 函数 | 路径 | 入参 |
|---|---|---|
| `GetCampaignList` | `/alice/ug/campaign/list/` | `{campaign_group_code, pinned_campaign_code, scene, AgwCommonParam}` |
| `GetCampaignV3Detail` | `/alice/ug/campaign/v3/detail/` | `{campaign_group_code, AgwCommonParam}` |
| `CreateCampaign` | `/alice/ug/campaign/create/` | `{campaign_code, scene, AgwCommonParam}` |
| `VerifyCampaign` | `/alice/ug/campaign/verify/` | `{invite_code, AgwCommonParam}` |
| `ClaimCampaignReward` | `/alice/ug/campaign/item/reward/claim/` | `{task...}` |
| `LandingEventReport` | `/alice/ug/campaign/landing/report` | `{event_type, biz_event_name, biz_params}` |
| `DailyCheckIn` | `/alice/ug/campaign/landing/checkin` | `{scene, biz_params}`(map) |
| `AGWJoinCampaign` | `/alice/commerce/incentive/campaign/join/` | `{campaign_id}` |
| `AGWGetPcNewUserCampaignPage` | `/alice/commerce/incentive/campaign/pc_new_user_page/detail/` | `{campaign_id}` |
| `AGWGetSubscriptionCampaign` | `/alice/commerce/incentive/campaign/subscription/query/` | 无 body |
| `AGWResolveFixedCTA` | `/alice/commerce/sale/marketing/cta/resolve_fixed_cta` | `{scene_key, sku_key}` |
| `AGWInitCampaignTrial` | `/alice/commerce/sale/campaign/trial/init/` | 无 body |
| `AGWQueryCampaignPage` | `/alice/commerce/sale/campaign/page/query/` | 无 body |
| `AGWMGetMarketingResources(V2)` | `/alice/commerce/marketing/resource/mget[/v2]/` | `{resource_keys: string[], is_eligible_for_intro_offer: bool}` |

### 12.1 死代码判定（重要）

用「路径字符串出现次数 vs 封装函数被调用次数」交叉验证，以下封装**只有定义、没有调用点**：

- `AGWInitCampaignTrial`（`campaign/trial/init`）
- `AGWJoinCampaign` / `AGWGetPcNewUserCampaignPage`
- `AGWQueryCampaignPage`（`page_status` 字段在 bundle 里 0 命中）

⇒ 这些接口即使打通也不会影响价格；不要再用它们推断"活动名额/售罄"。

### 12.2 新错误码

| code | 触发 | 含义 |
|---|---|---|
| `625002002` | `ug/campaign/create/` 空 body | 缺 `campaign_code`（端点存活） |
| `611070001` | `resolve_fixed_cta` 未知 scene | scene_key 未注册 |
| `611070003` | `resolve_fixed_cta` `default_member_link` | 该 scene 无固定 CTA |
| `611060101` | `trade/init` 未知 scene_key | scene 不合法 |
| `611060900` | `trade/init` scene/feature 组合不合法 | 参数组合错误 |
---

## 13. `samantha/fission/*` 与 `alice/auth/*`（R466–R467）

### 13.1 method 与真实入参

| 端点 | method | 入参 |
|---|---|---|
| `/samantha/fission/entrance` | **GET** | `{enter_from:int}` — `0=Desktop`, `1=Web` |
| `/samantha/fission/home_page` | **GET** | `{activity_id:int}` |
| `/samantha/fission/share_info` | **GET** | `{invited_code:string, activity_id:int}` |
| `/samantha/fission/draw` | POST | `{is_exchange:bool, activity_id:int}` |
| `/samantha/fission/approve` | POST | `{invited_code:string, activity_id:int}` |
| `/samantha/fission/report` | POST | `{report_type:int, activity_id:int}` |
| `/samantha/fission/check` | POST | `{data:string}` |
| `/samantha/fission/reward_info` | POST | `{order_id:string, activity_id:int}` |

> **类型陷阱**：`enter_from` / `activity_id` 都必须是 **int**。传字符串统一 `671010000 params invalid`。
> `activity_id` 传任意未存在的整数 → `710022001 record not found`。

### 13.2 `entrance` 响应 schema

```jsonc
{"code":0,"data":{
  "show_entrance": false,
  "show_popup": false,
  "entrance_banner": null,      // {guidance_type, activity_id, ...}
  "popup_data": null,
  "invite_info": null,
  "activity_info": null,
  "show_settings_entrance": false
}}
```

`entrance_banner.activity_id` 是 `home_page` 的合法输入来源；当前全池 212 号均为 `null`（无活动）。

### 13.3 `alice/auth` 族

```js
AuthGrant({order_id, src_platform, trigger})  → POST /alice/auth/grant
AuthVerify({order_id, src_platform, trigger}) → POST /alice/auth/verify
```

空 `order_id` → `ECOM_AUTH_INVALID_PARAM / 订单号不能为空`。语义是"按订单发/验权益"，不是"按资格发权益"。

### 13.4 实测摘要

- `entrance`：212 号 × {0,1} → 212/212 `code=0`，`show_*` 全 false。
- `home_page`：`0/1/2..10/100/1000/2026/999999/1e8/uid` → 全 `710022001`。
- `share_info`：假 `invited_code` → `710022001`。
- `check`：`{data:""}` → `710022001`。
- `draw/approve/report/reward_info`：空参 → `671010000`。