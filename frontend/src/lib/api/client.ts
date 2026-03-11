"use client";

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
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
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as {
      detail?: string | { message?: string };
      message?: string;
    };

    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (data.detail && typeof data.detail === "object" && typeof data.detail.message === "string") {
      return data.detail.message;
    }

    if (typeof data.message === "string") {
      return data.message;
    }
  } catch {
    // fall through to status text below
  }

  return response.statusText || "Unexpected API error";
}
