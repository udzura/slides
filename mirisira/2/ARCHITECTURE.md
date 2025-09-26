# ARCHITECTURE.md

## Rigel アーキテクチャ概要

Rigelは、LLM（大規模言語モデル）を活用したコマンド実行エージェントをCLIとして提供するGo製ツールです。ここでは `cmd/rigel/main.go` から主要ライブラリを辿り、全体の処理フローと構成を解説します。

---

### 1. エントリーポイント

- **`cmd/rigel/main.go`**
  - CLIの起動点。フラグや設定ファイルの読み込み、AgentEngineの初期化、REPLや単発コマンドの実行を担当。

- **`cmd/rigel/main.go`**
  - CLIの起動点。フラグや設定ファイルの読み込み、AgentEngineの初期化、REPLや単発コマンドの実行を担当。

#### コード引用
```go
func main() {
  if err := rootCmd.Execute(); err != nil {
    log.Fatal(err)
  }
}
```
`main()` でCobra CLIのエントリーポイント `rootCmd.Execute()` を呼び出します。
### 2. コア構成要素

#### AgentEngine
- 設定ファイルを読み込み、LLMプロバイダ・サンドボックス・コマンドレジストリを初期化。
- Agentのインスタンスを生成し、ユーザー入力を受けて処理を開始。


#### 設定ファイルの読み込み（`internal/config/config.go`）
```go
func Load(configFile string) (*Config, error) {
  if configFile == "" {
    configFile = ".env"
  }
  // ...省略...
  viper.SetEnvPrefix("RIGEL")
  viper.AutomaticEnv()
  viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

  cfg := &Config{
    Provider:        getEnv("PROVIDER", "ollama"),
    AnthropicAPIKey: os.Getenv("ANTHROPIC_API_KEY"),
    // ...省略...
  }
```
`.env`や環境変数から設定をロードし、LLMプロバイダやモデル名などを取得します。

#### サンドボックスの有効化（`internal/sandbox/sandbox.go`）
```go
func IsSandboxed() bool {
  return os.Getenv(sandboxEnvVar) == "1"
}

func EnableSandbox(sandboxDir string) error {
  // ...省略...
  // Only support macOS for now
  if runtime.GOOS != "darwin" {
    return fmt.Errorf("sandbox mode is currently only supported on macOS")
  }
  // ...省略...
}
```
macOSではデフォルトでサンドボックスを有効化し、ファイル操作を制限します。

#### LLMプロバイダの初期化（`internal/llm/provider.go`）
```go
type Provider interface {
  Generate(ctx context.Context, prompt string) (string, error)
  // ...省略...
}
```
LLMプロバイダは `Provider` インターフェースを実装し、`llm.NewProvider(cfg)` で初期化されます。

#### Agentの生成とツール登録（`internal/agent/agent.go`）
```go
func New(provider llm.Provider) *Agent {
  return &Agent{
    provider: provider,
    memory: &Memory{
      conversationHistory: []Message{},
      context:             make(map[string]interface{}),
    },
    tools:           []tools.Tool{},
    promptAnalyzer:  NewPromptAnalyzer(provider),
    autoToolEnabled: true,
  }
}
```
LLMプロバイダを受け取り、会話履歴やツール群を持つ `Agent` を生成します。

#### コマンド・ツールの登録と実行（`internal/command/commands.go`）
```go
// showHelp displays the help message
func showHelp() Result {
  var help strings.Builder
  help.WriteString("Available commands:\n\n")
  for _, cmd := range AvailableCommands {
    help.WriteString(fmt.Sprintf("  %s - %s\n", cmd.Command, cmd.Description))
  }
  // ...省略...
}
```
コマンドは `AvailableCommands` に登録され、ユーザー入力に応じて実行されます。
- 会話履歴や変数、プラン（計画）を保持。
- LLMやサンドボックス、コマンド実行のオーケストレーションを担う。

