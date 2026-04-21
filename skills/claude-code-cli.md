---
name: claude-code-cli
description: "Referencia rápida para usar el CLI de Claude Code: instalación, comandos, flags, autenticación y refresh token."
---

# Claude Code CLI — Guía de uso

## Instalación

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# macOS con Homebrew
brew install --cask claude-code

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# Actualizar
claude update
```

---

## Modos de ejecución

| Modo | Comando | Cuándo usarlo |
|---|---|---|
| Interactivo | `claude` | Trabajo manual, conversación |
| Con prompt inicial | `claude "tarea"` | Empezar directo con una tarea |
| No-interactivo (SDK) | `claude -p "query"` | Scripts, pipes, CI |
| Continuar sesión | `claude -c` | Retomar la última conversación |
| Retomar sesión nombrada | `claude -r "nombre"` | Volver a una sesión específica |

---

## Flags más usados

### Sesión
```
--name / -n "nombre"     → nombrar la sesión
--continue / -c          → retomar la última sesión
--resume / -r "id"       → retomar sesión por ID o nombre
--no-session-persistence → no guardar la sesión
```

### Modelo y esfuerzo
```
--model claude-sonnet-4-6        → especificar modelo
--effort [low|medium|high|max]   → nivel de esfuerzo
```

### Permisos
```
--permission-mode auto           → aprobar todo automáticamente
--permission-mode plan           → solo planificar, no ejecutar
--dangerously-skip-permissions   → saltear todos los prompts
```

### Output (solo modo -p)
```
--output-format [text|json|stream-json]
--max-turns N        → limitar turnos agénticos
--max-budget-usd 5   → límite de gasto en USD
```

### Herramientas y contexto
```
--tools "Bash,Edit,Read"   → restringir herramientas disponibles
--add-dir ../otro-repo     → agregar directorio de trabajo extra
--mcp-config ./mcp.json    → cargar servidores MCP desde archivo
--system-prompt "texto"    → reemplazar system prompt
--append-system-prompt ""  → agregar texto al system prompt
```

### Modo remoto / web
```
--remote "tarea"    → crear sesión web en claude.ai
--teleport          → traer sesión web al terminal local
```

---

## Autenticación

### Orden de precedencia (de mayor a menor)
1. Cloud providers: `CLAUDE_CODE_USE_BEDROCK` / `CLAUDE_CODE_USE_VERTEX`
2. `ANTHROPIC_AUTH_TOKEN` — para proxies/gateways
3. `ANTHROPIC_API_KEY` — API key de Anthropic Console
4. `apiKeyHelper` — script para credenciales dinámicas (vaults)
5. `CLAUDE_CODE_OAUTH_TOKEN` — token OAuth de larga duración
6. Login OAuth por suscripción (Pro/Max/Team) — default

### Flujo estándar (usuario individual)
```bash
claude          # pide login por browser la primera vez
                # guarda credenciales automáticamente en:
                # macOS → Keychain
                # Linux → ~/.claude/.credentials.json (modo 0600)
```

### Para CI/scripts (token de 1 año)
```bash
claude setup-token             # genera token OAuth de larga duración
export CLAUDE_CODE_OAUTH_TOKEN=tu-token
claude -p "tarea automatizada"
```

### Con API key directa
```bash
export ANTHROPIC_API_KEY=sk-ant-...
claude -p "fix this"
```

### Con credenciales dinámicas (vault, rotación automática)
```json
// .claude/settings.json
{
  "apiKeyHelper": "/ruta/al/script-que-devuelve-key.sh"
}
```
El script se ejecuta cada 5 minutos o ante HTTP 401.
Personalizable con: `CLAUDE_CODE_API_KEY_HELPER_TTL_MS=300000`

---

## Refresh token

- El refresh es **completamente automático** — Claude Code lo maneja solo.
- Antes de cada request verifica si el access token expiró; si sí, usa el refresh token guardado para obtener uno nuevo sin intervención del usuario.
- **No hay flag `--refresh-token`** — no se necesita.
- Para forzar re-autenticación: `/logout` en sesión interactiva, luego `/login`.

### Ver estado de autenticación
```bash
claude auth status          # JSON
claude auth status --text   # legible para humanos
```

---

## Slash commands útiles en sesión interactiva

| Comando | Acción |
|---|---|
| `/help` | Ver ayuda |
| `/login` | Iniciar sesión |
| `/logout` | Cerrar sesión |
| `/model` | Ver o cambiar modelo |
| `/fast` | Activar modo rápido (Opus 4.6) |
| `/clear` | Limpiar contexto de conversación |
| `/compact` | Compactar contexto largo |
| `/cost` | Ver costo de la sesión |
| `/status` | Ver estado de la sesión |

---

## Ejemplos prácticos

```bash
# Scraping no-interactivo con límite de costo
claude -p "scrapear snacks de DIA" --max-budget-usd 0.50

# Pipe de archivo a Claude
cat error.log | claude -p "identificá el error principal"

# Sesión nombrada para retomar después
claude --name "analisis-precios" "analizá los JSONs en resultados/"

# Retomar esa sesión
claude -r "analisis-precios"

# Usar modelo específico sin interacción
claude -p "resumí este archivo" --model claude-haiku-4-5 --output-format json
```

---

## Docs oficiales
- CLI reference: https://code.claude.com/docs/en/cli-reference
- Autenticación: https://code.claude.com/docs/en/authentication
