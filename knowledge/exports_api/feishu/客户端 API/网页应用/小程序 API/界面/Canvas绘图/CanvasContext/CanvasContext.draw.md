# CanvasContext.draw

# CanvasContext.draw(boolean reverse, function callback)

将所有的操作绘制到 Canvas 中

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
reverse | boolean | 否 | false | 是否保留之前的 Canvas 绘制结果
callback | function | 否 |  | 绘制完成之后触发回调函数

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.setFillStyle("red");
ctx.fillRect(10, 10, 150, 100);
ctx.draw();
ctx.fillRect(50, 50, 150, 100);
ctx.draw(true, () => {
  console.log("Last Draw End.");
});
```
