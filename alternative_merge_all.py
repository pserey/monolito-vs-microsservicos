import pandas as pd
from pathlib import Path

def get_cpu_data(directory_path):
    """
    Obtém dados de CPU de um diretório. Prioriza cpu_deployment.csv,
    se não existir, agrega cpu_pod_long.csv por timestamp.
    """
    cpu_deployment_file = directory_path / "cpu_deployment.csv"
    cpu_pod_file = directory_path / "cpu_pod_long.csv"
    
    if cpu_deployment_file.exists():
        # Opção 1: usar dados do deployment completo
        return pd.read_csv(cpu_deployment_file)
    elif cpu_pod_file.exists():
        # Opção 2: agregar dados por pod por timestamp
        df_pods = pd.read_csv(cpu_pod_file)
        # Agregar por timestamp somando os cores de todos os pods
        df_aggregated = df_pods.groupby('timestamp')['cores'].sum().reset_index()
        return df_aggregated
    else:
        return None

def get_hpa_data(directory_path):
    """
    Obtém dados de HPA (current, desired, max replicas) de um diretório.
    """
    hpa_files = {
        'hpa_current.csv': 'current_replicas',
        'hpa_desired.csv': 'desired_replicas', 
        'hpa_max.csv': 'max_replicas'
    }
    
    hpa_dfs = []
    for filename, column_name in hpa_files.items():
        file_path = directory_path / filename
        if file_path.exists():
            df = pd.read_csv(file_path)
            hpa_dfs.append(df)
    
    return hpa_dfs

def merge_service_data(directory_path):
    """
    Merge dados de CPU e HPA de um serviço/diretório.
    """
    # Obter dados de CPU
    cpu_df = get_cpu_data(directory_path)
    
    # Obter dados de HPA
    hpa_dfs = get_hpa_data(directory_path)
    
    if cpu_df is None:
        return None
    
    # Começar com dados de CPU
    merged_df = cpu_df.copy()
    
    # Fazer merge com cada arquivo HPA
    for hpa_df in hpa_dfs:
        merged_df = pd.merge(
            merged_df, hpa_df,
            on="timestamp",
            how="outer",
            suffixes=("", "_dup")
        )
        # Remover colunas duplicadas
        merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith("_dup")]
    
    return merged_df

base_dir = Path("results")
architectures = ["decoupled", "functional", "monolith"]

all_data = []
locust_data = []

for arch in architectures:
    arch_dir = base_dir / arch / "cpu_hpa"
    if arch_dir.exists():
        # ---------- cpu_hpa ----------
        if arch == "monolith":
            # Para monolith, pegar os dados de CPU e HPA
            merged_df = merge_service_data(arch_dir)
            
            if merged_df is not None:
                merged_df["service"] = "monolith"
                merged_df["architecture"] = "monolith"
                all_data.append(merged_df)
                print(f"✅ Dados coletados para {arch}: {len(merged_df)} registros")

        else:  # decoupled/functional
            # Para arquiteturas desacopladas, coletar dados de cada serviço
            service_data = []
            
            for service_dir in arch_dir.iterdir():
                if service_dir.is_dir():
                    parts = service_dir.name.split("-")
                    service_name = parts[1] if len(parts) > 1 else service_dir.name
                    
                    merged_df = merge_service_data(service_dir)
                    
                    if merged_df is not None:
                        merged_df["service"] = service_name
                        merged_df["architecture"] = arch
                        service_data.append(merged_df)
                        print(f"✅ Dados coletados para {arch}/{service_name}: {len(merged_df)} registros")
            
            # Agregar dados de todos os serviços por timestamp
            if service_data:
                # Criar dataset individual por serviço
                for service_df in service_data:
                    all_data.append(service_df)
                
                # Criar dataset agregado para toda a arquitetura (apenas cores)
                all_services_df = pd.concat(service_data, ignore_index=True)
                arch_aggregated = all_services_df.groupby('timestamp')['cores'].sum().reset_index()
                
                # Para HPA, usar a soma das replicas (assumindo que queremos o total da arquitetura)
                if 'current_replicas' in all_services_df.columns:
                    hpa_aggregated = all_services_df.groupby('timestamp')[
                        ['current_replicas', 'desired_replicas', 'max_replicas']
                    ].sum().reset_index()
                    arch_aggregated = pd.merge(arch_aggregated, hpa_aggregated, on='timestamp', how='outer')
                
                arch_aggregated["service"] = "all_services"
                arch_aggregated["architecture"] = arch
                all_data.append(arch_aggregated)
                print(f"✅ Dados agregados para {arch}: {len(arch_aggregated)} registros")

    # ---------- locust ----------
    locust_dir = base_dir / arch / "locust"
    locust_file = locust_dir / f"{arch}_run_stats_history.csv"
    if locust_file.exists():
        df_locust = pd.read_csv(locust_file)
        
        # Renomear colunas para manter compatibilidade com código R original
        column_mapping = {
            "Total Median Response Time": "total_median_response_time",
            "Requests/s": "req_s",
            "Total Average Response Time": "total_average_response_time",
            "Total Request Count": "total_request_count",
            "Total Failure Count": "total_failure_count",
            "User Count": "user_count",
            "Timestamp": "timestamp"
        }
        
        # Aplicar renomeação apenas para colunas que existem
        existing_columns = {old_name: new_name for old_name, new_name in column_mapping.items() 
                          if old_name in df_locust.columns}
        df_locust = df_locust.rename(columns=existing_columns)
        
        df_locust["architecture"] = arch
        locust_data.append(df_locust)

# concatena cpu_hpa
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    if "timestamp" in final_df.columns:
        final_df = final_df.sort_values("timestamp")
    final_df.to_csv("merged_all.csv", index=False)
    print("✅ Arquivo salvo em merged_all.csv")

# concatena locust
if locust_data:
    final_locust = pd.concat(locust_data, ignore_index=True)
    final_locust.to_csv("merged_locust.csv", index=False)
    print("✅ Arquivo salvo em merged_locust.csv")
