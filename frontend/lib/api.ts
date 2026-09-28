// Talks to DeskPilot's FastAPI backend (deskpilot/api.py). `streamChat`
// parses the raw SSE body itself instead of using `EventSource`, since
// EventSource can't send a POST body and `/chat` needs one (query + the
// demo "session" account id).

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type ToolCallEvent = {
  kind: "tool_call";
  name: string;
  arguments: Record<string, unknown>;
};

export type ToolResultEvent = {
  kind: "tool_result";
  name: string;
  result: Record<string, unknown>;
};

export type FinalEvent = {
  kind: "final";
  reply: string;
  tool_calls: string[];
  cited_doc_ids: string[];
  ticket_id: string | null;
};

export type ChatEvent = ToolCallEvent | ToolResultEvent | FinalEvent;

export type Account = {
  id: string;
  name: string;
  email: string;
  plan: string;
  seats_used: number;
  billing_cycle: string;
  renewal_date: string;
  status: string;
};

function parseSseBlock(block: string): { event: string; data: string } | null {
  const lines = block.split("\n");
  const eventLine = lines.find((l) => l.startsWith("event: "));
  const dataLine = lines.find((l) => l.startsWith("data: "));
  if (!eventLine || !dataLine) return null;
  return {
    event: eventLine.slice("event: ".length),
    data: dataLine.slice("data: ".length),
  };
}

export async function streamChat(
  query: string,
  accountId: string,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, account_id: accountId }),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let separatorIndex = buffer.indexOf("\n\n");
    while (separatorIndex !== -1) {
      const block = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);
      const parsed = parseSseBlock(block);
      if (parsed) {
        const data = JSON.parse(parsed.data);
        onEvent({ kind: parsed.event, ...data } as ChatEvent);
      }
      separatorIndex = buffer.indexOf("\n\n");
    }
  }
}

export async function getAccount(accountId: string): Promise<Account> {
  const response = await fetch(`${API_BASE_URL}/accounts/${accountId}`);
  if (!response.ok) throw new Error(`Account lookup failed: ${response.status}`);
  return response.json();
}
