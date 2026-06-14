# bridge.getData

# bridge.getData
获取[bridge.setData](https://open.feishu.cn/document/uAjLw4CM/uYjL24iN/base-extensions/base-view-extensions/api/bridge_setdata)存储的内容。

## 输出
Promise 对象。
## 示例代码
### 调用示例

```js
await bitable.bridge.setData({
    a:123
});

const res = await bitable.bridge.getData();
console.log(res)
```

### 返回示例
res:
```js
{a: 123}
```
