# CanvasContext.setLineJoin

# CanvasContext.setLineJoin(string join)

设置线连接点样式

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
join | string | 是 |  | 线连接点样式  
**可选值**：  
- `bevel` 类似于弧形，但是用直线连接  
- `round` 弧形连接  
- `miter` 默认样式，正常连接

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
const lineJoin = ["round", "bevel", "miter"];
ctx.lineWidth = 10;

for (let i = 0; i < lineJoin.length; ++i) {
  ctx.setLineJoin(lineJoin[i]);
  ctx.beginPath();
  ctx.moveTo(10, 10 + i * 40);
  ctx.lineTo(50, 50 + i * 40);
  ctx.lineTo(90, 10 + i * 40);
  ctx.lineTo(130, 50 + i * 40);
  ctx.lineTo(170, 10 + i * 40);
  ctx.stroke();
}

ctx.draw();
```
