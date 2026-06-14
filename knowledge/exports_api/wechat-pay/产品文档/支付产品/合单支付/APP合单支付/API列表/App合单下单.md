# App合单下单

# App合单下单

路径：产品文档/支付产品/合单支付/APP合单支付/API列表/App合单下单

用户在商户APP端选择微信支付后，商户需调用该接口在微信支付下单，生成用于[调起支付](https://pay.weixin.qq.com/doc/v3/merchant/4012266043)的预支付交易会话标识(prepay_id)。

| 注意普通商户模式只支持2-10笔订单进行合单支付。 |  | 注意普通商户模式只支持2-10笔订单进行合单支付。 |
| --- | --- | --- |
|  | 注意普通商户模式只支持2-10笔订单进行合单支付。 |  |

## 接口说明

支持商户：【普通商户】

请求方式：【POST】`/v3/combine-transactions/app`

请求域名：【主域名】https://api.mch.weixin.qq.com 使用该域名将访问就近的接入点

　　　　　【备域名】https://api2.mch.weixin.qq.com 使用该域名将访问异地的接入点 ，指引[点击查看](https://pay.weixin.qq.com/doc/v3/merchant/4012075113)

## 请求参数
    
    折叠全部参数

Header   HTTP头参数

 Authorization 　必填　string

请参考[签名认证](https://pay.weixin.qq.com/doc/v3/merchant/4012365342#%E8%AF%B7%E6%B1%82%E6%8E%A5%E5%8F%A3%E5%90%8E%E7%AB%AF%E7%AD%BE%E5%90%8D)生成认证信息

 Accept 　必填　string

请设置为`application/json`

 Content-Type 　必填　string

请设置为`application/json`

body  包体参数

 combine_appid 　必填   string(32)

【合单商户应用ID】合单发起方的APPID。APPID是微信[开放平台](https://open.weixin.qq.com/)(移动应用)或微信[公众平台](https://mp.weixin.qq.com/)(小程序、公众号)为开发者的应用程序提供的唯一标识。此处请填写移动应用类型的APPID，并确保该`combine_appid`与`combine_mchid`有绑定关系。详见：[商户号绑定APPID账号操作指南](https://pay.weixin.qq.com/doc/v3/merchant/4013426141#2%E3%80%81%E5%95%86%E6%88%B7%E5%8F%B7%E7%BB%91%E5%AE%9AAPPID%E8%B4%A6%E5%8F%B7%E6%93%8D%E4%BD%9C%E6%8C%87%E5%8D%97)。

 combine_out_trade_no 　必填   string(32)

【合单商户订单号】合单发起方商户系统内部订单号，要求6~32个字符内，只能是数字、大小写字母_-|*，且在同一个合单商户号下唯一。

 combine_mchid 　必填   string(32)

【合单商户号】 合单发起方的商户号，是由微信支付系统生成并分配给每个商户的唯一标识符，商户号获取方式请参考[普通商户模式开发必要参数说明](https://pay.weixin.qq.com/doc/v3/merchant/4013070756)。

 scene_info 　选填   object

【场景信息】场景信息

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | device_id 　选填   string(16)【商户端设备号】 终端设备号(门店号或收银设备ID) payer_client_ip 　必填   string(45)【用户终端IP】用户端实际IP，支持IPv4和IPv6两种格式的IP地址。IP获取请参考[获取用户IP指引](https://pay.weixin.qq.com/doc/v2/merchant/4011937139) |

 sub_orders 　必填   array[ReqSubOrderCompatible]

【商品单信息】 商品单列表，一笔合单支付订单可支持2-10笔商品单交易。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | mchid 　必填   string(32)【商品单商户号】商品单参与方的商户号，必须与`combine_appid`有绑定关系。详见：[商户号绑定APPID账号操作指南](https://pay.weixin.qq.com/doc/v3/merchant/4013426141#2%E3%80%81%E5%95%86%E6%88%B7%E5%8F%B7%E7%BB%91%E5%AE%9AAPPID%E8%B4%A6%E5%8F%B7%E6%93%8D%E4%BD%9C%E6%8C%87%E5%8D%97)。 attach 　必填   string(128)【商户数据包】商户在创建订单时可传入自定义数据包，该数据对用户不可见，用于存储订单相关的商户自定义信息，其总长度限制在128字符以内。支付成功后[查询合单订单API](https://pay.weixin.qq.com/doc/v3/merchant/4012557006)和[合单订单支付成功回调通知](https://pay.weixin.qq.com/doc/v3/merchant/4012158598)均会将此字段返回给商户，并且该字段还会体现在交易账单。 amount 　必填   object【商品单金额信息】 商品单收款金额信息。![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg)属性total_amount 　必填   integer【标价金额】 商品单的金额，整型，单位为分。商品单商户号为境外商户时，标价金额必需超过商户结算币种的最小单位金额，例如商户结算币种为美元，则标价金额必须大于1美分。 currency 　必填   string(8)【标价币种】标价金额的币种，符合ISO 4217标准的三位字母代码，境内商户固定传入：CNY，代表人民币。 out_trade_no 　必填   string(32)【商品单商户订单号】 合单发起方商户系统内部订单号，要求6~32个字符内，只能是数字、大小写字母_-\|*，且在同一个合单商户号下唯一。 description 　必填   string(127)【商品描述】商品信息描述，用户微信账单的商品字段中可见(可参考[APP合单支付模式介绍](https://pay.weixin.qq.com/doc/v3/merchant/4012077215#2%E3%80%81APP%E5%90%88%E5%8D%95%E6%94%AF%E4%BB%98%E6%A8%A1%E5%BC%8F%E4%BB%8B%E7%BB%8D)-6、账单示意图)，商户需传递能真实代表商品信息的描述，不能超过127个字符。 settle_info 　选填   object【结算信息】 结算信息![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg)属性profit_sharing 　选填   boolean【分账标识】订单的分账标识在下单时设置，传入`true`表示在订单支付成功后可进行分账操作。以下是详细说明：需要分账（传入`true`）：订单收款成功后，资金将被冻结并转入基本账户的不可用余额。商户可通过[请求分账API](https://pay.weixin.qq.com/doc/v3/merchant/4012524936)，将收款资金分配给其他商户或用户。完成分账操作后，可通过接口[解冻剩余资金](https://pay.weixin.qq.com/doc/v3/merchant/4012526374)，或在支付成功30天后自动解冻。不需要分账（传入`false`或不传，默认为`false`）：订单收款成功后，资金不会被冻结，而是直接转入基本账户的可用余额。 goods_tag 　选填   string(32)【订单优惠标记】[代金券](https://pay.weixin.qq.com/doc/v3/merchant/4012084079)在创建时可以配置多个订单优惠标记，标记的内容由创券商户自定义设置。详细参考：[创建代金券批次API](https://pay.weixin.qq.com/doc/v3/merchant/4012534633)。如果代金券有配置订单优惠标记，则必须在该参数传任意一个配置的订单优惠标记才能使用券。如果代金券没有配置订单优惠标记，则可以不传该参数。示例：如有两个活动，活动A设置了两个优惠标记：WXG1、WXG2；活动B设置了两个优惠标记：WXG1、WXG3；下单时优惠标记传WXG2，则订单参与活动A的优惠；下单时优惠标记传WXG3，则订单参与活动B的优惠；下单时优惠标记传共同的WXG1，则订单参与活动A、B两个活动的优惠； | ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |  | total_amount 　必填   integer【标价金额】 商品单的金额，整型，单位为分。商品单商户号为境外商户时，标价金额必需超过商户结算币种的最小单位金额，例如商户结算币种为美元，则标价金额必须大于1美分。 currency 　必填   string(8)【标价币种】标价金额的币种，符合ISO 4217标准的三位字母代码，境内商户固定传入：CNY，代表人民币。 | ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |  | profit_sharing 　选填   boolean【分账标识】订单的分账标识在下单时设置，传入`true`表示在订单支付成功后可进行分账操作。以下是详细说明：需要分账（传入`true`）：订单收款成功后，资金将被冻结并转入基本账户的不可用余额。商户可通过[请求分账API](https://pay.weixin.qq.com/doc/v3/merchant/4012524936)，将收款资金分配给其他商户或用户。完成分账操作后，可通过接口[解冻剩余资金](https://pay.weixin.qq.com/doc/v3/merchant/4012526374)，或在支付成功30天后自动解冻。不需要分账（传入`false`或不传，默认为`false`）：订单收款成功后，资金不会被冻结，而是直接转入基本账户的可用余额。 |
| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |  |  |  |  |  |  |  |  |
|  | total_amount 　必填   integer【标价金额】 商品单的金额，整型，单位为分。商品单商户号为境外商户时，标价金额必需超过商户结算币种的最小单位金额，例如商户结算币种为美元，则标价金额必须大于1美分。 currency 　必填   string(8)【标价币种】标价金额的币种，符合ISO 4217标准的三位字母代码，境内商户固定传入：CNY，代表人民币。 |  |  |  |  |  |  |  |  |
| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |  |  |  |  |  |  |  |  |
|  | profit_sharing 　选填   boolean【分账标识】订单的分账标识在下单时设置，传入`true`表示在订单支付成功后可进行分账操作。以下是详细说明：需要分账（传入`true`）：订单收款成功后，资金将被冻结并转入基本账户的不可用余额。商户可通过[请求分账API](https://pay.weixin.qq.com/doc/v3/merchant/4012524936)，将收款资金分配给其他商户或用户。完成分账操作后，可通过接口[解冻剩余资金](https://pay.weixin.qq.com/doc/v3/merchant/4012526374)，或在支付成功30天后自动解冻。不需要分账（传入`false`或不传，默认为`false`）：订单收款成功后，资金不会被冻结，而是直接转入基本账户的可用余额。 |  |  |  |  |  |  |  |  |

 time_expire 　选填   string

【支付结束时间】

1、定义：支付结束时间是指用户能够完成该笔订单支付的最后时限，并非订单关闭的时间。超过此时间后，用户将无法对该笔订单进行支付。如商户需在超时后关闭订单，请调用[关闭合单订单API](https://pay.weixin.qq.com/doc/v3/merchant/4012577452)接口。

2、格式要求：支付结束时间需遵循[rfc3339](https://datatracker.ietf.org/doc/html/rfc3339)标准格式：`yyyy-MM-DDTHH:mm:ss+TIMEZONE`。`yyyy-MM-DD` 表示年月日；`T` 字符用于分隔日期和时间部分；`HH:mm:ss` 表示具体的时分秒；`TIMEZONE` 表示时区（例如，`+08:00` 对应东八区时间，即北京时间）。

示例：`2015-05-20T13:29:35+08:00` 表示北京时间2015年5月20日13点29分35秒。

3、若未指定支付结束时间，系统默认以下单时间为起始点计算时效；超过 7 天未支付的订单，无法再支付。

4、注意事项：

- 若当前实际时间已超过订单设置的支付结束时间（time_expire），建议先使用关单接口关闭订单，再使用新的商户订单号重新下单，生成全新订单供用户支付。
- 支付结束时间不能早于下单时间后1分钟，若设置的支付结束时间早于该时间，系统将自动调整为下单时间后1分钟作为支付结束时间。
- 传递的支付结束时间需在下单时间的7天以内，如超过7天，微信支付会自动将该时间调整为下单时间后的第7天。

 notify_url 　必填   string(255)

【商户回调地址】商户接收[合单订单支付成功回调通知](https://pay.weixin.qq.com/doc/v3/merchant/4012158598)的地址，需按照[notify_url填写注意事项](https://pay.weixin.qq.com/doc/v3/merchant/4012075420)规范填写。

请求示例
curlJavaGo
POST

合单支付-APP合单下单-请求示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1curl -X POST \
2  https://api.mch.weixin.qq.com/v3/combine-transactions/app \
3  -H "Authorization: WECHATPAY2-SHA256-RSA2048 mchid=\"1900000001\",..." \
4  -H "Accept: application/json" \
5  -H "Content-Type: application/json" \
6  -d '{
7    "time_expire" : "2000-01-01T00:00:00+08:00",
8    "combine_appid" : "wxd678efh567hg6787",
9    "sub_orders" : [
10      {
11        "mchid" : "1230000109",
12        "attach" : "深圳分店",
13        "amount" : {
14          "total_amount" : 10,
15          "currency" : "CNY"
16        },
17        "out_trade_no" : "20150806125346",
18        "description" : "腾讯充值中心-QQ会员充值",
19        "settle_info" : {
20          "profit_sharing" : false
21        },
22        "goods_tag" : "WXG"
23      },
24      {
25        "mchid" : "1230000119",
26        "attach" : "广州分店",
27        "amount" : {
28          "total_amount" : 10,
29          "currency" : "CNY"
30        },
31        "out_trade_no" : "20150806125347",
32        "description" : "腾讯充值中心-微信充值",
33        "settle_info" : {
34          "profit_sharing" : false
35        },
36        "goods_tag" : "WXG"
37      }
38    ],
39    "combine_out_trade_no" : "20150806125345",
40    "notify_url" : "https://yourapp.com/notify",
41    "combine_mchid" : "1900000109",
42    "scene_info" : {
43      "device_id" : "POS1:1",
44      "payer_client_ip" : "14.17.22.32"
45    }
46  }'
47
```

需配合微信支付工具库 WXPayUtility 使用，请参考[Java](https://pay.weixin.qq.com/doc/v3/merchant/4014931831)
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1package com.java.demo;
2
3import com.java.utils.WXPayUtility; // 引用微信支付工具库，参考：https://pay.weixin.qq.com/doc/v3/merchant/4014931831
4
5import com.google.gson.annotations.SerializedName;
6import com.google.gson.annotations.Expose;
7import okhttp3.MediaType;
8import okhttp3.OkHttpClient;
9import okhttp3.Request;
10import okhttp3.RequestBody;
11import okhttp3.Response;
12
13import java.io.IOException;
14import java.io.UncheckedIOException;
15import java.security.PrivateKey;
16import java.security.PublicKey;
17import java.util.ArrayList;
18import java.util.HashMap;
19import java.util.List;
20import java.util.Map;
21
22/**
23 * 合单下单-APP
24 */
25public class UnionAppPrepay {
26  private static String HOST = "https://api.mch.weixin.qq.com";
27  private static String METHOD = "POST";
28  private static String PATH = "/v3/combine-transactions/app";
29
30  public static void main(String[] args) {
31    // TODO: 请准备商户开发必要参数，参考：https://pay.weixin.qq.com/doc/v3/merchant/4013070756
32    UnionAppPrepay client = new UnionAppPrepay(
33      "19xxxxxxxx",                    // 商户号，是由微信支付系统生成并分配给每个商户的唯一标识符，商户号获取方式参考 https://pay.weixin.qq.com/doc/v3/merchant/4013070756
34      "1DDE55AD98Exxxxxxxxxx",         // 商户API证书序列号，如何获取请参考 https://pay.weixin.qq.com/doc/v3/merchant/4013053053
35      "/path/to/apiclient_key.pem",     // 商户API证书私钥文件路径，本地文件路径
36      "PUB_KEY_ID_xxxxxxxxxxxxx",      // 微信支付公钥ID，如何获取请参考 https://pay.weixin.qq.com/doc/v3/merchant/4013038816
37      "/path/to/wxp_pub.pem"           // 微信支付公钥文件路径，本地文件路径
38    );
39
40    UnionAPIv3AppPrepayRequest request = new UnionAPIv3AppPrepayRequest();
41    request.combineAppid = "wxd678efh567hg6787";
42    request.combineOutTradeNo = "20150806125345";
43    request.combineMchid = "1900000109";
44    request.sceneInfo = new UnionSceneInfo();
45    request.sceneInfo.deviceId = "POS1:1";
46    request.sceneInfo.payerClientIp = "14.17.22.32";
47    request.subOrders = new ArrayList<>();
48    {
49      UnionSubOrder subOrdersItem0 = new UnionSubOrder();
50      subOrdersItem0.mchid = "1230000109";
51      subOrdersItem0.outTradeNo = "20150806125346";
52      subOrdersItem0.amount = new UnionAmountInfo();
53      subOrdersItem0.amount.totalAmount = 10L;
54      subOrdersItem0.amount.currency = "CNY";
55      subOrdersItem0.attach = "深圳分店";
56      subOrdersItem0.description = "腾讯充值中心-QQ会员充值";
57      subOrdersItem0.detail = "买单费用";
58      subOrdersItem0.goodsTag = "WXG";
59      subOrdersItem0.settleInfo = new UnionSettleInfo();
60      subOrdersItem0.settleInfo.profitSharing = false;
61      request.subOrders.add(subOrdersItem0);
62      UnionSubOrder subOrdersItem1 = new UnionSubOrder();
63      subOrdersItem1.mchid = "1230000119";
64      subOrdersItem1.outTradeNo = "20150806125347";
65      subOrdersItem1.amount = new UnionAmountInfo();
66      subOrdersItem1.amount.totalAmount = 10L;
67      subOrdersItem1.amount.currency = "CNY";
68      subOrdersItem1.attach = "广州分店";
69      subOrdersItem1.description = "腾讯充值中心-微信充值";
70      subOrdersItem1.detail = "买单费用";
71      subOrdersItem1.goodsTag = "WXG";
72      subOrdersItem1.settleInfo = new UnionSettleInfo();
73      subOrdersItem1.settleInfo.profitSharing = false;
74      request.subOrders.add(subOrdersItem1);
75    };
76    request.combinePayerInfo = new UnionAppPayerInfo();
77    request.combinePayerInfo.openid = "oUpF8uMuAJO_M2pxb1Q9zNjWeS6o";
78    request.timeExpire = "2000-01-01T00:00:00+08:00";
79    request.notifyUrl = "https://yourapp.com/notify";
80    try {
81      UnionAPIv3AppPrepayResponse response = client.run(request);
82        // TODO: 请求成功，继续业务逻辑
83        System.out.println(response);
84    } catch (WXPayUtility.ApiException e) {
85        // TODO: 请求失败，根据状态码执行不同的逻辑
86        e.printStackTrace();
87    }
88  }
89
90  public UnionAPIv3AppPrepayResponse run(UnionAPIv3AppPrepayRequest request) {
91    String uri = PATH;
92    String reqBody = WXPayUtility.toJson(request);
93
94    Request.Builder reqBuilder = new Request.Builder().url(HOST + uri);
95    reqBuilder.addHeader("Accept", "application/json");
96    reqBuilder.addHeader("Wechatpay-Serial", wechatPayPublicKeyId);
97    reqBuilder.addHeader("Authorization", WXPayUtility.buildAuthorization(mchid, certificateSerialNo,privateKey, METHOD, uri, reqBody));
98    reqBuilder.addHeader("Content-Type", "application/json");
99    RequestBody requestBody = RequestBody.create(MediaType.parse("application/json; charset=utf-8"), reqBody);
100    reqBuilder.method(METHOD, requestBody);
101    Request httpRequest = reqBuilder.build();
102
103    // 发送HTTP请求
104    OkHttpClient client = new OkHttpClient.Builder().build();
105    try (Response httpResponse = client.newCall(httpRequest).execute()) {
106      String respBody = WXPayUtility.extractBody(httpResponse);
107      if (httpResponse.code() >= 200 && httpResponse.code() = 200 && httpResponse.StatusCode < 300 {
123		// 2XX 成功，验证应答签名
124		err = wxpay_utility.ValidateResponse(
125			config.WechatPayPublicKeyId(),
126			config.WechatPayPublicKey(),
127			&httpResponse.Header,
128			respBody,
129		)
130		if err != nil {
131			return nil, err
132		}
133		response := &UnionApiv3AppPrepayResponse{}
134		if err := json.Unmarshal(respBody, response); err != nil {
135			return nil, err
136		}
137
138		return response, nil
139	} else {
140		return nil, wxpay_utility.NewApiException(
141			httpResponse.StatusCode,
142			httpResponse.Header,
143			respBody,
144		)
145	}
146}
147
148type UnionApiv3AppPrepayRequest struct {
149	CombineAppid      *string            `json:"combine_appid,omitempty"`
150	CombineOutTradeNo *string            `json:"combine_out_trade_no,omitempty"`
151	CombineMchid      *string            `json:"combine_mchid,omitempty"`
152	SceneInfo         *UnionSceneInfo    `json:"scene_info,omitempty"`
153	SubOrders         []UnionSubOrder    `json:"sub_orders,omitempty"`
154	CombinePayerInfo  *UnionAppPayerInfo `json:"combine_payer_info,omitempty"`
155	TimeExpire        *time.Time         `json:"time_expire,omitempty"`
156	NotifyUrl         *string            `json:"notify_url,omitempty"`
157	TradeScenario     *string            `json:"trade_scenario,omitempty"`
158}
159
160type UnionApiv3AppPrepayResponse struct {
161	PrepayId *string `json:"prepay_id,omitempty"`
162}
163
164type UnionSceneInfo struct {
165	DeviceId      *string `json:"device_id,omitempty"`
166	PayerClientIp *string `json:"payer_client_ip,omitempty"`
167}
168
169type UnionSubOrder struct {
170	Mchid       *string          `json:"mchid,omitempty"`
171	OutTradeNo  *string          `json:"out_trade_no,omitempty"`
172	Amount      *UnionAmountInfo `json:"amount,omitempty"`
173	Attach      *string          `json:"attach,omitempty"`
174	Description *string          `json:"description,omitempty"`
175	Detail      *string          `json:"detail,omitempty"`
176	GoodsTag    *string          `json:"goods_tag,omitempty"`
177	SettleInfo  *UnionSettleInfo `json:"settle_info,omitempty"`
178}
179
180type UnionAppPayerInfo struct {
181	Openid *string `json:"openid,omitempty"`
182}
183
184type UnionAmountInfo struct {
185	TotalAmount *int64  `json:"total_amount,omitempty"`
186	Currency    *string `json:"currency,omitempty"`
187}
188
189type UnionSettleInfo struct {
190	ProfitSharing *bool `json:"profit_sharing,omitempty"`
191}
192
```

## 应答参数

| 200 OK |  | 200 OK |
| --- | --- | --- |
|  | 200 OK |  |

 prepay_id 　必填   string(64)

【预支付交易会话标识】预支付交易会话标识，[APP调起支付](https://pay.weixin.qq.com/doc/v3/merchant/4012266043)时需要使用的参数，有效期为2小时，失效后需要重新请求该接口以获取新的prepay_id。

应答示例

200 OK
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1{
2  "prepay_id" : "wx201410272009395522657a690389285100"
3}
4
```
 
## 错误码

### 公共错误码

| 状态码 | 错误码 | 描述 | 解决方案 |
| --- | --- | --- | --- |
| 400 | PARAM_ERROR | 参数错误 | 请根据错误提示正确传入参数 |
| 400 | INVALID_REQUEST | HTTP 请求不符合微信支付 APIv3 接口规则 | 请参阅[接口规则](https://pay.weixin.qq.com/doc/v3/merchant/4012081709)检查传入的参数 |
| 401 | SIGN_ERROR | 验证不通过 | 请参阅[签名常见问题](https://pay.weixin.qq.com/doc/v3/merchant/4012365347)排查 |
| 500 | SYSTEM_ERROR | 系统异常，请稍后重试 | 请稍后重试 |

### 业务错误码

| 状态码 | 错误码 | 描述 | 解决方案 |
| --- | --- | --- | --- |
| 400 | APPID_MCHID_NOT_MATCH | AppID和mch_id不匹配 | 请确认AppID和mch_id是否匹配，参考：[查询商户号绑定的APPID账号](https://pay.weixin.qq.com/doc/v3/merchant/4013426141#1%E3%80%81%E6%9F%A5%E8%AF%A2%E5%95%86%E6%88%B7%E5%8F%B7%E7%BB%91%E5%AE%9A%E7%9A%84APPID%E8%B4%A6%E5%8F%B7) |
| 400 | INVALID_REQUEST | 无效请求 | 请根据接口返回的详细信息检查 |
| 400 | MCH_NOT_EXISTS | 商户号不存在 | 请检查商户号是否正确，商户号获取方式请参考：[普通商户模式开发必要参数说明](https://pay.weixin.qq.com/doc/v3/merchant/4013070756) |
| 400 | ORDER_CLOSED | 订单已关闭 | 当前订单已关闭，请重新下单 |
| 401 | SIGN_ERROR | 签名错误 | 请检查签名参数和方法是否都符合签名算法要求，参考：[如何生成签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365342#2.-%E4%BB%80%E4%B9%88%E6%97%B6%E5%80%99%E9%9C%80%E8%A6%81%E9%AA%8C%E7%AD%BE%EF%BC%9F%E5%A6%82%E4%BD%95%E9%AA%8C%E7%AD%BE%EF%BC%9F) |
| 403 | NOAUTH | 商户无权限 | 请商户联系对接运营申请此接口相关权限，参考：[快速开始-步骤3](https://pay.weixin.qq.com/doc/v3/merchant/4013420660) |
| 403 | OUT_TRADE_NO_USED | 商户订单号重复 | 请核实商户订单号是否重复提交 |
| 403 | RULELIMIT | 业务规则限制 | 因业务规则限制请求频率，请查看接口返回的详细信息 |
| 429 | FREQUENCY_LIMITED | 频率超限 | 请降低请求接口频率 |
| 500 | OPENID_MISMATCH | OpenID和AppID不匹配 | 请确认OpenID和AppID是否匹配，参考：[OpenID获取](https://pay.weixin.qq.com/doc/v3/merchant/4012068676) |
| 500 | SYSTEMERROR | 系统错误 | 系统异常，请用相同参数重新调用 |
