# JSAPI调起支付

# JSAPI调起支付

路径：产品文档/支付产品/JSAPI支付/API列表/JSAPI调起支付

商户通过[JSAPI/小程序下单](https://pay.weixin.qq.com/doc/v3/merchant/4012791856)接口获取到发起支付的必要参数prepay_id后，再通过微信浏览器内置对象方法(WeixinJSBridge)调起微信支付收银台。

## 接口说明

支持商户：【普通商户】

## 字段说明

### 请求参数

此API签名无后台接口交互，需要将列表中的数据签名

`appId`  必填  string(32)

填写下单时传入的appid，且必需与当前实际调起支付的公众号appid一致，否则无法调起支付。

`timeStamp`  必填  string(32)

Unix 时间戳，是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数。
注意：常见时间戳为秒级或毫秒级，该处必需传秒级时间戳。

`nonceStr`  必填  string(32)

随机字符串，不长于32位。该值建议使用随机数算法生成。

`package`  必填  string(128)

订单详情扩展字符串，JSAPI下单接口返回的prepay_id参数值，提交格式如：prepay_id=***。

`signType`  必填  string(32)

签名类型，固定填RSA。

`paySign`  必填  string(512)

签名，使用字段appId、timeStamp、nonceStr、package计算得出的签名值 注意：取值RSA格式。详细参考[JSAPI调起支付签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365339)

请求示例

示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1function onBridgeReady() {
2    WeixinJSBridge.invoke('getBrandWCPayRequest', {
3        "appId": "wx2421b1c4370ec43b",     //公众号ID，由商户传入     
4        "timeStamp": "1395712654",     //时间戳，自1970年以来的秒数     
5        "nonceStr": "e61463f8efa94090b1f366cccfbbb444",      //随机串     
6        "package": "prepay_id=wx21201855730335ac86f8c43d1889123400",
7        "signType": "RSA",     //微信签名方式：     
8        "paySign": "oR9d8PuhnIc+YZ8cBHFCwfgpaK9gd7vaRvkYD7rthRAZ\/X+QBhcCYL21N7cHCTUxbQ+EAt6Uy+lwSN22f5YZvI45MLko8Pfso0jm46v5hqcVwrk6uddkGuT+Cdvu4WBqDzaDjnNa5UK3GfE1Wfl2gHxIIY5lLdUgWFts17D4WuolLLkiFZV+JSHMvH7eaLdT9N5GBovBwu5yYKUR7skR8Fu+LozcSqQixnlEZUfyE55feLOQTUYzLmR9pNtPbPsu6WVhbNHMS3Ss2+AehHvz+n64GDmXxbX++IOBvm2olHu3PsOUGRwhudhVf7UcGcunXt8cqNjKNqZLhLw4jq\/xDg==" //微信签名 
9    },
10    function(res) {
11        if (res.err_msg == "get_brand_wcpay_request:ok") {
12            // 使用以上方式判断前端返回,微信团队郑重提示：
13            //res.err_msg将在用户支付成功后返回ok，但并不保证它绝对可靠，商户需进一步调用后端查单确认支付结果。
14        }
15    });
16}
17if (typeof WeixinJSBridge == "undefined") {
18    if (document.addEventListener) {
19        document.addEventListener('WeixinJSBridgeReady', onBridgeReady, false);
20    } else if (document.attachEvent) {
21        document.attachEvent('WeixinJSBridgeReady', onBridgeReady);
22        document.attachEvent('onWeixinJSBridgeReady', onBridgeReady);
23    }
24} else {
25    onBridgeReady();
26}
```

### 返回结果值说明

用户从微信收银台返回商户页面时会触发商户调用onBridgeReady拉起支付时传入的function回调方法，商户可通过回调err_msg参数展示相应支付结果。

注：前端回调并不保证它绝对可靠，不可只依赖前端回调判断订单支付状态，订单状态需以后端[查询订单](https://pay.weixin.qq.com/doc/v3/merchant/4012791859)和[支付成功回调通知](https://pay.weixin.qq.com/doc/v3/merchant/4012791861)为准。

| err_msg返回值 | 返回值说明 |
| --- | --- |
| get_brand_wcpay_request:ok | 调用后端接口查单，如果订单已支付则展示支付成功页面。 |
| get_brand_wcpay_request:cancel | 用户取消支付，商户可自行处理展示。 |
| get_brand_wcpay_request:fail | 支付失败，展示订单支付失败结果。 |
