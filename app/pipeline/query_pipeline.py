import logging

from app.domain.schemas import ChatRequest
from app.domain.schemas import QueryNormalizationResult  # 导入规整结果的数据结构
from app.framework.context import RequestContext  # 导入请求上下文，里面有 trace_id
from app.services.query_service import QueryServiceProtocol  # 导入 query 服务接口，保证这里能调用规整方法

_log = logging.getLogger(__name__)


async def run_query_pipeline(req: ChatRequest, ctx: RequestContext, query_service: QueryServiceProtocol) -> QueryNormalizationResult:
    q = await query_service.rewrite(req.query, req.history, ctx)
    did = (q or "").strip() != (req.query or "").strip()
    _log.info("Query rewriting 已完成。")

    result = QueryNormalizationResult(
        query=q,
        did_rewrite=did,
    )

    _log.info("Query 规整流水线已经完成。")
    return result  # 把规整结果返回给上层