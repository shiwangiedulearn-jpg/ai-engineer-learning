export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export interface ResearchDocument {
  document_id: string;
  filename: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  chunks_created?: number;
  message?: string;
}

export interface AskResponse {
  question: string;
  document_ids: string[];
  answer: string;
  source: string[];
  sources?: string[];
}

export interface DeleteResponse {
  document_id: string;
  filename: string;
  message?: string;
}

async function request<T>(
  url: string,
  options?: RequestInit,
): Promise<T> {
  try {
    const response = await fetch(url, options);
    const body = await readResponseBody(response);

    if (!response.ok) {
      throw new Error(getBackendError(body) || `Request failed (${response.status}).`);
    }

    return body as T;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(
        `Cannot reach the backend at ${API_BASE_URL}. Make sure FastAPI is running.`,
      );
    }
    throw error;
  }
}

async function readResponseBody(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) return null;

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getBackendError(body: unknown): string {
  if (!body) return "";

  if (typeof body === "string") {
    return body;
  }

  if (typeof body === "object" && body !== null) {
    const data = body as Record<string, unknown>;
    const detail = data.detail ?? data.message ?? data.error;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === "string"
            ? item
            : String((item as { msg?: unknown }).msg ?? ""),
        )
        .filter(Boolean)
        .join(", ");
    }
  }

  return "";
}

export async function getDocuments(): Promise<ResearchDocument[]> {
  const data = await request<{ documents?: ResearchDocument[] }>(
    `${API_BASE_URL}/documents`,
  );
  return data.documents ?? [];
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<UploadResponse>(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });
}

export async function askQuestion(
  question: string,
  documentIds: string[],
): Promise<AskResponse> {
  return request<AskResponse>(`${API_BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      document_ids: documentIds,
    }),
  });
}

export async function deleteDocument(
  documentId: string,
): Promise<DeleteResponse> {
  return request<DeleteResponse>(
    `${API_BASE_URL}/document/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
    },
  );
}
