# CanvasContext.strokeText

# CanvasContext.strokeText(string text, number x, number y, number maxWidth)

绘制文字路径

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | 预览
网页应用 | **X** | **X** | **X** | **X** | /

## 输入

名称 | 数据类型 | 必填 | 默认值 | 描述
--- | --- | --- | --- | ---
text | string | 是 |  | 文字
x | number | 是 |  | y 坐标
y | number | 是 |  | y 坐标
maxWidth | number | 否 |  | 文字最大宽度

## 输出

无

## 示例代码

下载示例代码

<div style="display: flex">
    预览小程序

</div> 

```javascript
ctx.setFontSize(20);
ctx.strokeText("Hello Block!", 20, 20);

ctx.draw();
```
