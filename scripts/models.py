"""
Pydantic Models e Database Enums para F1 Championship API.

Este módulo fornece:
- Modelos Pydantic para validação de dados
- Enums seguros para operações do banco de dados
- Tipos SQLAlchemy tipados
"""

from enum import Enum, auto
from typing import Optional
from datetime import date


# ============================================
# ENUMS PARA SEGURANÇA NO BANCO DE DADOS
# ============================================

class DatabaseTable(Enum):
    """
    Enum seguro para tabelas do banco de dados.
    
    Utilizado para referenciar tabelas SQL de forma tipada e segura,
    evitando erros de string literal em queries dinâmicas.
    
    Attributes:
        TEAMS: Tabela de equipes
        DRIVERS: Tabela de pilotos
        RACES: Tabela de corridas
        RESULTS: Tabela de resultados das corridas
        SCORES: Tabela de pontuação por posição
        
    Example:
        >>> table = DatabaseTable.TEAMS
        >>> table.table_name
        'teams'
    """
    
    TEAMS = "TEAMS"
    DRIVERS = "DRIVERS"
    RACES = "RACES"
    RESULTS = "RESULTS"
    SCORES = "SCORES"
    
    @property
    def table_name(self) -> str:
        """
        Retorna o nome da tabela em minúsculas.
        
        Returns:
            Nome da tabela SQL (ex: 'teams', 'drivers')
            
        Example:
            >>> DatabaseTable.RACES.table_name
            'races'
        """
        return self.value.lower()


class TableName(Enum):
    """
    Enum para nomes de tabelas SQL.
    
    Fornece acesso tipado aos nomes das tabelas em formato minúsculo
    utilizado diretamente em queries SQL.
    
    Attributes:
        TEAMS: Tabela de equipes ('teams')
        DRIVERS: Tabela de pilotos ('drivers')
        RACES: Tabela de corridas ('races')
        RESULTS: Tabela de resultados ('results')
        SCORES: Tabela de pontuação ('scores')
    """
    
    TEAMS = "teams"
    DRIVERS = "drivers"
    RACES = "races"
    RESULTS = "results"
    SCORES = "scores"


# ============================================
# Mapeamento entre Tabelas e Columns
# ============================================

class TableMapping(Enum):
    """
    Mapeamento de columns por tabela.
    
    Fornece acesso tipado aos nomes das columns utilizadas em queries SQL,
    organizadas por tabela para facilitar o acesso e evitar erros de string literal.
    
    Attributes:
        TEAMS_TEAM_ID: Column ID da tabela teams
        TEAMS_TEAM_NAME: Column name da tabela teams
        DRIVERS_DRIVER_ID: Column ID da tabela drivers
        DRIVERS_DRIVER_NAME: Column name da tabela drivers
        RACES_RACE_ID: Column ID da tabela races
        RACES_RACE_NAME: Column name da tabela races
        RACES_RACE_DATE: Column date da tabela races
        RACES_RACE_LOCATION: Column location da tabela races
        RACES_IS_SPRINT: Column sprint da tabela races
        RACES_YEAR: Column year da tabela races
        RESULTS_RESULT_ID: Column ID da tabela results
        RESULTS_RACE_ID: Column race_id da tabela results
        RESULTS_DRIVER_ID: Column driver_id da tabela results
        RESULTS_TEAM_ID: Column team_id da tabela results
        RESULTS_DRIVER_START_POSITION: Column start_position da tabela results
        RESULTS_DRIVER_FINAL_POSITION: Column final_position da tabela results
        RESULTS_GRID_RESULT: Column grid_result da tabela results
        RESULTS_DRIVER_FASTEST_LAP: Column fastest_lap da tabela results
        RESULTS_POINTS: Column points da tabela results
        RESULTS_YEAR: Column year da tabela results
        SCORES_SCORE_ID: Column ID da tabela scores
        SCORES_POSITION: Column position da tabela scores
        SCORES_POINTS: Column points da tabela scores
        SCORES_IS_SPRINT: Column is_sprint da tabela scores
    """
    
    TEAMS_TEAM_ID = "team_id"
    TEAMS_TEAM_NAME = "team_name"
    
    DRIVERS_DRIVER_ID = "driver_id"
    DRIVERS_DRIVER_NAME = "driver_name"
    
    RACES_RACE_ID = "race_id"
    RACES_RACE_NAME = "race_name"
    RACES_RACE_DATE = "race_date"
    RACES_RACE_LOCATION = "race_location"
    RACES_IS_SPRINT = "is_sprint"
    RACES_YEAR = "year"
    
    RESULTS_RESULT_ID = "result_id"
    RESULTS_RACE_ID = "race_id"
    RESULTS_DRIVER_ID = "driver_id"
    RESULTS_TEAM_ID = "team_id"
    RESULTS_DRIVER_START_POSITION = "driver_start_position"
    RESULTS_DRIVER_FINAL_POSITION = "driver_final_position"
    RESULTS_GRID_RESULT = "grid_result"
    RESULTS_DRIVER_FASTEST_LAP = "driver_fastest_lap"
    RESULTS_POINTS = "points"
    RESULTS_YEAR = "year"
    
    SCORES_SCORE_ID = "score_id"
    SCORES_POSITION = "position"
    SCORES_POINTS = "points"
    SCORES_IS_SPRINT = "is_sprint"


