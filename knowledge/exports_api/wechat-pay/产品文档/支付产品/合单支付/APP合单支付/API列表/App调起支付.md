# App调起支付

# App调起支付

路径：产品文档/支付产品/合单支付/APP合单支付/API列表/App调起支付

商户通过[APP合单下单](https://pay.weixin.qq.com/doc/v3/merchant/4012556944)接口获取到发起支付的必要参数`prepay_id`后，商户APP再通过openSDK(详见[安卓](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/Android.html)/[IOS](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/iOS.html)/[鸿蒙](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/ohos.html)接入指引)的sendReq方法拉起微信支付。

## 接口说明

支持商户：【普通商户】

## 字段说明

### 请求参数

PayReq对象

`appId` 必填 string(32)

【合单商户应用ID】请填写下单时传入`combine_appid`

`partnerId` 必填 string(32)

【合单商户号】请填写下单时传入的`combine_mchid`

`prepayId` 必填 string(64)

【预支付交易会话标识】[APP合单下单](https://pay.weixin.qq.com/doc/v3/merchant/4012556944)接口返回的prepay_id，该值有效期为2小时，超过有效期需要重新请求[APP合单下单](https://pay.weixin.qq.com/doc/v3/merchant/4012556944)接口以获取新的prepay_id。

`packageValue` 必填 string(128)

【固定值】填写固定值 Sign=WXPay
注意：如果是ios则请求参数为“package”

`nonceStr` 必填 string(32)

【随机字符串】不长于32位。该值建议使用随机数算法生成。

`timeStamp` 必填 string(10)

【时间戳】Unix时间戳，是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数。
注意：常见时间戳为秒级或毫秒级，该处必需传秒级时间戳。

`sign` 必填 string(512)

【签名值】使用字段appId、timeStamp、nonceStr、prepayId以及[商户API证书](https://kf.qq.com/faq/161222NneAJf161222U7fARv.html)私钥生成的RSA签名值，详细参考[APP调起支付签名](https://pay.weixin.qq.com/doc/v3/merchant/4012365340)。

请求示例

ios示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1PayReq *request = [[[PayReq alloc] init] autorelease];
2request.appId = "wxd930ea5d5a258f4f";
3request.partnerId = "1900000109";
4request.prepayId= "1101000000140415649af9fc314aa427",;
5request.package = "Sign=WXPay";
6request.nonceStr= "1101000000140429eb40476f8896f4c9";
7request.timeStamp= "1398746574";
8request.sign= "oR9d8PuhnIc+YZ8cBHFCwfgpaK9gd7vaRvkYD7rthRAZ\/X+QBhcCYL21N7cHCTUxbQ+EAt6Uy+lwSN22f5YZvI45MLko8Pfso0jm46v5hqcVwrk6uddkGuT+Cdvu4WBqDzaDjnNa5UK3GfE1Wfl2gHxIIY5lLdUgWFts17D4WuolLLkiFZV+JSHMvH7eaLdT9N5GBovBwu5yYKUR7skR8Fu+LozcSqQixnlEZUfyE55feLOQTUYzLmR9pNtPbPsu6WVhbNHMS3Ss2+AehHvz+n64GDmXxbX++IOBvm2olHu3PsOUGRwhudhVf7UcGcunXt8cqNjKNqZLhLw4jq\/xDg==";
9[WXApi sendReq：request];
```

android示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1IWXAPI api;
2PayReq request = new PayReq();
3request.appId = "wxd930ea5d5a258f4f";
4request.partnerId = "1900000109";
5request.prepayId= "1101000000140415649af9fc314aa427",;
6request.packageValue = "Sign=WXPay";
7request.nonceStr= "1101000000140429eb40476f8896f4c9";
8request.timeStamp= "1398746574";
9request.sign= "oR9d8PuhnIc+YZ8cBHFCwfgpaK9gd7vaRvkYD7rthRAZ\/X+QBhcCYL21N7cHCTUxbQ+EAt6Uy+lwSN22f5YZvI45MLko8Pfso0jm46v5hqcVwrk6uddkGuT+Cdvu4WBqDzaDjnNa5UK3GfE1Wfl2gHxIIY5lLdUgWFts17D4WuolLLkiFZV+JSHMvH7eaLdT9N5GBovBwu5yYKUR7skR8Fu+LozcSqQixnlEZUfyE55feLOQTUYzLmR9pNtPbPsu6WVhbNHMS3Ss2+AehHvz+n64GDmXxbX++IOBvm2olHu3PsOUGRwhudhVf7UcGcunXt8cqNjKNqZLhLw4jq\/xDg==";
10api.sendReq(request);
```

鸿蒙示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1IWXAPI api;
2let req = new wxopensdk.PayReq
3req.appId = 'wxd930ea5d5a258f4f'
4req.partnerId = '1900000109'
5req.prepayId = '1101000000140415649af9fc314aa427'
6req.packageValue = 'Sign=WXPay'
7req.nonceStr = '1101000000140429eb40476f8896f4c9'
8req.timeStamp = '1398746574'
9req.sign = 'oR9d8PuhnIc+YZ8cBHFCwfgpaK9gd7vaRvkYD7rthRAZ\/X+QBhcCYL21N7cHCTUxbQ+EAt6Uy+lwSN22f5YZvI45MLko8Pfso0jm46v5hqcVwrk6uddkGuT+Cdvu4WBqDzaDjnNa5UK3GfE1Wfl2gHxIIY5lLdUgWFts17D4WuolLLkiFZV+JSHMvH7eaLdT9N5GBovBwu5yYKUR7skR8Fu+LozcSqQixnlEZUfyE55feLOQTUYzLmR9pNtPbPsu6WVhbNHMS3Ss2+AehHvz+n64GDmXxbX++IOBvm2olHu3PsOUGRwhudhVf7UcGcunXt8cqNjKNqZLhLw4jq\/xDg=='
10api.sendReq(context: common.UIAbilityContext, req)
```

### 返回结果值说明

用户从微信收银台返回商户APP时openSDK会onResp回调，商户可通过回调errCode参数展示相应支付结果。

注：前端回调并不保证它绝对可靠，不可只依赖前端回调判断订单支付状态，订单状态需以后端[查询合单订单](https://pay.weixin.qq.com/doc/v3/merchant/4012557006)和[合单订单支付成功回调通知](https://pay.weixin.qq.com/doc/v3/merchant/4012158598)为准。
 
返回示例

ios示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1-(void)onResp：(BaseResp*)resp{
2if ([respisKindOfClass：[PayRespclass]]){
3    PayResp*response=(PayResp*)resp;
4    switch(response.errCode){
5                caseWXSuccess： //服务器端查询支付通知或查询API返回的结果再提示成功
6                          NSlog(@"支付成功");
7                break;
8                default：
9                          NSlog(@"支付失败，retcode=%d",resp.errCode);
10                break;
11      }
12  }
13}
```

android示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1public void onResp(BaseRespresp){
2    if(resp.getType()==ConstantsAPI.COMMAND_PAY_BY_WX){
3    Log.d(TAG,"onPayFinish,errCode="+resp.errCode);
4    AlertDialog.Builderbuilder=newAlertDialog.Builder(this);
5    builder.setTitle(R.string.app_tip);
6    }
7}
```

鸿蒙示例代码：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1onResp(resp: wxopensdk.BaseResp): void {
2    Log.i(kTag, "onResp:%s", JSON.stringify(resp))
3    this.onRespCallbacks.forEach((on) => {
4    on(resp)
5    })
6}
```

| errCode值 | 描述 | 商户APP处理方案 |
| --- | --- | --- |
| 0 | 成功 | 调用后端接口查单，如果订单已支付则展示支付成功页面 |
| -1 | 错误 | 可能的原因：签名错误、未注册AppID、项目设置AppID不正确、注册的AppID与设置的不匹配、其他异常原因等。 |
| -2 | 取消支付 | 用户取消支付返回App，商户可自行处理展示。 |
