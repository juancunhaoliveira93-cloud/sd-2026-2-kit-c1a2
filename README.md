# C1.A2 — Serviço de Inferência Distribuído

Serviço distribuído de inferência de inteligência artificial, com interfaces REST e gRPC e processamento assíncrono das tarefas recebidas pela API REST.

**Integrantes:** Carine, Gustavo, Lucas, Victor e Juan.

## Arquitetura

| Componente | Responsabilidade |
| --- | --- |
| API REST (FastAPI) | Receber solicitações, encaminhar as tarefas para a fila e retornar HTTP `202 Accepted`. |
| API gRPC | Disponibilizar uma interface de comunicação definida no arquivo `proto/inferencia.proto`. |
| Redis | Atuar como infraestrutura de mensageria e cache. |
| Worker | Consumir a fila em segundo plano, executar a inferência e armazenar os resultados. |
| Dead-Letter Queue (DLQ) | Receber tarefas que continuam falhando após o limite de tentativas. |

### Fluxo assíncrono via REST

1. O cliente envia uma solicitação à API REST.
2. A API coloca a tarefa na fila do Redis e retorna HTTP `202 Accepted`, indicando que a solicitação foi aceita para processamento.
3. O worker consome a tarefa e executa a inferência.
4. Em caso de sucesso, o resultado é armazenado. Em caso de falha, o processamento segue a política de até três tentativas.
5. Se a falha persistir após o limite de tentativas, a tarefa é encaminhada para a DLQ.

> A resposta HTTP `202 Accepted` confirma o aceite da tarefa; o processamento ocorre posteriormente.

## Pré-requisitos

- Python e `pip` instalados, em versões compatíveis com as dependências do projeto.
- Docker instalado e em execução, com Docker Compose disponível.
- Código do projeto disponível localmente.

Execute os comandos abaixo na **pasta raiz do projeto**.

## Como executar

### 1. Iniciar o Redis

Inicie os serviços definidos no arquivo de configuração do Docker Compose:

```bash
docker compose up -d
```

### 2. Criar o ambiente virtual e instalar as dependências

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente conforme seu sistema e terminal.

**Linux ou macOS:**

```bash
source .venv/bin/activate
```

**Windows — PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows — Prompt de Comando (CMD):**

```bat
.venv\Scripts\activate.bat
```

Com o ambiente virtual ativo, instale as dependências:

```bash
pip install -r requirements.txt
```

> Se o comando disponível no seu sistema for `python3`, utilize-o no lugar de `python` para criar o ambiente virtual.

### 3. Gerar os arquivos do gRPC

Gere os módulos Python a partir da definição do serviço:

```bash
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/inferencia.proto
```

Execute novamente esse comando sempre que alterar o arquivo `proto/inferencia.proto`.

### 4. Iniciar o worker

Em um terminal com o ambiente virtual ativo, execute:

```bash
python -m app.worker
```

Mantenha esse terminal aberto enquanto o serviço estiver em uso.

### 5. Iniciar as APIs

Abra **dois novos terminais** na raiz do projeto e ative o ambiente virtual em cada um deles.

**Terminal da API REST:**

```bash
uvicorn app.api_rest:app --port 8000
```

A documentação interativa estará disponível em [http://localhost:8000/docs](http://localhost:8000/docs).

**Terminal da API gRPC:**

```bash
python -m app.servidor_grpc
```

Ao final, mantenha o Redis em execução e os três processos ativos: worker, API REST e API gRPC.

## Verificação da execução

- Confira o estado dos serviços com `docker compose ps`.
- Verifique se os terminais do worker e das APIs apresentam erros de inicialização.
- Acesse a documentação interativa da API REST para consultar e testar as operações disponíveis.
- Ao enviar uma tarefa pela API REST, verifique a resposta HTTP `202 Accepted` e acompanhe o processamento no terminal do worker.

Para validar a instalação antes da entrega, obtenha uma cópia limpa do repositório em outra pasta e siga as instruções deste README.

## Como encerrar

Interrompa o worker e as APIs com `Ctrl+C` nos respectivos terminais. Em seguida, encerre os serviços do Docker Compose:

```bash
docker compose down
```