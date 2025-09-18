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

## 🧑‍🔬 Como Rodar os Experimentos

A seguir estão os passos para preparar o ambiente dentro da máquina virtual, criar o cluster Kubernetes com **Minikube** e executar cada experimento de deploy (monólito, desacoplado ou funcional).

### 1. Pré-requisitos

Certifique-se de que sua VM (Ubuntu Server) tenha os seguintes pacotes instalados:

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)  
- [kubectl](https://kubernetes.io/docs/tasks/tools/)  
- [Helm](https://helm.sh/docs/intro/install/)  
- [ServiceWeaver CLI](https://serviceweaver.dev/)  
- Prometheus + kube-state-metrics (monitoramento)

> 💡 Dica: o stack de monitoramento pode ser instalado via Helm chart do `kube-prometheus-stack`.

### 2. Criar o cluster Minikube

```bash
minikube start --driver=docker
```

Verifique se o cluster está ativo:

```bash
kubectl get nodes
```

### 4. Limpar recursos antigos

Antes de rodar um novo experimento, remova qualquer deploy anterior do Online Boutique (o stack de monitoramento continua ativo):

```bash
kubectl delete deploy,svc,hpa,cm,role,rolebinding -l serviceweaver/app=onlineboutique --ignore-not-found
kubectl delete rs,pod -l serviceweaver/app=onlineboutique --ignore-not-found
```

### 5. Gerar e aplicar manifests

Use o ServiceWeaver para gerar os manifests Kubernetes a partir do `config.yaml` desejado (monólito, desacoplado ou funcional):

```bash
weaver kube deploy config-functional.yaml
```

Troque `config-functional.yaml` pelo config do experimento que deseja rodar:

* `config-monolith.yaml`
* `config-decoupled.yaml`
* `config-functional.yaml`

Esse comando vai gerar um arquivo começando com `kube_` em `/tmp`. Rode o comando abaixo com ele para aplicar no seu cluster:

```bash
kubectl apply -f /tmp/kube_a349nbd.yaml
```

### 6. Acompanhar a inicialização

Verifique os recursos criados:

```bash
kubectl get deploy,svc,hpa -l serviceweaver/app=onlineboutique
```
> O nome do `svc` vai ser utilizado posteriormente para expor o serviço na rede.

E acompanhe os pods subindo:

```bash
kubectl get pods -l serviceweaver/app=onlineboutique -w
```

Depois que os pods estiverem **Running**, exponha o cluster para fora da VM com:

```bash
kubectl port-forward --address=0.0.0.0 svc/<nome-do-svc> 8888:80
```

Agora é possível acessar o serviço em `{vm-ip}:8888`, iniciar os testes de carga com o **Locust** e coletar métricas no Prometheus. 🎯

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
