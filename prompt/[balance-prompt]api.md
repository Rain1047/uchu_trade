[balance-prompt] api

http://localhost:8000/api/balance/list_balance

```
curl -X 'GET' \
  'http://localhost:8000/api/balance/list_balance' \
  -H 'accept: application/json'
```
返回结果：
```json
{
  "success": true,
  "data": [
    {
      "id": 103,
      "ccy": "SOL",
      "avail_bal": "83.448859932",
      "avail_eq": "83.448859932",
      "eq": "83.448859932",
      "cash_bal": "83.448859932",
      "u_time": "1734803156038",
      "dis_eq": "15320.960336935404",
      "eq_usd": "16127.32667045832",
      "notional_lever": "0",
      "ord_frozen": "0",
      "spot_iso_bal": "0",
      "upl": "0",
      "spot_bal": "35.16247923",
      "open_avg_px": "197.97972959770405",
      "acc_avg_px": "198.17221279267505",
      "spot_upl": "-165.95739395048525",
      "spot_upl_ratio": "-0.023839458753149",
      "total_pnl": "-172.72558029577704",
      "total_pnl_ratio": "-0.0247875962197291",
      "limit_order_switch": "false",
      "stop_loss_switch": "false"
    },
    {
      "id": 104,
      "ccy": "ETH",
      "avail_bal": "4.532833045820142",
      "avail_eq": "4.532833045820142",
      "eq": "4.532833045820142",
      "cash_bal": "4.532833045820142",
      "u_time": "1734863522320",
      "dis_eq": "15022.37441141207",
      "eq_usd": "15328.953481032722",
      "notional_lever": "0",
      "ord_frozen": "0",
      "spot_iso_bal": "0",
      "upl": "0",
      "spot_bal": "1.2086706458",
      "open_avg_px": "2771.744055533041",
      "acc_avg_px": "2774.321802029921",
      "spot_upl": "737.3083655471768",
      "spot_upl_ratio": "0.2200837928196244",
      "total_pnl": "734.192719024084",
      "total_pnl_ratio": "0.2189501583866831",
      "limit_order_switch": "true",
      "stop_loss_switch": "false"
    },
    {
      "id": 105,
      "ccy": "USDT",
      "avail_bal": "2027.5764672307141",
      "avail_eq": "2027.5764672307141",
      "eq": "6027.573262230714",
      "cash_bal": "6027.573262230714",
      "u_time": "1734984505276",
      "dis_eq": "6021.18403457275",
      "eq_usd": "6021.18403457275",
      "notional_lever": "0",
      "ord_frozen": "3999.996795",
      "spot_iso_bal": "0",
      "upl": "0",
      "spot_bal": "",
      "open_avg_px": "",
      "acc_avg_px": "",
      "spot_upl": "",
      "spot_upl_ratio": "",
      "total_pnl": "",
      "total_pnl_ratio": "",
      "limit_order_switch": "false",
      "stop_loss_switch": "true"
    },
    {
      "id": 106,
      "ccy": "BTC",
      "avail_bal": "0.0868346849529267",
      "avail_eq": "0.0868346849529267",
      "eq": "0.0868346849529267",
      "cash_bal": "0.0868346849529267",
      "u_time": "1734984505276",
      "dis_eq": "8075.26325264719",
      "eq_usd": "8240.064543517541",
      "notional_lever": "0",
      "ord_frozen": "0",
      "spot_iso_bal": "0",
      "upl": "0",
      "spot_bal": "0.08683468169",
      "open_avg_px": "84589.45966631845",
      "acc_avg_px": "84670.21811983503",
      "spot_upl": "894.7654294324966",
      "spot_upl_ratio": "0.1218147080538033",
      "total_pnl": "887.7527948276074",
      "total_pnl_ratio": "0.1207447211922322",
      "limit_order_switch": "false",
      "stop_loss_switch": "false"
    },
    {
      "id": 107,
      "ccy": "DOGE",
      "avail_bal": "12646.989867429",
      "avail_eq": "12646.989867429",
      "eq": "12646.989867429",
      "cash_bal": "12646.989867429",
      "u_time": "1734803181520",
      "dis_eq": "3878.085619938296",
      "eq_usd": "4082.195389408733",
      "notional_lever": "0",
      "ord_frozen": "0",
      "spot_iso_bal": "0",
      "upl": "0",
      "spot_bal": "12646.989867429",
      "open_avg_px": "0.3687460812630611",
      "acc_avg_px": "0.5214103838584913",
      "spot_upl": "-581.3325639793513",
      "spot_upl_ratio": "-0.1246551044166057",
      "total_pnl": "-2512.076452021871",
      "total_pnl_ratio": "-0.380948270321365",
      "limit_order_switch": "false",
      "stop_loss_switch": "false"
    }
  ]
}
```

http://127.0.0.1:8000/api/balance/update_account_balance_config_switch

```
curl -X 'POST' \
  'http://localhost:8000/api/balance/update_account_balance_config_switch' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ccy": "ETH",
  "type": "limit_order",
  "switch": "true"
}'
```

返回结果
```json
{
  "success": true,
  "data": true
}
```


http://localhost:8000/api/balance/list_configs/ETH/{type}?type_=stop_loss

```
curl -X 'GET' \
  'http://localhost:8000/api/balance/list_configs/ETH/{type}?type_=stop_loss' \
  -H 'accept: application/json'
```

返回结果
```json
{
  "success": true,
  "data": [
    {
      "id": 4,
      "ccy": "ETH",
      "type": "stop_loss",
      "indicator": "USDT",
      "indicator_val": null,
      "target_price": 2000,
      "percentage": null,
      "amount": 1000,
      "switch": "0",
      "exec_nums": 1,
      "is_del": "0"
    },
    {
      "id": 5,
      "ccy": "ETH",
      "type": "stop_loss",
      "indicator": "EMA",
      "indicator_val": "200",
      "target_price": null,
      "percentage": 30,
      "amount": null,
      "switch": "0",
      "exec_nums": 1,
      "is_del": "0"
    }
  ]
}
```