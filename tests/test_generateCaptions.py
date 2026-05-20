import csv
import json
import os
import pytest
from unittest.mock import MagicMock


# --- parseCaptionsResponse ---

def test_parseCaptionsResponse_plain_json():
    from execution.generateCaptions import parseCaptionsResponse
    raw = '[{"caption": "Teste!", "hashtags": "#teste"}]'
    result = parseCaptionsResponse(raw)
    assert len(result) == 1
    assert result[0]["caption"] == "Teste!"


def test_parseCaptionsResponse_markdown_block():
    from execution.generateCaptions import parseCaptionsResponse
    raw = '```json\n[{"caption": "Teste!", "hashtags": "#teste"}]\n```'
    result = parseCaptionsResponse(raw)
    assert result[0]["caption"] == "Teste!"


def test_parseCaptionsResponse_invalid_raises():
    from execution.generateCaptions import parseCaptionsResponse
    with pytest.raises(ValueError):
        parseCaptionsResponse("não é json nenhum")


# --- nextRowId ---

def test_nextRowId_no_file_returns_001(tmp_path):
    from execution.generateCaptions import nextRowId
    path = str(tmp_path / "queue.csv")
    assert nextRowId(path, "moacir") == "moacir-001"


def test_nextRowId_existing_rows_increments(tmp_path):
    from execution.generateCaptions import nextRowId, CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow({col: "" for col in CSV_COLUMNS})
        writer.writerow({col: "" for col in CSV_COLUMNS})
    assert nextRowId(path, "moacir") == "moacir-003"


# --- appendToQueue ---

def test_appendToQueue_creates_file_with_header(tmp_path):
    from execution.generateCaptions import appendToQueue, CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    row = {col: "" for col in CSV_COLUMNS}
    row.update({"id": "moacir-001", "client": "moacir", "platform": "instagram",
                "caption": "Olá!", "status": "draft"})
    appendToQueue(path, [row])
    with open(path) as f:
        lines = f.readlines()
    assert "id" in lines[0]
    assert "moacir-001" in lines[1]


def test_appendToQueue_appends_to_existing(tmp_path):
    from execution.generateCaptions import appendToQueue, CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    row = {col: "x" for col in CSV_COLUMNS}
    row["id"] = "moacir-001"
    appendToQueue(path, [row])
    row2 = {col: "y" for col in CSV_COLUMNS}
    row2["id"] = "moacir-002"
    appendToQueue(path, [row2])
    with open(path) as f:
        lines = f.readlines()
    assert len(lines) == 3  # header + 2 rows


# --- buildPrompt ---

def test_buildPrompt_contains_briefing():
    from execution.generateCaptions import buildPrompt
    result = buildPrompt("Tom: alegre", [], 3)
    assert "Tom: alegre" in result
    assert "3" in result


def test_buildPrompt_includes_theme_when_given():
    from execution.generateCaptions import buildPrompt
    result = buildPrompt("Tom: alegre", [], 2, theme="promoção de maio")
    assert "promoção de maio" in result


def test_buildPrompt_no_theme_when_empty():
    from execution.generateCaptions import buildPrompt
    result = buildPrompt("Tom: alegre", [], 2, theme="")
    assert "TEMA DESTA SEMANA" not in result
