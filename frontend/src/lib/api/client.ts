"use client";

type ApiErrorEnvelope = Readonly<{
  error_code?: string;
  category?: string;
  message?: string;
  retryable?: boolean;
  details?: unknown;
  debug_ref?: string;
}>;

export class ApiError extends Error {
  readonly status: number;
  readonly errorCode: string | null;
  readonly category: string | null;
  readonly retryable: boolean | null;
  readonly details: unknown;
  readonly debugRef: string | null;

  constructor(
    message: string,
    status: number,
    options?: Readonly<{
      errorCode?: string | null;
      category?: string | null;
      retryable?: boolean | null;
      details?: unknown;
      debugRef?: string | null;
    }>,
  ) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.errorCode = options?.errorCode ?? null;
    this.category = options?.category ?? null;
    this.retryable = options?.retryable ?? null;
    this.details = options?.details;
    this.debugRef = options?.debugRef ?? null;
  }
}

type ApiRequestInit = Omit<RequestInit, "body"> & {
  body?: BodyInit | Record<string, unknown> | null;
};

export async function apiRequest<T>(path: string, init?: ApiRequestInit): Promise<T> {
  const { body, headers, ...requestInit } = init ?? {};
  const isJsonBody = body !== undefined && body !== null && !(body instanceof FormData);

  const response = await fetch(path, {
    ...requestInit,
    headers: {
      ...(isJsonBody ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    body: isJsonBody ? JSON.stringify(body) : (body ?? undefined),
  });

  if (!response.ok) {
    const errorPayload = await getApiErrorPayload(response);
    throw new ApiError(errorPayload.message, response.status, {
      errorCode: errorPayload.errorCode,
      category: errorPayload.category,
      retryable: errorPayload.retryable,
      details: errorPayload.details,
      debugRef: errorPayload.debugRef,
    });
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function getApiErrorPayload(response: Response): Promise<
  Readonly<{
    message: string;
    errorCode: string | null;
    category: string | null;
    retryable: boolean | null;
    details: unknown;
    debugRef: string | null;
  }>
> {
  try {
    const data = (await response.json()) as
      | ({
          detail?: string | ApiErrorEnvelope;
          message?: string;
        } & ApiErrorEnvelope)
      | null;
    const detailEnvelope =
      data?.detail && typeof data.detail === "object" ? data.detail : undefined;
    const message =
      typeof data?.detail === "string"
        ? data.detail
        : (detailEnvelope?.message ??
            data?.message ??
            response.statusText ??
            "Unexpected API error");

    return {
      message,
      errorCode: detailEnvelope?.error_code ?? data?.error_code ?? null,
      category: detailEnvelope?.category ?? data?.category ?? null,
      retryable: detailEnvelope?.retryable ?? data?.retryable ?? null,
      details: detailEnvelope?.details ?? data?.details,
      debugRef: detailEnvelope?.debug_ref ?? data?.debug_ref ?? null,
    };
  } catch {
    return {
      message: response.statusText || "Unexpected API error",
      errorCode: null,
      category: null,
      retryable: null,
      details: undefined,
      debugRef: null,
    };
  }
}
