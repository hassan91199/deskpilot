"""Seed knowledge-base docs for the fictional Acme Cloud SaaS.

Each entry is one short doc: id, title, category, and body text. These are
what `deskpilot.ingest` chunks and embeds into pgvector. Kept as plain data
(no DB dependency) so tests can validate the corpus without a database.
"""

DOCS = [
    {
        "id": "plan-overview",
        "title": "Plan Overview",
        "category": "plans",
        "body": (
            "Acme Cloud has four plans: Free, Starter, Pro, and Enterprise. "
            "Free includes 1 seat, 1,000 API calls per month, and 1 GB of "
            "storage, with no SSO. Starter includes 5 seats, 20,000 API "
            "calls per month, and 10 GB of storage. Pro includes 10 seats, "
            "100,000 API calls per month, 100 GB of storage, and SAML SSO. "
            "Enterprise includes 100 seats, 1,000,000 API calls per month, "
            "1 TB of storage, SAML SSO, and SCIM provisioning. All plans "
            "can be billed monthly or annually; annual billing gets two "
            "months free."
        ),
    },
    {
        "id": "upgrading-your-plan",
        "title": "Upgrading Your Plan",
        "category": "plans",
        "body": (
            "You can upgrade at any time from Settings > Billing > Change "
            "Plan. Upgrades take effect immediately: new seat, storage, and "
            "API limits apply as soon as you confirm, and you're charged a "
            "prorated amount for the rest of the current billing period. "
            "No data is affected by an upgrade."
        ),
    },
    {
        "id": "downgrading-your-plan",
        "title": "Downgrading Your Plan",
        "category": "plans",
        "body": (
            "Downgrades take effect at the start of your next billing "
            "cycle, not immediately, so you keep your current plan's "
            "limits until then. If your usage at that point exceeds the "
            "new plan's seat or storage limits, see 'Data Retention Limits "
            "After Downgrade' for what happens to the excess. Downgrading "
            "from Pro or Enterprise to a plan without SSO disables SAML "
            "login for your organization; affected users fall back to "
            "email/password login."
        ),
    },
    {
        "id": "annual-vs-monthly-billing",
        "title": "Annual vs Monthly Billing",
        "category": "plans",
        "body": (
            "Monthly billing charges your card on the same day each month. "
            "Annual billing charges once a year and is equivalent to 10 "
            "months of the monthly price (2 months free). You can switch "
            "from monthly to annual at any time; the switch is prorated. "
            "Switching from annual to monthly takes effect at the end of "
            "the current annual term."
        ),
    },
    {
        "id": "how-billing-works",
        "title": "How Billing Works",
        "category": "billing",
        "body": (
            "Acme Cloud bills in advance for the upcoming period. Your "
            "renewal date is the day your current period ends and the next "
            "one is charged. You can see your exact renewal date and plan "
            "under Settings > Billing > Overview, or ask the support agent "
            "which will look it up on your account."
        ),
    },
    {
        "id": "updating-payment-method",
        "title": "Updating Payment Method",
        "category": "billing",
        "body": (
            "Go to Settings > Billing > Payment Methods to add a new card "
            "or change the default one. Changes apply to the next charge; "
            "we don't retry a failed past charge automatically when you "
            "add a new card, see 'Failed Payments and Grace Period' for "
            "that flow."
        ),
    },
    {
        "id": "invoices-and-receipts",
        "title": "Invoices and Receipts",
        "category": "billing",
        "body": (
            "Every successful charge generates a PDF invoice available "
            "under Settings > Billing > Invoices, and is also emailed to "
            "the account's billing contact. Invoices show plan, billing "
            "period, seats charged, and tax."
        ),
    },
    {
        "id": "failed-payments-and-grace-period",
        "title": "Failed Payments and Grace Period",
        "category": "billing",
        "body": (
            "If a charge fails, we retry it 3 times over 7 days. Your "
            "account stays fully active during this grace period. If all "
            "retries fail, the account is downgraded to Free at the end of "
            "the grace period until a valid payment method is added."
        ),
    },
    {
        "id": "seat-limits-by-plan",
        "title": "Seat Limits by Plan",
        "category": "limits",
        "body": (
            "Seat limits are hard caps: Free allows 1 seat, Starter allows "
            "5, Pro allows 10, and Enterprise allows 100. You cannot add "
            "seats beyond your plan's limit; the only way to add more "
            "seats than your current plan allows is to upgrade to a plan "
            "with a higher seat limit."
        ),
    },
    {
        "id": "api-rate-limits",
        "title": "API Rate Limits",
        "category": "limits",
        "body": (
            "API rate limits are enforced per month, not per second: Free "
            "allows 1,000 calls/month, Starter 20,000, Pro 100,000, and "
            "Enterprise 1,000,000. Requests beyond the monthly cap return "
            "HTTP 429 until the next billing cycle resets the counter. "
            "There is no burst throttling within a month."
        ),
    },
    {
        "id": "storage-limits",
        "title": "Storage Limits",
        "category": "limits",
        "body": (
            "Storage limits are 1 GB on Free, 10 GB on Starter, 100 GB on "
            "Pro, and 1 TB on Enterprise. Storage includes uploaded files "
            "and generated exports. You'll get an email warning at 90% of "
            "your limit."
        ),
    },
    {
        "id": "data-retention-limits-after-downgrade",
        "title": "Data Retention Limits After Downgrade",
        "category": "limits",
        "body": (
            "If a downgrade leaves you over the new plan's storage limit, "
            "your data is not deleted immediately: it's kept read-only for "
            "30 days so you can export or delete it yourself. After 30 "
            "days, the oldest files beyond the new limit are permanently "
            "deleted. If a downgrade leaves you with more active users "
            "than the new plan's seat limit, the extra seats are "
            "deactivated (not deleted) in order of least recent login; "
            "reactivating them requires upgrading again or removing other "
            "users first."
        ),
    },
    {
        "id": "creating-an-api-key",
        "title": "Creating an API Key",
        "category": "api_keys",
        "body": (
            "Go to Settings > API Keys > New Key. Choose a scope (see 'API "
            "Key Scopes and Permissions') and a name. The key's full value "
            "is shown once at creation time; store it securely, as it "
            "can't be viewed again afterward."
        ),
    },
    {
        "id": "rotating-an-api-key",
        "title": "Rotating an API Key",
        "category": "api_keys",
        "body": (
            "To rotate a key: go to Settings > API Keys, click 'Rotate' "
            "next to the key you want to replace, and confirm. This "
            "generates a new key value with the same name and scope, and "
            "keeps the old key valid for 24 hours so you can swap it into "
            "your systems without downtime. After 24 hours the old key "
            "stops working automatically. There's no way to keep both "
            "keys valid indefinitely; create a second key instead if you "
            "need two long-lived credentials."
        ),
    },
    {
        "id": "revoking-an-api-key",
        "title": "Revoking an API Key",
        "category": "api_keys",
        "body": (
            "Go to Settings > API Keys, click 'Revoke' next to the key, "
            "and confirm. Revocation is immediate and permanent: the key "
            "stops working right away and can't be un-revoked. This is "
            "different from rotation, which replaces a key but keeps the "
            "old one working for a 24-hour overlap."
        ),
    },
    {
        "id": "api-key-scopes-and-permissions",
        "title": "API Key Scopes and Permissions",
        "category": "api_keys",
        "body": (
            "Keys can be scoped to 'read-only' or 'read-write'. Read-only "
            "keys can call GET endpoints only. Read-write keys can also "
            "create, update, and delete resources. Scope is set at "
            "creation and can't be changed afterward; create a new key "
            "with the right scope instead."
        ),
    },
    {
        "id": "setting-up-sso-with-saml",
        "title": "Setting Up SSO with SAML",
        "category": "sso",
        "body": (
            "SAML SSO is available on Pro and Enterprise plans. Go to "
            "Settings > Security > SSO, upload your identity provider's "
            "metadata XML, and map the email attribute. Once enabled, "
            "members must log in through your identity provider; "
            "email/password login is disabled for the organization unless "
            "you keep a break-glass admin account exempted."
        ),
    },
    {
        "id": "supported-sso-providers",
        "title": "Supported SSO Providers",
        "category": "sso",
        "body": (
            "Acme Cloud supports any SAML 2.0-compliant identity provider, "
            "including Okta, Azure AD, Google Workspace, and OneLogin. "
            "SCIM provisioning (Enterprise only) is tested against Okta "
            "and Azure AD specifically; other SCIM-compliant providers may "
            "work but aren't officially verified."
        ),
    },
    {
        "id": "scim-user-provisioning",
        "title": "SCIM User Provisioning",
        "category": "sso",
        "body": (
            "SCIM is available on Enterprise only and requires SAML SSO to "
            "already be configured. It automatically creates, updates, and "
            "deactivates user accounts based on your identity provider's "
            "group membership, so you don't have to invite or remove "
            "users manually in Acme Cloud."
        ),
    },
    {
        "id": "troubleshooting-sso-login-failures",
        "title": "Troubleshooting SSO Login Failures",
        "category": "sso",
        "body": (
            "Most SSO login failures are caused by an email attribute "
            "mismatch between the identity provider and the Acme Cloud "
            "account, or an expired signing certificate on the identity "
            "provider side. Check Settings > Security > SSO > Login Logs "
            "for the specific SAML error before contacting support."
        ),
    },
    {
        "id": "refund-policy",
        "title": "Refund Policy",
        "category": "refunds",
        "body": (
            "Refunds are evaluated case by case by the billing team and "
            "are not automatic. Support agents and this chat cannot issue "
            "a refund directly or guarantee one will be approved; a "
            "request is logged as a support ticket and reviewed within 2 "
            "business days. Duplicate charges from a billing error are the "
            "most common approved case."
        ),
    },
    {
        "id": "cancelling-your-subscription",
        "title": "Cancelling Your Subscription",
        "category": "refunds",
        "body": (
            "Cancel from Settings > Billing > Cancel Subscription. "
            "Cancellation takes effect at the end of the current billing "
            "period; you keep access until then and are not charged "
            "again. There's no partial refund for the unused portion of "
            "the current period."
        ),
    },
    {
        "id": "chargebacks-and-disputes",
        "title": "Chargebacks and Disputes",
        "category": "refunds",
        "body": (
            "If you dispute a charge with your bank or card issuer instead "
            "of contacting us first, your account is suspended while the "
            "chargeback is investigated, per our payment processor's "
            "policy. Contacting support first is faster and doesn't risk "
            "suspension."
        ),
    },
    {
        "id": "adding-and-removing-team-members",
        "title": "Adding and Removing Team Members",
        "category": "account_management",
        "body": (
            "Admins can invite members from Settings > Team > Invite, up "
            "to the plan's seat limit (see 'Seat Limits by Plan'). "
            "Removing a member frees their seat immediately for a new "
            "invite; it does not delete content they created."
        ),
    },
    {
        "id": "changing-your-account-email",
        "title": "Changing Your Account Email",
        "category": "account_management",
        "body": (
            "Go to Settings > Profile > Email to change your login email. "
            "A confirmation link is sent to the new address; the change "
            "only takes effect once you click it. The old email keeps "
            "working until confirmation."
        ),
    },
    {
        "id": "exporting-your-data",
        "title": "Exporting Your Data",
        "category": "account_management",
        "body": (
            "Go to Settings > Data > Export to request a full export of "
            "your account's data as a downloadable zip. Exports are "
            "generated asynchronously and emailed as a download link "
            "within 24 hours; the link expires after 7 days."
        ),
    },
]
