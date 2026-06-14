# table.getViewById

# table.getViewById
根据id获取视图实例[IWidgetView](https://open.feishu.cn/document/uAjLw4CM/uYjL24iN/base-extensions/base-view-extensions/data-type/iwidgetview)。

## 权限要求
**Notice**：开启以下任一权限
查看、评论、编辑和管理多维表格(bitable:app)
查看、评论和导出多维表格(bitable:app:readonly)

## 输入
```
getViewById(viewId)
```

名称 | 数据类型 | 是否必填 | 描述
--- | --- | --- | ---
viewId | string | 是 | 视图id

## 输出
Promise视图实例[IWidgetView](https://open.feishu.cn/document/uAjLw4CM/uYjL24iN/base-extensions/base-view-extensions/data-type/iwidgetview)。

## 示例代码

```js
const viewMetaList = await table.getViewMetaList();// 获取数据表视图元信息列表

const res = await table.getViewById(viewMetaList[0].id);
```
