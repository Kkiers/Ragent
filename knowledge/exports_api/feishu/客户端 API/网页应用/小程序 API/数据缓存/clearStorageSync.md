# clearStorageSync

# clearStorageSync

调用 clearStorageSync() 清理全部本地缓存数据。

## 支持说明

该接口仅支持小程序调用，对应的客户端版本支持情况如下所示。

应用能力 | Android | iOS | PC | Harmony | 预览效果
--- | --- | --- | --- | --- | ---
小程序 | **✓** | **✓** | **✓** | V7.35.0+ | [预览](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=%2Fpage%2FAPI%2Fpages%2Fstorage%2Fstorage)
网页应用 | **x** | **x** | **x** | **x** | /

## 输入
无

## 输出
无

## 示例代码

下载示例代码

<div style="display: flex">
      [预览小程序](https://applink.feishu.cn/client/mini_program/open?appId=cli_9dff7f6ae02ad104&path=%2Fpage%2FAPI%2Fpages%2Fstorage%2Fstorage)

</div> 

```js
try {
    tt.clearStorageSync();
} catch (error) {
    console.log(`clearStorageSync fail: ${JSON.stringify(error)}`);
}
```
