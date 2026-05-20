#!/usr/bin/env python3
"""
SSH Client - VPS Integration Layer

Handles all remote execution on VPS without copy-paste.
Reads credentials from .env and executes commands directly.

Usage:
    from execution.sshClient import SSHClient
    client = SSHClient()
    result = client.run("docker ps")
    print(result.stdout)
"""

import os
import sys
import json
import logging
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# SSH CLIENT
# ============================================================================

class SSHClient:
    """
    Manages SSH connection to VPS.
    Reads config from .env automatically.
    """

    def __init__(self):
        self.host = os.getenv("VPS_HOST")
        self.port = int(os.getenv("VPS_PORT", 22))
        self.user = os.getenv("VPS_USER")
        self.sshKey = os.getenv("VPS_SSH_KEY")
        self.passphrase = os.getenv("VPS_SSH_PASSPHRASE") or None
        self._conn = None

        self._validate()

    def _validate(self):
        missing = [k for k, v in {
            "VPS_HOST": self.host,
            "VPS_USER": self.user,
            "VPS_SSH_KEY": self.sshKey,
        }.items() if not v]

        if missing:
            raise EnvironmentError(f"Missing .env vars: {missing}")

        if not os.path.exists(self.sshKey):
            raise FileNotFoundError(f"SSH key not found: {self.sshKey}")

    def _getConnection(self):
        """Return fabric Connection (lazy init)."""
        if self._conn is None:
            from fabric import Connection
            connect_kwargs = {"key_filename": self.sshKey}
            if self.passphrase:
                connect_kwargs["passphrase"] = self.passphrase

            self._conn = Connection(
                host=self.host,
                user=self.user,
                port=self.port,
                connect_kwargs=connect_kwargs
            )
        return self._conn

    def run(self, command: str, warn: bool = False) -> "fabric.runners.Result":
        """
        Execute command on VPS. Returns result with .stdout, .stderr, .return_code.

        Args:
            command: Shell command to run
            warn: If True, don't raise on non-zero exit

        Returns:
            fabric Result object
        """
        conn = self._getConnection()
        logger.debug(f"SSH [{self.host}]: {command}")
        result = conn.run(command, hide=True, warn=warn)
        return result

    def runJson(self, command: str) -> dict:
        """Run command and parse stdout as JSON."""
        result = self.run(command)
        return json.loads(result.stdout.strip())

    def put(self, localPath: str, remotePath: str):
        """Upload file to VPS."""
        conn = self._getConnection()
        conn.put(localPath, remotePath)
        logger.info(f"Uploaded {localPath} → {self.host}:{remotePath}")

    def get(self, remotePath: str, localPath: str):
        """Download file from VPS."""
        conn = self._getConnection()
        conn.get(remotePath, localPath)
        logger.info(f"Downloaded {self.host}:{remotePath} → {localPath}")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ============================================================================
# DOCKER / PORTAINER HELPERS
# ============================================================================

class DockerClient:
    """Run Docker commands on VPS via SSH."""

    def __init__(self, ssh: SSHClient = None):
        self.ssh = ssh or SSHClient()

    def listContainers(self, all_containers: bool = False) -> list:
        """List running (or all) containers."""
        flag = "-a" if all_containers else ""
        result = self.ssh.run(f"docker ps {flag} --format json")
        containers = []
        for line in result.stdout.strip().splitlines():
            if line.strip():
                containers.append(json.loads(line))
        return containers

    def listServices(self) -> list:
        """List Docker Swarm services."""
        result = self.ssh.run("docker service ls --format json")
        services = []
        for line in result.stdout.strip().splitlines():
            if line.strip():
                services.append(json.loads(line))
        return services

    def getServiceLogs(self, serviceName: str, lines: int = 50) -> str:
        """Fetch logs from a Docker Swarm service."""
        result = self.ssh.run(f"docker service logs --tail {lines} {serviceName}")
        return result.stdout

    def stackDeploy(self, stackName: str, composeFile: str) -> str:
        """Deploy or update a Docker stack."""
        import shlex
        result = self.ssh.run(
            f"docker stack deploy -c {shlex.quote(composeFile)} {shlex.quote(stackName)} --with-registry-auth"
        )
        return result.stdout

    def execInContainer(self, containerName: str, command: str) -> str:
        """Execute command inside a running container."""
        import shlex
        result = self.ssh.run(f"docker exec {shlex.quote(containerName)} {command}")
        return result.stdout


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="SSH Client CLI")
    parser.add_argument("command", nargs="?", default="echo OK", help="Command to run on VPS")
    parser.add_argument("--json", action="store_true", help="Parse output as JSON")
    args = parser.parse_args()

    with SSHClient() as client:
        if args.json:
            result = client.runJson(args.command)
            print(json.dumps(result, indent=2))
        else:
            result = client.run(args.command)
            print(result.stdout, end="")
