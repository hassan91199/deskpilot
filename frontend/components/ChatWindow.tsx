"use client";

import { useState } from "react";

export type Message = {
  role: "user" | "assistant";
  content: string;
};

function Bubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
          isUser
            ? "bg-zinc-900 text-zinc-50 dark:bg-zinc-100 dark:text-zinc-900"
            : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}

export function ChatWindow({
  messages,
  pending,
  onSend,
}: {
  messages: Message[];
  pending: boolean;
  onSend: (query: string) => void;
}) {
  const [input, setInput] = useState("");

  function submit() {
    const query = input.trim();
    if (!query || pending) return;
    onSend(query);
    setInput("");
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <p className="text-sm text-zinc-400">
            Ask a product question, check your plan, or report an issue.
          </p>
        )}
        {messages.map((message, i) => (
          <Bubble key={i} message={message} />
        ))}
        {pending && <p className="text-sm text-zinc-400">DeskPilot is thinking…</p>}
      </div>
      <div className="flex gap-2 border-t border-zinc-200 p-3 dark:border-zinc-800">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") submit();
          }}
          placeholder="Ask DeskPilot…"
          className="flex-1 rounded border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
        />
        <button
          onClick={submit}
          disabled={pending}
          className="rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-zinc-50 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
        >
          Send
        </button>
      </div>
    </div>
  );
}
