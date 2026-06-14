# Android

# Android

路径：产品文档/运营工具/商家转账/API列表/发起转账/APP调起用户确认收款/Android

## 简介

商家转账用户确认模式下，商户通过在移动端应用APP中集成开放SDK调起微信请求用户确认收款。

## 接入前注意事项

在接入前需详细阅读下方说明：

商户需先通过[发起转账](https://pay.weixin.qq.com/doc/v3/merchant/4012716434#%E5%BA%94%E7%AD%94%E5%8F%82%E6%95%B0)接口申请创建转账单，获取到跳转领取页面的package信息后，商户APP再通过微信[Open SDK](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/WeChat_Pay/Vendor_Service_Center.html)（详见[Android](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)接入指南）的sendReq方法拉起用户确认收款页。

## 接口说明

支持商户：【普通商户】

接口名称：WXOpenBusinessView

需要引用新的openSDK：

- Android openSDK下载地址（版本>=5.3.1）：[Android资源下载](https://developers.weixin.qq.com/doc/oplatform/Downloads/Android_Resource.html)
- Android 接入文档链接：[openSDK说明文档](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)

| 接口兼容：Android兼容性表现：若微信版本>=8.0.45.51，开发者可以通过此openSDK接口调起用户确认收款页面；若微信版本=8.0.45.51，开发者可以通过此openSDK接口调起用户确认收款页面；若微信版本=8.0.45.51，开发者可以通过此openSDK接口调起用户确认收款页面；若微信版本= 0x28002d33) {
3  WXOpenBusinessView.Req req = new WXOpenBusinessView.Req();
4  req.businessType = "requestMerchantTransfer";
5  req.query = "mchId=1230000000&appId=wx8888888888888888&package=affffddafdfafddffda%3D%3D";
6  Boolean ret = api.sendReq(req);
7} else {
8  /*需提示用户升级微信版本*/
9}
```

## 返回参数

Android对应对象：WXOpenBusinessView.Resp

businessType 必填 string(16)

【业务类型】打开的业务类型。

extMsg 必填 string

【扩展信息】返回的业务数据，格式为JSON字符串，如 `{"result":"success"}`。具体内部字段如下

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | result 必填 string【结果信息】`success`：展示页面成功。`fail`：展示页面失败。`cancel`：用户取消。发生场景：用户未确认收款，点击取消，返回APP |

返回示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1/********在WXEntryActivity的onResp里面接收回调，示例全码*******/
2@Override
3public void onResp(BaseResp r) {
4  if (r.getType() == ConstantsAPI.COMMAND_OPEN_BUSINESS_VIEW) {
5    WXOpenBusinessView.Resp launchMiniProgramResp = (WXOpenBusinessView.Resp) r;
6    string
7 text = string
8.format("nextMsg=%snerrStr=%snbusinessType=%s",
9                resp.extMsg, resp.errStr, resp.businessType);
10    Toast.makeText(this, text, Toast.LENGTH_lONG).show();
11  }
12}
```

| 注意：带有返回结果信息不代表订单确认成功，具体状态需以接口查询的结果为准。 |  | 注意：带有返回结果信息不代表订单确认成功，具体状态需以接口查询的结果为准。 |
| --- | --- | --- |
|  | 注意：带有返回结果信息不代表订单确认成功，具体状态需以接口查询的结果为准。 |  |
