# LifeCycle.notifyAppReady

# LifeCycle.notifyAppReady
通知文档应用加载完毕，配合配 `useHostLoading`使用，该方法为异步调用。
```json
// app.json
{
    "contributes": {
    "addPanel": {
        "useHostLoading": true, // true 的时候notifyAppReady才生效
        ...
    }
  }
}
```

## 可用性说明

权限要求 | 视图可用说明 | 平台可用 | 场景
--- | --- | --- | ---
可读 | 所有视图 | - PC  
- 移动端 | 演示模式

## 输入

无需传入参数。

## 输出

无

## 示例代码

### 调用示例

```js
const DocMiniApp = new BlockitClient().initAPI();
useEffect(() => {
    DocMiniApp.LifeCycle.notifyAppReady();
});
```

### 返回示例

无
