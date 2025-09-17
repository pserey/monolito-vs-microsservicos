import pandas as pd
from pathlib import Path

base_dir = Path("results")
architectures = ["decoupled", "functional", "monolith"]

all_data = []
locust_data = []

for arch in architectures:
    arch_dir = base_dir / arch / "cpu_hpa"
    if arch_dir.exists():
        # ---------- cpu_hpa ----------
        if arch == "monolith":
            mono_dir = arch_dir / "monolith"
            service_dfs = []

            for file in mono_dir.glob("*.csv"):
                if file.name.lower() == "cpu_pod_long.csv":
                    continue
                df = pd.read_csv(file)
                service_dfs.append(df)

            if service_dfs:
                merged_service = service_dfs[0]
                for df in service_dfs[1:]:
                    merged_service = pd.merge(
                        merged_service, df,
                        on="timestamp",
                        how="outer",
                        suffixes=("", "_dup")
                    )
                merged_service = merged_service.loc[:, ~merged_service.columns.str.endswith("_dup")]

                merged_service["service"] = "monolith"
                merged_service["architecture"] = "monolith"

                all_data.append(merged_service)

        else:  # decoupled/functional
            for service_dir in arch_dir.iterdir():
                if service_dir.is_dir():
                    parts = service_dir.name.split("-")
                    service_name = parts[1] if len(parts) > 1 else service_dir.name

                    service_dfs = []
                    for file in service_dir.glob("*.csv"):
                        if file.name.lower() == "cpu_pod_long.csv":
                            continue
                        df = pd.read_csv(file)
                        service_dfs.append(df)

                    if not service_dfs:
                        continue

                    merged_service = service_dfs[0]
                    for df in service_dfs[1:]:
                        merged_service = pd.merge(
                            merged_service, df,
                            on="timestamp",
                            how="outer",
                            suffixes=("", "_dup")
                        )
                    merged_service = merged_service.loc[:, ~merged_service.columns.str.endswith("_dup")]

                    merged_service["service"] = service_name
                    merged_service["architecture"] = arch

                    all_data.append(merged_service)

    # ---------- locust ----------
    locust_dir = base_dir / arch / "locust"
    locust_file = locust_dir / f"{arch}_run_stats_history.csv"
    if locust_file.exists():
        df_locust = pd.read_csv(locust_file)
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
