# 如何查看商户API证书或平台证书序列号？

# 如何查看商户API证书或平台证书序列号？

路径：通用规则/开发须知/常见问题/如何查看商户API证书或平台证书序列号？

登录商户平台【API安全】->【API证书】->【查看证书】，可查看商户API证书序列号。

商户API证书和微信支付平台证书均可以使用第三方的证书[解析工具](https://myssl.com/cert_decode.html)，查看证书内容。或者使用openssl命令行工具查看证书序列号。
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1$ openssl x509 -in 1900009191_20180326_cert.pem -noout -serial
2serial=1DDE55AD98ED71D6EDD4A4A16996DE7B47773A8C
```
