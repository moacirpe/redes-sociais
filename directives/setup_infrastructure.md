# Directive: Setup Infrastructure

## Goal
Configure and verify all infrastructure connections: VPS (SSH), PostgreSQL, and Docker Swarm. Create initial database schema.

## Inputs
- `.env` file filled with VPS, PostgreSQL, and API credentials

## Process

### Step 1: Verify Environment Variables
Check that `.env` is properly filled:
```bash
python execution/testConnections.py
```
Expected output: all sections show ✅ or ⏭️ (skipped = not configured yet, OK).

### Step 2: Test SSH Connection
```bash
python execution/sshClient.py "echo OK && hostname"
```
Expected: VPS hostname returned, no errors.

### Step 3: Test PostgreSQL Connection
```bash
python execution/dbClient.py --query "SELECT version()"
```
Expected: PostgreSQL version string returned.

### Step 4: Run Database Setup
```bash
python execution/setupDatabase.py
```
Expected: All tables created, `status: ok` in output.

### Step 5: Verify Swarm Services
```bash
python execution/sshClient.py "docker service ls"
```
Expected: List of running Swarm services.

## Outputs
- PostgreSQL schema created with tables:
  - `social_accounts` — linked social media accounts
  - `posts` — content drafts, scheduled, and published
  - `metrics` — analytics data per account per day
  - `scheduled_jobs` — automation queue
  - `execution_logs` — script run history

## Edge Cases

### SSH key not found
**Error**: `FileNotFoundError: SSH key not found`
**Fix**: Set `VPS_SSH_KEY` in `.env` to the correct absolute path (e.g., `/Users/moacirpereira/.ssh/id_rsa`)

### SSH connection refused
**Error**: `NoValidConnectionsError`
**Fix**:
1. Verify `VPS_HOST` is correct
2. Check VPS firewall allows SSH on `VPS_PORT`
3. Verify user exists on VPS: `VPS_USER=ubuntu` (or appropriate)

### PostgreSQL auth failure
**Error**: `FATAL: password authentication failed`
**Fix**: Check `POSTGRES_USER` and `POSTGRES_PASSWORD` in `.env`

### SSH tunnel fails
**Error**: `sshtunnel.BaseSSHTunnelForwarderError`
**Fix**:
1. SSH connection must work first (test Step 2)
2. Verify `POSTGRES_HOST` is `localhost` if DB is on same VPS
3. Verify `POSTGRES_PORT` is correct (default: 5432)

### Table already exists
Not an error — `setupDatabase.py` uses `IF NOT EXISTS` throughout.

## Tools Used
- `execution/testConnections.py` — Full environment check
- `execution/sshClient.py` — SSH + Docker CLI
- `execution/dbClient.py` — PostgreSQL via SSH tunnel
- `execution/setupDatabase.py` — Schema migration

## Success Criteria
- ✅ `testConnections.py` shows no ❌ items
- ✅ `setupDatabase.py` returns `status: ok`
- ✅ All 5 tables present in PostgreSQL
- ✅ Docker services are listed (Portainer, Swarm)

---
**Last Updated**: 2026-04-06
**Status**: Ready — awaiting .env credentials
