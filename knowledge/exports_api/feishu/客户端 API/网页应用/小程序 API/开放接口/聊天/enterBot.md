# enterBot

# enterBot(Object object)

打开机器人聊天页面
**Notice**：启用 Bot 能力即支持此 API

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | V2.7.0+ | V2.7.0+ | V2.7.0+ | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

继承[标准对象输入](https://open.feishu.cn/document/uYjL24iN/ukzNy4SO3IjL5cjM)，无扩展属性

## 输出

继承[标准对象输出](https://open.feishu.cn/document/uYjL24iN/ukzNy4SO3IjL5cjM#8c92acb8)，无扩展属性

## 示例代码

```js
tt.enterBot({
  success(res) {
    console.log(JSON.stringify(res));
  },
  fail(res) {
    console.log(`enterBot fail: ${JSON.stringify(res)}`);
  },
});
```

`success`返回对象示例：

```json
{
  "errMsg": "enterBot:ok"
}
```
