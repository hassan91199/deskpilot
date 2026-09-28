"use client";

// The three seeded demo accounts (deskpilot/seed/accounts.py). This stands
// in for a logged-in session in a demo with no real auth (out of scope per
// the build brief) — switching it changes which account `/chat` binds the
// session to, server-side, not anything read out of the chat message text.
export const DEMO_ACCOUNTS = [
  { id: "acct-1", label: "Aeon Robotics (Pro)" },
  { id: "acct-2", label: "Blue Harbor Logistics (Starter)" },
  { id: "acct-3", label: "Cascade Analytics (Enterprise)" },
] as const;

export function AccountSwitcher({
  accountId,
  onChange,
}: {
  accountId: string;
  onChange: (id: string) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
      Viewing as
      <select
        value={accountId}
        onChange={(e) => onChange(e.target.value)}
        className="rounded border border-zinc-300 bg-white px-2 py-1 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
      >
        {DEMO_ACCOUNTS.map((account) => (
          <option key={account.id} value={account.id}>
            {account.label}
          </option>
        ))}
      </select>
    </label>
  );
}
