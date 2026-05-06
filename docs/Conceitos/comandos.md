# Comandos úteis do projeto

## Gerar árvore de diretórios
tree -I '__pycache__|venv|.venv|.git|node_modules|migrations|staticfiles|*.pyc' -L 4 > scripts/estrutura.txt
~~~bash
~~~

## Exportar projeto completo (código + estrutura) para análise

~~~bash
python scripts/export_projeto.py
~~~

> 💡 Os arquivos `estrutura.txt` e `projeto_completo.txt` são gerados na raiz e ignorados pelo git.
