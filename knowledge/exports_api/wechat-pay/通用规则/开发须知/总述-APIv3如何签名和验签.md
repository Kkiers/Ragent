# 总述-APIv3如何签名和验签

# 总述-APIv3如何签名和验签

路径：通用规则/开发须知/总述-APIv3如何签名和验签

## 概述

在微信支付APIv3的所有请求应答场景、接口回调场景、调起支付场景，开发者都需要进行签名验签。

## 1. 什么时候需要签名？如何签名？

以下2种场景需要构造签名

![](https://gtimg.wechatpay.cn/resource/xres/mmpaydoc/static/img/d26a8bd7db226a16ee6cb9009a437985.png)

### 1.1 请求微信支付接口

商户调用微信支付接口的时候需要用到商户API证书（[申请商户API证书](https://pay.weixin.qq.com/doc/v3/merchant/4012072428)）构造请求签名，且根据请求参数类型的不同，签名方式有所差异，请参考一下的操作指引说明

（1）[请求参数里带Path参数（路径参数），如何计算签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365334)

（2）[请求参数里带Body参数(包体参数），如何计算签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365336)

（3）[请求参数里有Query（查询参数），如何计算签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365337)

（4）[图片上传接口，如何计算签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365335)

### 1.2 调起支付

商户在前端调起支付时，需要用到商户API证书（[申请商户API证书](https://pay.weixin.qq.com/doc/v3/merchant/4012072428)）构造调起支付签名，请根据需求参考对应的文档

（1）[JSAPI调起支付签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365339)

（2）[APP调起支付签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365340)

（3）[小程序调起支付签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365341)

## 2. 什么时候需要验签？如何验签？

以下2种场景商户需要验签，验证请求是来自微信支付

| 微信支付应答商户的请求时，商户需要验签（验证请求是来自微信支付） | 接收微信支付的回调时，商户需要验签（验证请求是来自微信支付） |
| --- | --- |
| ![](https://gtimg.wechatpay.cn/resource/xres/mmpaydoc/static/img/ce5110366910151937efeec0ccc6672a.png) | ![](https://gtimg.wechatpay.cn/resource/xres/mmpaydoc/static/img/c24fd077381f8e3489e11fd71ec80067.png) |

### 2.1 接收微信支付应答

微信支付应答商户的请求时，商户需要验签。

（1）【推荐】如果你使用的是微信支付公钥，参考[微信支付公钥如何验签](https://pay.weixin.qq.com/doc/v3/merchant/4013053249)

（2）如果你使用的是平台证书模式，参考[如何使用平台证书验签](https://pay.weixin.qq.com/doc/v3/merchant/4013053420)

### 2.2 接收微信支付回调请求

接收微信支付的回调时，商户需要验签

（1）微信支付会使用APIv3密钥加密回调信息，商户需要使用APIv3密钥解密回调信息，参考[如何解密微信支付回调报文](https://pay.weixin.qq.com/doc/v3/merchant/4012071382)

（2）【推荐】如果你使用的是微信支付公钥，参考[如何使用微信支付公钥验签](https://pay.weixin.qq.com/doc/v3/merchant/4013053249)

（3）如果你使用的是平台证书模式，参考[如何使用平台证书验签名](https://pay.weixin.qq.com/doc/v3/merchant/4013053420)
