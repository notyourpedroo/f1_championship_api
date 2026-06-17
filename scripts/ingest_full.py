#!/usr/bin/env python3
"""
Script de Ingestão Completa - F1 Championship API.

Executa o pipeline completo de ingestão para dados das temporadas 2025 e 2026.
Refatorado para usar serviços centralizados (scripts/services/ingestion.py) 
e eliminar duplicações de código.

Este script:
1. Configura logging básico
2. Carrega mapeamento de nomes de pilotos para normalização
3. Limpa e recria o schema do banco de dados
4. Executa ingestão sequencial para 2025 e 2026
5. Trata erros adequadamente com logging

Usage:
    python scripts/ingest_full.py
    
    # Executar como módulo (não recomendado)
    # python -m scripts.ingest_full

Logging Configuration:
    Level: INFO
    Format: %(asctime)s - %(levelname)s - %(message)s
"""

from scripts.services.ingestion import (
    ingest_2025,
    ingest_2026
)
from database import engine
from sqlalchemy import text
import logging
import os

# Configura logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from scripts.services.ingestion import (
    ingest_2025,
    ingest_2026
)
from database import engine
from sqlalchemy import text
import logging
import os

# Configura logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def setup_database():
    """
    Configura o banco de dados (limpa e recria schema).
    
    Remove todas as tabelas existentes e cria novo schema com estrutura
    inicial vazia pronta para ingestão. Este método deve ser chamado antes
    da primeira ingestão ou após reset do banco de dados.
    
    Cria as seguintes tabelas:
    - teams: Equipes da F1 (team_id, team_name)
    - drivers: Pilotos da F1 (driver_id, driver_name)
    - races: Corridas (race_id, race_name, race_date, race_location, is_sprint, year)
    - results: Resultados das corridas com relacionamentos FK para teams/drivers
    - scores: Sistema de pontuação por posição
    
    Args:
        engine: Instância SQLAlchemy Engine configurada
        
    Returns:
        None
        
    Raises:
        Exception: Se ocorrer erro durante criação do schema
        
    Example:
        >>> from scripts.ingest_full import setup_database
        >>> setup_database()  # Reset database to initial state
    """
    with engine.connect() as conn:
        for table in ['results', 'drivers', 'teams', 'races', 'scores']:
            conn.execute(text(f'DROP TABLE IF EXISTS {table}'))
        
        conn.execute(text('CREATE TABLE teams (team_id INTEGER PRIMARY KEY AUTOINCREMENT, team_name TEXT UNIQUE)'))
        conn.execute(text('CREATE TABLE drivers (driver_id INTEGER PRIMARY KEY AUTOINCREMENT, driver_name TEXT UNIQUE)'))
        conn.execute(text('CREATE TABLE races (race_id INTEGER PRIMARY KEY AUTOINCREMENT, race_name TEXT, race_date TEXT, race_location TEXT, is_sprint TEXT, year INTEGER)'))
        conn.execute(text('CREATE TABLE results (result_id INTEGER PRIMARY KEY AUTOINCREMENT, race_id INTEGER, driver_id INTEGER, team_id INTEGER, driver_start_position INTEGER, driver_final_position INTEGER, grid_result INTEGER, driver_fastest_lap TEXT, points INTEGER, year INTEGER, FOREIGN KEY (race_id) REFERENCES races (race_id), FOREIGN KEY (driver_id) REFERENCES drivers (driver_id), FOREIGN KEY (team_id) REFERENCES teams (team_id))'))
        conn.execute(text('CREATE TABLE scores (score_id INTEGER PRIMARY KEY AUTOINCREMENT, position INTEGER, points INTEGER, is_sprint TEXT)'))
        
        conn.commit()


def main():
    """
    Executa o pipeline completo de ingestão.
    
    Orquestra todo o processo de carregamento de dados para as temporadas 2025 e 2026:
    1. Imprime cabeçalho informatizado
    2. Carrega mapeamento de nomes de pilotos
    3. Configura/banca de dados (reset)
    4. Executa ingestão sequencial para 2025 e 2026
    5. Exibe mensagem de conclusão ou erro
    
    Args:
        None
        
    Returns:
        None
        
    Raises:
        Exception: Se ocorrer erro durante qualquer etapa do pipeline (carregamento,
                   setup ou ingestão). A exceção inclui mensagem de erro detalhada
                   e é re-raizada para permitir tratamento no nível superior.
        
    Example:
        >>> from scripts.ingest_full import main
        >>> main()  # Run full ingestion pipeline
        # Expected output:
        # ============================================================
        # F1 Championship API - Pipeline de Ingestão
        # ============================================================
        # [1/2] Processando dados de 2025...
        # ...
        # ✓ Ingestão concluída com sucesso!
    """
    print('=' * 60)
    print('F1 Championship API - Pipeline de Ingestão')
    print('=' * 60)
    
    try:
        # Carrega mapeamento de nomes
        name_map = load_name_mappings()
        
        # Setup do banco (limpa e recria schema)
        setup_database()
        
        # Executa ingestão para 2025
        print('\n[1/2] Processando dados de 2025...')
        print('-' * 40)
        ingest_2025(name_map)
        
        # Executa ingestão para 2026
        print('\n[2/2] Processando dados de 2026...')
        print('-' * 40)
        ingest_2026(name_map)
        
        print('\n' + '=' * 60)
        print('✓ Ingestão concluída com sucesso!')
        print('=' * 60)
        
    except Exception as e:
        logging.error(f'Pipeline de ingestão falhou: {str(e)}')
        raise


def load_name_mappings() -> dict:
    """
    Carrega mapeamento de nomes de pilotos.
    
    Lê o arquivo CSV contendo alterações de nomes de pilotos e retorna
    um dicionário com chave = nome antigo, valor = nome novo. Utilizado
    para normalizar nomes ao longo do tempo quando pilotos mudam seus nomes
    oficialmente.
    
    Args:
        mapping_file (str): Caminho relativo para o arquivo CSV de mapeamento
        
    Returns:
        dict: Dicionário {nome_antigo: nome_novo}. Retorna dict vazio se arquivo não existir ou estiver incorreto.
        
    Raises:
        Exception: Se ocorrer erro durante leitura do arquivo
        
    Example:
        >>> name_map = load_name_mappings()
        >>> old_name, new_name = "Max", "Maximilian"
        >>> name_map[old_name]  # e.g., 'Max' -> 'Maximilian'
        'Maximilian'
    """
    mapping_file = 'files/raw/name_changes/driver_names.csv'
    name_map = {}
    
    if not os.path.exists(mapping_file):
        print(f'⚠ Mapeamento de nomes não encontrado em {mapping_file}')
        return name_map
    
    with open(mapping_file, mode='r', encoding='utf-8') as f:
        # Skip header
        next(f)
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 2:
                old_name, new_name = parts
                name_map[old_name] = new_name
    
    return name_map


if __name__ == '__main__':
    main()
