import os
import glob
import re
from datetime import datetime

def filter_logs_by_id_and_separate_by_date(log_directory, target_id):
    """
    Busca em todos os arquivos .log de um diretório por um ID específico
    e separa os logs por data, criando um arquivo para cada dia
    """
    
    # Verifica se o diretório existe
    if not os.path.exists(log_directory):
        print(f"Erro: Diretório '{log_directory}' não encontrado!")
        return
    
    # Padrão para buscar todos os arquivos .log
    log_pattern = os.path.join(log_directory, "*.log")
    log_files = glob.glob(log_pattern)
    
    if not log_files:
        print(f"Nenhum arquivo .log encontrado em '{log_directory}'")
        return
    
    print(f"Encontrados {len(log_files)} arquivos .log")
    print(f"Buscando por padrões específicos do fazendapombo_2 e separando por datas...")
    
    # Dicionários para armazenar logs por data e tipo
    packages_by_date = {}  # Para #0-fazendapombo_2
    json_by_date = {}      # Para JSONs
    total_packages = 0
    total_jsons = 0
    
    # Padrões específicos para capturar as mensagens completas
    package_pattern = r'#0-fazendapombo_2[^$]*\$'  # Captura desde #0-fazendapombo_2 até o $
    json_patterns = [
        r'Enviando pacote para o icrop: (\{[^}]*"id":"fazendapombo_2"[^}]*\})',  # JSON do icrop
        r'(\{"id":"fazendapombo_2"[^}]*\})',  # JSON direto
    ]
    
    # Padrões de data comuns em logs
    date_patterns = [
        (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),          # 2025-07-10
        (r'(\d{2}/\d{2}/\d{4})', '%d/%m/%Y'),          # 10/07/2025
        (r'(\d{2}-\d{2}-\d{4})', '%d-%m-%Y'),          # 10-07-2025
    ]

    # Processa cada arquivo .log
    for log_file in log_files:
        print(f"Processando: {os.path.basename(log_file)}")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    # Extrai a data da linha primeiro
                    found_date = None
                    found_time = None
                    
                    for pattern, date_format in date_patterns:
                        match = re.search(pattern, line)
                        if match:
                            date_str = match.group(1)
                            try:
                                # Converte para formato padrão YYYY-MM-DD
                                parsed_date = datetime.strptime(date_str, date_format)
                                found_date = parsed_date.strftime('%Y-%m-%d')
                                found_time = parsed_date.strftime('%d/%m/%Y')
                                break
                            except ValueError:
                                continue
                    
                    # Se não encontrou data nos padrões, tenta extrair do timestamp na linha
                    if not found_date:
                        # Busca por timestamp no formato HH:mm:ss
                        time_match = re.search(r'(\d{1,2}:\d{2}:\d{2})', line)
                        if time_match:
                            found_time = f"{datetime.now().strftime('%d/%m/%Y')} {time_match.group(1)}"
                            found_date = datetime.now().strftime('%Y-%m-%d')
                    
                    if found_date:
                        # Verifica se é um pacote #0-fazendapombo_2
                        package_match = re.search(package_pattern, line)
                        if package_match:
                            if found_date not in packages_by_date:
                                packages_by_date[found_date] = []
                            
                            # Formato simplificado: DD/MM/YYYY HH:mm:ss -> #0-fazendapombo_2...
                            simple_entry = f"{found_time} -> {package_match.group(0)}"
                            packages_by_date[found_date].append(simple_entry)
                            total_packages += 1
                        
                        # Verifica se é um JSON
                        for json_pattern in json_patterns:
                            json_match = re.search(json_pattern, line)
                            if json_match:
                                if found_date not in json_by_date:
                                    json_by_date[found_date] = []
                                
                                # Formato simplificado: DD/MM/YYYY HH:mm:ss -> {...}
                                json_content = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group(0)
                                simple_entry = f"{found_time} -> {json_content}"
                                json_by_date[found_date].append(simple_entry)
                                total_jsons += 1
                                break
                        
        except Exception as e:
            print(f"Erro ao ler arquivo {log_file}: {e}")
    
    # Gera arquivos separados por data e tipo
    total_files_generated = 0
    
    # Gera arquivos de pacotes
    if packages_by_date:
        print(f"\n📦 Encontrados pacotes em {len(packages_by_date)} datas diferentes")
        
        for date, packages in packages_by_date.items():
            date_formatted = date.replace('-', '_')
            output_file = f"logs_packages_{date_formatted}.log"
            
            try:
                with open(output_file, 'w', encoding='utf-8') as output:
                    # Cabeçalho simples
                    output.write(f"# Pacotes #0-fazendapombo_2 da data: {date}\n")
                    output.write(f"# Total de pacotes: {len(packages)}\n")
                    output.write("#" + "="*50 + "\n\n")
                    
                    # Escreve os pacotes no formato simples
                    for package_entry in packages:
                        output.write(package_entry + "\n")
                
                print(f"📁 Arquivo gerado: {output_file} ({len(packages)} pacotes)")
                total_files_generated += 1
                
            except Exception as e:
                print(f"Erro ao criar arquivo de pacotes para data {date}: {e}")
    
    # Gera arquivos de JSONs
    if json_by_date:
        print(f"\n🔗 Encontrados JSONs em {len(json_by_date)} datas diferentes")
        
        for date, jsons in json_by_date.items():
            date_formatted = date.replace('-', '_')
            output_file = f"logs_json_{date_formatted}.log"
            
            try:
                with open(output_file, 'w', encoding='utf-8') as output:
                    # Cabeçalho simples
                    output.write(f"# JSONs fazendapombo_2 da data: {date}\n")
                    output.write(f"# Total de JSONs: {len(jsons)}\n")
                    output.write("#" + "="*50 + "\n\n")
                    
                    # Escreve os JSONs no formato simples
                    for json_entry in jsons:
                        output.write(json_entry + "\n")
                
                print(f"📁 Arquivo gerado: {output_file} ({len(jsons)} JSONs)")
                total_files_generated += 1
                
            except Exception as e:
                print(f"Erro ao criar arquivo de JSONs para data {date}: {e}")
    
    # Resumo final
    if total_files_generated > 0:
        print(f"\n📊 Resumo:")
        print(f"   📦 Total de pacotes encontrados: {total_packages}")
        print(f"   🔗 Total de JSONs encontrados: {total_jsons}")
        print(f"   📁 Total de arquivos gerados: {total_files_generated}")
    else:
        print(f"\n❌ Nenhum log encontrado com os padrões do fazendapombo_2")

def main():
    # Configurações
    LOG_DIRECTORY = "logs-monitor"
    TARGET_ID = "fazendapombo_2"
    
    print("🔍 Iniciando filtro de logs...")
    print(f"📂 Diretório: {LOG_DIRECTORY}")
    print(f"🎯 Separando em:")
    print(f"   📦 Pacotes: logs_packages_DD_MM_YYYY.log")
    print(f"   🔗 JSONs: logs_json_DD_MM_YYYY.log")
    print(f"📅 Agrupando automaticamente por data")
    print("-" * 50)
    
    filter_logs_by_id_and_separate_by_date(LOG_DIRECTORY, TARGET_ID)

if __name__ == "__main__":
    main()