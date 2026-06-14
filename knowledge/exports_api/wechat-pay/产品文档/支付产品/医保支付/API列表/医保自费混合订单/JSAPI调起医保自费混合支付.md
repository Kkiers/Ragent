# JSAPI调起医保自费混合支付

# JSAPI调起医保自费混合支付

路径：产品文档/支付产品/医保支付/API列表/医保自费混合订单/JSAPI调起医保自费混合支付

1. 如存在自费支付金额，通过自费下单接口获取到发起自费支付的必要参数timeStamp、nonceStr、package、signType、paySign
2. 通过【医保自费混合收款下单】接口获取到发起支付的必要参数mix_trade_no
3. 使用requestMedicalInsurancePay方法调起医保自费混合支付
4. 用户输入密码，确认收款
5. 返回医疗机构H5页面，医疗机构H5调用【查看医保自费混合收款结果】接口，查询收款结果，更新H5页面

## 接口说明

支持商户： 【普通商户】

调用接口前需要[通过config接口注入权限验证配置](https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/JS-SDK.html#4)。

## 接口兼容

iOS兼容性表现：若微信版本>=8.0.44，开发者可以通过此接口调起医保自费混合支付；若微信版本=8.0.44，开发者可以通过此接口调起医保自费混合支付；若微信版本=8.0.13，开发者可以通过此接口调起医保自费混合支付；若微信版本 {
21    // res: {"result":"success","err_msg":"requestMedicalInsurancePay:ok","msg":"已完成医保支付 ","err_desc":""}
22  });
23});
```

## 回调结果

| 回调类型 | errMsg | 说明 |
| --- | --- | --- |
| success | requestMedicalInsurancePay:ok | 调用支付成功 |
| fail | requestMedicalInsurancePay:fail | 调用支付失败 |