# ============================================
# Pydantic Models para Validação
# ============================================

from pydantic import BaseModel, Field, field_validator


class LoadDataRequest(BaseModel):
    """
    Modelo de request para endpoint /load.
    
    Representa os parâmetros necessários para carregar dados da API,
    incluindo ano e tipo de dados (races, drivers, results, teams, scores).
    Utilizado na validação de requisições HTTP para carregamento de dados.
    
    Attributes:
        year: Ano da temporada (int)
        file_type: Tipo de dados a carregar (str): 'races', 'drivers', 'results', 'teams', ou 'scores'
        
    Example:
        >>> request = LoadDataRequest(year=2025, file_type="races")
        >>> request.year
        2025
    """
    
    year: int = Field(..., description="Ano da temporada")
    file_type: str = Field(
        ..., 
        description="Tipo de dados a carregar",
        min_length=1,
        max_length=50
    )
    
    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v: str) -> str:
        """
        Valida e sanitiza o tipo de arquivo.
        
        Remove espaços em branco e converte para minúsculas para garantir
        consistência nos dados recebidos.
        
        Args:
            v: Valor string a validar
            
        Returns:
            String limpa e em minúsculas (ex: 'drivers')
            
        Example:
            >>> validate_file_type("  RACES  ")
            'races'
        """
        return v.strip().lower()


# ============================================
# Helpers para SQLAlchemy
    """
    Modelo para dados de pontuação.
    
    Representa o sistema de pontuação da Fórmula 1 por posição,
    com suporte diferenciado para corridas de sprint.
    Utilizado na validação de dados recebidos via API ou durante ingestão.
    
    Attributes:
        score_id: ID único do registro de pontuação (auto-incrementado no banco)
        position: Posição no grid/pódio
        points: Pontos associados a essa posição
        is_sprint: Indica se é para corrida de sprint (True/False)
        
    Example:
        >>> data = {"position": 1, "points": 25, "is_sprint": False}
        >>> score = Score(**data)
        >>> score.points
        25
    """
    
    score_id: Optional[int] = None
    position: Optional[int] = Field(None, description="Posição")
    points: Optional[int] = Field(None, description="Pontos")
    is_sprint: Optional[bool] = Field(None, description="Se é sprint")

class Race(BaseModel):
    """
    Modelo para dados de corrida (GP).
    
    Representa uma corrida da Fórmula 1 com seus atributos principais.
    Utilizado na validação de dados recebidos via API ou durante ingestão.
    
    Attributes:
        race_id: ID único da corrida (auto-incrementado no banco)
        race_name: Nome oficial da corrida (ex: "British Grand Prix")
        race_date: Data da corrida no formato YYYY-MM-DD
        race_location: Localização/cidade onde a corrida ocorre
        is_sprint: Indica se é uma corrida de sprint (True/False)
        year: Ano da temporada
        
    Example:
        >>> data = {"race_name": "Monaco GP", "race_date": "2025-05-25"}
        >>> race = Race(**data)
        >>> race.race_name
        'Monaco GP'
    """
    
    race_id: Optional[int] = None
    race_name: Optional[str] = Field(None, description="Nome da corrida")
    race_date: Optional[str] = Field(None, description="Data da corrida YYYY-MM-DD")
    race_location: Optional[str] = Field(None, description="Localização da corrida")
    is_sprint: Optional[bool] = Field(None, description="Se é uma sprint")
    year: Optional[int] = None


