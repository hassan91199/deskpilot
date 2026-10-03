"use client";

import { useState } from "react";

import { AccountSwitcher } from "@/components/AccountSwitcher";
import { ChatWindow, type Message } from "@/components/ChatWindow";
import { TracePanel } from "@/components/TracePanel";
import { type ChatEvent, streamChat } from "@/lib/api";

export default function Home() {
  const [accountId, setAccountId] = useState("acct-1");
  const [messages, setMessages] = useState<Message[]>([]);
  const [trace, setTrace] = useState<ChatEvent[]>([]);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend(query: string) {
    setMessages((prev) => [...prev, { role: "user", content: query }]);
    setTrace([]);
    setPending(true);
    setError(null);

    try {
      await streamChat(query, accountId, (event: ChatEvent) => {
        if (event.kind === "final") {
          setMessages((prev) => [...prev, { role: "assistant", content: event.reply }]);
        } else {
          setTrace((prev) => [...prev, event]);
        }
      });
    } catch {
      setError("DeskPilot couldn't reach the backend. Is the API running?");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
        <div>
          <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">DeskPilot</h1>
          <p className="text-xs text-zinc-500">Support agent for Acme Cloud (demo)</p>
        </div>
        <AccountSwitcher accountId={accountId} onChange={setAccountId} />
      </header>

      {error && (
        <p className="border-b border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </p>
      )}

      <div className="grid flex-1 grid-cols-1 overflow-hidden md:grid-cols-[1fr_320px]">
        <div className="min-h-0 border-zinc-200 md:border-r dark:border-zinc-800">
          <ChatWindow messages={messages} pending={pending} onSend={handleSend} />
        </div>
        <div className="min-h-0 overflow-y-auto p-4">
          <h2 className="mb-3 text-xs font-semibold tracking-wide text-zinc-500 uppercase">
            Trace
          </h2>
          <TracePanel events={trace} />
        </div>
      </div>
    </div>
  );
}
