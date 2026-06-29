import { jwtVerify, createRemoteJWKSet } from "jose";
import { Counter } from "./counter";

export { Counter };

export interface Env {
  MY_KV: KVNamespace;
  MY_BUCKET: R2Bucket;
  DB: D1Database;
  COUNTER: DurableObjectNamespace;
  MY_QUEUE: Queue<JobMessage>;
  TEAM_DOMAIN: string;
  POLICY_AUD: string;
}

interface JobMessage {
  type: string;
  payload: unknown;
  at: number;
}

const json = (data: unknown, status = 200) =>
  Response.json(data as object, { status });

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname;

    try {
      // --- トップ: 使い方一覧 ---
      if (path === "/") {
        return json({
          message: "Fukuoka.edge Cloudflare services sample",
          endpoints: [
            "GET  /kv            KV に書いて読む",
            "PUT  /r2/:key       R2 にボディを保存",
            "GET  /r2/:key       R2 から取得",
            "GET  /d1            D1 を SELECT",
            "GET  /counter/:room Durable Objects でカウント",
            "POST /jobs          Queues にジョブを積む",
            "GET  /whoami        Access の JWT から本人を取得",
          ],
        });
      }

      // --- KV ---
      if (path === "/kv") {
        const key = "last-access";
        const prev = await env.MY_KV.get(key);
        await env.MY_KV.put(key, new Date().toISOString(), {
          expirationTtl: 3600,
        });
        return json({ service: "KV", previous: prev, updated: true });
      }

      // --- R2 ---
      if (path.startsWith("/r2/")) {
        const key = path.slice("/r2/".length);
        if (req.method === "PUT") {
          await env.MY_BUCKET.put(key, req.body);
          return json({ service: "R2", put: key });
        }
        const obj = await env.MY_BUCKET.get(key);
        if (!obj) return json({ service: "R2", error: "not found" }, 404);
        return new Response(obj.body, {
          headers: { "content-type": "application/octet-stream" },
        });
      }

      // --- D1 ---
      if (path === "/d1") {
        const minAge = Number(url.searchParams.get("minAge") ?? "18");
        const { results } = await env.DB.prepare(
          "SELECT id, name, age FROM users WHERE age >= ? ORDER BY age",
        )
          .bind(minAge)
          .all();
        return json({ service: "D1", minAge, results });
      }

      // --- Durable Objects ---
      if (path.startsWith("/counter/")) {
        const room = path.slice("/counter/".length) || "default";
        const id = env.COUNTER.idFromName(room);
        const stub = env.COUNTER.get(id);
        const res = await stub.fetch(req);
        const body = (await res.json()) as { counter: number };
        return json({ service: "Durable Objects", room, ...body });
      }

      // --- Queues (producer) ---
      if (path === "/jobs" && req.method === "POST") {
        const payload = await req.json().catch(() => ({}));
        await env.MY_QUEUE.send({ type: "demo", payload, at: Date.now() });
        return json({ service: "Queues", queued: true });
      }

      // --- Access (認証情報の取得) ---
      if (path === "/whoami") {
        const identity = await verifyAccess(req, env);
        if (!identity) return json({ service: "Access", error: "unauthorized" }, 403);
        return json({ service: "Access", ...identity });
      }

      return json({ error: "not found", path }, 404);
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      return json({ error: message }, 500);
    }
  },

  // --- Queues (consumer) ---
  // producer が積んだメッセージをバッチで受け取り処理する。
  async queue(batch: MessageBatch<JobMessage>, _env: Env): Promise<void> {
    for (const msg of batch.messages) {
      try {
        console.log("processing job:", JSON.stringify(msg.body));
        // ここで重い処理・外部 API 連携・メール送信などを行う
        msg.ack();
      } catch (err) {
        console.error("job failed, will retry:", err);
        msg.retry();
      }
    }
  },
} satisfies ExportedHandler<Env>;

// Access の JWT を検証し、本人情報を返す。失敗時は null。
async function verifyAccess(
  req: Request,
  env: Env,
): Promise<{ email?: string; sub?: string } | null> {
  const token = req.headers.get("cf-access-jwt-assertion");
  if (!token || !env.POLICY_AUD) return null;

  const JWKS = createRemoteJWKSet(
    new URL(`${env.TEAM_DOMAIN}/cdn-cgi/access/certs`),
  );
  try {
    const { payload } = await jwtVerify(token, JWKS, {
      issuer: env.TEAM_DOMAIN,
      audience: env.POLICY_AUD,
    });
    return { email: payload.email as string, sub: payload.sub };
  } catch {
    return null;
  }
}
