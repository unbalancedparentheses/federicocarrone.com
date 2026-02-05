+++
title = "Building a SaaS with Elixir/Phoenix and React"
date = "2026-01-25"
description = "Our stack and practices for building SaaS applications: Elixir on the backend, React on the frontend, Nix for everything else. No Docker. No Kubernetes."
[taxonomies]
keywords=["elixir", "phoenix", "react", "SaaS", "nix"]
[extra]
author = "Federico Carrone"
pinned = false
+++

Most SaaS codebases I've seen share the same problems. Authentication that sort of works until someone finds an edge case. Caching layers that nobody fully understands. Deployment scripts held together with hope. The team moves fast early on, then spends years paying down the debt.

We got tired of this cycle. Over several projects, we developed a stack and a set of practices that let us move fast without leaving landmines for our future selves. Elixir on the backend, React on the frontend, Nix for everything else. No Docker. No Kubernetes. Decisions that raised eyebrows at first but have proven themselves in production.

This post explains what we use and why.

## The case for Elixir

Our backend runs on Elixir, which might seem like an unusual choice in a world dominated by Node, Python, and Go. The reason comes down to what happens when things go wrong.

Elixir runs on the Erlang VM, a runtime Ericsson built in the 1980s for telephone switches. These systems needed to stay up for years at a time, handling failures gracefully without human intervention. Crashes are expected in Elixir, even encouraged as an error-handling strategy. When a process crashes, it crashes in isolation. A supervisor notices and restarts it. The rest of the system keeps running. You don't get woken up at 3am because one user's request hit an edge case that brought down the whole server.

Phoenix is the web framework we use on top of Elixir, though we use it differently than most teams. Phoenix has become famous for LiveView, its technology for building interactive UIs with server-rendered HTML. We don't use it. Instead, Phoenix serves only JSON through a REST API, and a completely separate React application handles everything the user sees.

This creates a hard boundary between backend and frontend. Backend developers focus entirely on data and business logic without thinking about UI concerns. Frontend developers own the user experience end-to-end without needing to understand Elixir. The two teams communicate through the API contract, and neither steps on the other's work. When we eventually build mobile apps, they'll consume the same API with no new backend work required.

## Why we abandoned Docker for Nix

This is probably our most controversial choice. Docker has become the default for development environments and deployment. We use Nix instead.

When a new developer joins our team, the onboarding process is simple: clone the repository and run `nix develop`. A few minutes later, they have everything they need. Elixir, Node.js, PostgreSQL, Redis, Meilisearch, all running natively on their machine. Not in containers. Actually installed. Without container overhead, everything runs at native speed. Debugging is straightforward because there's no abstraction layer between you and the process. And there are no Docker Desktop licensing conversations.

But the real payoff comes in production, where our servers run NixOS. The entire server configuration is declarative and lives in version control alongside our code. When we push a change, every server ends up in exactly the same state. Deployments are atomic. They succeed completely or fail completely, with no partial states to debug. If something goes wrong, rolling back takes one command.

Nix has a steep learning curve. The documentation is notoriously difficult, and the language has unusual semantics. But once you've internalized the concepts, you get guarantees Docker can't provide. A build that works today will produce the exact same result in five years, because every input is pinned and reproducible.

## Building for offline use

Most web applications assume users have constant connectivity. Ours doesn't, and this assumption has shaped our entire frontend architecture.

The frontend stores data locally using Dexie.js, a library that wraps IndexedDB with a friendlier API. When a user makes changes, those changes save to the local database first. A sync queue tracks what needs to go to the server, and when the network becomes available, the queue drains automatically.

Consider how software actually gets used. A salesperson updates CRM records on a flight with no WiFi. A technician fills out inspection forms in a basement with no signal. Someone's home internet drops for thirty seconds while they're submitting an important form. In all these scenarios, our app keeps working. Users might not even notice the interruption. The UI responds immediately to their actions, and synchronization happens in the background.

We use TanStack Query for data fetching, but with caching completely disabled. Every API call fetches fresh data from the server. IndexedDB is our cache, and we control exactly when and how it syncs. No more stale data bugs because some cache somewhere wasn't invalidated properly.

## Database decisions

PostgreSQL. UUIDs as primary keys instead of auto-incrementing integers. This prevents enumeration attacks, where an attacker discovers they can access `/users/123` and starts systematically trying `/users/124`, `/users/125`, and so on. UUIDs also let us generate identifiers on the client before the record exists in the database.

