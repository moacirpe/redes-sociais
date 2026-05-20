#!/usr/bin/env python3
"""
Backup Manual de Métricas — @moacir.moper

Sistema de backup para quando as APIs falham.
Permite entrada manual de dados via planilha ou formulário.
"""

import os
import json
import csv
from datetime import datetime
from typing import Dict, List

from utils import setupLogging, getTimestamp, ensureTmpDir

logger = setupLogging()

class ManualBackup:
    """Sistema de backup manual de métricas."""

    def __init__(self, client: str = "moacir"):
        self.client = client
        self.backup_dir = ensureTmpDir("manual_backup")
        self.data_file = os.path.join(self.backup_dir, f"{client}_manual_data.json")

    def loadExistingData(self) -> Dict:
        """Carrega dados manuais existentes."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'entries': [], 'last_updated': None}

    def saveData(self, data: Dict) -> None:
        """Salva dados manuais."""
        data['last_updated'] = getTimestamp()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Dados manuais salvos em {self.data_file}")

    def addManualEntry(self, platform: str, metric_type: str, value: float,
                       date: str = None, notes: str = "") -> None:
        """Adiciona entrada manual de métrica."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        data = self.loadExistingData()

        entry = {
            'id': len(data['entries']) + 1,
            'date': date,
            'platform': platform,
            'metric_type': metric_type,
            'value': value,
            'notes': notes,
            'timestamp': getTimestamp(),
            'source': 'manual'
        }

        data['entries'].append(entry)
        self.saveData(data)

        print(f"✅ Entrada adicionada: {platform} - {metric_type} = {value}")

    def getLatestMetrics(self) -> Dict:
        """Retorna últimas métricas por plataforma."""
        data = self.loadExistingData()
        latest = {}

        for entry in data['entries']:
            platform = entry['platform']
            metric_type = entry['metric_type']

            key = f"{platform}_{metric_type}"
            if key not in latest or entry['date'] > latest[key]['date']:
                latest[key] = entry

        # Organizar por plataforma
        platforms = {}
        for key, entry in latest.items():
            platform = entry['platform']
            if platform not in platforms:
                platforms[platform] = {}
            platforms[platform][entry['metric_type']] = entry['value']

        return platforms

    def exportToCSV(self, filename: str = None) -> str:
        """Exporta dados para CSV."""
        if filename is None:
            filename = f"{self.client}_manual_backup_{datetime.now().strftime('%Y%m%d')}.csv"

        filepath = os.path.join(self.backup_dir, filename)
        data = self.loadExistingData()

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'platform', 'metric_type', 'value', 'notes', 'timestamp', 'source']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for entry in data['entries']:
                writer.writerow(entry)

        logger.info(f"Dados exportados para {filepath}")
        return filepath

    def generateReport(self) -> Dict:
        """Gera relatório baseado em dados manuais."""
        latest = self.getLatestMetrics()

        # Calcular totais
        total_followers = 0
        platforms_data = {}

        for platform, metrics in latest.items():
            if 'followers' in metrics or 'subscribers' in metrics:
                follower_key = 'followers' if 'followers' in metrics else 'subscribers'
                total_followers += metrics[follower_key]

            platforms_data[platform] = metrics

        raw = self.loadExistingData()
        return {
            'client': self.client,
            'total_followers': total_followers,
            'platforms': platforms_data,
            'last_updated': raw.get('last_updated'),
            'entries_count': len(raw['entries']),
            'source': 'manual_backup'
        }

    def showMenu(self) -> None:
        """Exibe menu interativo."""
        print(f"\n📊 BACKUP MANUAL — {self.client.upper()}")
        print("=" * 50)

        while True:
            print("\nOpções:")
            print("1. Adicionar métrica manual")
            print("2. Ver últimas métricas")
            print("3. Ver histórico completo")
            print("4. Exportar para CSV")
            print("5. Gerar relatório")
            print("6. Sair")

            try:
                choice = input("\nEscolha uma opção (1-6): ").strip()

                if choice == '1':
                    self.addMetricInteractive()
                elif choice == '2':
                    self.showLatestMetrics()
                elif choice == '3':
                    self.showHistory()
                elif choice == '4':
                    self.exportInteractive()
                elif choice == '5':
                    self.showReport()
                elif choice == '6':
                    print("👋 Até logo!")
                    break
                else:
                    print("❌ Opção inválida. Tente novamente.")

            except KeyboardInterrupt:
                print("\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")

    def addMetricInteractive(self) -> None:
        """Adiciona métrica via interface interativa."""
        print("\n📝 Adicionar Métrica Manual")

        platforms = ['instagram', 'tiktok', 'youtube']
        metrics = {
            'instagram': ['followers', 'engagement_rate', 'posts_today', 'comments_unanswered'],
            'tiktok': ['followers', 'engagement_rate', 'videos_today', 'duets_pending'],
            'youtube': ['subscribers', 'ctr', 'videos_today', 'comments_unanswered']
        }

        # Selecionar plataforma
        print("Plataformas disponíveis:")
        for i, p in enumerate(platforms, 1):
            print(f"{i}. {p.capitalize()}")
        plat_choice = int(input("Escolha plataforma (1-3): ")) - 1
        platform = platforms[plat_choice]

        # Selecionar métrica
        print(f"\nMétricas para {platform}:")
        plat_metrics = metrics[platform]
        for i, m in enumerate(plat_metrics, 1):
            print(f"{i}. {m}")
        metric_choice = int(input(f"Escolha métrica (1-{len(plat_metrics)}): ")) - 1
        metric_type = plat_metrics[metric_choice]

        # Valor
        value = float(input(f"Valor para {metric_type}: "))

        # Data (opcional)
        date_input = input("Data (YYYY-MM-DD) ou Enter para hoje: ").strip()
        date = date_input if date_input else None

        # Notas
        notes = input("Notas (opcional): ").strip()

        self.addManualEntry(platform, metric_type, value, date, notes)

    def showLatestMetrics(self) -> None:
        """Exibe últimas métricas."""
        latest = self.getLatestMetrics()

        if not latest:
            print("📊 Nenhuma métrica registrada ainda.")
            return

        print("\n📊 ÚLTIMAS MÉTRICAS POR PLATAFORMA")
        print("-" * 40)

        for platform, metrics in latest.items():
            print(f"\n🔹 {platform.upper()}")
            for metric, value in metrics.items():
                print(f"  {metric}: {value}")

    def showHistory(self) -> None:
        """Exibe histórico completo."""
        data = self.loadExistingData()

        if not data['entries']:
            print("📊 Nenhum histórico encontrado.")
            return

        print(f"\n📊 HISTÓRICO COMPLETO ({len(data['entries'])} entradas)")
        print("-" * 60)
        print(f"{'ID':<5} {'Data':<12} {'Plataforma':<12} {'Métrica':<15} {'Valor':<10} {'Notas'}")
        print("-" * 60)

        for entry in data['entries'][-10:]:  # Últimas 10
            print(f"{entry['id']:<5} {entry['date']:<12} {entry['platform']:<12} {entry['metric_type']:<15} {entry['value']:<10} {entry['notes']}")

    def exportInteractive(self) -> None:
        """Exporta dados via interface."""
        filename = input("Nome do arquivo CSV (ou Enter para automático): ").strip()
        if not filename:
            filename = None

        filepath = self.exportToCSV(filename)
        print(f"✅ Dados exportados para: {filepath}")

    def showReport(self) -> None:
        """Exibe relatório consolidado."""
        report = self.generateReport()

        print(f"\n📊 RELATÓRIO CONSOLIDADO — {report['client'].upper()}")
        print("=" * 50)
        print(f"👥 Total de seguidores: {report['total_followers']:,}")
        print(f"📅 Última atualização: {report['last_updated'] or 'Nunca'}")
        print(f"📝 Total de entradas: {report['entries_count']}")
        print(f"🔍 Fonte: {report['source']}")

        print(f"\n📱 Por Plataforma:")
        for platform, metrics in report['platforms'].items():
            print(f"\n🔹 {platform.upper()}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value}")

def main():
    """Executa backup manual."""
    backup = ManualBackup()

    if len(sys.argv) > 1:
        # Modo comando
        command = sys.argv[1]

        if command == 'add':
            if len(sys.argv) < 5:
                print("Uso: python manualBackup.py add <platform> <metric_type> <value> [date] [notes]")
                sys.exit(1)

            platform = sys.argv[2]
            metric_type = sys.argv[3]
            value = float(sys.argv[4])
            date = sys.argv[5] if len(sys.argv) > 5 else None
            notes = sys.argv[6] if len(sys.argv) > 6 else ""

            backup.addManualEntry(platform, metric_type, value, date, notes)

        elif command == 'report':
            report = backup.generateReport()
            print(json.dumps(report, indent=2, default=str))

        elif command == 'export':
            filename = sys.argv[2] if len(sys.argv) > 2 else None
            filepath = backup.exportToCSV(filename)
            print(f"Exportado: {filepath}")

        else:
            print("Comandos: add, report, export")
            sys.exit(1)
    else:
        # Modo interativo
        backup.showMenu()

if __name__ == "__main__":
    main()