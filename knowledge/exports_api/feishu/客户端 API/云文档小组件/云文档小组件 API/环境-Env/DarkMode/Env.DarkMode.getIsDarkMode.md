# Env.DarkMode.getIsDarkMode

# Env.DarkMode.getIsDarkMode
获取当前是否暗黑模式，该方法为异步调用。

## 可用性说明

权限要求 | 视图可用说明 | 平台可用 | 场景
--- | --- | --- | ---
可读 | 所有视图 | - PC  
- 移动端 | 演示模式

## 输入

无需传入参数。

## 输出

返回一个布尔值，true为暗黑模式，false为非暗黑模式

## 示例代码

### 调用示例

```js
const DocMiniApp = new BlockitClient().initAPI();
const isDarkModePromise = await docMiniApp.Env.DarkMode.getIsDarkMode();
console.log('debug', isDarkModePromise);
```

### 返回示例

```
false
```
