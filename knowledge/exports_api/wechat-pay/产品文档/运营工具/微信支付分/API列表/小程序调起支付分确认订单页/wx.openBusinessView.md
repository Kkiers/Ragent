# wx.openBusinessView

# wx.openBusinessView

路径：产品文档/运营工具/微信支付分/API列表/小程序调起支付分确认订单页/wx.openBusinessView

商户通过[创建支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587900)接口获取确认订单的必要参数package后可使用微信支付提供的小程序方法调起微信支付分小程序，引导用户确认订单（小程序端）

## 接口说明

支持商户： 【普通商户】

商户小程序跳转微信侧小程序建议使用wx.openBusinessView的调用方式，不占用小程序跳转其他小程序的数量名额。

| 兼容性表现说明小程序版本库 >= 2.6.0，低版本需提示用户升级微信版本。iOS兼容性表现：若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本= 2.6.0，低版本需提示用户升级微信版本。iOS兼容性表现：若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本= 2.6.0，低版本需提示用户升级微信版本。iOS兼容性表现：若微信版本>=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本=7.0.3，开发者可以通过此openSDK接口跳转到微信支付分小程序；若微信版本< 7.0.3，开发者通过此openSDK接口不能跳转到微信，此时开发者应提示用户更新微信版本。 |  |
 
接口名称: wx.openBusinessView

## 字段说明

#### 请求参数

businessType  必填  string(32)

固定值，请传入wxpayScoreUse

extraData  必填  Object

需要传递给支付分的业务数据。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | package  必填  string(128)【跳转支付分小程序订单数据包】创建支付分订单成功后返回，用于拉起支付分小程序确认订单页面，由数字大小写字母_-符号组成，不超过300字符。 |

wx.openBusinessView 请求示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1if (wx.openBusinessView) {
2  wx.openBusinessView({
3    businessType: 'wxpayScoreUse',
4    extraData: {
5      package: 'AAQTnZoAAAABAAAAAAD8m2b8VRdZ2kVdKmHNZiAAAABcwQVtru-5k9MmEOZJ_Pv_Nq7Cw56dNKKN5Ej3Knt5jTHF-NdsP_McFW-iaU3iuJ0gWlNQeG9UihoKi0k2pv1t71M6mpk15X6L1545yNpmPD5uhi3poFV8e_5EdYwi_cbc6tXYVfa0AJUO4OzHGPhMdT4ZMwmFFhD0HQi9mRHQhFRKPwFai4NkkW7vm9mv1test',
6    },
7    success() {
8      //dosomething
9    },
10    fail() {
11      //dosomething
12    },
13    complete() {
14      //dosomething
15    }
16  });
17} else {
18  //引导用户升级微信版本
19}
```
 
#### 返回参数

触发场景: 用户从商户小程序页面进入到支付分后再返回到商户小程序页面。

返回参数获取说明: 商户小程序可在 App.onLaunch，App.onShow 中获取到这份数据。
 
query_id  必填  string(64)

单据查询ID，对应[《查询支付分订单》](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口中入参query_id。
 
| 提示带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准；只有用户点击支付分页面内返回按钮时，才会带上返回参数；如果用户点击小程序页面左上角的返回图标按钮，则不会带上返回参数。 |  | 提示带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准；只有用户点击支付分页面内返回按钮时，才会带上返回参数；如果用户点击小程序页面左上角的返回图标按钮，则不会带上返回参数。 |
| --- | --- | --- |
|  | 提示带有返回参数不代表订单确认成功，具体状态需以[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口返回的结果为准；只有用户点击支付分页面内返回按钮时，才会带上返回参数；如果用户点击小程序页面左上角的返回图标按钮，则不会带上返回参数。 |  |

返回商家侧小程序请求示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1// app.js
2onShow(res) {
3  if (res.scene === 1038) { // 场景值1038：从被打开的小程序返回
4    const { appId, extraData } = res.referrerInfo;
5    if (appId === 'wxd8f3793ea3b935b8') { // 建议检查来源 appId，确保从支付分返回商户小程序页面，支付分 appId 为 wxd8f3793ea3b935b8
6      let query_id = extraData.query_id;
7      let result = this.queryOrderStatus(query_id);
8      if (result) {
9        // 成功
10      } else {
11        // 失败
12      }
13    }
14  }
15}
16
17/**
18 * 查询订单状态函数
19 * 由商家后台服务提供
20 * @param query_id {string
21} 单据id，可以在接口【查询订单】进行单据查询
22 */
23queryOrderStatus: function(query_id) {
24  // 商家小程序向商家后台服务请求查询订单状态，
25  // 这里的前后端接口和数据协议由商家侧设计
26  // 函数返回查询结果，这里以布尔值true代表成功，布尔值false代表失败
27}
```
