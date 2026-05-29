# HCM 出差申请数据接口文档

## 1. 文档修改记录

| 修订版本 | 修订人 | 修订时间 | 修订内容 |
| :--- | :--- | :--- | :--- |
| V1.0 | Rohn | 2025-10-27 | 初始版本 |

---

## 2. 身份验证与授权 (OAuth 2.0)

HCM 接口服务采用 OAuth 2.0 密码模式（`password`）进行身份验证和授权。在调用其他数据接口前，必须先调用此接口获取票据 `access_token`。

### 2.1 获取 Token 接口

* **请求地址**: `https://hcm.tianbang.com/oauth/token?tid=00001`
* **请求方式**: `POST`
* **Content-Type**: `application/x-www-form-urlencoded`

#### 请求参数 (Body)

| 参数名称 | 类型 | 是否必填 | 默认/示例值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `grant_type` | String | 是 | `password` | 授权验证模式，固定为 `password` |
| `username` | String | 是 | `CRM` | 用户名 |
| `password` | String | 是 | `!TianBang@1234%^&*` | 密码 |
| `client_id` | String | 是 | `TianBang` | 客户端 ID |
| `client_secret` | String | 是 | `95DBD7D3894047638C1A0578AF433A3F3f65` | 客户端密钥 |

> [!IMPORTANT]
> 以上所有参数均不能为空。

#### 参数传递形式
支持以下三种传递方式：
1. **Form 表单传递**: 在请求的 body 中以 form 表单形式（`application/x-www-form-urlencoded`）传递。
2. **纯文本 Raw 拼接**: 以纯文本的形式将参数放入请求 body 中，例如：
   ```http
   username=abc&password=pwd&client_id=OA&client_secret=343uu34324fefapesct44et5fdasa&grant_type=password
   ```
3. **HTTP Header 传递**: 在 HTTP Header 中以参数形式直接传递。

#### 网关/EAI 适配器配置参考
若通过 WebApi 适配器/网关进行转发配置，可参考以下配置 JSON：
```json
{
  "name": "获取token",
  "type": "WebApi",
  "config": {
    "request": {
      "url": "http://***/oauth/token?tid=00001",
      "method": "POST",
      "contentType": "application/x-www-form-urlencoded",
      "body": {
        "grant_type": "password",
        "username": "OA",
        "password": "11111a",
        "client_id": "00001",
        "client_secret": "f6b6cf315eb390e5ee7ebe4d2"
      }
    }
  }
}
```

---

### 2.2 响应格式与说明

无论是成功还是失败，接口响应都以 `JSON` 格式返回。

* **执行成功**: HTTP 响应状态码为 `200`，且返回的数据中包含 `access_token` 等信息。
* **执行失败**: 响应状态码为非 `200`，错误原因会记录在返回 JSON 的 `error` 属性中。

#### 错误响应示例 (HTTP 4xx / 5xx)
```json
{
  "error": "invalid_client"
}
```

#### 成功响应示例 (HTTP 200)
```json
{
  "access_token": "Xo79vXnAd0TYDMcm7RLF4Pf1MJKaJFVZAva6CY13uQL6_x48GH1DnSKUd7Sj9xmcSGlS...",
  "token_type": "bearer",
  "expires_in": 863999,
  "refresh_token": "c289c4956da64330a735a00a021a244f57ed080d175e4e4389d339e290bc1dd9"
}
```

#### 成功响应参数说明

| 参数名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| `access_token` | String | 后续调用 WebAPI 业务接口时使用的访问凭证（票据） |
| `token_type` | String | 凭证类型，一般固定为 `bearer` |
| `expires_in` | Integer | 凭证的有效时长，单位为秒 |
| `refresh_token` | String | 刷新凭证，在当前 token 过期后用于重新换取新 token 时的凭证 |

---

### 2.3 使用 access_token 进行接口鉴权

后续调用业务 WebAPI 时，请求必须携带有效的 `access_token`，否则服务器将返回 `403` 权限不足错误。有以下两种携带方式：

#### 方式一：URL 请求参数中携带
在业务接口的请求 URL 后拼接 `access_token` 字段：
```http
https://hcm.tianbang.com/api/services/DI/DIExport/DataList?access_token={access_token_value}
```
> [!WARNING]
> 由于 `access_token` 字符串中可能包含非 URL 安全的字符，在将其作为 Query 参数进行拼接前，必须先进行 **URL 转义（URL Encode）**。

