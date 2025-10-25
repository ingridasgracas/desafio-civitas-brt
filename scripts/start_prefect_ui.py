"""
Script para iniciar Prefect Server localmente (sem Docker)
"""

import subprocess
import sys
import time
import webbrowser
from loguru import logger

def start_prefect_server():
    """Inicia o Prefect Server localmente"""
    
    logger.info("="*60)
    logger.info("🚀 Iniciando Prefect Server")
    logger.info("="*60)
    
    # Configurar backend
    logger.info("Configurando backend para 'server'...")
    subprocess.run(["prefect", "backend", "server"], check=True)
    
    logger.info("\n📊 Iniciando Prefect Server UI...")
    logger.info("Aguarde alguns segundos para o servidor iniciar...\n")
    
    try:
        # Iniciar servidor em background
        process = subprocess.Popen(
            ["prefect", "server", "start", "--no-agent"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Aguardar inicialização
        logger.info("⏳ Aguardando servidor inicializar (30 segundos)...")
        time.sleep(30)
        
        # Verificar se está rodando
        if process.poll() is None:
            logger.success("\n✅ Prefect Server iniciado!")
            logger.info("="*60)
            logger.info("📊 INTERFACE WEB DISPONÍVEL:")
            logger.info("="*60)
            logger.info("\n🌐 URL: http://localhost:8080")
            logger.info("\nPressione Ctrl+C para parar o servidor\n")
            
            # Abrir navegador
            time.sleep(2)
            webbrowser.open("http://localhost:8080")
            
            # Manter rodando e mostrar logs
            try:
                for line in process.stdout:
                    print(line, end='')
            except KeyboardInterrupt:
                logger.info("\n\n⏹️  Parando Prefect Server...")
                process.terminate()
                process.wait()
                logger.success("✅ Servidor parado!")
        else:
            logger.error("❌ Falha ao iniciar servidor")
            logger.info("Verifique se não há outro processo usando a porta 8080")
            return False
        
    except FileNotFoundError:
        logger.error("❌ Comando 'prefect server start' não encontrado")
        logger.info("\nPrefect 1.4.1 pode não suportar este comando.")
        logger.info("Alternativa: use Prefect Cloud (gratuito)")
        logger.info("  1. Crie conta em: https://cloud.prefect.io")
        logger.info("  2. Execute: prefect backend cloud")
        logger.info("  3. Execute: prefect auth login")
        return False
    
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True


if __name__ == "__main__":
    start_prefect_server()
