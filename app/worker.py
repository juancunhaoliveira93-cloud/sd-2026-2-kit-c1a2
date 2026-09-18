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
        
        max_tentativas = 3
        sucesso = False
        
        for tentativa in range(max_tentativas):
            try:
                # Executa a inferência
                resultado = modelo.prever(tarefa["texto"])
                resultado["status"] = "pronto"
                tempo_execucao = round((time.time() - inicio) * 1000, 2)
                resultado["tempo_ms"] = tempo_execucao
    
                # TAREFA 3 (Lucas): guarde o resultado para o cliente consultar depois.
                fila.guardar_resultado(tarefa["id"], resultado)
                sucesso = True
                
                # TAREFA 6 (Victor): Log de requisições
                tamanho_texto = len(tarefa.get("texto", ""))
                print(f"[LOG] ID: {tarefa['id']} | Tamanho: {tamanho_texto} chars | Tempo: {tempo_execucao}ms")
                break # Sai do loop de tentativas se deu certo
    
            except Exception as erro:
                # TAREFA 5 (Lucas): retentativa
                print(f"[worker] ERRO em {tarefa['id']} (Tentativa {tentativa + 1}/{max_tentativas}): {erro}")
                time.sleep(1) # Pausa curta antes de tentar novamente
        
        # TAREFA 5 (Victor): dead-letter em caso de falha após 3 tentativas
        if not sucesso:
            print(f"[worker] FALHA CRÍTICA. Enviando tarefa {tarefa['id']} para dead-letter.")
            try:
                # Se houver um método implementado no fila.py
                fila.enviar_dead_letter(tarefa) 
            except AttributeError:
                # Fallback: salva com status de erro para não travar o cliente
                fila.guardar_resultado(tarefa["id"], {"status": "erro", "detalhe": "Falha após 3 tentativas."})


if __name__ == "__main__":
    main()