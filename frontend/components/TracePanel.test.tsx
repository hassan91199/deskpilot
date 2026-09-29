import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ChatEvent } from "@/lib/api";

import { TracePanel } from "./TracePanel";

describe("TracePanel", () => {
  it("shows a hint when there are no trace events yet", () => {
    render(<TracePanel events={[]} />);

    expect(screen.getByText(/tool calls and retrieved sources/i)).toBeInTheDocument();
  });

  it("labels a search_docs call with its query", () => {
    const events: ChatEvent[] = [
      { kind: "tool_call", name: "search_docs", arguments: { query: "rotate API key" } },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText(/searching docs: "rotate api key"/i)).toBeInTheDocument();
  });

  it("labels a get_account call generically, without leaking an id", () => {
    const events: ChatEvent[] = [{ kind: "tool_call", name: "get_account", arguments: {} }];
    render(<TracePanel events={events} />);

    expect(screen.getByText(/looking up your account/i)).toBeInTheDocument();
  });

  it("labels a create_ticket call with its subject", () => {
    const events: ChatEvent[] = [
      {
        kind: "tool_call",
        name: "create_ticket",
        arguments: { subject: "Double charge" },
      },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText(/filing a ticket: "double charge"/i)).toBeInTheDocument();
  });

  it("renders cited doc chunks for a confident search_docs result", () => {
    const events: ChatEvent[] = [
      {
        kind: "tool_result",
        name: "search_docs",
        result: {
          confident: true,
          chunks: [{ doc_id: "api-keys", doc_title: "API Keys", text: "Rotate from Settings." }],
        },
      },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText("API Keys")).toBeInTheDocument();
    expect(screen.getByText("Rotate from Settings.")).toBeInTheDocument();
  });

  it("shows no-match copy for an unconfident search_docs result", () => {
    const events: ChatEvent[] = [
      { kind: "tool_result", name: "search_docs", result: { confident: false } },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText(/no confident match/i)).toBeInTheDocument();
  });

  it("renders account fields for a get_account result", () => {
    const events: ChatEvent[] = [
      {
        kind: "tool_result",
        name: "get_account",
        result: { plan: "Pro", seats_used: 4, renewal_date: "2026-11-01" },
      },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText("Pro")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText("2026-11-01")).toBeInTheDocument();
  });

  it("shows an error for a get_account result that failed", () => {
    const events: ChatEvent[] = [
      { kind: "tool_result", name: "get_account", result: { error: "account not found" } },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText("account not found")).toBeInTheDocument();
  });

  it("renders the ticket id and status for a create_ticket result", () => {
    const events: ChatEvent[] = [
      {
        kind: "tool_result",
        name: "create_ticket",
        result: { ticket_id: "TCK-1001", status: "open" },
      },
    ];
    render(<TracePanel events={events} />);

    expect(screen.getByText("TCK-1001")).toBeInTheDocument();
    expect(screen.getByText(/open/)).toBeInTheDocument();
  });
});
