# CanvasContext.save

# CanvasContext.save()

创建新的绘图上下文，并将之前的上下文保存在栈中

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
// save the default fill style
ctx.save();
ctx.setFillStyle("red");
ctx.fillRect(10, 10, 150, 100);

// restore to the previous saved state
ctx.restore();
ctx.fillRect(50, 50, 150, 100);

ctx.draw();
```
