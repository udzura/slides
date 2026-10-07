# 日本語版 SVG から英語版 (*-en.svg) を生成する。
# 使い方: cd assets && python3 svg_en.py
# 日本語の SVG を直したら、ここの対応表も直して再生成する。
# 新しい図を足すときの全体の手順は add_hover.py の冒頭を参照。
import re

T = {
'bitemporal-history': {
 '有効時間とトランザクション時間による履歴の分割': 'Splitting history by valid time and transaction time',
 '9月1日にTokyoを登録。10月17日に、10月1日からHakataだったと記録する。更新前のTokyoの行はトランザクション終了時刻を10月17日にして保持し、更新後は有効時間で分けたTokyoとHakataの2行を追加する。横軸がトランザクション時間、縦軸が有効時間。上と右は未来へ続く。':
   'Tokyo is registered on 9/1. On 10/17, we record that the location has been Hakata since 10/1. The old Tokyo row is kept with its transaction end set to 10/17, and two new rows, Tokyo and Hakata, split by valid time, are added. The horizontal axis is transaction time and the vertical axis is valid time. Both continue into the future.',
 '10/17に「10/1からHakataだった」と記録する': 'On 10/17, record “It has been Hakata since 10/1”',
 '有効時間': 'Valid time',
 '業務上いつ有効か': 'When it is valid',
 '更新前の記録 / 行A': 'Record before update / Row A',
 '過去の認識として残る': 'Kept as past knowledge',
 '新しい行C：10/1以降': 'New row C: from 10/1',
 '新しい行B：9/1〜10/1未満': 'New row B: 9/1 to before 10/1',
 '9/1 登録': '9/1 Created',
 '10/17 更新': '10/17 Updated',
 '未来へ →': 'Future →',
 '未来へ': 'Future',
 'トランザクション時間：DB上でその内容を正しいと扱った期間': 'Transaction time: when the DB treated the content as correct',
 '[transaction_from, transaction_to)　／　各矩形＝1レコード（上端・右端は表示を省略）':
   '[transaction_from, transaction_to)  /  Each rectangle = one record (top and right edges omitted)',
},
'carrierwave-lifecycle': {
 'CarrierWaveのキャッシュ・永続化・復元': 'CarrierWave: caching, storing, and retrieving',
 'cache!で一時保存しcache_idを生成。cache_nameはcache_idと元ファイル名からなる。バリデーションエラー後などはretrieve_from_cache!にcache_nameを渡して復元し保存を再開する。store!でキャッシュを永続化しidentifierを得る。その後はretrieve_from_store!にidentifierを渡し、store_dirなどの情報と合わせて保存済みファイルへの参照を復元する。':
   'cache! stores the file temporarily and generates a cache_id. The cache_name consists of the cache_id and the original filename. After a validation error, retrieve_from_cache! takes the cache_name to restore the file and resume saving. store! persists the cached file and returns an identifier. After that, retrieve_from_store! takes the identifier and, together with store_dir and other information, restores the reference to the stored file.',
 '① cache!：ファイルを一時保存': '① cache!: store the file temporarily',
 'cache_id を生成': 'Generates a cache_id',
 '② 再開に使う cache_name を保持': '② Keep the cache_name for resuming',
 'cache_id / 元ファイル名': 'cache_id / original filename',
 '③ store!：キャッシュから永続化': '③ store!: persist from the cache',
 '保存先へコピー（設定・ストレージにより移動等）': 'Copied to storage (or moved, depending on settings)',
 '④ identifier を得る（DBに保存する値）': '④ Get the identifier (saved in the DB)',
 '保存済みファイルへの参照を復元 → URL・読み出し': 'Restores the reference to the stored file → URL / read',
 'バリデーションエラー後などの再開': 'Resume after a validation error',
 'キャッシュ済みファイルを復元': 'Restores the cached file',
 'cache_id ≠ モデルのID': 'cache_id ≠ model ID',
 'identifier だけでパスは決まらない': 'identifier ≠ full path',
 'store_dir などの情報も使って': 'The path is built with store_dir',
 '保存先を組み立てる': 'and other information',
},
'cache-path-before': {
 'cache_path固定：変更以前': 'Fixing cache_path: before',
 'cache作成時にパスAへ保存。同じIDで復元しても、計算ロジックや入力が変わるとパスBを参照し、パスAに残っているファイルへ到達できない。':
   'At cache creation, the file is saved to Path A. When restoring with the same ID, if the logic or inputs have changed, the app looks at Path B and cannot reach the file that remains at Path A.',
 '① cache作成時': '① On cache creation',
 '② 復元時': '② On restore',
 'キャッシュID': 'Cache ID',
 '同じID：C123': 'Same ID: C123',
 'その時点の状態から計算': 'Calculated from current state',
 '計算結果：パスA': 'Result: Path A',
 '復元時の状態から再計算': 'Recalculated at restore',
 '計算結果：パスB': 'Result: Path B',
 'この間に、計算ロジックや入力が変わると…': 'If the logic or inputs change in between…',
 'パスA': 'Path A',
 'ファイルを保存': 'File saved',
 'パスB': 'Path B',
 'ファイルが見つからない': 'File not found',
 'IDは同じでも、参照先がずれる。実体はパスAに残っている': 'Same ID, wrong location. The file is still at Path A',
 '概念図：ID・パス名は説明用。IDはキャッシュの識別子で、モデルのIDとは別。':
   'Conceptual diagram: IDs and paths are examples. The ID identifies the cache, not the model.',
},
'cache-path-after': {
 'cache_path固定：変更以後': 'Fixing cache_path: after',
 'cache作成時にIDとパスAの対応をKVSへ記録。復元時には再計算せず、同じIDでKVSを引き、パスAのファイルへアクセスする。':
   'At cache creation, the mapping from the ID to Path A is recorded in a KVS. At restore time, the app does not recalculate; it looks up the same ID in the KVS and accesses the file at Path A.',
 '① cache作成時': '① On cache creation',
 '② 復元時': '② On restore',
 'キャッシュID': 'Cache ID',
 '同じID：C123': 'Same ID: C123',
 'KVSへ対応を記録': 'Record mapping in KVS',
 'C123 → パスA': 'C123 → Path A',
 'KVSから取得': 'Read from KVS',
 '保存した対応を使う': 'Reuse the mapping',
 'パスA': 'Path A',
 'ファイルを保存': 'File saved',
 '同じファイルを復元': 'Same file restored',
 '計算するのは作成時だけ。復元時は記録したパスを使う': 'Calculate only at creation. Use the recorded path on restore',
 '概念図：ID・パス名は説明用。IDはキャッシュの識別子で、モデルのIDとは別。':
   'Conceptual diagram: IDs and paths are examples. The ID identifies the cache, not the model.',
},
'upload-architecture': {
 'アプリから依存の有無に応じて処理を振り分ける設計案': 'Design draft: routing processing from the app by dependency',
 'アプリケーションから二方向へ分岐する。CarrierWaveの内部挙動に依存する処理は互換レイヤに閉じ込め、ストレージライブラリを呼び出す。内部挙動に依存しないリサイズやEXIF処理は、互換レイヤを経由せず外部サービスに任せる。':
   'The application branches in two directions. Processing that depends on CarrierWave’s internal behavior is contained in the compatibility layer, which calls the storage library. Resizing and EXIF processing, which do not depend on internal behavior, are delegated to an external service without going through the layer.',
 'アプリケーション': 'Application',
 '業務ロジック・履歴管理・記録したパス': 'Business logic / history / recorded paths',
 '内部挙動に依存する処理': 'Depends on internal behavior',
 '内部挙動に依存しない処理': 'Independent of internal behavior',
 '挙動を保ち、内部への依存を閉じ込める': 'Keeps behavior; contains internal dependencies',
 'ストレージライブラリ': 'Storage library',
 '今はCarrierWave': 'CarrierWave for now',
 '決まったパスにバイト列を置く': 'Puts bytes at a fixed path',
 '外部サービスに任せる': 'Delegate to an external service',
 'リサイズサービス': 'Resizing service',
 'サイズ違い画像をオンデマンド生成': 'Generates resized images on demand',
 '出力時のEXIF除去も担う': 'Also removes EXIF on output',
 '互換レイヤを経由せずに利用する': 'Used without going through the layer',
 '依存する処理は閉じ込め、独立できる処理は外へ切り出す': 'Contain what depends; move out what can stand alone',
},
'ai-qa-flow': {
 'ストーリーから構造化シナリオ・実行・観測結果・レポートへ': 'From story to structured scenario, execution, observation, and report',
 '人間が書いたストーリーをAIが可読性を保ってscenario.ymlに構造化。別のAIが実行し、確認事項と観測結果をobservation.ymlに記録する。レポート役のAIが期待値と照合し、人が読める判定・根拠付きレポートにまとめ、人がPRでレビューする。':
   'An AI structures the human-written story into scenario.yml while keeping it readable. Another AI runs it and records checks and observations in observation.yml. A reporting AI compares them with the expected results and writes a human-readable report with verdicts and reasons, which a human reviews in a PR.',
 '人間': 'Human',
 'ストーリーを書く': 'Write a story',
 '前提・操作・期待値を、人の言葉で記述': 'Preconditions, actions, and expected results in plain words',
 '入力': 'Input',
 '構造化するAI': 'Structuring AI',
 '読みやすさを保って構造化': 'Structure it, keeping it readable',
 'scenario.yml：手順・確認事項・期待値': 'scenario.yml: steps, checks, expected results',
 '曖昧なら推測せず止まる': 'Stops instead of guessing',
 '別のAI（実行役）': 'Another AI (executor)',
 'シナリオを受け取り、実行する': 'Receive and run the scenario',
 'ブラウザ操作・DOM・通信ログ・スクリーンショット': 'Browser actions, DOM, network logs, screenshots',
 'ファイルとスキーマで渡す': 'Passed via files and schemas',
 '実行役の出力': 'Executor’s output',
 '確認事項・観測結果を構造化': 'Structure checks and observations',
 'observation.yml：観測した事実と証跡': 'observation.yml: observed facts and evidence',
 'ここでは判定しない': 'No verdicts here',
 'レポート役のAI': 'Reporting AI',
 '人が読めるレポートにまとめる': 'Write a human-readable report',
 '期待値と照合し、判定と根拠を記述': 'Compare with expectations; give verdicts and reasons',
 '人がPRで証跡をレビュー': 'Human reviews it in a PR',
 '人が読める入力 → 構造化して受け渡す → 人が読める結果': 'Human-readable input → structured handoff → human-readable result',
},
'bench-preprocess': {
 '画像付き申請承認処理の所要時間内訳': 'Time breakdown of approving an application with images',
 '前処理全部ありは合計17.9秒で、うちGCS処理12.56秒、サムネ画像縮小処理2.27秒、画像サイズ取得処理1.42秒、EXIF関係の操作0.60秒、その他1.10秒。前処理なしは合計5.8秒で、うちGCS処理4.96秒、その他0.85秒。ローカルでの3回平均。':
   'With all preprocessing, the total is 17.9 s: GCS operations 12.56 s, thumbnail resizing 2.27 s, getting the image size 1.42 s, EXIF operations 0.60 s, and other 1.10 s. Without preprocessing, the total is 5.8 s: GCS operations 4.96 s and other 0.85 s. Average of three local runs.',
 'GCS 処理　12.56s → 4.96s': 'GCS operations  12.56s → 4.96s',
 'サムネ画像縮小処理　2.27s → 0.00s': 'Thumbnail resizing  2.27s → 0.00s',
 '画像サイズ取得処理　1.42s → 0.00s': 'Getting image size  1.42s → 0.00s',
 'EXIF 関係の操作　0.60s → 0.00s': 'EXIF operations  0.60s → 0.00s',
 'その他　1.10s → 0.85s': 'Other  1.10s → 0.85s',
 '秒（ローカル計測・3回平均）': 'Seconds (local, average of 3 runs)',
 '前処理全部あり': 'With preprocessing',
 '前処理なし': 'Without preprocessing',
 'GCS 処理 12.56s': 'GCS 12.56s',
 'GCS 処理 4.96s': 'GCS 4.96s',
},
}

