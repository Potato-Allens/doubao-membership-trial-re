# -*- coding: utf-8 -*-
p="README.md"; t=open(p,encoding="utf-8").read()
add = r'''

## 5. 订阅状态 / 取消自动续费（2026-10-26 新增）

### 5.1 命令
```powershell
# 只读：看订阅状态（不含任何写操作）
python doubao_yuan.py status --pool pool/trial_batch_212.json --uid <uid>
python doubao_yuan.py status --ck "<cookie string>"

# 取消自动续费：默认 dry-run，只打印将要发送的请求
python doubao_yuan.py cancel --pool pool/trial_batch_212.json --uid <uid>
# 真正调用（会打印 before/after，并判断 end_time 是否被改）
python doubao_yuan.py cancel --pool pool/trial_batch_212.json --uid <uid> --yes
# 或直接指定订阅 id
python doubao_yuan.py cancel --ck "<ck>" --sid <subscription_id> --yes
```

### 5.2 接口契约（从 9880.95b5c7ce.js 逆向得到，已实测）
| 方法 | 路径 | body | 说明 |
|---|---|---|---|
| POST | `/alice/commerce/sale/subscription/cancel/` | `{"subscription_id": "<id>"}` | 取消订阅/自动续费 |
| POST | `/alice/commerce/sale/subscription/overview/` | `{}` 或 `{"product_line":"membership"}` | 订阅详情（end_time / trial_info / agreement_*） |
| POST | `/alice/commerce/sale/subscription/status/` | `{}` | `{has_subscribed, is_subscribing}` |
| POST | `/alice/commerce/sale/order/list/` | `{}` | `data.items[]`（order_id / actual_pay_amount / paid_at_ms） |
| POST | `/alice/commerce/sale/subscription/entry/config/` | `{}` | 设置页入口 URL、`subs_status` |
| POST | `/alice/commerce/sale/trade/result/` | `{order_id, subscription_id}` | 支付结果查询 |
| POST | `/alice/commerce/sale/trade/refresh_qrcode` | `{order_id, subscription_id}` | 刷新二维码 |

JS 里的原始封装（可直接对照）：
```js
t.AGWCancelSubscription = function(e,t){var r=this.genBaseURL("/alice/commerce/sale/subscription/cancel/"),
  a={subscription_id:e.subscription_id};return this.request({url:r,method:"POST",data:a},t)}
```

### 5.3 零副作用探针
`subscription/cancel/` 传假 id（`"0"` / 空 body）→ **HTTP 200 + code 710010702 "system error"**。
说明端点存在且按 `subscription_id` 校验；该错误码可作为"接口可达"的判断依据。

### 5.4 ⚠️ 语义未验证（重要）
- **没有**验证过"调用 cancel 后剩余的已付天数是否保留"。
- 实测：支付宝侧关闭免密代扣后，豆包服务端 `agreement_status` 仍为 **4**、`is_subscribing` 仍 **true**、
  `next_deduct_time` 未变 → 两端状态不同步，**豆包侧并不知道你在支付宝关了协议**。
- 建议顺序：先在支付宝关代扣（阻断扣款，7 天不受影响）→ 到期前一天再调 `cancel --yes`，
  用 `--yes` 输出的 before/after 判断 `end_time` 是否被砍。

### 5.5 会员状态落到账号的四路验证（2026-10-26 实测）
1. `overview.current_subscription`：`start_time` / `end_time` 差值 **604,800,000ms = 7.000 天整**，
   `trial_info.is_trialing=true`、`trial_price=100`、`agreement_price=6800`
2. `order/list`：`actual_pay_amount=100`、`paid_at_ms`、`status_view=1`
3. Web UI `https://www.doubao.com/member/subscription` **必须先点「标准」tab**，才显示「到期时间 11月2日」
   （默认落在「加强」tab，只显示 ¥200 升级价，容易误判"没买成功"）
4. 计费引擎：¥68 试算返回的 `start_time` = 当前 `end_time` ⇒ 新购在当前到期日后顺延
'''
if "## 5. 订阅状态" not in t:
    t = t.rstrip() + add
open(p,"w",encoding="utf-8").write(t)
print("README",len(t))
