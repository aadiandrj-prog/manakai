import type { components } from './api-schema';

export type Standard = components['schemas']['Standard'];
export type StandardRelationship = components['schemas']['StandardRelationship'];
export type Laboratory = components['schemas']['Laboratory'];
export type ComplianceProfile = components['schemas']['ComplianceProfile'];
export type JourneyStep = components['schemas']['JourneyStep'];
export type QueryResponse = components['schemas']['QueryResponse'];
export type Document = components['schemas']['Document'];
export type ProductAnalyseRequest = components['schemas']['ProductAnalyseRequest'];
export type LabSearchRequest = components['schemas']['LabSearchRequest'];

const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly kind: 'backend' | 'network' | 'validation',
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    const headers = new Headers(init?.headers);
    headers.set('Content-Type', 'application/json');
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers,
    });
  } catch {
    throw new ApiError('Cannot reach the ManakAI API. Check that the backend is running.', 0, 'network');
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as
      | { detail?: string | Array<{ msg: string }> }
      | null;
    const detail = Array.isArray(body?.detail)
      ? body.detail.map((item) => item.msg).join(', ')
      : body?.detail;
    throw new ApiError(
      detail || `The API returned HTTP ${response.status}.`,
      response.status,
      response.status === 422 ? 'validation' : 'backend',
    );
  }
  return response.json() as Promise<T>;
}

export const api = {
  standards: (query = '') => request<Standard[]>(`/api/v1/standards?q=${encodeURIComponent(query)}`),
  standard: (id: string) => request<Standard>(`/api/v1/standards/${encodeURIComponent(id)}`),
  relationships: (id: string) => request<StandardRelationship[]>(`/api/v1/standards/${encodeURIComponent(id)}/relationships`),
  analyse: (payload: ProductAnalyseRequest) =>
    request<ComplianceProfile>('/api/v1/products/analyse', { method: 'POST', body: JSON.stringify(payload) }),
  compliance: (id: string) => request<ComplianceProfile>(`/api/v1/compliance/${encodeURIComponent(id)}`),
  journey: (id: string) => request<JourneyStep[]>(`/api/v1/compliance/${encodeURIComponent(id)}/journey`),
  labs: () => request<Laboratory[]>('/api/v1/labs'),
  searchLabs: (payload: LabSearchRequest) =>
    request<Laboratory[]>('/api/v1/labs/search', { method: 'POST', body: JSON.stringify(payload) }),
  ask: (query: string) =>
    request<QueryResponse>('/api/v1/qa', { method: 'POST', body: JSON.stringify({ query, language: 'auto' }) }),
  document: (id: string) => request<Document>(`/api/v1/documents/${encodeURIComponent(id)}`),
};

export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'An unexpected error occurred.';
}
