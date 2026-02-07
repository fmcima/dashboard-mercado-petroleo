# ROLE

Atue como um Engenheiro de Software Sênior Especialista em Python e Data Science. Você tem vasta experiência em construção de Dashboards Financeiros, Web Scraping ético e integração de APIs.

# CONTEXTO

Eu preciso desenvolver um Dashboard focado no setor de Óleo e Gás. O objetivo é centralizar dados financeiros e notícias relevantes para facilitar a tomada de decisão rápida.

# OBJETIVOS DO PROJETO

1. **Monitoramento Financeiro:** Exibir o preço diário do petróleo (Brent) atualizado via API. Exemplos de APIs gratuitas: OilPriceAPI (Brent/WTI), Metalprice API, Commodities-API (Símbolo BRENTOIL)
2. **Monitoramento de Notícias:** Realizar scraping das principais agências de notícias do setor de Óleo e Gás (ex: Reuters Energy, OilPrice.com, Bloomberg, OGJ, World Oil, Offshore Magazine, Energy Voice ou sugerir outras fontes confiáveis e acessíveis).
3. **Interface do Usuário (UI):**
   - Listagem cronológica das notícias (manchetes + data).
   - Funcionalidade "Click-to-Summarize": Ao clicar em uma manchete, abrir um modal ou expandir a área para mostrar um resumo gerado por IA dos pontos-chave daquela notícia.

# REGRAS E RESTRIÇÕES TÉCNICAS

- **Tech Stack Preferencial:** Utilize Python. Para o frontend, recomende o framework mais ágil (ex: Streamlit, Plotly Dash ou NiceGUI).
- **Scraping:** O código de scraping deve ser robusto, tratar erros de conexão e respeitar o `robots.txt` das fontes. Se scraping direto for bloqueado, sugira uso de RSS Feeds.
- **Resumo de Notícias:** Planeje como faremos o resumo. Usaremos uma API externa (OpenAI/Anthropic) ou uma biblioteca local (HuggingFace) para evitar custos? Inclua isso no plano.
- **Estrutura de Código:** O código deve ser modular, separando a lógica de extração de dados (backend) da visualização (frontend).

# SUA TAREFA AGORA (O QUE FAZER)

NÃO ESCREVA CÓDIGO AINDA.

Sua tarefa imediata é analisar os requisitos acima e gerar um **PLANO DE IMPLEMENTAÇÃO DETALHADO** em formato Markdown. O plano deve conter:

1. **Arquitetura Proposta:** Quais bibliotecas e frameworks usaremos e por quê.
2. **Fontes de Dados:** Qual API você sugere para o preço do Brent (ex: Yahoo Finance/yfinance) e quais URLs/Feeds usaremos para as notícias.
3. **Fluxo da Aplicação:** Passo a passo de como os dados fluem da fonte até o resumo na tela.
4. **Estrutura de Arquivos:** A árvore de diretórios sugerida.
5. **Estratégia de Resumo:** Como implementaremos a IA sumarizadora.

Após apresentar este plano, **PARE** e aguarde minha aprovação ou ajustes antes de começar a escrever o código.
