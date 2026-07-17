# hermes-modelscope-api

Native ModelScope model-provider plugin for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

It registers `modelscope` as a first-class OpenAI-compatible chat-completions
provider using the ModelScope Inference API directly.

## Provider

- Provider ID: `modelscope`
- Alias: `ms`
- Base URL: `https://api-inference.modelscope.cn/v1`
- Chat completions URL: `https://api-inference.modelscope.cn/v1/chat/completions`
- Auth env var: `MODELSCOPE_API_KEY`
- Optional base URL override: `MODELSCOPE_BASE_URL`
- Wire protocol: OpenAI-compatible `/chat/completions`

## Prerequisites

- Hermes Agent with model-provider plugin support installed and available on
  your `PATH` as `hermes`.
- Python 3.10+ for local development/tests in this repository.
- A ModelScope Access Token with access to ModelScope Inference API.

If `hermes --help` fails, install Hermes Agent first, then return to these
steps. This repository only contains the ModelScope provider plugin; it does
not install Hermes itself.

## Install

This is a copy-only Hermes plugin. `pip install .` is **not required** for
normal use.

### 1. Clone the repository

```bash
git clone https://github.com/modelscope/hermes-modelscope-api.git
cd hermes-modelscope-api
```

### 2. Copy the plugin into Hermes' plugin directory

```bash
mkdir -p ~/.hermes/plugins/model-providers
rm -rf ~/.hermes/plugins/model-providers/modelscope
cp -R plugins/model-providers/modelscope ~/.hermes/plugins/model-providers/modelscope
```

### 3. Configure your ModelScope API key

Get your Access Token at
[modelscope.cn/my/access/token](https://modelscope.cn/my/access/token),
then add it to `~/.hermes/.env`:

```bash
# Append to ~/.hermes/.env (create the file if it doesn't exist)
echo 'MODELSCOPE_API_KEY=your_access_token' >> ~/.hermes/.env
```

> **Tip**: You can also run `hermes setup` for an interactive prompt that
> writes the key into `~/.hermes/.env` for you.

Or export it in your shell:

```bash
export MODELSCOPE_API_KEY="your_access_token"
```

Optional: point Hermes at a non-production ModelScope-compatible endpoint:

```bash
export MODELSCOPE_BASE_URL="https://api-inference.modelscope.cn/v1"
```

### 4. (Desktop only) Configure via Hermes Desktop settings

If you use the Hermes desktop app, you can also set the API key from the UI:

1. Open **Hermes Desktop**
2. Go to **Settings** → **Provider** (or run `hermes setup`)
3. Find **ModelScope** in the provider list
4. Paste your Access Token into the `MODELSCOPE_API_KEY` field

The plugin auto-registers on the next Hermes session — no restart needed for
subsequent sessions.

## Verify installation without credentials

First confirm Hermes is installed:

```bash
hermes --help
```

Then confirm the plugin files landed in the directory Hermes scans:

```bash
test -f ~/.hermes/plugins/model-providers/modelscope/plugin.yaml
test -f ~/.hermes/plugins/model-providers/modelscope/__init__.py
```

The simplest runtime verification is to start `hermes chat` — ModelScope
will appear in the provider picker:

```bash
hermes chat
```

Then type `/model` in the chat to open the provider/model picker and look
for `modelscope` (alias: `ms`).

## Use

```bash
hermes chat --provider modelscope --model Qwen/Qwen3.5-397B-A17B
```

You can also use the alias:

```bash
hermes chat --provider ms --model deepseek-ai/DeepSeek-V4-Flash
```

Or set the provider permanently in `config.yaml`:

```yaml
model:
  provider: "modelscope"
  default: "Qwen/Qwen3.5-397B-A17B"
```

## Fallback model catalog

The plugin ships a static fallback catalog for offline picker behavior. When
Hermes can reach ModelScope with `MODELSCOPE_API_KEY`, it should prefer the
live `/v1/models` endpoint.

Key fallback models include:

- `Qwen/Qwen3-235B-A22B`
- `Qwen/Qwen3.5-27B`
- `Qwen/Qwen3.5-397B-A17B`
- `deepseek-ai/DeepSeek-V3.2`
- `deepseek-ai/DeepSeek-V4-Flash`
- `deepseek-ai/DeepSeek-V4-Pro`
- `deepseek-ai/DeepSeek-R1-0528`
- `ZhipuAI/GLM-5.1`
- `MiniMax/MiniMax-M2.7`
- `moonshotai/Kimi-K2.5`

## Troubleshooting

### `hermes: command not found`

Hermes Agent is not installed or is not on your `PATH`. Install Hermes first,
then re-run `hermes --help`.

### Provider is not found by Hermes

Re-copy the plugin from the repository root and make sure the final path is
exactly:

```
~/.hermes/plugins/model-providers/modelscope/plugin.yaml
~/.hermes/plugins/model-providers/modelscope/__init__.py
```

Avoid copying the parent `plugins/` directory into `~/.hermes`; Hermes expects
provider plugins under `~/.hermes/plugins/model-providers/<provider-id>`.

### `MODELSCOPE_API_KEY` is missing or unauthorized

Set a ModelScope Access Token before making a live chat-completions request:

```bash
export MODELSCOPE_API_KEY="your_access_token"
```

Create or rotate tokens at [modelscope.cn/my/access/token](https://modelscope.cn/my/access/token).

### Python version errors during development

This repository requires Python 3.10+ for local test environments. If your
system `python3` is older, use a newer interpreter for development:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip pytest pyyaml
python -m pytest -q
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip pytest pyyaml
python -m pytest -q
```

The tests include:

- Static manifest/provider shape checks.
- A runtime import smoke test using stubbed Hermes provider APIs, so provider
  registration is validated even when Hermes is not installed in the test
  environment.

## License

Apache License 2.0 — see [LICENSE](LICENSE).