# CanvasContext.clip

# CanvasContext.clip()

剪切当前路径，限制后续的渲染范围

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

无

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.save();
ctx.arc(100, 100, 75, 0, Math.PI * 2, false);
ctx.clip();
ctx.fillRect(0, 0, 100, 100);

ctx.restore();
ctx.draw();
```
