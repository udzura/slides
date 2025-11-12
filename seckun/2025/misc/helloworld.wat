(module
  ;; WASI の fd_write 関数をインポート
  ;; fd_write(fd, iovs, iovs_len, nwritten) -> errno
  (import "wasi_snapshot_preview1" "fd_write" 
    (func $fd_write (param i32 i32 i32 i32) (result i32)))
  
  ;; メモリを1ページ(64KB)確保
  (memory 1)
  (export "memory" (memory 0))
  
  ;; "Hello, World!\n" の文字列データをメモリのオフセット8に配置
  (data (i32.const 8) "Hello, World!\n")
  
  ;; _start 関数（WASIのエントリーポイント）
  (func $main (export "_start")
    ;; iovec構造体を作成
    ;; メモリレイアウト:
    ;; オフセット 0-3: 文字列へのポインタ (8)
    ;; オフセット 4-7: 文字列の長さ (14)
    
    ;; iov.buf = 8 (文字列の開始位置)
    i32.const 0
    i32.const 8
    i32.store
    
    ;; iov.buf_len = 14 (文字列の長さ)
    i32.const 4
    i32.const 14
    i32.store
    
    ;; fd_write を呼び出す
    ;; fd_write(1, 0, 1, 20)
    ;; 1: stdout のファイルディスクリプタ
    ;; 0: iovec構造体の配列へのポインタ
    ;; 1: iovec構造体の数
    ;; 20: 書き込んだバイト数を格納する場所
    i32.const 1   ;; stdout
    i32.const 0   ;; iovecの開始位置
    i32.const 1   ;; iovecの数
    i32.const 20  ;; 書き込んだバイト数を格納
    call $fd_write
    drop          ;; 戻り値(errno)を破棄
  )
)