For multi-tenancy, we use row-level isolation. Every table that holds customer data includes an `org_id` column, and every query filters by it. The alternative is giving each tenant their own database schema. That provides stronger isolation, but migrations have to run once per tenant, connection pools multiply, and cross-tenant queries for admin purposes become complicated. Row-level isolation is simpler and scales well for most SaaS applications.

We also have a strict rule: no random data in tests. We don't use Faker. Every test uses explicit, predictable inputs. When a test fails, it fails the same way every time you run it. You can debug it, reproduce it, and fix it. Random test data causes tests that fail one time in twenty for reasons nobody can reproduce.

## Authentication

Most tutorials get authentication wrong in ways that create real security vulnerabilities.

We use JWT tokens with a two-token system. The access token is short-lived, expiring after 15 minutes. It's stateless, so the backend validates it without touching the database. The refresh token lasts 7 days and is stored in the database. When the access token expires, the frontend uses the refresh token to get a new one.

Because refresh tokens live in the database, we can revoke them instantly. When a user clicks "log out of all devices," it actually works. We delete their refresh tokens, and within 15 minutes every session everywhere is invalidated.

Both tokens live in httpOnly cookies rather than localStorage. JavaScript cannot read httpOnly cookies, which means an XSS vulnerability cannot steal the tokens. Most tutorials store JWTs in localStorage because it's simpler, but it leaves users vulnerable to script injection.

Password hashing uses Argon2, OWASP's current recommendation over bcrypt.

## Libraries

For JWT handling, we use Joken instead of Guardian. Guardian is popular but tries to do too much. It has opinions about plugs, permissions, token types. We found ourselves fighting these abstractions. Joken just encodes and decodes tokens. We handle the rest.

Oban handles background jobs. Unlike Sidekiq or Celery, Oban uses PostgreSQL as its backend instead of Redis. One less service to run. Job state is transactional with your application data. You can insert a database record and enqueue a job in the same transaction, with the guarantee that either both happen or neither does.

On the frontend: Zustand for client state, TanStack Query for API calls, React Hook Form with Zod for forms. For components, shadcn/ui built on Radix primitives. Radix handles accessibility correctly, which is hard to do from scratch.

## Deployment

We deploy to bare metal servers running NixOS. No Docker in production. No Kubernetes.

Kubernetes solves problems of scale that most SaaS applications don't have. For a typical SaaS with a handful of services, it adds operational complexity without proportional benefits. You end up managing Kubernetes instead of building your product.

Our setup is simple. systemd supervises the Phoenix processes. Caddy handles TLS and reverse proxying, automatically getting certificates from Let's Encrypt. When we deploy, we push the new NixOS configuration to our servers using deploy-rs. The switch is atomic. If something goes wrong, we roll back in seconds.

Secrets are encrypted in the git repository using agenix. Each server has its own age encryption key, and secrets are decrypted at deployment time on the target machine.

## Observability

We set up logging, metrics, and error tracking before writing the first feature. Finding out about outages from users is embarrassing and preventable.

Logs are structured JSON. Every entry includes a request ID, user ID, and organization ID. These logs ship to Grafana Loki through Promtail.

The request ID is generated when a request enters our system and propagates through everything: API calls, background jobs, external service calls. When a user reports a problem and we have their request ID, we can trace exactly what happened across the entire system.

Metrics go to Prometheus, errors to Sentry. Dashboards and alerts exist before the first feature because retrofitting them later never happens.

## Build order

First comes the foundation: Nix configuration, Makefile, project structure, database setup. Feels like yak shaving, but a shaky foundation causes problems forever.

Second, we build admin tools. A dashboard for internal use. User impersonation, which lets us log in as any user to see what they see. Seed data that creates realistic test scenarios. You need to demo to stakeholders before the product is done. You need to debug issues by experiencing the product as users do.

Third is authentication, because almost everything else depends on knowing who the user is.

Then the actual product features. Polish like error handling, loading states, and accessibility comes last but isn't optional.

## The full guide

The complete guide is at [github.com/unbalancedparentheses/saas_guidelines](https://github.com/unbalancedparentheses/saas_guidelines). Database connection pooling, rate limiting, circuit breakers, health checks, graceful shutdown, disaster recovery, and more.
