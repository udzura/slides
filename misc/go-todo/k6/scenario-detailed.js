import http from 'k6/http';
import { check, sleep } from 'k6';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.1.0/index.js'

// vus: 仮想ユーザー数。それぞれが独立して default() を繰り返す
export const options = {
    vus: 15,
    duration: '5s',
    summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};
// export const options = {
//     vus: 50,
//     duration: '3m',
// };

const BASE = __ENV.BASE_URL || 'http://localhost:8080';
const HEAD = { headers: { 'Content-Type': 'application/json' } };

// この関数が 1 VU = 1ユーザーの「行動シナリオ」
export default function () {
    // __VU: このVUのID、__ITER: このVUの繰り返し回数
    const title = `task-vu${__VU}-iter${__ITER}`;

    const created = http.post(`${BASE}/todos`,
        JSON.stringify({ title }), HEAD);
    check(created, { 'created': (r) => r.status === 201 });
    const id = created.json('id');

    const listed = http.get(`${BASE}/todos`);
    check(listed, { 'listed': (r) => r.status === 200 });

    const updated = http.put(`${BASE}/todos/${id}`,
        JSON.stringify({ title: 'updated' }), HEAD);
    check(updated, { 'updated': (r) => r.status === 200 });

    const deleted = http.del(`${BASE}/todos/${id}`);
    check(deleted, { 'deleted': (r) => r.status === 204 });

    sleep(1); // Think Time: 次のループまで待つ（人間らしく）
}

export function handleSummary(data) {
  return {
    "summary.html": htmlReport(data), // カレントディレクトリに summary.html を出力
    stdout: textSummary(data, { indent: " ", enableColors: true }), // ターミナルにも通常通り出力
  };
}