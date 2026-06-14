# CanvasContext.fill

# CanvasContext.fill()

填充当前路径

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
// begin path
ctx.rect(10, 10, 100, 30);
ctx.fillStyle = "yellow";
ctx.fill();

ctx.beginPath();
ctx.rect(10, 40, 100, 30);

// only fill this rect, not in current path
ctx.setFillStyle("blue");
ctx.fillRect(10, 70, 100, 30);

ctx.rect(10, 100, 100, 30);

// it will fill current path
ctx.setFillStyle("red");
ctx.fill();
ctx.draw();
```
