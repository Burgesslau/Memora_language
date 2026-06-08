/**
 * API 请求层 — 封装与 FastAPI 后端的通信。
 * 开发环境通过 next.config.ts rewrites 代理到 localhost:8000。
 */

import type {
  BKTMatrixResponse,
  DiagnoseRequest,
  DiagnoseResponse,
  HealthResponse,
  SpeakRequest,
  SpeakResponse,
} from "@/types/api";

const DEFAULT_USER_ID =
  process.env.NEXT_PUBLIC_DEFAULT_USER_ID ?? "user_001";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let body: unknown;
    try {
      body = await res.json();
    } catch {
      body = await res.text();
    }
    throw new ApiError(`API ${res.status}: ${res.statusText}`, res.status, body);
  }

  return res.json() as Promise<T>;
}

/** 健康检查 */
export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

/**
 * 双轨制口语/文本语法评价
 * POST /api/v1/speak
 */
export async function evaluateSpeech(
  payload: SpeakRequest,
): Promise<SpeakResponse> {
  return request<SpeakResponse>("/api/v1/speak", {
    method: "POST",
    body: JSON.stringify({
      ...payload,
      user_id: payload.user_id ?? DEFAULT_USER_ID,
    }),
  });
}

/**
 * 语法瓶颈逆向诊断
 * POST /api/v1/diagnose
 */
export async function diagnoseBottleneck(
  payload: DiagnoseRequest,
): Promise<DiagnoseResponse> {
  return request<DiagnoseResponse>("/api/v1/diagnose", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * 用户 BKT 掌握度矩阵（管理/调试）
 * GET /api/v1/admin/bkt-status/{user_id}
 */
export async function getBktStatus(userId: string): Promise<BKTMatrixResponse> {
  return request<BKTMatrixResponse>(`/api/v1/admin/bkt-status/${userId}`);
}

export { ApiError, DEFAULT_USER_ID };
