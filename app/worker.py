"""
Worker: consome a fila e executa a inferencia.

O QUE JA ESTA PRONTO: o laco principal e o carregamento do modelo.
O QUE VOCE PRECISA FAZER (TAREFAS.md, itens 3 e 5):
  - guardar o resultado ao terminar
  - tratar erro com retentativa e fila de descarte (dead-letter)

Rodar:  python -m app.worker
Suba mais de um worker em terminais diferentes e veja a carga se dividir.
"""
import time

from app import fila
from app.modelo import carregar_modelo


def main():
    print("[worker] carregando modelo...")
    modelo = carregar_modelo()
    print("[worker] pronto. aguardando tarefas (Ctrl+C para sair)")

    while True:
        tarefa = fila.proxima_tarefa(timeout=5)
        if tarefa is None:
            continue

        print(f"[worker] processando {tarefa['id']}")
        inicio = time.time()
        try:
            resultado = modelo.prever(tarefa["texto"])
            resultado["status"] = "pronto"
            resultado["tempo_ms"] = round((time.time() - inicio) * 1000, 2)

            # TAREFA 3: guarde o resultado para o cliente consultar depois.
            fila.guardar_resultado(tarefa["id"], resultado)
            sucesso = True
            
            raise NotImplementedError("guarde o resultado na TAREFA 3")

        except NotImplementedError:
            raise
        except Exception as erro:  # noqa: BLE001
            # TAREFA 5: dead-letter em caso de falha após 3 tentativas
            if not sucesso:
                print(f"[worker] FALHA CRÍTICA. Enviando tarefa {tarefa['id']} para dead-letter.")
            # Certifiquem-se de que a função existe no fila.py ou criem uma logica simples no Redis
            try:
                fila.enviar_dead_letter(tarefa) 
            except AttributeError:
                # Fallback caso não tenham implementado a dead letter no fila.py ainda
                fila.guardar_resultado(tarefa["id"], {"status": "erro", "detalhe": "Falha após 3 tentativas."})

if __name__ == "__main__":
    main()