`internal/agent/agent.go` でAgent本体を実装。会話履歴や変数、プラン（計画）を保持し、LLMやサンドボックス、コマンド実行のオーケストレーションを担います。
- `internal/llm/anthropic.go` や `internal/llm/ollama.go` で具体的な実装。
- 設定に応じて動的にロード。

`internal/llm/provider.go` でProviderインターフェースを定義し、AnthropicやOllamaなどの具体的実装が存在します。
- コマンド実行を分離プロセスで行い、リソース制限や副作用の隔離を実現。


`internal/sandbox/sandbox.go` でコマンド実行を分離プロセスで行い、リソース制限や副作用の隔離を実現します。
- `internal/command/handler.go` でユーザー入力に応じたコマンドディスパッチ。
- 各コマンドは `CommandContext` を受け取り、AgentやSandbox、Logger等にアクセス可能。

`internal/command/commands.go` でコマンドを登録し、ユーザー入力に応じてディスパッチされます。
- コマンドやLLM生成コードから呼び出し可能。


`internal/tools/` 配下にドメイン固有のツール（例: `code_tool.go`）があり、コマンドやLLM生成コードから呼び出し可能です。
- `internal/history/` で履歴の保存・リプレイも可能。


`internal/state/` 配下でチャットログやLLMメタデータを永続化し、`internal/history/` で履歴の保存・リプレイも可能です。

---

`internal/config/config.go` でYAML/JSON設定ファイルをロード・バリデートします。
### 3. 処理フロー概要

1. **CLI起動**: main.goでフラグ・設定を読み込み、AgentEngineを初期化。
2. **Agent生成**: Agentインスタンスを作成し、LLMやSandbox、コマンドレジストリをセットアップ。
3. **ユーザー入力受付**: REPLまたは単発コマンドでユーザー入力を受け付け。
1. **CLI起動**: main.goでフラグ・設定を読み込み、AgentEngineを初期化。
   - `main()` → `rootCmd.Execute()`
2. **Agent生成**: Agentインスタンスを作成し、LLMやSandbox、コマンドレジストリをセットアップ。
   - `agent.New(provider)` でAgent生成
3. **ユーザー入力受付**: REPLまたは単発コマンドでユーザー入力を受け付け。
   - 対話UI: `runTermflowChatMode(provider)`
   - パイプ入力: `intelligentAgent.Execute(context.Background(), prompt)`
4. **コマンド解釈・実行**: 入力を解析し、該当コマンドをハンドラ経由で実行。
   - `internal/command/commands.go` のコマンド群
5. **LLM連携**: 必要に応じてLLMにプロンプトを投げ、応答を取得。
   - `provider.Generate(ctx, prompt)` など
6. **サンドボックス実行**: 外部コマンドやファイル操作はサンドボックス内で安全に実行。
   - `sandbox.EnableSandbox()` など
7. **状態・履歴管理**: 会話やコマンド履歴を保存し、セッションを継続。
   - `internal/state/`, `internal/history/`

#### コード引用（main.goより）
```go
// パイプ入力時
intelligentAgent := agent.New(provider)
fileTool := tools.NewFileTool()
intelligentAgent.RegisterTool(fileTool)
response, err := intelligentAgent.Execute(context.Background(), prompt)

// 対話UI時
runTermflowChatMode(provider)
```
パイプ入力時はAgentを生成し、ツールを登録してプロンプトを実行。対話モードでは `runTermflowChatMode` でUIセッションを開始します。
### 4. 依存関係図（簡易）

```
+-----------------------------+
|          CLI (main.go)      |
+-----------------------------+
            |
            v
+-----------------------------+
|        AgentEngine          |
+-----------------------------+
            |
            v
+-----------------------------+
|           Agent             |
+-----------------------------+
     /            \
    v              v
+-----+        +------------+
| LLM |        |  Sandbox   |
+-----+        +------------+
    ^              |
    |              v
+-----------------------------+
|  External Providers        |
+-----------------------------+
```

