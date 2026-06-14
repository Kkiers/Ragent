# iOS

# iOS

路径：产品文档/运营工具/微信支付分/API列表/APP调起支付分确认订单页/iOS

商户通过[创建支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587900)接口获取确认订单的必要参数package后可使用微信支付提供的[openSDK](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/iOS.html)调起微信支付分小程序，引导用户确认订单（App端）

## openSDK资源下载及说明

App调起微信支付分小程序需引用版本号大于>=1.8.4的openSDK（建议使用最新版本的openSDK）

openSDK下载地址：[iOS资源下载](https://developers.weixin.qq.com/doc/oplatform/Downloads/iOS_Resource.html)

接入文档链接：[openSDK说明文档](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/iOS.html)

| 兼容性表现说明若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本< 7.0.3，开发者通过此openSDK接口可以跳转到微信，但不能跳转到微信支付分小程序，此时微信会提示用户可能由于应用的请求非法或者微信版本过低。 |  |

## 接口说明

支持商户： 【普通商户】

接口名称：WXOpenBusinessView

接口对象：WXOpenBusinessViewReq

## 字段说明

### 请求参数

businessType  必填  string(16)

固定值，请传入wxpayScoreUse

query  必填  string(2048)

使用URL的query string方式传递参数，格式为key=value&key2=value2，其中value，value2需要进行UrlEncode处理。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | package  必填  string(128)【跳转支付分小程序订单数据包】创建支付分订单成功后返回，用于拉起支付分小程序确认订单页面，由数字大小写字母_-符号组成，不超过300字符。 |

extInfo  选填  string(128)

【跳转的小程序版本】，目前仅支持跳正式版本，传值为 {"miniProgramType": 0}。
type取值说明：
0:正式版；

示例代码
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1WXOpenBusinessViewReq *req = [WXOpenBusinessViewReq object];
2req.businessType = @"wxpayScoreUse";
3req.query = @"package=AAQTnZoAAAABAAAAAAD8m2b8VRdZ2kVdKmHNZiAAAABcwQVtru-5k9MmEOZJ_Pv_Nq7Cw56dNKKN5Ej3Knt5jTHF-NdsP_McFW-iaU3iuJ0gWlNQeG9UihoKi0k2pv1t71M6mpk15X6L1545yNpmPD5uhi3poFV8e_5EdYwi_cbc6tXYVfa0AJUO4OzHGPhMdT4ZMwmFFhD0HQi9mRHQhFRKPwFai4NkkW7vm9mv1test";
4req.extInfo = @"{\"miniProgramType\":0}";
5[WXApi sendReq:req]
6
```
   
### 返回参数

返回对象：WXOpenBusinessViewResp

businessType  必填  string(16)

【跳转类型】，在确认订单场景下返回类型为：wxpayScoreUse。

extMsg  必填  string

支付分返回的业务数据，json格式。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | query_id  必填  string(64)单据查询ID，对应[查询订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口中入参query_id。appid  必填  string(32)支付分小程序appid，固定值wxd8f3793ea3b935b8。。 |
 
| 注意带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准。 |  | 注意带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准。 |
| --- | --- | --- |
|  | 注意带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准。 |  |
