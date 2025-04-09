# image-recognition
Este repositório contém diversas ferramentas relativas ao pipeline de Coleta e Limpeza de dados para Datasets, Treinamento e Avaliação de Modelos de Detecção de Objetos em Imagens baseados em YOLO.

## DataScrapper
- Coletar imagens da Web baseando-se em strings de busca.
- Algoritmos para gerar strings de busca que combinem mais de uma classe, com a possibilidade de adição de contexto.

## AutoAnotador
- Realizar a auto-anotação de imagens, podendo-se definir o modelo utilizado pelos pesos, anotar uma classe específica e desenhar as bounding boxes para análise visual.

## Avaliador
- Implementação de um avaliador de "Assertividade" -- em imagens que contém ao menos uma instância de uma classe, verifica se há ao menos uma instância daquela classe predita.
