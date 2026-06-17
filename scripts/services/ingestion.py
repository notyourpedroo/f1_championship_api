"""
Serviços de Ingestão de Dados F1 Championship.

Este módulo contém as funções refinadas para ingestão de dados da Fórmula 1,
implementando o padrão "get or create" para entidades (teams, drivers) e
gerenciando pipelines específicos para cada temporada (2025, 2026).

A estrutura separa a lógica por:
- Entidade: Teams, Drivers, Races, Results, Scores
- Formato de arquivo: CSV tradicional (2025) vs Custom format (2026)
- Ano: Diferentes esquemas de arquivos para cada temporada

Arquivos dependentes:
    - database.py: Configuração SQLAlchemy engine e SessionLocal
    - scripts/models.py: Pydantic models e Database enums
    
Usage:
    from scripts.services.ingestion import ingest_2025, get_or_create_entity
    
    # Ingestar dados 2025
    name_map = {...}
    ingest_2025(name_map)
    
    # Usar função de get or create diretamente
    with engine.connect() as conn:
        team_id = get_or_create_entity(conn, 'teams', 'team_name', 'Red Bull')
"""

from typing import Dict, List, Any
from database import engine, SessionLocal
from sqlalchemy import text
import pandas as pd
import os
import io

from typing import Dict, List, Any
from database import engine, SessionLocal
from sqlalchemy import text
import pandas as pd
import os
import io


def ingest_2025(name_map: Dict[str, str]) -> None:
    """
    Executa o pipeline completo de ingestão para dados de 2025.
    
    Lê arquivos CSV tradicionais (formato padrão) das pastas /files/raw/2025:
    - teams.csv: Equipes com team_id e team_name
    - drivers.csv: Pilotos com driver_id e driver_name  
    - races.csv: Corridas com metadados
    - scores.csv: Sistema de pontuação por posição
    - results.csv: Resultados detalhados das corridas
    
    Para cada entidade, implementa "get or create" padrão para evitar duplicatas.
    
    Args:
        name_map: Dicionário {nome_antigo: nome_novo} para normalização de pilotos
        
    Raises:
        Exception: Se ocorrer erro durante leitura de arquivos ou execução de queries
        
    Example:
        >>> from scripts.services.ingestion import ingest_2025
        >>> # Carregar mapeamento de nomes primeiro
        >>> name_map = load_name_mappings()
        >>> ingest_2025(name_map)
    """
    raw_dir = 'files/raw/2025'
    year = 2025
    
    print('Ingesting 2025 data...')
    
    try:
        with engine.connect() as conn:
            # Carrega todos os arquivos CSV
            teams_csv = pd.read_csv(os.path.join(raw_dir, 'teams.csv'))
            drivers_csv = pd.read_csv(os.path.join(raw_dir, 'drivers.csv'))
            races_csv = pd.read_csv(os.path.join(raw_dir, 'races.csv'))
            scores_csv = pd.read_csv(os.path.join(raw_dir, 'scores.csv'))
            results_csv = pd.read_csv(os.path.join(raw_dir, 'results.csv'))
            
            # 1. Ingest Teams
            print('  → Ingesting teams...')
            for _, row in teams_csv.iterrows():
                get_or_create_entity(conn, 'teams', 'team_name', row['team_name'])
            
            # 2. Ingest Drivers
            print('  → Ingesting drivers...')
            for _, row in drivers_csv.iterrows():
                driver_name = str(row['driver_name']) if pd.notna(row['driver_name']) else None
                if not driver_name:
                    continue
                norm_name = normalize_name(driver_name, name_map)
                get_or_create_entity(conn, 'drivers', 'driver_name', norm_name)
            
            # 3. Ingest Races - cria mapeamento para lookup posterior
            print('  → Ingesting races...')
            race_map = {}
            for _, row in races_csv.iterrows():
                res = conn.execute(
                    text("INSERT INTO races (race_name, race_date, race_location, is_sprint, year) "
                         "VALUES (:race_name, :race_date, :race_location, :is_sprint, :year)"),
                    {
                        'race_name': row['race_name'],
                        'race_date': row['race_date'],
                        'race_location': row['race_location'],
                        'is_sprint': str(row['is_sprint']).upper(),
                        'year': year
                    }
                )
                race_map[row['race_id']] = res.lastrowid
            
              # 4. Ingest Scores
            print('  → Ingesting scores...')
            for _, row in scores_csv.iterrows():
                conn.execute(
                    text("INSERT INTO scores (position, points, is_sprint) "
                         "VALUES (:position, :points, :is_sprint)"),
                    {
                        'position': row['position'],
                        'points': row['points'],
                        'is_sprint': str(row['is_sprint']).upper()
                    }
                )
            
            # 5. Ingest Results (mais complexo)
            print('  → Ingesting results...')
            for _, row in results_csv.iterrows():
                race_id_val = int(row['race_id']) if pd.notna(row['race_id']) else 0
                real_race_id = race_map.get(race_id_val)
                
                # Verifica se é sprint
                is_sprint_result = conn.execute(
                    text("SELECT is_sprint FROM races WHERE race_id = :race_id"),
                    {'race_id': real_race_id}
                ).fetchone()
                is_sprint_val = is_sprint_result[0] if is_sprint_result else False
                
                # Busca pontos correspondentes
                points_result = conn.execute(
                    text("SELECT points FROM scores WHERE position = :position AND is_sprint = :is_sprint"),
                    {
                        'position': int(row['driver_final_position']) if pd.notna(row['driver_final_position']) else 0,
                        'is_sprint': str(is_sprint_val).upper()
                    }
                ).fetchone()
                points = points_result[0] if points_result else 0
                
                # Normaliza e busca driver_id
                driver_row = drivers_csv[drivers_csv['driver_id'] == row['driver_id']]
                real_driver_id = 0
                if not driver_row.empty and pd.notna(driver_row['driver_name'].iloc[0]):
                    driver_name = str(driver_row['driver_name'].iloc[0])
                    norm_driver_name = normalize_name(driver_name, name_map)
                    real_driver_id = get_or_create_entity(conn, 'drivers', 'driver_name', norm_driver_name)
                
                # Busca team_id
                team_row = teams_csv[teams_csv['team_id'] == row['team_id']]
                real_team_id = 0
                if not team_row.empty and pd.notna(team_row['team_name'].iloc[0]):
                    team_name = str(team_row['team_name'].iloc[0])
                    real_team_id = get_or_create_entity(conn, 'teams', 'team_name', team_name)
                
                # Cria registro de resultado
                conn.execute(
                    text("INSERT INTO results (race_id, driver_id, team_id, driver_start_position, driver_final_position, grid_result, driver_fastest_lap, points, year) "
                         "VALUES (:race_id, :driver_id, :team_id, :driver_start_position, :driver_final_position, :grid_result, :driver_fastest_lap, :points, :year)"),
                    {
                        'race_id': real_race_id,
                        'driver_id': real_driver_id,
                        'team_id': real_team_id,
                        'driver_start_position': row['driver_start_position'],
                        'driver_final_position': row['driver_final_position'],
                        'grid_result': row['grid_result'],
                        'driver_fastest_lap': row['driver_fastest_lap'],
                        'points': points,
                        'year': year
                    }
                )
            
            conn.commit()
        print('2025 data successfully ingested.')
    except Exception as e:
        print(f'Error during 2025 ingestion: {str(e)}')
        raise


