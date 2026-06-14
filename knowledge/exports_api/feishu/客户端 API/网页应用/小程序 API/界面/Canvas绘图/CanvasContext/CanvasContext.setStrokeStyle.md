# CanvasContext.setStrokeStyle

# CanvasContext.setStrokeStyle(string | CanvasPattern | CanvasGradient style)

设置绘制线样式

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
style | string | CanvasPattern | CanvasGradient | 是 |  | 线样式，兼容 CSS Color 值、模式对象、渐变对象

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.setStrokeStyle("red");
ctx.strokeRect(10, 10, 150, 75);

ctx.draw();
```
