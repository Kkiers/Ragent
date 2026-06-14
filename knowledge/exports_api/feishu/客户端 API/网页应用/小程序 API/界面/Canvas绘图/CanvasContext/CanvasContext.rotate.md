# CanvasContext.rotate

# CanvasContext.rotate(number angle)

旋转坐标点

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
angle | number | 是 |  | 旋转弧度

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.strokeRect(100, 10, 150, 100);
ctx.rotate(20 * Math.PI / 180);
ctx.strokeRect(100, 10, 150, 100);
ctx.rotate(20 * Math.PI / 180);
ctx.strokeRect(100, 10, 150, 100);

ctx.draw();
```
