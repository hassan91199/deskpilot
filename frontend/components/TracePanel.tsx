"use client";

import type { ChatEvent } from "@/lib/api";

function ToolCallRow({ name, args }: { name: string; args: Record<string, unknown> }) {
  const label =
    name === "search_docs"
      ? `Searching docs: "${String(args.query ?? "")}"`
      : name === "get_account"
        ? "Looking up your account"
        : name === "create_ticket"
          ? `Filing a ticket: "${String(args.subject ?? "")}"`
          : `Calling ${name}`;
  return (
    <div className="flex items-start gap-2 text-sm">
      <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-amber-500" />
      <span className="text-zinc-700 dark:text-zinc-300">{label}</span>
    </div>
  );
}

function SearchDocsResult({ result }: { result: Record<string, unknown> }) {
  if (!result.confident) {
    return <p className="text-sm text-zinc-500">No confident match in the docs.</p>;
  }
  const chunks = (result.chunks as Array<Record<string, unknown>>) ?? [];
  return (
    <ul className="space-y-2">
      {chunks.map((chunk) => (
        <li
          key={String(chunk.doc_id)}
          className="rounded border border-zinc-200 p-2 text-sm dark:border-zinc-800"
        >
          <p className="font-medium text-zinc-900 dark:text-zinc-100">
            {String(chunk.doc_title)}
          </p>
          <p className="mt-1 line-clamp-2 text-zinc-500">{String(chunk.text)}</p>
        </li>
      ))}
    </ul>
  );
}

function GetAccountResult({ result }: { result: Record<string, unknown> }) {
  if (result.error) {
    return <p className="text-sm text-red-600">{String(result.error)}</p>;
  }
  const fields: [string, string][] = [
    ["Plan", String(result.plan ?? "")],
    ["Seats used", String(result.seats_used ?? "")],
    ["Renews", String(result.renewal_date ?? "")],
  ];
  return (
    <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
      {fields.map(([label, value]) => (
        <div key={label} className="contents">
          <dt className="text-zinc-500">{label}</dt>
          <dd className="text-zinc-900 dark:text-zinc-100">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function CreateTicketResult({ result }: { result: Record<string, unknown> }) {
  return (
    <p className="text-sm text-zinc-700 dark:text-zinc-300">
      Ticket <span className="font-mono font-medium">{String(result.ticket_id)}</span> filed (
      {String(result.status)}).
    </p>
  );
}

function ToolResultRow({ name, result }: { name: string; result: Record<string, unknown> }) {
  return (
    <div className="ml-4 border-l border-zinc-200 pl-3 dark:border-zinc-800">
      {name === "search_docs" && <SearchDocsResult result={result} />}
      {name === "get_account" && <GetAccountResult result={result} />}
      {name === "create_ticket" && <CreateTicketResult result={result} />}
    </div>
  );
}

export function TracePanel({ events }: { events: ChatEvent[] }) {
  if (events.length === 0) {
    return (
      <p className="text-sm text-zinc-400">
        Tool calls and retrieved sources for the current turn show up here.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {events.map((event, i) => {
        if (event.kind === "tool_call") {
          return <ToolCallRow key={i} name={event.name} args={event.arguments} />;
        }
        if (event.kind === "tool_result") {
          return <ToolResultRow key={i} name={event.name} result={event.result} />;
        }
        return null;
      })}
    </div>
  );
}
