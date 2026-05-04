import http from 'k6/http';
import { check, sleep } from 'k6';

// vus: 仮想ユーザー数。それぞれが独立して default() を繰り返す
export const options = {
    vus: 15,
    duration: '30s',
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
