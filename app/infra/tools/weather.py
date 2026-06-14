from __future__ import annotations

from typing import Any

import requests

from app.infra.tools.tool_base import BaseTool, ToolContext, ToolResult


class WeatherTool(BaseTool):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Get weather forecast by latitude and longitude"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude of the target location",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude of the target location",
                },
            },
            "required": ["latitude", "longitude"],
        }

    # 请求头，向 weather.gov 请求天气预报数据
    def _build_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/geo+json",
            "User-Agent": "Ragent/0.1 (weather tool)",
        }

    def _get_forecast_url(self, latitude: float, longitude: float, timeout_seconds: float) -> str:
        response = requests.get(
            f"https://api.weather.gov/points/{latitude},{longitude}",
            headers=self._build_headers(),
            timeout=timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        forecast_url = payload.get("properties", {}).get("forecast")
        if not forecast_url:
            raise ValueError("weather.gov 响应中缺少 forecast 地址")
        return forecast_url

    def _fetch_forecast(self, forecast_url: str, timeout_seconds: float) -> dict[str, Any]:
        response = requests.get(
            forecast_url,
            headers=self._build_headers(),
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def _format_forecast(self, forecast_payload: dict[str, Any], latitude: float, longitude: float) -> str:
        periods = forecast_payload.get("properties", {}).get("periods", [])
        if not periods:
            return f"已查询到天气服务，但暂时没有拿到 {latitude}, {longitude} 的预报数据。"

        current = periods[0]
        name = current.get("name", "Current")
        temperature = current.get("temperature", "N/A")
        temperature_unit = current.get("temperatureUnit", "")
        wind_speed = current.get("windSpeed", "N/A")
        wind_direction = current.get("windDirection", "")
        short_forecast = current.get("shortForecast", "N/A")
        detailed_forecast = current.get("detailedForecast", "N/A")

        return (
            f"Weather for ({latitude}, {longitude}): "
            f"{name}. "
            f"Temperature: {temperature}{temperature_unit}. "
            f"Wind: {wind_speed} {wind_direction}. "
            f"Summary: {short_forecast}. "
            f"Details: {detailed_forecast}"
        )

    async def run(
        self,
        arguments: dict[str, Any],
        ctx: ToolContext,
    ) -> ToolResult:
        try:
            latitude = float(arguments["latitude"])
            longitude = float(arguments["longitude"])

            forecast_url = self._get_forecast_url(
                latitude=latitude,
                longitude=longitude,
                timeout_seconds=ctx.timeout_seconds,
            )
            forecast_payload = self._fetch_forecast(
                forecast_url=forecast_url,
                timeout_seconds=ctx.timeout_seconds,
            )
            content = self._format_forecast(
                forecast_payload=forecast_payload,
                latitude=latitude,
                longitude=longitude,
            )

            return ToolResult(
                tool_name=self.name,
                ok=True,
                content=content,
                raw=forecast_payload,
                error=None,
            )
        except KeyError as exc:
            return ToolResult(
                tool_name=self.name,
                ok=False,
                content="天气工具缺少必要参数。",
                raw=None,
                error=f"missing argument: {exc}",
            )
        except (TypeError, ValueError) as exc:
            return ToolResult(
                tool_name=self.name,
                ok=False,
                content="天气工具参数格式不正确。",
                raw=None,
                error=str(exc),
            )
        except requests.RequestException as exc:
            return ToolResult(
                tool_name=self.name,
                ok=False,
                content="天气服务调用失败。",
                raw=None,
                error=str(exc),
            )

# # 测试
# import asyncio
# if __name__ == "__main__":
#     async def main():
#         tool = WeatherTool()
#         result = await tool.run(
#             {"latitude": 38.8977, "longitude": -77.0365},
#             ToolContext(trace_id="test-weather"),
#         )
#         print(result.ok)
#         print(result.content)
#         print(result.error)
#     asyncio.run(main())