---

### 5. 拡張ポイント
- コマンドやツールの追加は `internal/command/` や `internal/tools/` にファイルを追加し、`commands.go` で登録。
- LLMプロバイダの追加は `internal/llm/` にProvider実装を追加。

---

### 6. 参考
- 詳細は `AGENTS.md` も参照。
- 各パッケージの役割や拡張方法はリポジトリ内コメント・READMEも参照。


---

## 付録: 主要処理のコード引用付き解説

### 1. エントリーポイント（`cmd/rigel/main.go`）

```go
func main() {
  if err := rootCmd.Execute(); err != nil {
    log.Fatal(err)
  }
}
```
- `main()` でCobra CLIのエントリーポイント `rootCmd.Execute()` を呼び出します。

---

### 2. 設定ファイルの読み込み（`internal/config/config.go`）

```go
func Load(configFile string) (*Config, error) {
  if configFile == "" {
    configFile = ".env"
  }
  // ...省略...
  viper.SetEnvPrefix("RIGEL")
  viper.AutomaticEnv()
  viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

  cfg := &Config{
    Provider:        getEnv("PROVIDER", "ollama"),
    AnthropicAPIKey: os.Getenv("ANTHROPIC_API_KEY"),
    // ...省略...
  }
```
`.env`や環境変数から設定をロードし、LLMプロバイダやモデル名などを取得します。

---

### 3. サンドボックスの有効化（`internal/sandbox/sandbox.go`）

```go
func IsSandboxed() bool {
  return os.Getenv(sandboxEnvVar) == "1"
}

func EnableSandbox(sandboxDir string) error {
  // ...省略...
  // Only support macOS for now
  if runtime.GOOS != "darwin" {
    return fmt.Errorf("sandbox mode is currently only supported on macOS")
  }
  // ...省略...
}
```
macOSではデフォルトでサンドボックスを有効化し、ファイル操作を制限します。

---

### 4. LLMプロバイダの初期化（`internal/llm/provider.go`）

```go
type Provider interface {
  Generate(ctx context.Context, prompt string) (string, error)
  // ...省略...
}
```
LLMプロバイダは `Provider` インターフェースを実装し、`llm.NewProvider(cfg)` で初期化されます。

---

### 5. Agentの生成とツール登録（`internal/agent/agent.go`）

```go
func New(provider llm.Provider) *Agent {
  return &Agent{
    provider: provider,
    memory: &Memory{
      conversationHistory: []Message{},
      context:             make(map[string]interface{}),
    },
    tools:           []tools.Tool{},
    promptAnalyzer:  NewPromptAnalyzer(provider),
    autoToolEnabled: true,
  }
}
```
LLMプロバイダを受け取り、会話履歴やツール群を持つ `Agent` を生成します。

---

### 6. コマンド・ツールの登録と実行（`internal/command/commands.go`）

```go
// showHelp displays the help message
func showHelp() Result {
  var help strings.Builder
  help.WriteString("Available commands:\n\n")
  for _, cmd := range AvailableCommands {
    help.WriteString(fmt.Sprintf("  %s - %s\n", cmd.Command, cmd.Description))
  }
  // ...省略...
}
```
コマンドは `AvailableCommands` に登録され、ユーザー入力に応じて実行されます。

---

### 7. 対話・実行フロー（`cmd/rigel/main.go`）

```go
// パイプ入力時
intelligentAgent := agent.New(provider)
fileTool := tools.NewFileTool()
intelligentAgent.RegisterTool(fileTool)
response, err := intelligentAgent.Execute(context.Background(), prompt)

// 対話UI時
runTermflowChatMode(provider)
```
パイプ入力時はAgentを生成し、ツールを登録してプロンプトを実行。対話モードでは `runTermflowChatMode` でUIセッションを開始します。
