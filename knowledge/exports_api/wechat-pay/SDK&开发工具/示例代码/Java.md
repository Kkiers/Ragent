# Java

# Java

路径：SDK&开发工具/示例代码/Java

## 一、概述

本工具类 WXPayUtility 为使用 Java 接入微信支付的开发者提供了一系列实用的功能，包括 JSON 处理、密钥加载、加密签名、请求头构建、响应验证等。通过使用这个工具类，开发者可以更方便地完成与微信支付相关的开发工作。

## 二、安装（引入依赖的第三方库）

本工具类依赖以下第三方库：

1. Google Gson：用于 JSON 数据的序列化和反序列化。
2. OkHttp：用于 HTTP 请求处理。

你可以通过 Maven 或 Gradle 来引入这些依赖。

如果你使用的 [Gradle](https://gradle.org/)，请在 build.gradle 中加入：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1implementation 'com.google.code.gson:gson:${VERSION}'
2implementation 'com.squareup.okhttp3:okhttp:${VERSION}'
```

如果你使用的 [Maven](https://maven.apache.org/)，请在 pom.xml 中加入：
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1
2
3    com.google.code.gson
4    gson
5    ${VERSION}
6
7
8
9    com.squareup.okhttp3
10    okhttp
11    ${VERSION}
12
```

## 三、必需的证书和密钥

运行 SDK 必需以下的商户身份信息，用于构造请求的签名和验证应答的签名：

- [商户 API 私钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053053#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E5%95%86%E6%88%B7API%E8%AF%81%E4%B9%A6%E7%A7%81%E9%92%A5%EF%BC%9F)
- [商户 API 证书](https://pay.weixin.qq.com/doc/v3/merchant/4013053053)的证书序列号
- [APIv3 密钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053267)

## 四、工具类代码
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1package com.java.utils;
2
3import com.google.gson.ExclusionStrategy;
4import com.google.gson.FieldAttributes;
5import com.google.gson.Gson;
6import com.google.gson.GsonBuilder;
7import com.google.gson.JsonElement;
8import com.google.gson.JsonObject;
9import com.google.gson.JsonSyntaxException;
10import com.google.gson.annotations.Expose;
11import com.google.gson.annotations.SerializedName;
12import java.util.List;
13import java.util.Map.Entry;
14import okhttp3.Headers;
15import okhttp3.Response;
16import okio.BufferedSource;
17
18import javax.crypto.BadPaddingException;
19import javax.crypto.Cipher;
20import javax.crypto.IllegalBlockSizeException;
21import javax.crypto.NoSuchPaddingException;
22import javax.crypto.spec.GCMParameterSpec;
23import javax.crypto.spec.SecretKeySpec;
24import java.io.IOException;
25import java.io.UncheckedIOException;
26import java.io.UnsupportedEncodingException;
27import java.net.URLEncoder;
28import java.nio.charset.StandardCharsets;
29import java.nio.file.Files;
30import java.nio.file.Paths;
31import java.security.InvalidAlgorithmParameterException;
32import java.security.InvalidKeyException;
33import java.security.KeyFactory;
34import java.security.NoSuchAlgorithmException;
35import java.security.PrivateKey;
36import java.security.PublicKey;
37import java.security.SecureRandom;
38import java.security.Signature;
39import java.security.SignatureException;
40import java.security.spec.InvalidKeySpecException;
41import java.security.spec.PKCS8EncodedKeySpec;
42import java.security.spec.X509EncodedKeySpec;
43import java.time.DateTimeException;
44import java.time.Duration;
45import java.time.Instant;
46import java.util.Base64;
47import java.util.HashMap;
48import java.util.Map;
49import java.util.Objects;
50import java.security.MessageDigest;
51import java.io.InputStream;
52import org.bouncycastle.crypto.digests.SM3Digest;
53import org.bouncycastle.jce.provider.BouncyCastleProvider;
54import java.security.Security;
55
56public class WXPayUtility {
57    private static final Gson gson = new GsonBuilder()
58            .disableHtmlEscaping()
59            .addSerializationExclusionStrategy(new ExclusionStrategy() {
60                @Override
61                public boolean shouldSkipField(FieldAttributes fieldAttributes) {
62                    final Expose expose = fieldAttributes.getAnnotation(Expose.class);
63                    return expose != null && !expose.serialize();
64                }
65
66                @Override
67                public boolean shouldSkipClass(Class aClass) {
68                    return false;
69                }
70            })
71            .addDeserializationExclusionStrategy(new ExclusionStrategy() {
72                @Override
73                public boolean shouldSkipField(FieldAttributes fieldAttributes) {
74                    final Expose expose = fieldAttributes.getAnnotation(Expose.class);
75                    return expose != null && !expose.deserialize();
76                }
77
78                @Override
79                public boolean shouldSkipClass(Class aClass) {
80                    return false;
81                }
82            })
83            .create();
84    private static final char[] SYMBOLS =
85            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".toCharArray();
86    private static final SecureRandom random = new SecureRandom();
87
88    /**
89     * 将 Object 转换为 JSON 字符串
90     */
91    public static String toJson(Object object) {
92        return gson.toJson(object);
93    }
94
95    /**
96     * 将 JSON 字符串解析为特定类型的实例
97     */
98    public static  T fromJson(String json, Class classOfT) throws JsonSyntaxException {
99        return gson.fromJson(json, classOfT);
100    }
101
102    /**
103     * 从公私钥文件路径中读取文件内容
104     *
105     * @param keyPath 文件路径
106     * @return 文件内容
107     */
108    private static String readKeyStringFromPath(String keyPath) {
109        try {
110            return new String(Files.readAllBytes(Paths.get(keyPath)), StandardCharsets.UTF_8);
111        } catch (IOException e) {
112            throw new UncheckedIOException(e);
113        }
114    }
115
116    /**
117     * 读取 PKCS#8 格式的私钥字符串并加载为私钥对象
118     *
119     * @param keyString 私钥文件内容，以 -----BEGIN PRIVATE KEY----- 开头
120     * @return PrivateKey 对象
121     */
122    public static PrivateKey loadPrivateKeyFromString(String keyString) {
123        try {
124            keyString = keyString.replace("-----BEGIN PRIVATE KEY-----", "")
125                    .replace("-----END PRIVATE KEY-----", "")
126                    .replaceAll("\\s+", "");
127            return KeyFactory.getInstance("RSA").generatePrivate(
128                    new PKCS8EncodedKeySpec(Base64.getDecoder().decode(keyString)));
129        } catch (NoSuchAlgorithmException e) {
130            throw new UnsupportedOperationException(e);
131        } catch (InvalidKeySpecException e) {
132            throw new IllegalArgumentException(e);
133        }
134    }
135
136    /**
137     * 从 PKCS#8 格式的私钥文件中加载私钥
138     *
139     * @param keyPath 私钥文件路径
140     * @return PrivateKey 对象
141     */
142    public static PrivateKey loadPrivateKeyFromPath(String keyPath) {
143        return loadPrivateKeyFromString(readKeyStringFromPath(keyPath));
144    }
145
146    /**
147     * 读取 PKCS#8 格式的公钥字符串并加载为公钥对象
148     *
149     * @param keyString 公钥文件内容，以 -----BEGIN PUBLIC KEY----- 开头
150     * @return PublicKey 对象
151     */
152    public static PublicKey loadPublicKeyFromString(String keyString) {
153        try {
154            keyString = keyString.replace("-----BEGIN PUBLIC KEY-----", "")
155                    .replace("-----END PUBLIC KEY-----", "")
156                    .replaceAll("\\s+", "");
157            return KeyFactory.getInstance("RSA").generatePublic(
158                    new X509EncodedKeySpec(Base64.getDecoder().decode(keyString)));
159        } catch (NoSuchAlgorithmException e) {
160            throw new UnsupportedOperationException(e);
161        } catch (InvalidKeySpecException e) {
162            throw new IllegalArgumentException(e);
163        }
164    }
165
166    /**
167     * 从 PKCS#8 格式的公钥文件中加载公钥
168     *
169     * @param keyPath 公钥文件路径
170     * @return PublicKey 对象
171     */
172    public static PublicKey loadPublicKeyFromPath(String keyPath) {
173        return loadPublicKeyFromString(readKeyStringFromPath(keyPath));
174    }
175
176    /**
177     * 创建指定长度的随机字符串，字符集为[0-9a-zA-Z]，可用于安全相关用途
178     */
179    public static String createNonce(int length) {
180        char[] buf = new char[length];
181        for (int i = 0; i  0) {
481            result.append("&");
482        }
483
484        String valueString;
485        // 如果是基本类型、字符串或枚举，直接转换；如果是对象，序列化为JSON
486        if (value instanceof String || value instanceof Number ||
487                value instanceof Boolean || value instanceof Enum) {
488            valueString = value.toString();
489        } else {
490            valueString = toJson(value);
491        }
492
493        result.append(key)
494                .append("=")
495                .append(urlEncode(valueString));
496    }
497
498    /**
499     * 从应答中提取 Body
500     *
501     * @param response HTTP 请求应答对象
502     * @return 应答中的Body内容，Body为空时返回空字符串
503     */
504    public static String extractBody(Response response) {
505        if (response.body() == null) {
506            return "";
507        }
508
509        try {
510            BufferedSource source = response.body().source();
511            return source.readUtf8();
512        } catch (IOException e) {
513            throw new RuntimeException(String.format("An error occurred during reading response body. " +
514                    "Status: %d", response.code()), e);
515        }
516    }
517
518    /**
519     * 根据微信支付APIv3应答验签规则对应答签名进行验证，验证不通过时抛出异常
520     *
521     * @param wechatpayPublicKeyId 微信支付公钥ID
522     * @param wechatpayPublicKey   微信支付公钥对象
523     * @param headers              微信支付应答 Header 列表
524     * @param body                 微信支付应答 Body
525     */
526    public static void validateResponse(String wechatpayPublicKeyId, PublicKey wechatpayPublicKey,
527                                        Headers headers,
528                                        String body) {
529        String timestamp = headers.get("Wechatpay-Timestamp");
530        String requestId = headers.get("Request-ID");
531        try {
532            Instant responseTime = Instant.ofEpochSecond(Long.parseLong(timestamp));
533            // 拒绝过期请求
534            if (Duration.between(responseTime, Instant.now()).abs().toMinutes() >= 5) {
535                throw new IllegalArgumentException(
536                        String.format("Validate response failed, timestamp[%s] is expired, request-id[%s]",
537                                timestamp, requestId));
538            }
539        } catch (DateTimeException | NumberFormatException e) {
540            throw new IllegalArgumentException(
541                    String.format("Validate response failed, timestamp[%s] is invalid, request-id[%s]",
542                            timestamp, requestId));
543        }
544        String serialNumber = headers.get("Wechatpay-Serial");
545        if (!Objects.equals(serialNumber, wechatpayPublicKeyId)) {
546            throw new IllegalArgumentException(
547                    String.format("Validate response failed, Invalid Wechatpay-Serial, Local: %s, Remote: " +
548                            "%s", wechatpayPublicKeyId, serialNumber));
549        }
550
551        String signature = headers.get("Wechatpay-Signature");
552        String message = String.format("%s\n%s\n%s\n", timestamp, headers.get("Wechatpay-Nonce"),
553                body == null ? "" : body);
554
555        boolean success = verify(message, signature, "SHA256withRSA", wechatpayPublicKey);
556        if (!success) {
557            throw new IllegalArgumentException(
558                    String.format("Validate response failed,the WechatPay signature is incorrect.%n"
559                                    + "Request-ID[%s]\tresponseHeader[%s]\tresponseBody[%.1024s]",
560                            headers.get("Request-ID"), headers, body));
561        }
562    }
563
564    /**
565     * 根据微信支付APIv3通知验签规则对通知签名进行验证，验证不通过时抛出异常
566     * @param wechatpayPublicKeyId 微信支付公钥ID
567     * @param wechatpayPublicKey 微信支付公钥对象
568     * @param headers 微信支付通知 Header 列表
569     * @param body 微信支付通知 Body
570     */
571    public static void validateNotification(String wechatpayPublicKeyId,
572                                            PublicKey wechatpayPublicKey, Headers headers,
573                                            String body) {
574        String timestamp = headers.get("Wechatpay-Timestamp");
575        try {
576            Instant responseTime = Instant.ofEpochSecond(Long.parseLong(timestamp));
577            // 拒绝过期请求
578            if (Duration.between(responseTime, Instant.now()).abs().toMinutes() >= 5) {
579                throw new IllegalArgumentException(
580                        String.format("Validate notification failed, timestamp[%s] is expired", timestamp));
581            }
582        } catch (DateTimeException | NumberFormatException e) {
583            throw new IllegalArgumentException(
584                    String.format("Validate notification failed, timestamp[%s] is invalid", timestamp));
585        }
586        String serialNumber = headers.get("Wechatpay-Serial");
587        if (!Objects.equals(serialNumber, wechatpayPublicKeyId)) {
588            throw new IllegalArgumentException(
589                    String.format("Validate notification failed, Invalid Wechatpay-Serial, Local: %s, " +
590                                    "Remote: %s",
591                            wechatpayPublicKeyId,
592                            serialNumber));
593        }
594
595        String signature = headers.get("Wechatpay-Signature");
596        String message = String.format("%s\n%s\n%s\n", timestamp, headers.get("Wechatpay-Nonce"),
597                body == null ? "" : body);
598
599        boolean success = verify(message, signature, "SHA256withRSA", wechatpayPublicKey);
600        if (!success) {
601            throw new IllegalArgumentException(
602                    String.format("Validate notification failed, WechatPay signature is incorrect.\n"
603                                    + "responseHeader[%s]\tresponseBody[%.1024s]",
604                            headers, body));
605        }
606    }
607
608    /**
609     * 对微信支付通知进行签名验证、解析，同时将业务数据解密。验签名失败、解析失败、解密失败时抛出异常
610     * @param apiv3Key 商户的 APIv3 Key
611     * @param wechatpayPublicKeyId 微信支付公钥ID
612     * @param wechatpayPublicKey   微信支付公钥对象
613     * @param headers              微信支付请求 Header 列表
614     * @param body                 微信支付请求 Body
615     * @return 解析后的通知内容，解密后的业务数据可以使用 Notification.getPlaintext() 访问
616     */
617    public static Notification parseNotification(String apiv3Key, String wechatpayPublicKeyId,
618                                                 PublicKey wechatpayPublicKey, Headers headers,
619                                                 String body) {
620        validateNotification(wechatpayPublicKeyId, wechatpayPublicKey, headers, body);
621        Notification notification = gson.fromJson(body, Notification.class);
622        notification.decrypt(apiv3Key);
623        return notification;
624    }
625
626    /**
627     * 微信支付API错误异常，发送HTTP请求成功，但返回状态码不是 2XX 时抛出本异常
628     */
629    public static class ApiException extends RuntimeException {
630        private static final long serialVersionUID = 2261086748874802175L;
631
632        private final int statusCode;
633        private final String body;
634        private final Headers headers;
635        private final String errorCode;
636        private final String errorMessage;
637
638        public ApiException(int statusCode, String body, Headers headers) {
639            super(String.format("微信支付API访问失败，StatusCode: [%s], Body: [%s], Headers: [%s]", statusCode,
640                    body, headers));
641            this.statusCode = statusCode;
642            this.body = body;
643            this.headers = headers;
644
645            if (body != null && !body.isEmpty()) {
646                JsonElement code;
647                JsonElement message;
648
649                try {
650                    JsonObject jsonObject = gson.fromJson(body, JsonObject.class);
651                    code = jsonObject.get("code");
652                    message = jsonObject.get("message");
653                } catch (JsonSyntaxException ignored) {
654                    code = null;
655                    message = null;
656                }
657                this.errorCode = code == null ? null : code.getAsString();
658                this.errorMessage = message == null ? null : message.getAsString();
659            } else {
660                this.errorCode = null;
661                this.errorMessage = null;
662            }
663        }
664
665        /**
666         * 获取 HTTP 应答状态码
667         */
668        public int getStatusCode() {
669            return statusCode;
670        }
671
672        /**
673         * 获取 HTTP 应答包体内容
674         */
675        public String getBody() {
676            return body;
677        }
678
679        /**
680         * 获取 HTTP 应答 Header
681         */
682        public Headers getHeaders() {
683            return headers;
684        }
685
686        /**
687         * 获取 错误码 （错误应答中的 code 字段）
688         */
689        public String getErrorCode() {
690            return errorCode;
691        }
692
693        /**
694         * 获取 错误消息 （错误应答中的 message 字段）
695         */
696        public String getErrorMessage() {
697            return errorMessage;
698        }
699    }
700
701    public static class Notification {
702        @SerializedName("id")
703        private String id;
704        @SerializedName("create_time")
705        private String createTime;
706        @SerializedName("event_type")
707        private String eventType;
708        @SerializedName("resource_type")
709        private String resourceType;
710        @SerializedName("summary")
711        private String summary;
712        @SerializedName("resource")
713        private Resource resource;
714        private String plaintext;
715
716        public String getId() {
717            return id;
718        }
719
720        public String getCreateTime() {
721            return createTime;
722        }
723
724        public String getEventType() {
725            return eventType;
726        }
727
728        public String getResourceType() {
729            return resourceType;
730        }
731
732        public String getSummary() {
733            return summary;
734        }
735
736        public Resource getResource() {
737            return resource;
738        }
739
740        /**
741         * 获取解密后的业务数据（JSON字符串，需要自行解析）
742         */
743        public String getPlaintext() {
744            return plaintext;
745        }
746
747        private void validate() {
748            if (resource == null) {
749                throw new IllegalArgumentException("Missing required field `resource` in notification");
750            }
751            resource.validate();
752        }
753
754        /**
755         * 使用 APIv3Key 对通知中的业务数据解密，解密结果可以通过 getPlainText 访问。
756         * 外部拿到的 Notification 一定是解密过的，因此本方法没有设置为 public
757         * @param apiv3Key 商户APIv3 Key
758         */
759        private void decrypt(String apiv3Key) {
760            validate();
761
762            plaintext = aesAeadDecrypt(
763                    apiv3Key.getBytes(StandardCharsets.UTF_8),
764                    resource.associatedData.getBytes(StandardCharsets.UTF_8),
765                    resource.nonce.getBytes(StandardCharsets.UTF_8),
766                    Base64.getDecoder().decode(resource.ciphertext)
767            );
768        }
769
770        public static class Resource {
771            @SerializedName("algorithm")
772            private String algorithm;
773
774            @SerializedName("ciphertext")
775            private String ciphertext;
776
777            @SerializedName("associated_data")
778            private String associatedData;
779
780            @SerializedName("nonce")
781            private String nonce;
782
783            @SerializedName("original_type")
784            private String originalType;
785
786            public String getAlgorithm() {
787                return algorithm;
788            }
789
790            public String getCiphertext() {
791                return ciphertext;
792            }
793
794            public String getAssociatedData() {
795                return associatedData;
796            }
797
798            public String getNonce() {
799                return nonce;
800            }
801
802            public String getOriginalType() {
803                return originalType;
804            }
805
806            private void validate() {
807                if (algorithm == null || algorithm.isEmpty()) {
808                    throw new IllegalArgumentException("Missing required field `algorithm` in Notification" +
809                            ".Resource");
810                }
811                if (!Objects.equals(algorithm, "AEAD_AES_256_GCM")) {
812                    throw new IllegalArgumentException(String.format("Unsupported `algorithm`[%s] in " +
813                            "Notification.Resource", algorithm));
814                }
815
816                if (ciphertext == null || ciphertext.isEmpty()) {
817                    throw new IllegalArgumentException("Missing required field `ciphertext` in Notification" +
818                            ".Resource");
819                }
820
821                if (associatedData == null || associatedData.isEmpty()) {
822                    throw new IllegalArgumentException("Missing required field `associatedData` in " +
823                            "Notification.Resource");
824                }
825
826                if (nonce == null || nonce.isEmpty()) {
827                    throw new IllegalArgumentException("Missing required field `nonce` in Notification" +
828                            ".Resource");
829                }
830
831                if (originalType == null || originalType.isEmpty()) {
832                    throw new IllegalArgumentException("Missing required field `originalType` in " +
833                            "Notification.Resource");
834                }
835            }
836        }
837    }
838    /**
839     * 根据文件名获取对应的Content-Type
840     * @param fileName 文件名
841     * @return Content-Type字符串
842     */
843    public static String getContentTypeByFileName(String fileName) {
844        if (fileName == null || fileName.isEmpty()) {
845            return "application/octet-stream";
846        }
847
848        // 获取文件扩展名
849        String extension = "";
850        int lastDotIndex = fileName.lastIndexOf('.');
851        if (lastDotIndex > 0 && lastDotIndex ();
857        // 图片类型
858        contentTypeMap.put("png", "image/png");
859        contentTypeMap.put("jpg", "image/jpeg");
860        contentTypeMap.put("jpeg", "image/jpeg");
861        contentTypeMap.put("gif", "image/gif");
862        contentTypeMap.put("bmp", "image/bmp");
863        contentTypeMap.put("webp", "image/webp");
864        contentTypeMap.put("svg", "image/svg+xml");
865        contentTypeMap.put("ico", "image/x-icon");
866
867        // 文档类型
868        contentTypeMap.put("pdf", "application/pdf");
869        contentTypeMap.put("doc", "application/msword");
870        contentTypeMap.put("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
871        contentTypeMap.put("xls", "application/vnd.ms-excel");
872        contentTypeMap.put("xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
873        contentTypeMap.put("ppt", "application/vnd.ms-powerpoint");
874        contentTypeMap.put("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation");
875
876        // 文本类型
877        contentTypeMap.put("txt", "text/plain");
878        contentTypeMap.put("html", "text/html");
879        contentTypeMap.put("css", "text/css");
880        contentTypeMap.put("js", "application/javascript");
881        contentTypeMap.put("json", "application/json");
882        contentTypeMap.put("xml", "application/xml");
883        contentTypeMap.put("csv", "text/csv");
884
885        // 音视频类型
886        contentTypeMap.put("mp3", "audio/mpeg");
887        contentTypeMap.put("wav", "audio/wav");
888        contentTypeMap.put("mp4", "video/mp4");
889        contentTypeMap.put("avi", "video/x-msvideo");
890        contentTypeMap.put("mov", "video/quicktime");
891
892        // 压缩文件类型
893        contentTypeMap.put("zip", "application/zip");
894        contentTypeMap.put("rar", "application/x-rar-compressed");
895        contentTypeMap.put("7z", "application/x-7z-compressed");
896
897
898        return contentTypeMap.getOrDefault(extension, "application/octet-stream");
899    }
900}
```
