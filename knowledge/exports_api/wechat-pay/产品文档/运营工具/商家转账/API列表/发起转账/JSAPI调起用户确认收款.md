# JSAPI调起用户确认收款

# JSAPI调起用户确认收款

路径：产品文档/运营工具/商家转账/API列表/发起转账/JSAPI调起用户确认收款

商家转账用户确认模式下，在微信客户端通过小程序或H5拉起页面请求用户确认收款。
 
## 接口说明

支持商户：【普通商户】

| 注意：WeixinJSBridge内置对象在其他浏览器中无效。商户需参考下方对应的调用示例，用接口判断微信客户端版本、小程序基础库版本是否支持requestMerchantTransfer 方法，如不支持，需做好兼容性处理 |  | 注意：WeixinJSBridge内置对象在其他浏览器中无效。商户需参考下方对应的调用示例，用接口判断微信客户端版本、小程序基础库版本是否支持requestMerchantTransfer 方法，如不支持，需做好兼容性处理 |
| --- | --- | --- |
|  | 注意：WeixinJSBridge内置对象在其他浏览器中无效。商户需参考下方对应的调用示例，用接口判断微信客户端版本、小程序基础库版本是否支持requestMerchantTransfer 方法，如不支持，需做好兼容性处理 |  |

## 接口定义

名称：requestMerchantTransfer

## 请求参数

mchId 必填 string(32)

【商户号】商户号，由微信支付生成并下发，和发起转账传入的mchid必须是同一个

appId 必填 string(32)

【商户AppID】商户绑定的AppID（企业号corpid即为此AppID），由微信生成，和发起转账传入的appid必须是同一个

package 必填 string(1024)

【package信息】对应[发起转账](https://pay.weixin.qq.com/doc/v3/merchant/4012716434#%E5%BA%94%E7%AD%94%E5%8F%82%E6%95%B0)接口应答参数中的 package_info（仅当转账单据状态为WAIT_USER_CONFIRM: 待收款用户确认时才返回），用于唤起用户确认收款页面。

调用示例
小程序示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1if (wx.canIUse('requestMerchantTransfer')) {
2  wx.requestMerchantTransfer({
3    mchId: '1230000000',
4    appId: wx.getAccountInfoSync().miniProgram.appId,
5    package: 'affffddafdfafddffda==',
6    success: (res) => {
7      // res.err_msg将在页面展示成功后返回应用时返回ok，并不代表付款成功
8      console.log('success:', res);
9    },
10    fail: (res) => {
11      console.log('fail:', res);
12    },
13  });
14} else {
15  wx.showModal({
16    content: '你的微信版本过低，请更新至最新版本。',
17    showCancel: false,
18  });
19}
20
```

H5示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1wx.config({
2  // 参考：https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html
3});
4wx.ready(function () {
5  wx.checkJsApi({
6    jsApiList: ['requestMerchantTransfer'],
7    success: function (res) {
8      if (res.checkResult['requestMerchantTransfer']) {
9        WeixinJSBridge.invoke('requestMerchantTransfer', {
10            mchId: '1230000000',
11            appId: 'wx8888888888888888',
12            package: 'affffddafdfafddffda==',
13          },
14          function (res) {
15            if (res.err_msg === 'requestMerchantTransfer:ok') {
16              // res.err_msg将在页面展示成功后返回应用时返回success，并不代表付款成功
17            }
18          }
19        );
20      } else {
21        alert('你的微信版本过低，请更新至最新版本。');
22      }
23    }
24  });
25});
26
```

## 返回结果值说明

| 描述 | 解决方案 |
| --- | --- |
| requestMerchantTransfer:ok | 展示页面成功 |
| requestMerchantTransfer:fail | 展示页面失败 |
| requestMerchantTransfer:cancel | 用户取消。发生场景：用户未确认收款，点击取消，返回APP |
