# App拉起微信支付分停车服务开通页

# App拉起微信支付分停车服务开通页

路径：产品文档/运营工具/微信支付分停车服务/API列表/服务/App拉起微信支付分停车服务开通页

通过调用该接口打开微信支付分停车服务小程序，引导用户进行服务开通。 商户的来源AppID必须要和商户号相关联。
 
## 接口说明

支持商户： 【普通商户】

接口名称： App拉起小程序标准流程参考《[App拉起小程序功能](https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Launching_a_Mini_Program/Launching_a_Mini_Program.html)》

微信支付分停车服务小程序AppID为： wxbcad394b3d99dac9

微信支付分停车服务小程序路径为： /pages/auth-creditpay/auth-creditpay

微信支付分停车服务小程序username为： gh_518c42c65952

### 接口参数
 
`mchid`  必填  string(32)

商户号。

`openid`  必填  string(32)

用户在商户对应AppID下的唯一标识。

`plate_number`  必填  string(32)

待开通车牌。

`plate_color`  必填  string(32)

待开通车牌的颜色
BLUE：蓝色
GREEN：绿色
YELLOW：黄色
BLACK：黑色
WHITE：白色
LIMEGREEN：黄绿色

`trade_scene`  选填  string(32)

开通场景信息，目前只支持PARKING

### 请求示例
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1/pages/auth-creditpay/auth-creditpay?mchid=1230000100&openid=5K8264ILTKCH16CQ250&plate_number=粤B888888&plate_color=BLUE&trade_scene=PARKING
```
 
用户开通/授权完成之后，会跳转回到商户的App，暂时不返回参数。商户侧App接收到客户端回调后再次调用查询车牌开通信息接口获取用户的最新车主状态。
