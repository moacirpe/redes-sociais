#!/bin/bash
# Coleta diária de métricas — todos os clientes configurados
# Executado via crontab. Logs em .tmp/logs/

PROJECT_DIR="/Users/moacirpereira/Library/CloudStorage/GoogleDrive-moacirper@gmail.com/Meu Drive/Claude Code/REDES SOCIAIS"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/.tmp/logs"
LOG_FILE="$LOG_DIR/collect_$(date +%Y-%m-%d).log"

mkdir -p "$LOG_DIR"

if [ ! -f "$PYTHON" ]; then
    echo "ERRO: virtualenv não encontrado em $PYTHON" >&2
    exit 1
fi

ts() { date '+%Y-%m-%d %H:%M:%S'; }

echo "=== $(ts) — Coleta iniciada ===" >> "$LOG_FILE"

cd "$PROJECT_DIR"

echo "--- $(ts) moacir ---" >> "$LOG_FILE"
PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/fetchInstagramData.py --client moacir --period 7 --save >> "$LOG_FILE" 2>&1
echo "moacir: exit $?" >> "$LOG_FILE"

echo "--- $(ts) moper ---" >> "$LOG_FILE"
PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/fetchInstagramData.py --client moper --period 7 --save >> "$LOG_FILE" 2>&1
echo "moper: exit $?" >> "$LOG_FILE"

echo "--- $(ts) laika ---" >> "$LOG_FILE"
PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/fetchInstagramData.py --client laika --period 7 --save >> "$LOG_FILE" 2>&1
echo "laika: exit $?" >> "$LOG_FILE"

echo "--- $(ts) publish ---" >> "$LOG_FILE"
PYTHONPATH="$PROJECT_DIR" "$PYTHON" execution/publishScheduled.py >> "$LOG_FILE" 2>&1
echo "publish: exit $?" >> "$LOG_FILE"

echo "=== $(ts) — Coleta concluída ===" >> "$LOG_FILE"
