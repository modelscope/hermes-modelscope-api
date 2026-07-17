"""ModelScope provider profile.

ModelScope (魔搭社区) provides OpenAI-compatible API inference for
open-source models including Qwen, DeepSeek, GLM, Kimi, and more.
Auth is a Bearer token (Access Token) on
``https://api-inference.modelscope.cn/v1``; the standard
``/v1/chat/completions`` and ``/v1/models`` routes apply, so the default
``chat_completions`` transport handles it with no per-provider quirks.

Model discovery uses ModelScope's ``GET /v1/models`` endpoint (requires
auth); ``fallback_models`` below is the offline catalog shown when live
discovery fails.
"""

from __future__ import annotations

from providers import register_provider
from providers.base import ProviderProfile

modelscope = ProviderProfile(
    name="modelscope",
    aliases=("ms",),
    env_vars=("MODELSCOPE_API_KEY", "MODELSCOPE_BASE_URL"),
    base_url="https://api-inference.modelscope.cn/v1",
    display_name="ModelScope",
    description="ModelScope — open-source model inference (Qwen, DeepSeek, GLM, Kimi)",
    signup_url="https://modelscope.cn",
    auth_type="api_key",
    default_aux_model="Qwen/Qwen3.5-27B",
    fallback_models=(
        "Qwen/Qwen3-235B-A22B",
        "Qwen/Qwen3.5-27B",
        "Qwen/Qwen3.5-397B-A17B",
        "deepseek-ai/DeepSeek-V3.2",
        "deepseek-ai/DeepSeek-V4-Flash",
        "deepseek-ai/DeepSeek-V4-Pro",
        "deepseek-ai/DeepSeek-R1-0528",
        "ZhipuAI/GLM-5.2",
        "MiniMax/MiniMax-M2.7",
        "moonshotai/Kimi-K2.7",
        "MiniMax/MiniMax-M3",
        "XiaomiMiMo/MiMo-V2-Flash",
    ),
)

register_provider(modelscope)