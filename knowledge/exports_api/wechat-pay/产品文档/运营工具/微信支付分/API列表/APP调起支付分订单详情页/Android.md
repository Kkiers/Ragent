# Android

# Android

路径：产品文档/运营工具/微信支付分/API列表/APP调起支付分订单详情页/Android

商户使用微信支付提供的[openSDK](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)调起微信支付分小程序，引导用户查看订单详情（App端）

## openSDK资源下载及说明

App调起微信支付分小程序需引用版本号大于>=5.3.1的openSDK（建议使用最新版本的openSDK）

openSDK下载地址（版本>=5.3.1）：[Android资源下载](https://developers.weixin.qq.com/doc/oplatform/Downloads/Android_Resource.html)

接入文档链接：[openSDK说明文档](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)

| 兼容性表现说明若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本= Build.OPEN_BUSINESS_VIEW_SDK_iNT) {
3  WXOpenBusinessView.Req req = new WXOpenBusinessView.Req();
4  req.businessType = "wxpayScoreDetail";
5  req.query = "mch_id=1230000109&service_id=88888888000011&out_order_no=1234323JKHDFE1243252×tamp=1530097563&nonce_str=zyx53Nkey8o4bHpxTQvd8m7e92nG5mG2&sign_type=HMAC-SHA256&sign=029B52F67573D7E3BE74904BF9AEA";
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

无