#### 方式二：Bearer Token 授权头携带 (推荐)
在请求的 HTTP Header 中添加 `Authorization` 字段，格式如下：
```http
Authorization: Bearer {access_token_value}
```
> [!IMPORTANT]
> 请注意 Header 参数值的格式，`Bearer` 为固定的关键字，其与 token 值之间**必须用空格隔开**。

---

## 3. 业务数据接收接口

外部系统通过 HCM 提供的 WebAPI 获取或推送数据。

### 3.1 出差申请查询接口

* **请求地址**: `https://hcm.tianbang.com/api/services/DI/DIExport/DataList`
* **请求方式**: `POST`
* **Content-Type**: `application/json`

#### 请求参数 (Body)

| 参数名称 | 类型 | 是否必填 | 示例值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `settingCode` | String | 是 | `"DI.StaffBusiness"` | 配置的“对象列表页”的代码。不能为空，不同的数据类型需提供对应的 Code。 |
| `filter` | Object | 否 | 见 JSON 示例 | 过滤条件对象。如果不需要筛选，该项可以为空或不提供。 |
| `filter.beginDate` | String | 否 | `"2025-07-01"` | 查询时间轴的起始日期（格式：`YYYY-MM-DD`）。不传时默认默认为当前日期。 |
| `filter.endDate` | String | 否 | `"2023-10-27"` | 查询时间轴的结束日期（格式：`YYYY-MM-DD`）。不传时默认默认为 `9999-12-31`。 |
| `filter.Filters` | Array | 否 | 见 JSON 示例 | 精细化筛选条件列表，支持对特定字段（如工号、组织代码）使用模糊或精确查询。 |
| `skipCount` | Integer | 否 | `0` | 分页查询时跳过的记录条数。 |
| `maxResultCount` | Integer | 否 | `-1` | 单次查询最多返回的记录数。如果设置为 `-1`，则表示不分页，返回全部记录。 |

#### 请求 JSON 示例
```json
{
  "settingCode": "DI.StaffBusiness",
  "filter": {
    "beginDate": "2025-07-01",
    "endDate": "2023-10-27",
    "Filters": [
      {
        "field": "E.HRMB0001..ObjectID.ID",
        "operation": "like",
        "values": [
          "02013347"
        ]
      },
      {
        "field": "O.TreePath..OrgTreePath",
        "operation": "like",
        "values": [
          "00000002"
        ]
      }
    ]
  },
  "skipCount": 0,
  "maxResultCount": -1
}
```

---

## 4. 接口返回数据格式

### 4.1 统一返回数据结构

接口成功调用后返回的统一结构如下。

#### 成功返回 JSON 示例
```json
{
  "status": 200,
  "error": null,
  "data": {
    "totalCount": 1,
    "items": [
      {
        "PERNR": "02013347",
        "BeginDate": "2025-07-01",
        "Enddate": "2023-10-27",
        "BeginTime": "09:00",
        "EndTime": "18:00",
        "Hours": 8.0,
        "Days": 1.0,
        "FullDay": true,
        "Destination": "南京",
        "OtherDestination": ""
      }
    ]
  }
}
```

#### 返回结果核心字段说明

| 字段名称 | 类型 | 说明 |
| :--- | :--- | :--- |
| `status` | Integer | 接口执行状态。等于 `200` 时表示执行成功；非 `200` 表示执行失败。 |
| `error` | String | 当 `status` 不等于 `200` 时返回的错误原因描述；成功时为 `null`。 |
| `data` | Object | 成功时返回的业务数据载荷。 |
| `data.totalCount` | Integer | 符合筛选条件的数据总数（分页前的总数）。 |
| `data.items` | Array | 实际返回的数据列表，包含出差记录明细。 |

#### Items (出差记录) 明细字段说明
*注意：出差记录明细字段名称与 SAP 到 HCM 系统的接口字段名完全一致。*

| 字段名称 | 类型 | 说明 | 示例值 |
| :--- | :--- | :--- | :--- |
| `PERNR` | String | 员工工号 | `"02013347"` |
| `BeginDate` | String | 出差开始日期 | `"2025-07-01"` |
| `Enddate` | String | 出差结束日期 | `"2023-10-27"` |
| `BeginTime` | String | 出差开始时间 | `"09:00"` |
| `EndTime` | String | 出差结束时间 | `"18:00"` |
| `Hours` | Float | 累计小时数 | `8.0` |
| `Days` | Float | 累计天数 | `1.0` |
| `FullDay` | Boolean | 是否全天出差标记 | `true` |
| `Destination` | String | 目的地地点名称 | `"南京"` |
| `OtherDestination` | String | 其它自定义目的地描述 | `""` |
