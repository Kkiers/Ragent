# Go

# Go

路径：SDK&开发工具/示例代码/Go

## 一、概述

本工具类 wxpay_utility 为使用 Go 接入微信支付的开发者提供了一系列实用的功能，包括 JSON 处理、密钥加载、加密签名、请求头构建、响应验证等。通过使用这个工具类，开发者可以更方便地完成与微信支付相关的开发工作。

## 二、环境要求

- Go 1.16+

## 三、必需的证书和密钥

运行 SDK 必需以下的商户身份信息，用于构造请求的签名和验证应答的签名：

- [商户 API 私钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053053#%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E5%95%86%E6%88%B7API%E8%AF%81%E4%B9%A6%E7%A7%81%E9%92%A5%EF%BC%9F)
- [商户 API 证书](https://pay.weixin.qq.com/doc/v3/merchant/4013053053)的证书序列号
- [APIv3 密钥](https://pay.weixin.qq.com/doc/v3/merchant/4013053267)

## 四、工具类代码
![](https://gtimg.wechatpay.cn/resource/xres/img/202409/5236a3a065efe1276d29855d7cad26f8_16x16.svg)
```
1package wxpay_utility
2
3import (
4	"bytes"
5	"crypto"
6	"crypto/aes"
7	"crypto/cipher"
8	"crypto/rand"
9	"crypto/rsa"
10	"crypto/sha1"
11	"crypto/sha256"
12	"crypto/x509"
13	"encoding/base64"
14	"encoding/json"
15	"encoding/pem"
16	"errors"
17	"fmt"
18	"hash"
19	"io"
20	"net/http"
21	"os"
22	"strconv"
23	"time"
24
25	"github.com/tjfoc/gmsm/sm3"
26)
27
28// MchConfig 商户信息配置，用于调用商户API
29type MchConfig struct {
30	mchId                      string
31	certificateSerialNo        string
32	privateKeyFilePath         string
33	wechatPayPublicKeyId       string
34	wechatPayPublicKeyFilePath string
35	privateKey                 *rsa.PrivateKey
36	wechatPayPublicKey         *rsa.PublicKey
37}
38
39// MchId 商户号
40func (c *MchConfig) MchId() string {
41	return c.mchId
42}
43
44// CertificateSerialNo 商户API证书序列号
45func (c *MchConfig) CertificateSerialNo() string {
46	return c.certificateSerialNo
47}
48
49// PrivateKey 商户API证书对应的私钥
50func (c *MchConfig) PrivateKey() *rsa.PrivateKey {
51	return c.privateKey
52}
53
54// WechatPayPublicKeyId 微信支付公钥ID
55func (c *MchConfig) WechatPayPublicKeyId() string {
56	return c.wechatPayPublicKeyId
57}
58
59// WechatPayPublicKey 微信支付公钥
60func (c *MchConfig) WechatPayPublicKey() *rsa.PublicKey {
61	return c.wechatPayPublicKey
62}
63
64// CreateMchConfig MchConfig 构造函数
65func CreateMchConfig(
66	mchId string,
67	certificateSerialNo string,
68	privateKeyFilePath string,
69	wechatPayPublicKeyId string,
70	wechatPayPublicKeyFilePath string,
71) (*MchConfig, error) {
72	mchConfig := &MchConfig{
73		mchId:                      mchId,
74		certificateSerialNo:        certificateSerialNo,
75		privateKeyFilePath:         privateKeyFilePath,
76		wechatPayPublicKeyId:       wechatPayPublicKeyId,
77		wechatPayPublicKeyFilePath: wechatPayPublicKeyFilePath,
78	}
79	privateKey, err := LoadPrivateKeyWithPath(mchConfig.privateKeyFilePath)
80	if err != nil {
81		return nil, err
82	}
83	mchConfig.privateKey = privateKey
84	wechatPayPublicKey, err := LoadPublicKeyWithPath(mchConfig.wechatPayPublicKeyFilePath)
85	if err != nil {
86		return nil, err
87	}
88	mchConfig.wechatPayPublicKey = wechatPayPublicKey
89	return mchConfig, nil
90}
91
92// LoadPrivateKey 通过私钥的文本内容加载私钥
93func LoadPrivateKey(privateKeyStr string) (privateKey *rsa.PrivateKey, err error) {
94	block, _ := pem.Decode([]byte(privateKeyStr))
95	if block == nil {
96		return nil, fmt.Errorf("decode private key err")
97	}
98	if block.Type != "PRIVATE KEY" {
99		return nil, fmt.Errorf("the kind of PEM should be PRVATE KEY")
100	}
101	key, err := x509.ParsePKCS8PrivateKey(block.Bytes)
102	if err != nil {
103		return nil, fmt.Errorf("parse private key err:%s", err.Error())
104	}
105	privateKey, ok := key.(*rsa.PrivateKey)
106	if !ok {
107		return nil, fmt.Errorf("not a RSA private key")
108	}
109	return privateKey, nil
110}
111
112// LoadPublicKey 通过公钥的文本内容加载公钥
113func LoadPublicKey(publicKeyStr string) (publicKey *rsa.PublicKey, err error) {
114	block, _ := pem.Decode([]byte(publicKeyStr))
115	if block == nil {
116		return nil, errors.New("decode public key error")
117	}
118	if block.Type != "PUBLIC KEY" {
119		return nil, fmt.Errorf("the kind of PEM should be PUBLIC KEY")
120	}
121	key, err := x509.ParsePKIXPublicKey(block.Bytes)
122	if err != nil {
123		return nil, fmt.Errorf("parse public key err:%s", err.Error())
124	}
125	publicKey, ok := key.(*rsa.PublicKey)
126	if !ok {
127		return nil, fmt.Errorf("%s is not rsa public key", publicKeyStr)
128	}
129	return publicKey, nil
130}
131
132// LoadPrivateKeyWithPath 通过私钥的文件路径内容加载私钥
133func LoadPrivateKeyWithPath(path string) (privateKey *rsa.PrivateKey, err error) {
134	privateKeyBytes, err := os.ReadFile(path)
135	if err != nil {
136		return nil, fmt.Errorf("read private pem file err:%s", err.Error())
137	}
138	return LoadPrivateKey(string(privateKeyBytes))
139}
140
141// LoadPublicKeyWithPath 通过公钥的文件路径加载公钥
142func LoadPublicKeyWithPath(path string) (publicKey *rsa.PublicKey, err error) {
143	publicKeyBytes, err := os.ReadFile(path)
144	if err != nil {
145		return nil, fmt.Errorf("read certificate pem file err:%s", err.Error())
146	}
147	return LoadPublicKey(string(publicKeyBytes))
148}
149
150// EncryptOAEPWithPublicKey 使用 OAEP padding方式用公钥进行加密
151func EncryptOAEPWithPublicKey(message string, publicKey *rsa.PublicKey) (ciphertext string, err error) {
152	if publicKey == nil {
153		return "", fmt.Errorf("you should input *rsa.PublicKey")
154	}
155	ciphertextByte, err := rsa.EncryptOAEP(sha1.New(), rand.Reader, publicKey, []byte(message), nil)
156	if err != nil {
157		return "", fmt.Errorf("encrypt message with public key err:%s", err.Error())
158	}
159	ciphertext = base64.StdEncoding.EncodeToString(ciphertextByte)
160	return ciphertext, nil
161}
162
163// DecryptAES256GCM 使用 AEAD_AES_256_GCM 算法进行解密
164//
165// 可以使用此算法完成微信支付回调报文解密
166func DecryptAES256GCM(aesKey, associatedData, nonce, ciphertext string) (plaintext string, err error) {
167	decodedCiphertext, err := base64.StdEncoding.DecodeString(ciphertext)
168	if err != nil {
169		return "", err
170	}
171	c, err := aes.NewCipher([]byte(aesKey))
172	if err != nil {
173		return "", err
174	}
175	gcm, err := cipher.NewGCM(c)
176	if err != nil {
177		return "", err
178	}
179	dataBytes, err := gcm.Open(nil, []byte(nonce), decodedCiphertext, []byte(associatedData))
180	if err != nil {
181		return "", err
182	}
183	return string(dataBytes), nil
184}
185
186// SignSHA256WithRSA 通过私钥对字符串以 SHA256WithRSA 算法生成签名信息
187func SignSHA256WithRSA(source string, privateKey *rsa.PrivateKey) (signature string, err error) {
188	if privateKey == nil {
189		return "", fmt.Errorf("private key should not be nil")
190	}
191	h := crypto.Hash.New(crypto.SHA256)
192	_, err = h.Write([]byte(source))
193	if err != nil {
194		return "", nil
195	}
196	hashed := h.Sum(nil)
197	signatureByte, err := rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, hashed)
198	if err != nil {
199		return "", err
200	}
201	return base64.StdEncoding.EncodeToString(signatureByte), nil
202}
203
204// VerifySHA256WithRSA 通过公钥对字符串和签名结果以 SHA256WithRSA 验证签名有效性
205func VerifySHA256WithRSA(source string, signature string, publicKey *rsa.PublicKey) error {
206	if publicKey == nil {
207		return fmt.Errorf("public key should not be nil")
208	}
209
210	sigBytes, err := base64.StdEncoding.DecodeString(signature)
211	if err != nil {
212		return fmt.Errorf("verify failed: signature is not base64 encoded")
213	}
214	hashed := sha256.Sum256([]byte(source))
215	err = rsa.VerifyPKCS1v15(publicKey, crypto.SHA256, hashed[:], sigBytes)
216	if err != nil {
217		return fmt.Errorf("verify signature with public key error:%s", err.Error())
218	}
219	return nil
220}
221
222// GenerateNonce 生成一个长度为 NonceLength 的随机字符串（只包含大小写字母与数字）
223func GenerateNonce() (string, error) {
224	const (
225		// NonceSymbols 随机字符串可用字符集
226		NonceSymbols = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
227		// NonceLength 随机字符串的长度
228		NonceLength = 32
229	)
230
231	bytes := make([]byte, NonceLength)
232	_, err := rand.Read(bytes)
233	if err != nil {
234		return "", err
235	}
236	symbolsByteLength := byte(len(NonceSymbols))
237	for i, b := range bytes {
238		bytes[i] = NonceSymbols[b%symbolsByteLength]
239	}
240	return string(bytes), nil
241}
242
243// BuildAuthorization 构建请求头中的 Authorization 信息
244func BuildAuthorization(
245	mchid string,
246	certificateSerialNo string,
247	privateKey *rsa.PrivateKey,
248	method string,
249	canonicalURL string,
250	body []byte,
251) (string, error) {
252	const (
253		SignatureMessageFormat = "%s\n%s\n%d\n%s\n%s\n" // 数字签名原文格式
254		// HeaderAuthorizationFormat 请求头中的 Authorization 拼接格式
255		HeaderAuthorizationFormat = "WECHATPAY2-SHA256-RSA2048 mchid=\"%s\",nonce_str=\"%s\",timestamp=\"%d\",serial_no=\"%s\",signature=\"%s\""
256	)
257
258	nonce, err := GenerateNonce()
259	if err != nil {
260		return "", err
261	}
262	timestamp := time.Now().Unix()
263	message := fmt.Sprintf(SignatureMessageFormat, method, canonicalURL, timestamp, nonce, body)
264	signature, err := SignSHA256WithRSA(message, privateKey)
265	if err != nil {
266		return "", err
267	}
268	authorization := fmt.Sprintf(
269		HeaderAuthorizationFormat,
270		mchid, nonce, timestamp, certificateSerialNo, signature,
271	)
272	return authorization, nil
273}
274
275// ExtractResponseBody 提取应答报文的 Body
276func ExtractResponseBody(response *http.Response) ([]byte, error) {
277	if response.Body == nil {
278		return nil, nil
279	}
280
281	body, err := io.ReadAll(response.Body)
282	if err != nil {
283		return nil, fmt.Errorf("read response body err:[%s]", err.Error())
284	}
285	response.Body = io.NopCloser(bytes.NewBuffer(body))
286	return body, nil
287}
288
289const (
290	WechatPayTimestamp = "Wechatpay-Timestamp" // 微信支付回包时间戳
291	WechatPayNonce     = "Wechatpay-Nonce"     // 微信支付回包随机字符串
292	WechatPaySignature = "Wechatpay-Signature" // 微信支付回包签名信息
293	WechatPaySerial    = "Wechatpay-Serial"    // 微信支付回包平台序列号
294	RequestID          = "Request-Id"          // 微信支付回包请求ID
295)
296
297func validateWechatPaySignature(
298	wechatpayPublicKeyId string,
299	wechatpayPublicKey *rsa.PublicKey,
300	headers *http.Header,
301	body []byte,
302) error {
303	timestampStr := headers.Get(WechatPayTimestamp)
304	serialNo := headers.Get(WechatPaySerial)
305	signature := headers.Get(WechatPaySignature)
306	nonce := headers.Get(WechatPayNonce)
307
308	// 拒绝过期请求
309	timestamp, err := strconv.ParseInt(timestampStr, 10, 64)
310	if err != nil {
311		return fmt.Errorf("invalid timestamp: %w", err)
312	}
313	if time.Now().Sub(time.Unix(timestamp, 0)) > 5*time.Minute {
314		return fmt.Errorf("timestamp expired: %d", timestamp)
315	}
316
317	if serialNo != wechatpayPublicKeyId {
318		return fmt.Errorf(
319			"serial-no mismatch: got %s, expected %s",
320			serialNo,
321			wechatpayPublicKeyId,
322		)
323	}
324
325	message := fmt.Sprintf("%s\n%s\n%s\n", timestampStr, nonce, body)
326	if err := VerifySHA256WithRSA(message, signature, wechatpayPublicKey); err != nil {
327		return fmt.Errorf("invalid signature: %v", err)
328	}
329
330	return nil
331}
332
333// ValidateResponse 验证微信支付回包的签名信息
334func ValidateResponse(
335	wechatpayPublicKeyId string,
336	wechatpayPublicKey *rsa.PublicKey,
337	headers *http.Header,
338	body []byte,
339) error {
340	if err := validateWechatPaySignature(wechatpayPublicKeyId, wechatpayPublicKey, headers, body); err != nil {
341		return fmt.Errorf("validate response err: %w, RequestID: %s", err, headers.Get(RequestID))
342	}
343	return nil
344}
345
346func validateNotification(
347	wechatpayPublicKeyId string,
348	wechatpayPublicKey *rsa.PublicKey,
349	headers *http.Header,
350	body []byte,
351) error {
352	if err := validateWechatPaySignature(wechatpayPublicKeyId, wechatpayPublicKey, headers, body); err != nil {
353		return fmt.Errorf("validate notification err: %w", err)
354	}
355	return nil
356}
357
358// Resource 微信支付通知请求中的资源数据
359type Resource struct {
360	Algorithm      string `json:"algorithm"`
361	Ciphertext     string `json:"ciphertext"`
362	AssociatedData string `json:"associated_data"`
363	Nonce          string `json:"nonce"`
364	OriginalType   string `json:"original_type"`
365}
366
367// Notification 微信支付通知的数据结构
368type Notification struct {
369	ID           string     `json:"id"`
370	CreateTime   *time.Time `json:"create_time"`
371	EventType    string     `json:"event_type"`
372	ResourceType string     `json:"resource_type"`
373	Resource     *Resource  `json:"resource"`
374	Summary      string     `json:"summary"`
375
376	Plaintext string // 解密后的业务数据（JSON字符串）
377}
378
379func (c *Notification) validate() error {
380	if c.Resource == nil {
381		return errors.New("resource is nil")
382	}
383
384	if c.Resource.Algorithm != "AEAD_AES_256_GCM" {
385		return fmt.Errorf("unsupported algorithm: %s", c.Resource.Algorithm)
386	}
387
388	if c.Resource.Ciphertext == "" {
389		return errors.New("ciphertext is empty")
390	}
391
392	if c.Resource.AssociatedData == "" {
393		return errors.New("associated_data is empty")
394	}
395
396	if c.Resource.Nonce == "" {
397		return errors.New("nonce is empty")
398	}
399
400	if c.Resource.OriginalType == "" {
401		return fmt.Errorf("original_type is empty")
402	}
403
404	return nil
405}
406
407func (c *Notification) decrypt(apiv3Key string) error {
408	if err := c.validate(); err != nil {
409		return fmt.Errorf("notification format err: %w", err)
410	}
411
412	plaintext, err := DecryptAES256GCM(
413		apiv3Key,
414		c.Resource.AssociatedData,
415		c.Resource.Nonce,
416		c.Resource.Ciphertext,
417	)
418	if err != nil {
419		return fmt.Errorf("notification decrypt err: %w", err)
420	}
421
422	c.Plaintext = plaintext
423	return nil
424}
425
426// ParseNotification 解析微信支付通知的报文，返回通知中的业务数据
427// Notification.PlainText 为解密后的业务数据JSON字符串，请自行反序列化后使用
428func ParseNotification(
429	wechatpayPublicKeyId string,
430	wechatpayPublicKey *rsa.PublicKey,
431	apiv3Key string,
432	headers *http.Header,
433	body []byte,
434) (*Notification, error) {
435	if err := validateNotification(wechatpayPublicKeyId, wechatpayPublicKey, headers, body); err != nil {
436		return nil, err
437	}
438
439	notification := &Notification{}
440	if err := json.Unmarshal(body, notification); err != nil {
441		return nil, fmt.Errorf("parse notification err: %w", err)
442	}
443
444	if err := notification.decrypt(apiv3Key); err != nil {
445		return nil, fmt.Errorf("notification decrypt err: %w", err)
446	}
447
448	return notification, nil
449}
450
451// ApiException 微信支付API错误异常，发送HTTP请求成功，但返回状态码不是 2XX 时抛出本异常
452type ApiException struct {
453	statusCode   int         // 应答报文的 HTTP 状态码
454	header       http.Header // 应答报文的 Header 信息
455	body         []byte      // 应答报文的 Body 原文
456	errorCode    string      // 微信支付回包的错误码
457	errorMessage string      // 微信支付回包的错误信息
458}
459
460func (c *ApiException) Error() string {
461	buf := bytes.NewBuffer(nil)
462	buf.WriteString(fmt.Sprintf("api error:[StatusCode: %d, Body: %s", c.statusCode, string(c.body)))
463	if len(c.header) > 0 {
464		buf.WriteString(" Header: ")
465		for key, value := range c.header {
466			buf.WriteString(fmt.Sprintf("\n - %v=%v", key, value))
467		}
468		buf.WriteString("\n")
469	}
470	buf.WriteString("]")
471	return buf.String()
472}
473
474func (c *ApiException) StatusCode() int {
475	return c.statusCode
476}
477
478func (c *ApiException) Header() http.Header {
479	return c.header
480}
481
482func (c *ApiException) Body() []byte {
483	return c.body
484}
485
486func (c *ApiException) ErrorCode() string {
487	return c.errorCode
488}
489
490func (c *ApiException) ErrorMessage() string {
491	return c.errorMessage
492}
493
494func NewApiException(statusCode int, header http.Header, body []byte) error {
495	ret := &ApiException{
496		statusCode: statusCode,
497		header:     header,
498		body:       body,
499	}
500
501	bodyObject := map[string]interface{}{}
502	if err := json.Unmarshal(body, &bodyObject); err == nil {
503		if val, ok := bodyObject["code"]; ok {
504			ret.errorCode = val.(string)
505		}
506		if val, ok := bodyObject["message"]; ok {
507			ret.errorMessage = val.(string)
508		}
509	}
510
511	return ret
512}
513
514// Time 复制 time.Time 对象，并返回复制体的指针
515func Time(t time.Time) *time.Time {
516	return &t
517}
518
519// String 复制 string 对象，并返回复制体的指针
520func String(s string) *string {
521	return &s
522}
523
524// Bytes 复制 []byte 对象，并返回复制体的指针
525func Bytes(b []byte) *[]byte {
526	return &b
527}
528
529// Bool 复制 bool 对象，并返回复制体的指针
530func Bool(b bool) *bool {
531	return &b
532}
533
534// Float64 复制 float64 对象，并返回复制体的指针
535func Float64(f float64) *float64 {
536	return &f
537}
538
539// Float32 复制 float32 对象，并返回复制体的指针
540func Float32(f float32) *float32 {
541	return &f
542}
543
544// Int64 复制 int64 对象，并返回复制体的指针
545func Int64(i int64) *int64 {
546	return &i
547}
548
549// Int32 复制 int64 对象，并返回复制体的指针
550func Int32(i int32) *int32 {
551	return &i
552}
553
554// generateHashFromStream 从io.Reader流中生成哈希值的通用函数
555func generateHashFromStream(reader io.Reader, hashFunc func() hash.Hash, algorithmName string) (string, error) {
556	hash := hashFunc()
557	if _, err := io.Copy(hash, reader); err != nil {
558		return "", fmt.Errorf("failed to read stream for %s: %w", algorithmName, err)
559	}
560	return fmt.Sprintf("%x", hash.Sum(nil)), nil
561}
562
563// GenerateSHA256FromStream 从io.Reader流中生成SHA256哈希值
564func GenerateSHA256FromStream(reader io.Reader) (string, error) {
565	return generateHashFromStream(reader, sha256.New, "SHA256")
566}
567
568// GenerateSHA1FromStream 从io.Reader流中生成SHA1哈希值
569func GenerateSHA1FromStream(reader io.Reader) (string, error) {
570	return generateHashFromStream(reader, sha1.New, "SHA1")
571}
572
573// GenerateSM3FromStream 从io.Reader流中生成SM3哈希值
574func GenerateSM3FromStream(reader io.Reader) (string, error) {
575	h := sm3.New()
576	if _, err := io.Copy(h, reader); err != nil {
577		return "", fmt.Errorf("failed to read stream for SM3: %w", err)
578	}
579	return fmt.Sprintf("%x", h.Sum(nil)), nil
580}
581
```
