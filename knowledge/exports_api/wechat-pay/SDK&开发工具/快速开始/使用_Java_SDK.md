# 使用 Java SDK

# 使用 Java SDK

路径：SDK&开发工具/快速开始/使用 Java SDK

在本教程中，你将简要了解微信支付的 Java SDK。在学习过程中，你将

- 掌握如何安装 Java SDK
- 了解请求微信支付需要哪些密钥和证书
- 了解如何使用 Java SDK 请求微信支付

## 环境要求

- Java 1.8+

## 安装

使用包管理系统，例如 Maven、Gradle，快速添加微信支付官方 SDK。

如果你使用的 [Gradle](https://gradle.org/)，请在 build.gradle 中加入：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1implementation 'com.github.wechatpay-apiv3:wechatpay-java:${VERSION}'
```

如果你使用的 [Maven](https://maven.apache.org/)，请在 pom.xml 中加入：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1
2  com.github.wechatpay-apiv3
3  wechatpay-java
4  ${VERSION}
5
```

你可以在 GitHub 找到 [Java SDK](https://github.com/wechatpay-apiv3/wechatpay-java) 的源代码、使用说明和最新版本信息。

## 必需的证书和密钥

运行 SDK 必需以下的商户身份信息，用于构造请求的签名和验证应答的签名：

- [商户 API 私钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053053#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E5%95%86%E6%88%B7API%E8%AF%81%E4%B9%A6%E7%A7%81%E9%92%A5%EF%BC%9F)
- [商户 API 证书](https://pay.weixin.qq.com/doc/v3/merchant/4013053053)的证书序列号
- [APIv3 密钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053267)

## 发起请求

以 Native 支付为例，向微信支付发起你的第一个请求：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1package com.wechat.pay.java.service;
2import com.wechat.pay.java.core.Config;
3import com.wechat.pay.java.core.RSAAutoCertificateConfig;
4import com.wechat.pay.java.service.payments.nativepay.NativePayService;
5import com.wechat.pay.java.service.payments.nativepay.model.Amount;
6import com.wechat.pay.java.service.payments.nativepay.model.PrepayRequest;
7import com.wechat.pay.java.service.payments.nativepay.model.PrepayResponse;
8/** Native 支付下单为例 */
9public class QuickStart {
10    /** 商户号 */
11    public static String merchantId = "190000****";
12    /** 商户API私钥路径 */
13    public static String privateKeyPath = "/Users/yourname/your/path/apiclient_key.pem";
14    /** 商户证书序列号 */
15    public static String merchantSerialNumber = "5157F09EFDC096DE15EBE81A47057A72********";
16    /** 商户APIV3密钥 */
17    public static String apiV3key = "...";
18    public static void main(String[] args) {
19        // 使用自动更新平台证书的RSA配置
20        // 建议将 config 作为单例或全局静态对象，避免重复的下载浪费系统资源
21        Config config =
22                new RSAAutoCertificateConfig.Builder()
23                        .merchantId(merchantId)
24                        .privateKeyFromPath(privateKeyPath)
25                        .merchantSerialNumber(merchantSerialNumber)
26                        .apiV3Key(apiV3key)
27                        .build();
28        // 构建service
29        NativePayService service = new NativePayService.Builder().config(config).build();
30        // request.setXxx(val)设置所需参数，具体参数可见Request定义
31        PrepayRequest request = new PrepayRequest();
32        Amount amount = new Amount();
33        amount.setTotal(100);
34        request.setAmount(amount);
35        request.setAppid("wxa9d9651ae******");
36        request.setMchid("190000****");
37        request.setDescription("测试商品标题");
38        request.setNotifyUrl("https://notify_url");
39        request.setOutTradeNo("out_trade_no_001");
40        // 调用下单方法，得到应答
41        PrepayResponse response = service.prepay(request);
42        // 使用微信扫描 code_url 对应的二维码，即可体验Native支付
43        System.out.println(response.getCodeUrl());
44    }
45}
```

## 联系 SDK 团队获取帮助

- 在[开发者社区](https://developers.weixin.qq.com/community/pay)提交问题
- 在 GitHub 上[提交 issue](https://github.com/wechatpay-apiv3/wechatpay-java/issues)
- 联系我们的[在线技术支持](https://support.pay.weixin.qq.com/aidevhelper)

## 接下来阅读

通过这个快速介绍，你已经安装了 Java SDK 并学习了一些基础知识。接下来，你可以：

- 阅读 [SDK 配置详解](https://github.com/wechatpay-apiv3/wechatpay-java/wiki/SDK-%E9%85%8D%E7%BD%AE%E8%AF%A6%E8%A7%A3)，详细了解如何配置商户信息和超时等网络设置。
- 阅读具体的产品文档，学习如何接入微信支付。