class Driver(BaseModel):
    """
    Modelo para dados de piloto.
    
    Representa um piloto da Fórmula 1 e suas participações em uma temporada.
    Utilizado na validação de dados recebidos via API ou durante ingestão.
    
    Attributes:
        driver_id: ID único do piloto (auto-incrementado no banco)
        driver_name: Nome oficial do piloto
        team_id: ID da equipe associada ao piloto
        year: Ano da temporada
        
    Example:
        >>> data = {"driver_name": "Max Verstappen", "team_id": 1, "year": 2025}
        >>> driver = Driver(**data)
        >>> driver.driver_name
        'Max Verstappen'
    """
    
    driver_id: Optional[int] = None
    driver_name: Optional[str] = Field(None, description="Nome do piloto")
    team_id: Optional[int] = None
    year: Optional[int] = None


class Team(BaseModel):
    """
    Modelo para dados de equipe.
    
    Representa uma equipe construtora da Fórmula 1.
    Utilizado na validação de dados recebidos via API ou durante ingestão.
    
    Attributes:
        team_id: ID único da equipe (auto-incrementado no banco)
        team_name: Nome oficial da equipe/construtora
        year: Ano da temporada
        
    Example:
        >>> data = {"team_name": "Red Bull Racing", "year": 2025}
        >>> team = Team(**data)
        >>> team.team_name
        'Red Bull Racing'
    """
    
    team_id: Optional[int] = None
    team_name: Optional[str] = Field(None, description="Nome da equipe")
    year: Optional[int] = None


class Result(BaseModel):
    """
    Modelo para dados de resultado de corrida.
    
    Representa o desempenho de um piloto em uma corrida específica,
    incluindo posição final, grid, pontos e marcas.
    Utilizado na validação de dados recebidos via API ou durante ingestão.
    
    Attributes:
        result_id: ID único do resultado (auto-incrementado no banco)
        race_id: ID da corrida onde o resultado ocorreu
        driver_id: ID do piloto
        team_id: ID da equipe do piloto
        driver_start_position: Posição inicial na grid
        driver_final_position: Posição final após a corrida
        grid_result: Diferença entre final e start (final - start)
        driver_fastest_lap: Indica se o piloto marcou o melhor tempo
        points: Pontos ganhos na corrida
        year: Ano da temporada
        
    Example:
        >>> data = {
        ...     "race_id": 1,
        ...     "driver_id": 5,
        ...     "team_id": 3,
        ...     "driver_final_position": 1,
        ...     "points": 25
        ... }
        >>> result = Result(**data)
        >>> result.driver_final_position
        1
    """
    
    result_id: Optional[int] = None
    race_id: Optional[int] = None
    driver_id: Optional[int] = None
    team_id: Optional[int] = None
    driver_start_position: Optional[int] = Field(None, description="Posição na grid")
    driver_final_position: Optional[int] = Field(None, description="Posição final")
    grid_result: Optional[int] = Field(None, description="Resultado da grid (final - start)")
    driver_fastest_lap: Optional[str] = Field(None, description="Marca no pódio")
    points: Optional[int] = Field(None, description="Pontos ganhos")
    year: Optional[int] = None


class Score(BaseModel):
    """
    Modelo para dados de pontuação.
    
    Representa o sistema de pontuação da Fórmula 1 por posição,
    com suporte diferenciado para corridas de sprint.
    Utilizado na validação de dados recebidos via API ou durante ingestão.
    
    Attributes:
        score_id: ID único do registro de pontuação (auto-incrementado no banco)
        position: Posição no grid/pódio
        points: Pontos associados a essa posição
        is_sprint: Indica se é para corrida de sprint (True/False)
        
    Example:
        >>> data = {"position": 1, "points": 25, "is_sprint": False}
        >>> score = Score(**data)
        >>> score.points
        25
    """
    
    score_id: Optional[int] = None
    position: Optional[int] = Field(None, description="Posição")
    points: Optional[int] = Field(None, description="Pontos")
    is_sprint: Optional[bool] = Field(None, description="Se é sprint")


