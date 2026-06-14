# CanvasContext.createLinearGradient

# CanvasContext.createLinearGradient(number x0, number y0, number x1, number y1)

创建线性渐变对象

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
x0 | number | 是 |  | 起始点 X 坐标
y0 | number | 是 |  | 起始点 Y 坐标
x1 | number | 是 |  | 终止点的 X 坐标
y1 | number | 是 |  | 终止点的 Y 坐标

## 输出

返回值：
`CanvasLinearGradient`

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
// Create linear gradient
const gradient = ctx.createLinearGradient(0, 0, 200, 0);
gradient.addColorStop(0, "red");
gradient.addColorStop(1, "white");

// Fill with gradient
ctx.setFillStyle(gradient);
ctx.fillRect(10, 10, 150, 80);

ctx.draw();
```
