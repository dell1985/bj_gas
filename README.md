# 北京燃气信息查询

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Stable](https://img.shields.io/github/v/release/zhaoyibo/bj_gas)](https://github.com/zhaoyibo/bj_gas/releases/latest)

通过“北京燃气” APP 的接口，采集你的家庭用气信息。


# 特性
- 支持北京燃气智能物联网燃气表（简称 NB 表，见下图）的用气信息采集，目前仅支持单户号
- 数据为定时更新，更新间隔为 10 分钟
- 支持阶梯用气

![5371667306978_pic_hd](https://user-images.githubusercontent.com/11988080/199236469-4a841838-d3be-4552-bff7-4594bae3c30f.jpg)


# 使用之前
下载“北京燃气” APP，注册登录并绑定户号，然后点击“用气分析”，应该就可以看到该户号的用气信息。

使用任何网络抓包软件，如安卓手机的 Fiddler， 苹果手机的 Stream，进行抓包，可以只关注 zt.bjgas.com 域名下的请求。
抓包时在“北京燃气” APP 上进行操作，查看一下用气分析。看到 HTTP HEADER 中有内容为 “Authorization: Bearer XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX” 的内容，**将 “Authorization: Bearer ” 后的内容复制下来，这个字符串就是 token**，保存备用。

![http_sniff](https://user-images.githubusercontent.com/11988080/199236229-b1307db7-8823-46e5-a1e5-5b5e9ecb1a13.jpg)


# 安装
使用 HACS 以自定义存储库方式安装，或者从 [Latest release](https://github.com/zhaoyibo/bj_gas/releases/latest) 下载最新的 Release 版本，将其中的 `custom_components/bj_gas` 放到你 Home Assistant 的 `custom_components/bj_gas` 中。


# 配置
在 `configuration.yaml` 中，增加配置如下：

```yaml
bj_gas:
  token: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX # 此为 APP 中抓取的 token
  user_code: XXXXXXXXXXX                      # 此为燃气户号
```

重新启动 Home Assistant


## 传感器
包含的传感器

| entity_id 形式                          | 含义             | 属性                                                         | 备注              |
| --------------------------------------- | ---------------- | ------------------------------------------------------------ | ----------------- |
| sensor.XXXXXXXXXXX_balance              | 燃气费余额       | last_update - 网端数据更新时间                               |                   |
| sensor.XXXXXXXXXXX_current_level        | 当前用气阶梯     |                                                              |                   |
| sensor.XXXXXXXXXXX_current_level_remain | 当前阶梯剩余额度 |                                                              |                   |
| sensor.XXXXXXXXXXX_current_price        | 当前气价         |                                                              |                   |
| sensor.XXXXXXXXXXX_year_consume         | 本年度用气量     |                                                              |                   |
| sensor.XXXXXXXXXXX_month_reg_qty        | 本月用气量       |                                                              |                   |
| sensor.XXXXXXXXXXX_battery_voltage      | 气表电量         |                                                              |                   |
| sensor.XXXXXXXXXXX_mtr_status           | 阀门状态         |                                                              |                   |
| sensor.XXXXXXXXXXX_monthly_*            | 月度用气情况   | name - 月份<br/>state - 用气量<br />consume_bill - 该月燃气费 | \*取值为1-12<br/> |
| sensor.XXXXXXXXXX_daily_*               | 最近一周用气     | name - 日期<br/>state - 用气量                               | \*取值为1-7       |

其中 XXXXXXXXXXX 为北京燃气用户户号

# 示例
历史数据采用 [flex-table-card](https://github.com/custom-cards/flex-table-card)展示

```yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: sensor.XXXXXXXXXXX_balance
      - entity: sensor.XXXXXXXXXXX_month_reg_qty
      - entity: sensor.XXXXXXXXXXX_current_level
      - entity: sensor.XXXXXXXXXXX_current_level_remain
      - entity: sensor.XXXXXXXXXXX_current_price
      - entity: sensor.XXXXXXXXXXX_year_consume
      - entity: sensor.XXXXXXXXXXX_battery_voltage
      - entity: sensor.XXXXXXXXXXX_mtr_status
    title: 燃气信息
  - type: custom:flex-table-card
    title: 月度用气情况
    entities:
      include: sensor.XXXXXXXXXXX_monthly_*
    columns:
      - name: 月份
        data: name
      - name: 用气量
        data: state
      - name: 费用
        data: consume_bill
  - type: custom:flex-table-card
    title: 最近一周用气情况
    entities:
      include: sensor.XXXXXXXXXXX_daily_*
    columns:
      - name: 日期
        data: name
      - name: 用气量
        data: state
```

![screenshot_1](https://user-images.githubusercontent.com/11988080/199235178-e7318fdc-7f01-4377-8ce5-ad26d2558d86.jpg)


你也可以根据需要采用自己的展示形式

# 特别鸣谢
[瀚思彼岸论坛](https://bbs.hassbian.com/) 的 [@crazysiri](https://bbs.hassbian.com/thread-13355-1-1.html) 和 [@involute](https://bbs.hassbian.com/thread-13820-1-1.html)
