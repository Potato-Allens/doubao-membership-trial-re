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