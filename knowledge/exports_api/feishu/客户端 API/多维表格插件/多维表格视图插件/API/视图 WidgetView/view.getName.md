# view.getName

# view.getName
获取视图名字。

## 权限要求
**Notice**：开启以下任一权限
查看、评论、编辑和管理多维表格(bitable:app)
查看、评论和导出多维表格(bitable:app:readonly)

## 示例代码
### 调用示例

```js
const selection = await bitable.base.getSelection();
const table = await bitable.base.getTableById(selection.tableId);
const viewMetaList = await table.getViewMetaList();
const view = await table.getViewById(viewMetaList[0].id);

const res = await view.getName(); // '表格'
```

### 返回示例
res:
```
'表格'
```
