# JSAPI调起支付分确认订单页

# JSAPI调起支付分确认订单页

路径：产品文档/运营工具/微信支付分/API列表/JSAPI调起支付分确认订单页

商户通过[创建支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587900)接口获取确认订单的必要参数package后可使用微信支付提供的JS调起微信支付分小程序，引导用户确认订单（公众号端）

## 接口说明

支持商户： 【普通商户】

接口名称： openBusinessView

| 提示此接口引用 JSAPI版本1.5.0，引用地址：[https://res.wx.qq.com/open/js/jweixin-1.5.0.js](https://res.wx.qq.com/open/js/jweixin-1.5.0.js)要求用户微信版本>=7.0.5 |  | 提示此接口引用 JSAPI版本1.5.0，引用地址：[https://res.wx.qq.com/open/js/jweixin-1.5.0.js](https://res.wx.qq.com/open/js/jweixin-1.5.0.js)要求用户微信版本>=7.0.5 |
| --- | --- | --- |
|  | 提示此接口引用 JSAPI版本1.5.0，引用地址：[https://res.wx.qq.com/open/js/jweixin-1.5.0.js](https://res.wx.qq.com/open/js/jweixin-1.5.0.js)要求用户微信版本>=7.0.5 |  |

## 字段说明

### 请求参数

businessType  必填  string(16)

固定值，请传入wxpayScoreUse。

queryString  必填  string(2048)

使用URL的query string方式传递参数，格式为key=value&key2=value2，其中value，value2需要进行UrlEncode处理。

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | package  必填  string(128)【跳转支付分小程序订单数据包】创建支付分订单成功后返回，用于拉起支付分小程序确认订单页面，由数字大小写字母_-符号组成，不超过300字符。 |

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
24                    businessType: 'wxpayScoreUse',
25                    queryString
26:'package=AAQTnZoAAAABAAAAAAD8m2b8VRdZ2kVdKmHNZiAAAABcwQVtru-5k9MmEOZJ_Pv_Nq7Cw56dNKKN5Ej3Knt5jTHF-NdsP_McFW-iaU3iuJ0gWlNQeG9UihoKi0k2pv1t71M6mpk15X6L1545yNpmPD5uhi3poFV8e_5EdYwi_cbc6tXYVfa0AJUO4OzHGPhMdT4ZMwmFFhD0HQi9mRHQhFRKPwFai4NkkW7vm9mv1test'
27                },
28                function (res) {
29                // 从支付分返回时会执行这个回调函数
30                    if (parseint(res.err_code) === 0) {
31                    // 返回成功 
32                    } else {
33                    // 返回失败
34                    }
35                });
36            }
37        }
38    });
39 }
40
41 /**
42  * 版本号比较
43  * @param {string
44} v1 
45  * @param {string
46} v2 
47  */
48function compareVersion(v1, v2) {
49    v1 = v1.split('.')
50    v2 = v2.split('.')
51    const len = Math.max(v1.length, v2.length)
52  
53    while (v1.length  num2) {
65        return 1
66      } else if (num1 < num2) {
67        return -1
68      }
69    }
70  
71    return 0
72 }
```
 
### 返回参数

err_code  必填  Number/string(32)

返回码，由于iOS和Android实现的差异，err_code类型可能为Number或string

err_msg  必填  string(128)

返回信息。

extraData  选填  Object

当err_code为0时，extraData才返回

| ![](https://gtimg.wechatpay.cn/resource/xres/img/202409/2a1a0741836e71dcb14320f2fcac3a6e_32x32.svg) | 属性 |
| --- | --- |
|  | query_id  必填  string(64)单据查询ID，对应[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口中入参query_id。appid  必填  string(32)支付分小程序appid，固定值wxd8f3793ea3b935b8。 |
 
| 注意只有用户点支付分页面内返回按钮时，才会带上返回参数；如果用户左滑返回或者点击页面左上角的返回图标返回，则不会带上返回参数。所以推荐在[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口使用out_order_no作为入参。另外商户侧后台在创建支付分订单时需向前端返回out_order_no，同时前端需缓存out_order_no，以便在接口中查询订单状态。 |  | 注意只有用户点支付分页面内返回按钮时，才会带上返回参数；如果用户左滑返回或者点击页面左上角的返回图标返回，则不会带上返回参数。所以推荐在[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口使用out_order_no作为入参。另外商户侧后台在创建支付分订单时需向前端返回out_order_no，同时前端需缓存out_order_no，以便在接口中查询订单状态。 |
| --- | --- | --- |
|  | 注意只有用户点支付分页面内返回按钮时，才会带上返回参数；如果用户左滑返回或者点击页面左上角的返回图标返回，则不会带上返回参数。所以推荐在[查询支付分订单](https://pay.weixin.qq.com/doc/v3/merchant/4012587902)接口使用out_order_no作为入参。另外商户侧后台在创建支付分订单时需向前端返回out_order_no，同时前端需缓存out_order_no，以便在接口中查询订单状态。 |  |
