# VideoContext.play

# VideoContext.play()

播放视频

## 支持说明

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | V4.3.0+ | V4.3.0+ | V6.1.0+ | V7.35.0+ | [预览](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=page%2Fcomponent%2Fpages%2Fvideo%2Fvideo)
网页应用 | **X** | **X** | **X** | **X** | /

## 输入
无

## 输出
无

## 示例代码

下载示例代码

<div style="display: flex">
          [预览小程序](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=page%2Fcomponent%2Fpages%2Fvideo%2Fvideo)

</div> 

```html
<video id="myVideo"
  src="http://sf3-cn.feishucdn.com/obj/ttfe/tma/test.mp4"
  loop="{{true}}"
  initial-time=5
  auto-fullscreen="{{true}}"
  bindtimeupdate="bindupdatetime"
  muted="{{myMuted}}">
</video>
```

```js
Page({
  onReady (res) {
    this.videoContext = tt.createVideoContext('myVideo');
    this.videoContext.play();
  },
  pause: function () {
      this.videoContext.pause();
  }
})
```
