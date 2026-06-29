import { DurableObject } from "cloudflare:workers";

// Durable Object: 名前ごとに 1 インスタンスが割り当てられ、
// その中の状態は常に整合する。ここではアクセス回数を数える。
export class Counter extends DurableObject {
  async fetch(_req: Request): Promise<Response> {
    let value = (await this.ctx.storage.get<number>("value")) ?? 0;
    value += 1;
    await this.ctx.storage.put("value", value);
    return Response.json({ counter: value });
  }
}
