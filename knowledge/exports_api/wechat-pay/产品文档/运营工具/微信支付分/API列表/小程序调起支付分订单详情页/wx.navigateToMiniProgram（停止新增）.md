# wx.navigateToMiniProgram（停止新增）

# wx.navigateToMiniProgram（停止新增）

路径：产品文档/运营工具/微信支付分/API列表/小程序调起支付分订单详情页/wx.navigateToMiniProgram（停止新增）

商户使用微信支付提供的小程序方法调起微信支付分小程序，引导用户查看订单（小程序端）
 
## 接口说明

支持商户： 【普通商户】

2024年1月31日后接入的商户已无法使用wx.navigateToMiniProgram接口，商户需调用[wx.openBusinessView](https://pay.weixin.qq.com/doc/v3/merchant/4012587984)接口来实现从商户小程序跳转到微信支付分小程序。

| 兼容性表现说明小程序版本库 >= 2.6.0，低版本需提示用户升级微信版本。iOS兼容性表现：若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本= 2.6.0，低版本需提示用户升级微信版本。iOS兼容性表现：若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本= 2.6.0，低版本需提示用户升级微信版本。iOS兼容性表现：若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本< 7.0.3，开发者通过此openSDK接口不能跳转到微信，此时开发者应提示用户更新微信版本。 |  |
 
接口名称: wx.navigateToMiniProgram，详见[小程序API文档](https://developers.weixin.qq.com/miniprogram/dev/api/navigate/wx.navigateToMiniProgram.html)。

| 特别提醒每个小程序可跳转的其他小程序数量限制为不超过 10 个。 |  | 特别提醒每个小程序可跳转的其他小程序数量限制为不超过 10 个。 |
| --- | --- | --- |
|  | 特别提醒每个小程序可跳转的其他小程序数量限制为不超过 10 个。 |  |

## 字段说明

#### 请求参数

appId  必填  string(32)

支付分小程序appid，固定值wxd8f3793ea3b935b8。

path  必填  string(64)

固定配置：pages/record/detail

extraData  必填  Object

需要传递给支付分的业务数据。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | mch_id  必填  string(32)【商户号】调用支付分创单接口提交的商户号，商户号需开通支付分产品权限，且与appid有绑定关系，详见[直连商户与AppID账号关联管理](https://kf.qq.com/faq/1801116VJfua1801113QVNVz.html)。service_id 必填  string(128)【服务ID】商户支付分服务的唯一标识，由32位数字组成。支付分产品权限审核通过后，微信支付运营会向商户提供该ID。out_order_no 必填  string(32)【商户服务订单号】 商户系统内部服务订单号，要求32个字符内，只能是数字、大小写字母_-\|* 且在同一个商户号下唯一。需要开发者特别注意，该参数不可用于申请退款接口中的 out_trade_no 参数。timestamp  必填  string(32)【时间戳】标准北京时间，时区为东八区，自1970年1月1日 0点0分0秒以来的秒数。注意：部分系统取到的值为毫秒级，需要转换成秒(10位数字)。nonce_str  必填  string(32)生成签名随机串。由数字、大小写字母组成，长度不超过32位。sign_type  必填  string(32)签名类型，仅支持HMAC-SHA256。sign  必填  string(64)使用字段mch_id、service_id、out_order_no、timestamp、nonce_str、sign_type按照[签名生成算法](https://pay.weixin.qq.com/doc/v2/merchant/4011985891)计算得出的签名值。注意：该接口签名需使用APIv2密钥 |

wx.navigateToMiniProgram 请求示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1wx.navigateToMiniProgram({
2  appId: 'wxd8f3793ea3b935b8',
3  path: 'pages/record/detail',
4  extraData: {
5    mch_id: '1230000109',
6    service_id: '88888888000011',
7    out_order_no: '1234323JKHDFE1243252',
8    timestamp: '1530097563',
9    nonce_str: 'zyx53Nkey8o4bHpxTQvd8m7e92nG5mG2',
10    sign_type: 'HMAC-SHA256',
11    sign: '029B52F67573D7E3BE74904BF9AEA'
12  },
13  success() {
14    //dosomething
15  },
16  fail() {
17    //dosomething
18  },
19  complete() {
20    //dosomething
21  }
22})
```
 
#### 返回参数

无
