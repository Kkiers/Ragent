# 使用 Go SDK

# 使用 Go SDK

路径：SDK&开发工具/快速开始/使用 Go SDK

在本教程中，你将简要了解微信支付的 Go SDK。在学习过程中，你将

- 掌握如何安装 Go SDK
- 了解请求微信支付需要哪些密钥和证书
- 了解如何使用 Go SDK 请求微信支付

## 环境要求

- Go 1.16+

## 安装

使用 [Go Modules](https://github.com/golang/go/wiki/Modules) 安装最新版本 SDK：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1go get github.com/wechatpay-apiv3/wechatpay-go
```

你可以在 GitHub 找到 [Go SDK](https://github.com/wechatpay-apiv3/wechatpay-go) 的源代码、使用说明和最新版本信息。

## 必需的证书和密钥

运行 SDK 必需以下的证书和密钥：

- [商户 API 私钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053053#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E5%95%86%E6%88%B7API%E8%AF%81%E4%B9%A6%E7%A7%81%E9%92%A5%EF%BC%9F)
- [商户 API 证书](https://pay.weixin.qq.com/doc/v3/merchant/4013053053)的证书序列号
- [API v3密钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053267)

## 发起请求

以 Native 支付为例，向微信支付发起你的第一个请求。
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1package main
2import (
3    "context"
4    "log"
5    "github.com/wechatpay-apiv3/wechatpay-go/core"
6    "github.com/wechatpay-apiv3/wechatpay-go/core/option"
7    "github.com/wechatpay-apiv3/wechatpay-go/services/payments/native"
8    "github.com/wechatpay-apiv3/wechatpay-go/utils"
9)
10func main() {
11    var (
12        mchID string = "190000****" // 商户号
13        mchCertificateSerialNumber string = "3775B6A45ACD588826D15E583A95F5DD********" // 商户证书序列号
14        mchAPIv3Key string = "2ab9****************************" // 商户APIv3密钥
15    )
16    // 使用 utils 提供的函数从本地文件中加载商户私钥，商户私钥会用来生成请求的签名
17    mchPrivateKey, err: = utils.LoadPrivateKeyWithPath("/path/to/merchant/apiclient_key.pem")
18    if err != nil {
19        log.Fatal("load merchant private key error")
20    }
21    ctx: = context.Background()
22    // 使用商户私钥等初始化 client，并使它具有自动定时获取微信支付平台证书的能力
23    opts: = [] core.ClientOption {
24        option.WithWechatPayAutoAuthCipher(mchID, mchCertificateSerialNumber, mchPrivateKey, mchAPIv3Key),
25    }
26    client, err: = core.NewClient(ctx, opts...)
27    if err != nil {
28        log.Fatalf("new wechat pay client err:%s", err)
29    }
30    // 以 Native 支付为例
31    svc := native.NativeApiService{Client: client}
32    // 发送请求
33    resp, result, err: = svc.Prepay(ctx,
34        native.PrepayRequest {
35            Appid: core.String("wxd678efh567hg6787"),
36            Mchid: core.String("1900009191"),
37            Description: core.String("Image形象店-深圳腾大-QQ公仔"),
38            OutTradeNo: core.String("1217752501201407033233368018"),
39            Attach: core.String("自定义数据说明"),
40            NotifyUrl: core.String("https://www.weixin.qq.com/wxpay/pay.php"),
41            Amount: & native.Amount {
42                Total: core.Int64(100),
43            },
44        },
45    )
46    // 使用微信扫描 resp.code_url 对应的二维码，即可体验Native支付
47    log.Printf("status=%d resp=%s", result.Response.StatusCode, resp)
48}
```

## 联系 SDK 团队获取帮助

- 在[开发者社区](https://developers.weixin.qq.com/community/pay)提交问题
- 在 GitHub 上[提交 issue](https://github.com/wechatpay-apiv3/wechatpay-go/issues)
- 联系我们的[在线技术支持](https://support.pay.weixin.qq.com/aidevhelper)

## 接下来阅读

通过这个快速介绍，你已经安装了 Go SDK 并学习了一些基础知识。接下来，你可以阅读具体的产品文档，学习如何接入微信支付。
