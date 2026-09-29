import { afterEach, describe, expect, it, vi } from "vitest";

import { type ChatEvent, getAccount, streamChat } from "./api";

function sseBlock(event: string, data: unknown): string {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
}

function streamFromChunks(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let i = 0;
  return new ReadableStream({
    pull(controller) {
      if (i >= chunks.length) {
        controller.close();
        return;
      }
      controller.enqueue(encoder.encode(chunks[i]));
      i += 1;
    },
  });
}

function mockFetchOnce(response: Record<string, unknown>) {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response as unknown as Response));
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("streamChat", () => {
  it("parses tool_call, tool_result, and final events in order", async () => {
    const body =
      sseBlock("tool_call", { name: "search_docs", arguments: { query: "api keys" } }) +
      sseBlock("tool_result", { name: "search_docs", result: { confident: true, chunks: [] } }) +
      sseBlock("final", {
        reply: "You rotate keys from Settings.",
        tool_calls: ["search_docs"],
        cited_doc_ids: ["api-keys"],
        ticket_id: null,
      });

    mockFetchOnce({ ok: true, body: streamFromChunks([body]) });

    const events: ChatEvent[] = [];
    await streamChat("How do I rotate an API key?", "acct-1", (e) => events.push(e));

    expect(events).toEqual([
      { kind: "tool_call", name: "search_docs", arguments: { query: "api keys" } },
      {
        kind: "tool_result",
        name: "search_docs",
        result: { confident: true, chunks: [] },
      },
      {
        kind: "final",
        reply: "You rotate keys from Settings.",
        tool_calls: ["search_docs"],
        cited_doc_ids: ["api-keys"],
        ticket_id: null,
      },
    ]);
  });

  it("reassembles an SSE block split across multiple stream chunks", async () => {
    const whole = sseBlock("final", {
      reply: "hi",
      tool_calls: [],
      cited_doc_ids: [],
      ticket_id: null,
    });
    const splitPoint = Math.floor(whole.length / 2);

    mockFetchOnce({
      ok: true,
      body: streamFromChunks([whole.slice(0, splitPoint), whole.slice(splitPoint)]),
    });

    const events: ChatEvent[] = [];
    await streamChat("hello", "acct-1", (e) => events.push(e));

    expect(events).toEqual([
      { kind: "final", reply: "hi", tool_calls: [], cited_doc_ids: [], ticket_id: null },
    ]);
  });

  it("sends the query and account id as the POST body", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, body: streamFromChunks([]) } as unknown as Response);
    vi.stubGlobal("fetch", fetchMock);

    await streamChat("what plan am I on?", "acct-2", () => {});

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/chat"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ query: "what plan am I on?", account_id: "acct-2" }),
      }),
    );
  });

  it("throws when the response is not ok", async () => {
    mockFetchOnce({ ok: false, status: 500, body: streamFromChunks([]) });

    await expect(streamChat("hi", "acct-1", () => {})).rejects.toThrow("500");
  });
});

describe("getAccount", () => {
  it("returns the parsed account on success", async () => {
    const account = {
      id: "acct-1",
      name: "Aeon Robotics",
      email: "ops@aeon.example",
      plan: "Pro",
      seats_used: 4,
      billing_cycle: "monthly",
      renewal_date: "2026-11-01",
      status: "active",
    };
    mockFetchOnce({ ok: true, json: async () => account });

    await expect(getAccount("acct-1")).resolves.toEqual(account);
  });

  it("throws when the lookup fails", async () => {
    mockFetchOnce({ ok: false, status: 404 });

    await expect(getAccount("unknown")).rejects.toThrow("404");
  });
});
