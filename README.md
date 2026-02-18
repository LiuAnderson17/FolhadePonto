# Controle de Ponto

Sistema web simples e moderno para registro de ponto eletrônico, desenvolvido com **Django** + **HTMX** + **Bootstrap 5**. Ideal para pequenas empresas, freelancers ou uso pessoal que precisam controlar horas trabalhadas de forma flexível.

## Funcionalidades Principais

- Registro de ponto com botão único (alternando Entrada/Saída automaticamente)
- Limite de **4 marcações por dia** (para evitar erros)
- Atualização da lista de marcações **sem recarregar a página** (graças ao HTMX)
- Toast de aviso quando tentar registrar além do limite
- Dashboard limpo com marcações do dia atual
- Relatório mensal (ou por período personalizado) com:
  - Tempo trabalhado por dia
  - Intervalo real de almoço exibido
  - Saldo diário (+/-) e acumulado do período
  - Layout otimizado para impressão (estilo relatório RH)
- Filtro por período (data inicial e final) no relatório
- Painel admin para edição de registros (data/hora editável para superusuário)
- Login/logout com sessão segura

## Tecnologias Utilizadas

- Backend: Django 5.x
- Frontend: Bootstrap 5.3 + Bootstrap Icons
- Interatividade sem recarregar página: HTMX 1.9
- Banco de dados: SQLite (padrão, fácil de trocar para PostgreSQL/MySQL)
- Autenticação: Django built-in

## Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Ambiente virtual recomendado (venv)

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/LiuAnderson17/FolhadePonto.git
   cd controle-de-ponto

2. Crie e ative o ambiente virtual:
```bash
  python -m venv venv
# Windows
  venv\Scripts\activate
# Linux/Mac
  source venv/bin/activate

3. Instale as dependências:
```bash
pip install -r requirements.txt
