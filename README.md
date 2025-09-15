# ServiceWeaver Online Boutique – Experimentos de Escalabilidade

Este repositório contém a configuração e os resultados experimentais dos testes realizados com a aplicação **Online Boutique** utilizando [ServiceWeaver](https://serviceweaver.dev/), Kubernetes, Prometheus e Locust.

## 📌 Objetivos do Experimento
- Comparar três estratégias de deploy: **Monólito**, **Desacoplado (Microserviços)** e **Agrupamento Funcional (Híbrido)**.
- Medir diferenças de **latência**, **throughput** e **comportamento de escalonamento** (via HPA).
- Entender os trade-offs entre **simplicidade, modularidade e desempenho**.

## ⚙️ Ambiente
- **Cluster:** Minikube em VM Ubuntu Server (VirtualBox)  
- **Monitoramento:** Prometheus + kube-state-metrics  
- **Geração de carga:** Locust (modo headless)  
- **Escalonamento:** Horizontal Pod Autoscaler (HPA) configurado com:
  - `requests.cpu: 100m`
  - `limits.cpu: 1`
  - `averageUtilization: 60%`

O acesso aos serviços foi feito via **NodePort** ou `minikube tunnel`.

## 📂 Deployments Testados
1. **Monólito**  
   Todos os serviços em um único grupo de deployment.

2. **Desacoplado (Microserviços)**  
   Cada serviço em seu próprio pod, com escalonamento independente.

3. **Agrupamento Funcional (Híbrido)**  
   Serviços agrupados por fluxo de negócio:
   - `edge`: frontend
   - `cart`: serviço de carrinho + cache
   - `ordering`: checkout, pagamento, envio, e-mail, câmbio
   - `catalog`: catálogo de produtos, recomendação, anúncios

Cada estratégia utilizou seu próprio `config.yaml` gerado com o ServiceWeaver.

## 🚀 Teste de Carga
A carga foi aplicada com o Locust em modo headless.  
Exemplo de execução para o deploy **funcional**:

```bash
locust -f ./load-testing/locustfile.py \
  --host http://192.168.56.101:12345 \
  --headless \
  -u 200 \
  -r 20 \
  -t 15m \
  --csv results/functional/locust/functional_run \
  BoutiqueUser
```

* `-u 200` → 200 usuários concorrentes
* `-r 20` → 20 novos usuários por segundo
* `-t 15m` → duração de 15 minutos
* `--csv` → exporta métricas em formato estruturado

Comandos semelhantes foram executados para os deploys **monólito** e **desacoplado**, com resultados armazenados em `results/<deploy>/`.

## 📊 Métricas Coletadas

* **Latência** (média, P95, P99)
* **Throughput** (req/s)
* **Uso de CPU** (por pod e agregado)
* **Escalonamento do HPA** (máximo, atual e desejado de réplicas)

As métricas foram extraídas do Prometheus via scripts customizados para `.csv` e depois visualizadas em gráficos.

## Referências

- GoogleCloudPlatform. *microservices-demo*. Disponível em: [GitHub](https://github.com/GoogleCloudPlatform/microservices-demo)  
- Mendonça Filho, R. C.; Mendonça, N. C. *Impacto de Desempenho da Granularidade de Microsserviços: Uma Avaliação com o Service Weaver*. **SBRC 2024**, Niterói/RJ. DOI: [10.5753/sbrc.2024.1453](https://doi.org/10.5753/sbrc.2024.1453)  

---

## Autores

- João Henrique Simões Ramalho  
- Lorenna Victoria Marinho Lucena  
- Pedro René de Lucena Serey  
- Vandressa Galdino Soares  
- Wendell Rafael Oliveira Nascimento  

---
