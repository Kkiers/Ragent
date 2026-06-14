# bridge.setData

# bridge.setData
在当前 base 中存储自定义内容。 

>  在调试阶段使用该接口需要将 `@lark-opdev/block-bitable-webpack-utils` 依赖版本升级至 `0.1.6` 及以上。

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
