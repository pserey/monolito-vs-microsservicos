# Avaliação Comparativa de Desempenho entre Monólito e Microsserviços

Este repositório contém a proposta e o planejamento de um experimento que compara o desempenho entre **arquiteturas monolíticas** e **de microsserviços** em um sistema web de e-commerce. O estudo é baseado na aplicação **[OnlineBoutique](https://github.com/GoogleCloudPlatform/microservices-demo)**, adaptada com o framework **[Service Weaver](https://serviceweaver.dev/)**, e executada em ambiente Kubernetes.

---

## Objetivo

O experimento busca avaliar, de forma empírica, como diferentes granularidades arquiteturais impactam:

- **Latência (tempo de resposta)** percebida pelo usuário  
- **Consumo de CPU** como métrica de custo computacional  
- **Escalabilidade automática** via Horizontal Pod Autoscaler (HPA)  

---

## Justificativa

Apesar da popularidade dos microsserviços, ainda não há consenso claro sobre qual abordagem é mais eficiente em termos de custo-benefício e desempenho. Muitas migrações são feitas por tendências de mercado sem avaliação quantitativa.  
Este projeto propõe uma análise **neutra e controlada**, evidenciando os contextos em que cada arquitetura pode se mostrar mais vantajosa.

---

## Escopo do Experimento

- Aplicação: **OnlineBoutique** (versão Go + Service Weaver)  
- Ambiente: **Kubernetes** em infraestrutura de nuvem privada (Oracle Cloud free-tier / OpenStack)  
- Estratégias de implantação analisadas:  
  - **Monolítica** – todos os serviços em um único contêiner  
  - **Totalmente distribuída** – cada serviço em seu próprio contêiner  
  - **Agrupamento por funcionalidade** – serviços organizados conforme domínio e acoplamento  

---

## Tecnologias Utilizadas

- **Framework:** Service Weaver  
- **Orquestração:** Kubernetes (via Minikube)  
- **Containers:** Docker  
- **Escalabilidade:** Horizontal Pod Autoscaler (HPA)  
- **Carga de testes:** [Locust.io](https://locust.io/)  
- **Monitoramento:** [Prometheus](https://prometheus.io/) + kube-state-metrics  

---

## Critérios de Comparação

- **Latência** – tempo de resposta coletado com Locust  
- **Uso de CPU** – monitorado pelo Prometheus  
- **Escalabilidade automática** – número de réplicas geradas pelo HPA  

---

## Ferramentas de Medição

- **Locust**: geração de carga e medição de latência  
- **Prometheus**: coleta periódica de métricas do cluster  
- **kube-state-metrics**: monitoramento do número de réplicas  

---

## Estrutura do Projeto

- **docs/** → Proposta detalhada e planejamento do experimento  
- **k8s/** → Manifests para deployment no Kubernetes  
- **scripts/** → Automação de testes e coleta de métricas  
- **results/** → Resultados dos experimentos (logs, gráficos, tabelas)  

---

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