# ============================================
# Helpers para SQLAlchemy
# ============================================

def get_table_column_identifier(table: DatabaseTable) -> str:
    """
    Retorna o identificador da column ID para uma tabela.
    
    Gera o nome do identificador primário com base no enum da tabela,
    seguindo a convenção de nomenclatura <tabela>_id.
    
    Args:
        table: Enum DatabaseTable identificando a tabela
        
    Returns:
        String contendo o nome do identificador (ex: 'team_id', 'driver_id')
        
    Example:
        >>> get_table_column_identifier(DatabaseTable.TEAMS)
        'teams_id'
        >>> get_table_column_identifier(DatabaseTable.DRIVERS)
        'drivers_id'
    """
    return f"{table.value}_id"


def get_entity_from_db(conn, table: DatabaseTable, name_column: str, value: str):
    """
    Busca entidade no banco ou retorna None se não existir.
    
    Executa uma query SQL para encontrar um registro por nome em uma tabela
    específica, retornando o ID correspondente ou 0 se não encontrado.
    
    Args:
        conn: Conexão SQLAlchemy ativa
        table: Enum DatabaseTable identificando a tabela a buscar
        name_column: Nome da coluna contendo o nome do entidade (ex: 'team_name', 'driver_name')
        value: Valor exato do nome a buscar
        
    Returns:
        Inteiro com o ID da entidade ou 0 se não encontrada
        
    Raises:
        Exception: Se ocorrer erro durante execução da query SQL
        
    Example:
        >>> from database import SessionLocal
        >>> with SessionLocal() as conn:
        ...     entity_id = get_entity_from_db(conn, DatabaseTable.TEAMS, 'team_name', 'Red Bull')
        ...     print(entity_id)  # e.g., 5
    """
    from sqlalchemy import text
    
    table_name = table.table_name
    entity_id_col = get_table_column_identifier(table)
    
    query = text(f"""
        SELECT {entity_id_col} FROM {table_name} 
        WHERE {name_column} = :name_val
    """)
    
    result = conn.execute(query, {"name_val": value}).fetchone()
    return result[0] if result else 0


def create_entity_if_not_exists(conn, table: DatabaseTable, name_column: str, value: str):
    """
    Cria entidade no banco se não existir.
    
    Implementa padrão de "get or create": verifica se um registro já existe
    por nome na tabela especificada. Se existir, retorna o ID existente.
    Se não existir, insere novo registro e retorna o ID criado.
    
    Args:
        conn: Conexão SQLAlchemy ativa para execução de queries
        table: Enum DatabaseTable identificando a tabela
        name_column: Nome da coluna contendo o nome do entidade (ex: 'team_name', 'driver_name')
        value: Valor exato do nome a buscar ou criar
        
    Returns:
        Inteiro com o ID existente (se encontrado) ou ID criado (se novo registro)
        
    Raises:
        Exception: Se ocorrer erro durante execução de INSERT
        
    Example:
        >>> from database import SessionLocal
        >>> with SessionLocal() as conn:
        ...     entity_id = create_entity_if_not_exists(conn, DatabaseTable.TEAMS, 'team_name', 'New Team')
        ...     print(entity_id)  # e.g., 5
    """
    from sqlalchemy import text
    
    # Busca primeiro
    existing_id = get_entity_from_db(conn, table, name_column, value)
    if existing_id and existing_id > 0:
        return existing_id
    
    # Cria se não existe
    table_name = table.table_name
    insert_query = text(f"""
        INSERT INTO {table_name} ({name_column}) VALUES (:name_val)
    """)
    
    conn.execute(insert_query, {"name_val": value})
    conn.commit()
    
    # Retorna último ID inserido
    return conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]
