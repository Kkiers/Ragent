# UTF-8 调用 /api/chat（避免 PowerShell + curl 下 JSON 中文被弄坏）
# 用法：在项目根目录执行  .\scripts\call_chat_debug.ps1
# 端口须与 uvicorn 一致，例如：.\scripts\call_chat_debug.ps1 -BaseUrl "http://127.0.0.1:8001"
# 也可设环境变量：$env:RAGENT_CHAT_BASE_URL = "http://127.0.0.1:8001"
#
# 使用 HttpClient + ReadAsStringAsync 按 UTF-8 读响应，避免 Windows PowerShell 5.x 下
# Invoke-WebRequest 的 .Content 把 UTF-8 误当成系统单字节编码（出现 æ¯ç 类乱码）。

param(
    [string]$BaseUrl = ""
)

if (-not $BaseUrl) {
    $BaseUrl = if ($env:RAGENT_CHAT_BASE_URL) { $env:RAGENT_CHAT_BASE_URL } else { "http://127.0.0.1:8001" }
}

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$jsonPath = Join-Path $root "scripts\examples\chat_debug.json"
$bytes = [System.IO.File]::ReadAllBytes($jsonPath)
$uri = "$BaseUrl/api/chat"
Write-Host "POST $uri" -ForegroundColor Cyan

$client = [System.Net.Http.HttpClient]::new()
try {
    $body = [System.Net.Http.ByteArrayContent]::new($bytes)
    $null = $body.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/json; charset=utf-8")
    $task = $client.PostAsync($uri, $body)
    $response = $task.GetAwaiter().GetResult()
    $jsonText = $response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    $code = [int]$response.StatusCode
    if (-not $response.IsSuccessStatusCode) {
        Write-Host "HTTP $code" -ForegroundColor Yellow
        Write-Host $jsonText
        exit 1
    }
    ($jsonText | ConvertFrom-Json) | ConvertTo-Json -Depth 30
} finally {
    $client.Dispose()
}
