# IWidgetField

# IWidgetField
字段实例，类型如下：
<br><br>

```js
interface IWidgetField{
    id: string;
    tableId: string;
    /** 获取字段名 */
    getName(): Promise<string>;
    /** 获取字段类型 */
    getType(): Promise<FieldType>;
    /** 获取公式代理列类型 */
    getProxyType(): Promise<FieldType | void>;
    /** 获取 cellValue 并转化为 string 格式 */
    getCellString(recordId: string): Promise<string>;
    /** 获取当前 field meta 信息 */
    getMeta(): Promise<IFieldMeta>;
    /** 获取整列不为空的 cellValue */
    getFieldValueList(): Promise<(IFieldValue | IUndefinedFieldValue)[]>;
}

```