# 図を描き直したもの・新しく足したもの（上の対応表より優先）
T['bitemporal-history'] = {
 '有効時間とトランザクション時間による履歴の分割': 'Splitting history by valid time and transaction time',
 '横軸は有効時間で左から右、縦軸はトランザクション時間で上から下へ進む。9/1にTokyoを登録。10/17に10/1からHakataだったと記録する。上段の旧行Aを残し、下段に9/1から10/1未満のTokyoの行Bと10/1以降のHakataの行Cを追加する。':
   'Valid time runs left to right and transaction time runs top to bottom. Tokyo is registered on 9/1. On 10/17, we record that the location has been Hakata since 10/1. The old row A stays at the top, and row B (Tokyo, 9/1 to before 10/1) and row C (Hakata, from 10/1) are added below.',
 '10/17に「10/1からHakataだった」と記録する': 'On 10/17, record “It has been Hakata since 10/1”',
 '有効時間 → 業務上いつ有効か': 'Valid time → when it is valid in business',
 'トランザクション時間': 'Transaction time',
 'DB上でその内容を': 'When the DB treated',
 '正しいと扱った期間': 'the content as correct',
 '更新前の記録 / 行A': 'Record before update / Row A',
 '過去の認識として残る': 'Kept as past knowledge',
 '行B：9/1〜10/1未満': 'Row B: 9/1 to before 10/1',
 '行C：10/1以降': 'Row C: from 10/1',
 '9/1 登録': '9/1 Created',
 '10/17 更新': '10/17 Updated',
 '未来へ ↓': 'Future ↓',
 '未来へ': 'Future',
 '各矩形＝1レコード ／ 右端・下端は表示を省略（未来へ続く）':
   'Each rectangle = one record  /  right and bottom edges omitted (they continue into the future)',
}
T['carrierwave-lifecycle-write'] = {
 '書き込み：キャッシュから永続化へ': 'Write: from the cache to persistent storage',
 '① cache!：画像を一時保存': '① cache!: store the image temporarily',
 'cache_id を生成し、cache_path に保存': 'Generates a cache_id and saves to cache_path',
 '② cache_name を保持': '② Keep the cache_name',
 'cache_id / 元ファイル名（再開に使う）': 'cache_id / original filename (for resuming)',
 '③ store!：画像を永続化': '③ store!: persist the image',
 'キャッシュから store_path へコピー・移動等': 'Copied or moved from the cache to store_path',
 '④ identifier をDBに保存': '④ Save the identifier to the DB',
 '例：photo.jpg（画像本体ではなく識別子）': 'e.g., photo.jpg (an identifier, not the image)',
 '保存を再開するとき': 'When resuming a save',
 'キャッシュ済み画像を復元': 'Restores the cached image',
 'cacheとstoreは別の段階': 'cache and store are separate steps',
 '画像本体 → ストレージ': 'Image → storage',
 '概念図：DBへの書き込みとstore!の厳密な順序は、モデル連携のコールバックによる':
   'Conceptual diagram: the exact order of the DB write and store! depends on model callbacks',
}
T['carrierwave-lifecycle-read'] = {
 '読み出し・参照：DBのidentifierからファイルへ': 'Read: from the identifier in the DB to the file',
 '① DBからidentifierを読み出す': '① Read the identifier from the DB',
 'モデルのカラムに保存された値：photo.jpg': 'Value stored in the model’s column: photo.jpg',
 '読み出した識別子をUploaderへ渡す': 'Passes the identifier to the Uploader',
 '③ 保存先のパスを組み立てる': '③ Build the storage path',
 'store_dir などの情報 ＋ identifier → store_path': 'store_dir and other info + identifier → store_path',
 '④ 保存済み画像への参照が使える': '④ The stored image can be referenced',
 'URLの生成や、必要に応じたファイルの読み出し': 'Generate URLs, or read the file when needed',
 'retrieveは参照の復元。呼び出した時点で画像の全バイトを取得するとは限らない':
   'retrieve restores a reference; it does not always fetch all the bytes at call time',
}
T['cache-path-after'].update({
 'cache作成時にIDとパスAの対応をRedisへ記録。復元時には再計算せず、同じIDでRedisを引き、パスAのファイルへアクセスする。':
   'At cache creation, the mapping from the ID to Path A is recorded in Redis. At restore time, the app does not recalculate; it looks up the same ID in Redis and accesses the file at Path A.',
 'Redisへ対応を記録': 'Record mapping in Redis',
 'Redisから取得': 'Read from Redis',
})

# 英語のほうが長くなるラベルだけ文字を小さくする
FONT_SIZE = {
 'cache-path-before': {'Calculated from current state': 22, 'Recalculated at restore': 22},
 'bench-preprocess': {'With preprocessing': 18, 'Without preprocessing': 18},
}

JA = re.compile(r'[぀-ヿ一-鿿！-～]')

for name, table in T.items():
    src = open(f'{name}.svg', encoding='utf-8').read()

    def repl(m):
        tag, text, close = m.groups()
        if not JA.search(text):
            return m.group(0)  # 記号や英字だけのラベルはそのまま
        if text not in table:
            raise SystemExit(f'{name}: 対応表にない文字列 {text!r}')
        out = table[text]
        size = FONT_SIZE.get(name, {}).get(out)
        if size:
            tag = re.sub(r'font-size="\d+"', f'font-size="{size}"', tag)
        return tag + out.replace('&', '&amp;') + close

    dst = re.sub(r'(<(?:text|title|desc)\b[^>]*>)([^<]+)(</(?:text|title|desc)>)', repl, src)
    assert not JA.search(dst), f'{name}: 日本語が残っている'
    open(f'{name}-en.svg', 'w', encoding='utf-8').write(dst)
    print(f'wrote {name}-en.svg')
