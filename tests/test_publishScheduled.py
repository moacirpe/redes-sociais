import csv
import os
import pytest
from datetime import datetime, timedelta


# --- detectMediaType ---

def test_detectMediaType_mp4_returns_reels():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("video.mp4") == "REELS"


def test_detectMediaType_mov_returns_reels():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("clip.MOV") == "REELS"


def test_detectMediaType_jpg_returns_image():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("foto.jpg") == "IMAGE"


def test_detectMediaType_png_returns_image():
    from execution.publishScheduled import detectMediaType
    assert detectMediaType("banner.PNG") == "IMAGE"


# --- isDue ---

def test_isDue_approved_past_time_returns_true():
    from execution.publishScheduled import isDue
    past = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    assert isDue({"status": "approved", "scheduled_at": past}) is True


def test_isDue_approved_future_time_returns_false():
    from execution.publishScheduled import isDue
    future = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
    assert isDue({"status": "approved", "scheduled_at": future}) is False


def test_isDue_draft_returns_false():
    from execution.publishScheduled import isDue
    past = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    assert isDue({"status": "draft", "scheduled_at": past}) is False


def test_isDue_empty_scheduled_at_returns_false():
    from execution.publishScheduled import isDue
    assert isDue({"status": "approved", "scheduled_at": ""}) is False


# --- readQueue / writeQueue ---

def test_readQueue_returns_empty_for_missing_file(tmp_path):
    from execution.publishScheduled import readQueue
    assert readQueue(str(tmp_path / "missing.csv")) == []


def test_readQueue_returns_rows(tmp_path):
    from execution.publishScheduled import readQueue
    from execution.generateCaptions import CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerow({col: "x" if col == "id" else "" for col in CSV_COLUMNS})
    rows = readQueue(path)
    assert len(rows) == 1
    assert rows[0]["id"] == "x"


def test_writeQueue_overwrites_file(tmp_path):
    from execution.publishScheduled import writeQueue
    from execution.generateCaptions import CSV_COLUMNS
    path = str(tmp_path / "queue.csv")
    rows = [{col: "v" for col in CSV_COLUMNS}]
    writeQueue(path, rows)
    with open(path) as f:
        content = f.read()
    assert "id" in content
    assert "v" in content
