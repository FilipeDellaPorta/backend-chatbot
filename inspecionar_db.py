from sqlalchemy import inspect, text
from database import engine
from sqlalchemy.orm import Session

# Criar inspetor para ver as tabelas
inspector = inspect(engine)
tabelas = inspector.get_table_names()
print("Tabelas no banco:", tabelas)

# Abrir sessão
with Session(engine) as session:
    for tabela in tabelas:
        print(f"\nConteúdo da tabela '{tabela}':")
        # Consulta todos os registros da tabela
        result = session.execute(text(f"SELECT * FROM {tabela}"))
        for row in result.fetchall():
            print(row)