# JSAPI调起支付分订单详情页

# JSAPI调起支付分订单详情页

路径：产品文档/运营工具/微信支付分/API列表/JSAPI调起支付分订单详情页

商户使用微信支付提供的JS调起微信支付分小程序，引导用户查看订单（公众号端）

## 接口说明

支持商户： 【普通商户】

接口名称： openBusinessView

| 提示在JSAPI调起支付分相关接口前，需详细阅读JS-SDK说明文档并进行相应配置JS-SDK配置为链接: [https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html](https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html)此接口引用 JSAPI版本1.5.0，引用地址：[https://res.wx.qq.com/open/js/jweixin-1.5.0.js](https://res.wx.qq.com/open/js/jweixin-1.5.0.js)要求用户微信版本>=7.0.5 |  | 提示在JSAPI调起支付分相关接口前，需详细阅读JS-SDK说明文档并进行相应配置JS-SDK配置为链接: [https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html](https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html)此接口引用 JSAPI版本1.5.0，引用地址：[https://res.wx.qq.com/open/js/jweixin-1.5.0.js](https://res.wx.qq.com/open/js/jweixin-1.5.0.js)要求用户微信版本>=7.0.5 |
| --- | --- | --- |
|  | 提示在JSAPI调起支付分相关接口前，需详细阅读JS-SDK说明文档并进行相应配置JS-SDK配置为链接: [https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html](https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html)此接口引用 JSAPI版本1.5.0，引用地址：[https://res.wx.qq.com/open/js/jweixin-1.5.0.js](https://res.wx.qq.com/open/js/jweixin-1.5.0.js)要求用户微信版本>=7.0.5 |  |

## 字段说明

### 请求参数

businessType  必填  string(16)

固定配置：wxpayScoreDetail。

queryString  必填  string(2048)

使用URL的query string方式传递参数，格式为key=value&key2=value2，其中value，value2需要进行UrlEncode处理。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | mch_id  必填  string(32)【商户号】调用支付分创单接口提交的商户号，商户号需开通支付分产品权限，且与appid有绑定关系，详见[直连商户与AppID账号关联管理](https://kf.qq.com/faq/1801116VJfua1801113QVNVz.html)。service_id  必填  string(32)【服务ID】商户支付分服务的唯一标识，由32位数字组成。支付分产品权限审核通过后，微信支付运营会向商户提供该ID。out_order_no  必填  string(32)【商户服务订单号】 商户系统内部服务订单号，要求32个字符内，只能是数字、大小写字母_-\|* 且在同一个商户号下唯一。需要开发者特别注意，该参数不可用于申请退款接口中的 out_trade_no 参数。timestamp  必填  string(32)【时间戳】标准北京时间，时区为东八区，自1970年1月1日 0点0分0秒以来的秒数。注意：部分系统取到的值为毫秒级，需要转换成秒(10位数字)。nonce_str  必填  string(32)生成签名随机串。由数字、大小写字母组成，长度不超过32位。sign_type  必填  string(32)签名类型，仅支持HMAC-SHA256。sign  必填  string(64)使用字段mch_id、service_id、out_order_no、timestamp、nonce_str、sign_type按照[签名生成算法](https://pay.weixin.qq.com/doc/v2/merchant/4011985891)计算得出的签名值。注意：该接口签名需使用APIv2密钥 |

请求示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1let wechatInfo = navigator.userAgent.match(/MicroMessenger\/([\d\.]+)/i);
2let wechatVersion = wechatInfo[1];
3
4if (compareVersion(wechatVersion, '7.0.5') >= 0) {
5   goToWXScore();
6} else {
7   // 提示用户升级微信客户端版本
8   window.href = 'https://support.weixin.qq.com/cgi-bin/readtemplate?t=page/common_page__upgrade&
9   text=text005&btn_text=btn_text_0'
10}
11
12/**
13 * 跳转微信支付分
14 */
15function goToWXScore() {
16    wx.checkJsApi({
17        jsApiList: ['openBusinessView'], // 需要检测的JS接口列表
18        success: function (res) {
19        // 以键值对的形式返回，可用的api值true，不可用为false
20        // 如：{"checkResult":{"openBusinessView":true},"errMsg":"checkJsApi:ok"}
21        if (res.checkResult.openBusinessView) {
22            wx.invoke(
23                'openBusinessView', {
24                    businessType: 'wxpayScoreDetail',
25                    queryString
26:'mch_id=1230000109&service_id=88888888000011&out_order_no=1234323JKHDFE1243252×tamp=1530097563&nonce_str=zyx53Nkey8o4bHpxTQvd8m7e92nG5mG2&sign_type=HMAC-SHA256&sign=029B52F67573D7E3BE74904BF9AEA'
27                },
28                
29                function (res) {
30                // 从支付分返回时会执行这个回调函数
31                    if (parseint(res.err_code) === 0) {
32                    // 返回成功 
33                    } else {
34                    // 返回失败
35                    }
36                });
37            }
38        }
39    });
40 }
41
42 /**
43  * 版本号比较
44  * @param {string
45} v1 
46  * @param {string
47} v2 
48  */
49function compareVersion(v1, v2) {
50    v1 = v1.split('.')
51    v2 = v2.split('.')
52    const len = Math.max(v1.length, v2.length)
53  
54    while (v1.length  num2) {
66        return 1
67      } else if (num1 < num2) {
68        return -1
69      }
70    }
71  
72    return 0
73 }
```
 
### 返回参数

无
