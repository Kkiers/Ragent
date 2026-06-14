# Android

# Android

路径：产品文档/运营工具/微信支付分/API列表/APP调起支付分确认订单页/Android

商户通过[创建支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587900)接口获取确认订单的必要参数package后可使用微信支付提供的[openSDK](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)调起微信支付分小程序，引导用户确认订单（App端） 

## openSDK资源下载及说明

App调起微信支付分小程序需引用版本号大于>=5.3.1的openSDK（建议使用最新版本的openSDK）

openSDK下载地址：[Android资源下载](https://developers.weixin.qq.com/doc/oplatform/Downloads/Android_Resource.html)

接入文档链接：[openSDK说明文档](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)

| 兼容性表现说明若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本= Build.OPEN_BUSINESS_VIEW_SDK_iNT) {
3  WXOpenBusinessView.Req req = new WXOpenBusinessView.Req();
4  req.businessType = "wxpayScoreUse";
5  req.query = "package=AAQTnZoAAAABAAAAAAD8m2b8VRdZ2kVdKmHNZiAAAABcwQVtru-5k9MmEOZJ_Pv_Nq7Cw56dNKKN5Ej3Knt5jTHF-NdsP_McFW-iaU3iuJ0gWlNQeG9UihoKi0k2pv1t71M6mpk15X6L1545yNpmPD5uhi3poFV8e_5EdYwi_cbc6tXYVfa0AJUO4OzHGPhMdT4ZMwmFFhD0HQi9mRHQhFRKPwFai4NkkW7vm9mv1test";
6  req.extInfo = "{\"miniProgramType\": 0}";
7  Boolean ret = api.sendReq(req);
8} else {
9  /*需提示用户升级微信版本*/
10}
11
12/********在WXEntryActivity的onResp里面接收回调，示例全码*******/
13@Override
14public void onResp(BaseResp r) {
15  if (r.getType() == ConstantsAPI.COMMAND_OPEN_BUSINESS_VIEW) {
16    WXOpenBusinessView.Resp launchMiniProgramResp = (WXOpenBusinessView.Resp) r;
17    string
18 text = string
19.format("nextMsg=%snerrStr=%snbusinessType=%s",
20                resp.extMsg, resp.errStr, resp.businessType);
21    Toast.makeText(this, text, Toast.LENGTH_lONG).show();
22  }
23}
```
  
### 返回参数

返回对象：WXOpenBusinessView.Resp

businessType  必填  string(16)

【跳转类型】，在确认订单场景下返回类型为：wxpayScoreUse。

extMsg  必填  string

支付分返回的业务数据，json格式。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | query_id  必填  string(64)单据查询ID，对应[查询订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口中入参query_id。appid  必填  string(32)支付分小程序appid，固定值wxd8f3793ea3b935b8。 |
 
| 注意带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准。 |  | 注意带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准。 |
| --- | --- | --- |
|  | 注意带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准。 |  |
