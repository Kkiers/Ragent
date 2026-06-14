# CanvasContext.setLineWidth

# CanvasContext.setLineWidth(number width)

设置线宽

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
width | number | 是 |  | 线宽，单位 px

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
const lineWidthList = [5, 10, 15, 20];

for (let i = 0; i < lineWidthList.length; ++i) {
  ctx.setLineWidth(lineWidthList[i]);
  ctx.beginPath();
  ctx.moveTo(10, 10 + i * 20);
  ctx.lineTo(150, 10 + i * 20);
  ctx.stroke();
}

ctx.draw();
```
