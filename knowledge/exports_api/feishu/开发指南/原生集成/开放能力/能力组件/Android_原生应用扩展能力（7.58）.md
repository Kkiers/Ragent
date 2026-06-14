# Android 原生应用扩展能力（7.58）

# Android 原生应用扩展能力（7.58）

| 组件名称 | 组件类型 | 组件版本 | 生效基线 |
| --- | --- | --- | --- |
| native-app-extension-ability | 协议组件 | 2.0.5-release | 7.58.0 |

## 功能简介
通过调用飞书开放平台的 OpenAPI 能力，开发者的原生应用可以调用飞书开放平台接口，实现更丰富和个性化的功能；通过实现对应的协议 API，可以将自有的原生集成的业务逻辑、能力，暴露给基于飞书小程序、H5 开发的页面，供其通过 JsBridge 调用

### 更新日志
- 新增 `INativeAppPluginFactory` 作用域注解 `@TrimisScope(ScopeType.GLOBAL)`，声明工厂实现为全局作用域
- `INativeAppPluginFactory` 新增 `getPluginApiNames()`，用于返回插件支持的全部 API 名称列表

## 示例代码
完整示例请查看 [SampleApp](https://github.com/larksuite/alchemy_app_demo/tree/main/alchemy_app_demo_android)

```java
import com.ss.android.lark.plugin.annotation.TrimisImpl;
import com.ss.android.lark.extension_interfaces.INativeAppPluginFactory;
import com.ss.android.lark.extension_interfaces.INativeAppPlugin;
import java.util.Arrays;
import java.util.List;

@TrimisImpl(INativeAppPluginFactory.class)
public class SamplePluginFactory implements INativeAppPluginFactory {
    @Override
    public String getPluginName() {
        return "samplePlugin";
    }

@Override
    public List<String> getPluginApiNames() {
        return Arrays.asList("sampleAPI1", "sampleAPI2");
    }

@Override
    public INativeAppPlugin createPlugin() {
        return new SamplePlugin();
    }
}
```

## INTERFACE
### IApiCallback
Api 回调接口

```java
interface IApiCallback {
    void onResult(ApiResult result, JSONObject data); // 结果回调
}
```

#### 方法列表
#### `onResult(ApiResult result, JSONObject data)`
结果回调

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| result | ApiResult | 是 | 调用结果 |
| data | JSONObject | 是 | 返回数据 |

### IApiGateway
客户端 Open API 调用

```java
interface IApiGateway {
    void invokeLarkApi(Context context, NativeAppPluginEvent event, IApiCallback callback); // 调用飞书客户端 OpenAPI
}
```

#### 方法列表
#### `invokeLarkApi(Context context, NativeAppPluginEvent event, IApiCallback callback)`
调用飞书客户端 OpenAPI

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| context | Context | 是 | 上下文 |
| event | NativeAppPluginEvent | 是 | 事件 |
| callback | IApiCallback | 否 | 回调 |

### INativeAppPlugin
自定义 JS API 实现类

```java
interface INativeAppPlugin {
    void onCreate(INativeAppPluginContext pluginContext); // plugin onCreate
    NativeAppPluginResult handleEvent(Context context, NativeAppPluginEvent event, IApiCallback callback); // 事件处理方法
    boolean handleActivityResult(int requestCode, int resultCode, Intent data); // 接收 onActivityResult
    void release(); // release plugin
}
```

#### 方法列表
#### `onCreate(INativeAppPluginContext pluginContext)`
plugin onCreate

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| pluginContext | INativeAppPluginContext | 是 | 插件上下文 |

#### `handleEvent(Context context, NativeAppPluginEvent event, IApiCallback callback)`
事件处理方法

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| context | Context | 是 | context |
| event | NativeAppPluginEvent | 是 | event |
| callback | IApiCallback | 否 | callback |

**返回值**：NativeAppPluginResult 处理结果

#### `handleActivityResult(int requestCode, int resultCode, Intent data)`
接收 onActivityResult

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| requestCode | int | 是 | 请求码 |
| resultCode | int | 是 | 结果码 |
| data | Intent | 是 | 数据 |

**返回值**：boolean 是否处理

#### `release()`
release plugin

### INativeAppPluginContext
NativeAppPlugin 上下文

```java
interface INativeAppPluginContext {
    void fireEvent(NativeAppCustomEvent event); // 向 JS 发送第三方 Event
}
```

#### 方法列表
#### `fireEvent(NativeAppCustomEvent event)`
向 JS 发送第三方 Event

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| event | NativeAppCustomEvent | 是 | 事件 |

### INativeAppPluginFactory
自定义 JS API 的工厂

```java
@TrimisScope(ScopeType.GLOBAL)
interface INativeAppPluginFactory {
    String getPluginName(); // 返回 Plugin 唯一的名字，用于后续的注册与调用
    List<String> getPluginApiNames(); // 返回 Plugin 支持的 api name list
    INativeAppPlugin createPlugin(); // 返回 INativeAppPlugin 实例
}
```

#### 方法列表
#### `getPluginName()`
返回 Plugin 唯一的名字，用于后续的注册与调用

**返回值**：String 插件名称

#### `getPluginApiNames()`
返回 Plugin 支持的 api name list

**返回值**：List<String> api name list

#### `createPlugin()`
返回 INativeAppPlugin 实例

**返回值**：INativeAppPlugin native app plugin

## CLASS
### NativeAppCustomEvent
自定义事件模型

```java
class NativeAppCustomEvent implements Parcelable {
    String getEventName(); // 获取事件名
    void setEventName(String eventName); // 设置事件名
    JSONObject getParams(); // 获取参数
    void setParams(JSONObject params); // 设置参数
}
```

#### 方法列表
#### `getEventName()`
获取事件名

**返回值**：String 事件名

#### `setEventName(String eventName)`
设置事件名

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| eventName | String | 是 | 事件名 |

#### `getParams()`
获取参数

**返回值**：JSONObject 参数

#### `setParams(JSONObject params)`
设置参数

| 参数名称 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| params | JSONObject | 是 | 参数 |

### NativeAppPluginEvent
前端调用事件模型

```java
class NativeAppPluginEvent implements Parcelable {
    String getEventName(); // 获取 API 名称
    JSONObject getParams(); // 获取参数
    String getAppId(); // 获取应用 ID
}
```

#### 方法列表
#### `getEventName()`
获取 API 名称

**返回值**：String API 名称

#### `getParams()`
获取参数

**返回值**：JSONObject 参数

#### `getAppId()`
获取应用 ID

**返回值**：String 应用 ID

### NativeAppPluginResult
Js API 调用结果

```java
class NativeAppPluginResult implements Parcelable {
    JSONObject getResult(); // 获取结果
    int getErrorCode(); // 获取错误码
    String getErrorMsg(); // 获取错误信息
}
```

#### 方法列表
#### `getResult()`
获取结果

**返回值**：JSONObject 结果

#### `getErrorCode()`
获取错误码

**返回值**：int 错误码

#### `getErrorMsg()`
获取错误信息

**返回值**：String 错误信息

## ENUM
### ApiResult
API 调用结果枚举

```java
enum ApiResult {
    SUCCESS, // 成功
    FAIL     // 失败
}
```

#### 枚举成员
| 成员名 | 值 | 描述 |
| --- | --- | --- |
| SUCCESS | 0 | 成功 |
| FAIL | 1 | 失败 |

## ANNOTATION
### ApiGateway
仅供飞书侧使用

```java
@BasePlugin(value = IApiGateway.class)
@interface ApiGateway {
}
```

### NativeAppPlugin
仅供飞书侧使用

```java
@BasePlugin(value = INativeAppPlugin.class)
@interface NativeAppPlugin {
}
```

### NativeAppPluginFactory
仅供飞书侧使用

```java
@BasePlugin(value = INativeAppPluginFactory.class)
@interface NativeAppPluginFactory {
}
```

## CONSTANT
### NativeAppPluginResult
错误码常量

```java
static final int ERROR_CODE_NO_ERROR = 0;
static final String ERROR_MSG_NO_ERROR = "ok";
```

| 常量名 | 类型 | 值 | 描述 |
| --- | --- | --- | --- |
| ERROR_CODE_NO_ERROR | int | 0 | 无错误 |
| ERROR_MSG_NO_ERROR | String | "ok" | 无错误描述 |
