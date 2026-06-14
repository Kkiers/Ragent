# CanvasContext.quadraticCurveTo

# CanvasContext.quadraticCurveTo(number cpx, number cpy, number x, number y)

添加二次贝塞尔曲线到路径中

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
cpx | number | 是 |  | 控制点 x 坐标
cpy | number | 是 |  | 控制点 y 坐标
x | number | 是 |  | x 坐标
y | number | 是 |  | y 坐标

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
// Quadratic Bézier curve
ctx.beginPath();
ctx.moveTo(50, 20);
ctx.quadraticCurveTo(230, 30, 50, 100);
ctx.stroke();

// Start and end points
ctx.fillStyle = "blue";
ctx.beginPath();
ctx.arc(50, 20, 5, 0, 2 * Math.PI);   // Start point
ctx.fill();
ctx.beginPath();
ctx.arc(50, 100, 5, 0, 2 * Math.PI);  // End point
ctx.fill();

// Control point
ctx.fillStyle = "red";
ctx.beginPath();
ctx.arc(230, 30, 5, 0, 2 * Math.PI);
ctx.fill();

ctx.draw();
```
