# 使用 PHP SDK

# 使用 PHP SDK

路径：SDK&开发工具/快速开始/使用 PHP SDK

在本教程中，你将简要了解微信支付的 PHP SDK。在学习过程中，你将

- 掌握如何安装 PHP SDK
- 了解请求微信支付需要哪些密钥和证书
- 了解如何使用 PHP SDK 请求微信支付

## 环境要求

- Guzzle 7.0，PHP >= 7.2.5。
- Guzzle 6.5，PHP >= 7.1.2

我们推荐使用目前处于 [Active Support](https://www.php.net/supported-versions.php) 阶段的 PHP 8 和 Guzzle 7。

## 安装

使用 [Composer](https://getcomposer.org/) 安装最新版本的 SDK：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1composer require wechatpay/wechatpay
```

你可以在 GitHub 找到 [PHP SDK](https://github.com/wechatpay-apiv3/wechatpay-php) 的源代码、使用说明和最新版本信息。

## 必需的证书和密钥

运行 SDK 必需以下的证书和密钥：

- [商户 API 私钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053053#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E5%95%86%E6%88%B7API%E8%AF%81%E4%B9%A6%E7%A7%81%E9%92%A5%EF%BC%9F)
- [商户 API 证书](https://pay.weixin.qq.com/doc/v3/merchant/4013053053)的证书序列号
- [APIv3 密钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053267)
- [微信支付平台证书](https://pay.weixin.qq.com/doc/v3/merchant/4012068814#4.-%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E5%B9%B3%E5%8F%B0%E8%AF%81%E4%B9%A6)或[微信支付公钥](https://pay.weixin.qq.com/doc/v3/merchant/4012153196)

由于 [PHP-FPM](https://www.php.net/manual/zh/install.fpm.php) 进程模型限制，PHP SDK 不支持自动获取和更新微信支付平台证书。你可以使用 SDK 自带的[工具](https://github.com/wechatpay-apiv3/wechatpay-php/blob/main/bin/README.md)下载微信支付平台证书。
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1composerexec CertificateDownloader.php -- -k ${apiV3key} -m ${mchId} -f ${mchPrivateKeyFilePath} -s ${mchSerialNo} -o ${outputFilePath}
```

| 注意：如果使用上述命令下载平台证书报错：{"code": "RESOURCE_NOT_EXISTS","message": "无可用的平台证书，请在商户平台-API安全申请使用微信支付公钥。"}，即表示商户仅能使用微信支付公钥，可参考下方发起请求中的使用微信支付公钥初始化示例 |  | 注意：如果使用上述命令下载平台证书报错：{"code": "RESOURCE_NOT_EXISTS","message": "无可用的平台证书，请在商户平台-API安全申请使用微信支付公钥。"}，即表示商户仅能使用微信支付公钥，可参考下方发起请求中的使用微信支付公钥初始化示例 |
| --- | --- | --- |
|  | 注意：如果使用上述命令下载平台证书报错：{"code": "RESOURCE_NOT_EXISTS","message": "无可用的平台证书，请在商户平台-API安全申请使用微信支付公钥。"}，即表示商户仅能使用微信支付公钥，可参考下方发起请求中的使用微信支付公钥初始化示例 |  |

## 发起请求

以 Native 支付为例，向微信支付发起你的第一个请求。
使用微信支付平台证书初始化使用微信支付公钥初始化![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1 $merchantId,
30    'serial' => $merchantCertificateSerial,
31    'privateKey' => $merchantPrivateKeyInstance,
32    'certs' => [
33        $platformCertificateSerial => $platformPublicKeyInstance,
34    ],
35]);
36
37// 以 Native 支付为例，发送请求
38$resp = $instance -> chain('v3/pay/transactions/native') -> post(['json' => [
39        'mchid' => '1900006XXX',
40        'out_trade_no' => 'native12177525012014070332333',
41        'appid' => 'wxdace645e0bc2cXXX',
42        'description' => 'Image形象店-深圳腾大-QQ公仔',
43        'notify_url' => 'https://weixin.qq.com/',
44        'amount' => [
45            'total' => 1,
46            'currency' => 'CNY'
47        ],
48    ],
49    //在http请求增加一个Wechatpay-Serial请求头，具体作用可参考：https://pay.weixin.qq.com/doc/v3/merchant/4012154180#5.2-%E5%88%87%E6%8D%A2%E9%AA%8C%E7%AD%BE%E5%92%8C%E5%AE%9E%E7%8E%B0%E5%9B%9E%E8%B0%83%E5%85%BC%E5%AE%B9
50    'headers' => [
51        'Wechatpay-Serial' => '134912410000000000000xxxxxxx',
52    ],
53]);
54
55print_r(json_decode((string) $resp->getBody(), true));
56//当程序进入「异常捕获」逻辑，输出形如：
57{
58    "code": "RESOURCE_NOT_EXISTS",
59    "message": "无可用的平台证书，请在商户平台-API安全申请使用微信支付公钥。"
60}
61//即表示商户仅能使用微信支付公钥初始化模式
```
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1 账户中心 -> API安全 查询
26$platformPublicKeyId = 'PUB_KEY_ID_01142321349124100000000000********';
27
28// 构造一个 APIv3 客户端实例
29$instance = Builder::factory([
30    'mchid' => $merchantId,
31    'serial' => $merchantCertificateSerial,
32    'privateKey' => $merchantPrivateKeyInstance,
33    'certs' => [
34        $platformPublicKeyId => $twoPlatformPublicKeyInstance,
35    ],
36]);
37
38// 以 Native 支付为例，发送请求
39$resp = $instance -> chain('v3/pay/transactions/native') -> post(['json' => [
40        'mchid' => '1900006XXX',
41        'out_trade_no' => 'native12177525012014070332333',
42        'appid' => 'wxdace645e0bc2cXXX',
43        'description' => 'Image形象店-深圳腾大-QQ公仔',
44        'notify_url' => 'https://weixin.qq.com/',
45        'amount' => [
46            'total' => 1,
47            'currency' => 'CNY'
48        ],
49    ],
50    //在http请求增加一个Wechatpay-Serial请求头，具体作用可参考：https://pay.weixin.qq.com/doc/v3/merchant/4012154180#5.2-%E5%88%87%E6%8D%A2%E9%AA%8C%E7%AD%BE%E5%92%8C%E5%AE%9E%E7%8E%B0%E5%9B%9E%E8%B0%83%E5%85%BC%E5%AE%B9
51    'headers' => [
52        'Wechatpay-Serial' => 'PUB_KEY_ID_0112232134912010000100000000',
53    ],
54]);
55print_r(json_decode((string) $resp ->getBody(), true));
```

## 联系 SDK 团队获取帮助

- 在[开发者社区](https://developers.weixin.qq.com/community/pay)提交问题
- 在 GitHub 上[提交 issue](https://github.com/wechatpay-apiv3/wechatpay-php/issues)
- 联系我们的[在线技术支持](https://support.pay.weixin.qq.com/aidevhelper)

## 接下来阅读

通过这个快速介绍，你已经安装了 PHP SDK 并学习了一些基础知识。接下来，你可以阅读具体的产品文档，学习如何接入微信支付。