def ingest_2026(name_map: Dict[str, str]) -> None:
    """
    Executa o pipeline completo de ingestão para dados de 2026.
    
    Diferente de 2025, os arquivos do ano 2026 têm estrutura customizada:
    - Cada arquivo CSV representa uma corrida específica (GP)
    - Filenames codificam metadados: nome_gp_tipo_data (ex: 'monaco_sprint_25.csv')
    - Formato de dados diferente: linhas com cabeçalho personalizado (Piloto, Equipe, Pos., Grid, Melhor tempo)
    
    Para cada arquivo:
    1. Parse filename para extrair tipo (race/sprint) e data
    2. Cria ou busca race_id no banco
    3. Processa dados line-by-line do arquivo
    4. Cria/insere registros de resultado com lookup de entidades
    
    Args:
        name_map: Dicionário {nome_antigo: nome_novo} para normalização de pilotos
        
    Raises:
        Exception: Se ocorrer erro durante leitura de arquivos customizados ou execução de queries
        
    Example:
        >>> from scripts.services.ingestion import ingest_2026
        >>> # Carregar mapeamento de nomes primeiro
        >>> name_map = load_name_mappings()
        >>> ingest_2026(name_map)
    """
    raw_dir = 'files/raw/2026'
    year = 2026
    
    print('Ingesting 2026 data...')
    
    try:
        with engine.connect() as conn:
            # Lista e ordena arquivos por data (secondary) e tipo sprint (terciary)
            files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.csv')], 
                           key=lambda x: (x.split('_')[-1], 0 if 'sprint' in x.lower() else 1))
            
            race_map = {}
            
            for filename in files:
                print(f'    Processing {filename}...')
                
                # Parse filename para extrair metadados
                parts = filename.replace('.csv', '').split('_')
                if len(parts) < 3: 
                    continue
                
                gp_name = ' '.join(parts[:-2]).title()
                race_type = parts[-2].lower()
                race_date = parts[-1]
                is_sprint = race_type == 'sprint'
                full_race_name = f'GP de {gp_name}' + (' (SPRINT)' if is_sprint else '')
                
                # Busca ou cria race_id
                existing = conn.execute(
                    text("SELECT race_id FROM races WHERE race_name = :race_name AND race_date = :race_date"),
                    {'race_name': full_race_name, 'race_date': race_date}
                ).fetchone()
                
                if existing:
                    race_id = existing[0]
                else:
                    res = conn.execute(
                        text("INSERT INTO races (race_name, race_date, race_location, is_sprint, year) "
                             "VALUES (:race_name, :race_date, :race_location, :is_sprint, :year)"),
                        {
                            'race_name': full_race_name,
                            'race_date': race_date,
                            'race_location': gp_name,
                            'is_sprint': str(is_sprint).upper(),
                            'year': year
                        }
                    )
                    race_id = res.lastrowid
                
                # Carrega dados do arquivo (formato customizado)
                with open(os.path.join(raw_dir, filename), mode='r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                    section1_lines = []
                    for line in lines:
                        stripped = line.strip()
                        if not stripped or all(c == ',' for c in stripped): 
                            break
                        section1_lines.append(line)
                    
                    df = pd.read_csv(io.StringIO(''.join(section1_lines)))
                    
                    for _, row in df.iterrows():
                        piloto = str(row.get('Piloto', '')).strip()
                        if not piloto or piloto == 'Pessoa': 
                            continue
                        
                        norm_piloto = normalize_name(piloto, name_map)
                        equipe = str(row.get('Equipe', '')).strip()
                        
                        # Busca team_id
                        real_team_id = get_or_create_entity(conn, 'teams', 'team_name', equipe)
                        
                        # Busca driver_id
                        real_driver_id = get_or_create_entity(conn, 'drivers', 'driver_name', norm_piloto)
                        
                        # Parse posições
                        try:
                            final_pos = int(row.get('Pos.', 0))
                            start_pos = int(row.get('Grid', 0))
                            grid_result = final_pos - start_pos
                        except:
                            final_pos, grid_result = 0, 0
                        
                        # Busca pontos por posição
                        points_result = conn.execute(
                            text("SELECT points FROM scores WHERE position = :position AND is_sprint = :is_sprint"),
                            {'position': final_pos, 'is_sprint': str(is_sprint).upper()}
                        ).fetchone()
                        points = points_result[0] if points_result else 0
                        
                        # Cria resultado
                        conn.execute(
                            text("INSERT INTO results (race_id, driver_id, team_id, driver_start_position, driver_final_position, grid_result, driver_fastest_lap, points, year) "
                                 "VALUES (:race_id, :driver_id, :team_id, :driver_start_position, :driver_final_position, :grid_result, :driver_fastest_lap, :points, :year)"),
                            {
                                'race_id': race_id,
                                'driver_id': real_driver_id,
                                'team_id': real_team_id,
                                'driver_start_position': row.get('Grid'),
                                'driver_final_position': final_pos,
                                'grid_result': grid_result,
                                'driver_fastest_lap': row.get('Melhor tempo'),
                                'points': points,
                                'year': year
                            }
                        )
                
                conn.commit()
            
            print('2026 data successfully ingested.')
    except Exception as e:
        print(f'Error during 2026 ingestion: {str(e)}')
        raise


def normalize_name(name: str, name_map: Dict[str, str]) -> str:
    """
    Normaliza nome de piloto usando mapeamento.
    
    Consulta o dicionário de mapeamento para retornar o nome atualizado.
    Se o nome não estiver no mapeamento, retorna o nome original.
    Utilizado para manter consistência quando pilotos mudam seus nomes
    oficialmente (ex: "Max" -> "Maximilian").
    
    Args:
        name: Nome original do piloto (ex: "Lewis Hamilton")
        name_map: Dicionário {nome_antigo: nome_novo} carregado de CSV
        
    Returns:
        str: Nome normalizado (atualizado se estiver no mapeamento)
        
    Example:
        >>> name_map = {"Max": "Maximilian", "Lewis": "Lewis"}
        >>> normalize_name("Max", name_map)
        'Maximilian'
        >>> normalize_name("Oscar", name_map)  # Not in map
        'Oscar'
    """
    return name_map.get(name, name)


def get_or_create_entity(conn, table: str, name_col: str, name_val: str):
    """
    Busca entidade no banco ou cria se não existir.
    
    Implementa padrão "get or create" para evitar duplicatas de registros.
    Primeiro consulta se um registro com o mesmo nome já existe na tabela
    especificada. Se existir, retorna o ID existente. Caso contrário, insere
    novo registro e retorna o ID recém-criado.
    
    Args:
        conn: Conexão SQLAlchemy ativa para execução de queries (with engine.connect())
        table: Nome da tabela SQL (ex: 'teams', 'drivers', 'races')
        name_col: Nome da coluna contendo o nome do entidade
        name_val: Valor exato do nome a buscar ou criar
        
    Returns:
        Inteiro: ID existente se encontrado, ou ID novo criado se não existir
        
    Raises:
        Exception: Se ocorrer erro durante busca ou inserção de registro
        
    Example:
        >>> with engine.connect() as conn:
        ...     team_id = get_or_create_entity(
        ...         conn, 'teams', 'team_name', 'Red Bull Racing'
        ...     )
        ...     print(team_id)  # e.g., 5
    """
    from sqlalchemy import text
    
    # Busca primeiro
    result = conn.execute(
        text(f'SELECT {table[:-1]}_id FROM {table} WHERE {name_col} = :name_val'),
        {'name_val': name_val}
    ).fetchone()
    
    if result and result[0] > 0:
        return result[0]
    
    # Cria se não existe
    conn.execute(
        text(f'INSERT INTO {table} ({name_col}) VALUES (:name_val)'),
        {'name_val': name_val}
    )
    conn.commit()
    
    # Retorna último ID inserido
    return conn.execute(text('SELECT last_insert_rowid()')).fetchone()[0]
