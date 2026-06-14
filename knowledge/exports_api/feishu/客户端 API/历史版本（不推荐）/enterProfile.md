# enterProfile

# enterProfile

显示用户信息卡片。warning
该接口为历史版本，已停止维护，新版本云文档小组件推荐使用[View.Action.showUserProfile](https://open.feishu.cn/document/uAjLw4CM/uYjL24iN/docs-add-on/05-api-doc/basic-data-reference---base/View.Action.showUserProfile)。
- 该 API 仅老版本云文档小组件 PC 环境支持。
- 调用前确保已经调用 tt.login 接口成功登录。

## 输入

param 继承自[标准对象输入](https://open.feishu.cn/document/uAjLw4CM/uYjL24iN/block/api/standard-object-input)，扩展属性描述：

| **名称** | **数据类型** | **是否必填** | **默认值** | **描述**                                                                          |
| ------ | ------ | ------- | ------ | ------------------------------------------------------------------------------- | ---------- | 
| openid | string | 是      | --      | 用户的 [OpenID](https://open.feishu.cn/document/ukTMukTMukTM/uUTO5UjL1kTO14SN5kTN)，有关 OpenID 解释可以参考[名词解释](https://open.feishu.cn/document/ukTMukTMukTM/uYTM5UjL2ETO14iNxkTN/terminology)| PC 端 1.0.3 |
| left   | number | 否       | 0      | 卡片显示位置，距离视口左侧距离                                                                 | PC 端 1.0.3 |
| top    | number | 否       | 0      | 卡片显示位置，距离视口顶部距离                                                                 | PC 端 1.0.3 |
| unCoverArea | object | 是 | --    | 禁止卡片遮盖的区域，通常指目标元素的区域，会结合left、top进行自适应计算 |
| &emsp;&emsp; ∟ width | number | 是 | --    | 禁止卡片遮盖区域的宽度 |
| &emsp;&emsp; ∟ height | number | 是 | --    | 禁止卡片遮盖区域的高度 |
## 输出

各 callback 返回对象参数均无额外扩展属性。

## 示例代码

### 调用示例

```js
tt.enterProfile({
  openid: 'ou_xxx',
  left: 50,
  top: 50,
  unCoverArea: {
    width: 100,
    height: 100
  },
  success (res) {
    console.log('enterProfile 调用成功', res.errMsg);
  },
  fail (res) {
    console.log('enterProfile 调用失败', res.errMsg);
  },
  complete (res) {
    console.log('enterProfile 调用结束', res.errMsg);
  } 
});
```

### 返回示例

```json
{
  "errMsg": "enterProfile:ok"
}
```
