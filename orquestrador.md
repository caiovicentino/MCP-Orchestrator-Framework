**Persona:** Você é um Arquiteto de Software Sênior especializado na criação de frameworks e infraestruturas modulares e reutilizáveis, com profunda experiência em Python, integração de sistemas de IA, LLMs e práticas modernas de desenvolvimento.

**Objetivo:** Projetar e definir a estrutura de código para um **framework genérico e extensível em Python (versão 3.8 ou superior)** que permita orquestrar múltiplos "Model Context Protocols" (MCPs - veja https://github.com/modelcontextprotocol). O framework deve permitir que diferentes projetos utilizem e combinem contexto de várias fontes (representadas por implementações de MCP) antes de interagir com um Large Language Model (LLM).

**Tecnologias Definidas:**

*   **Linguagem Principal:** Python (>= 3.8, para aproveitar `typing.Protocol` e `asyncio`).
*   **Tipagem:** Uso mandatório de Type Hints do Python para clareza e robustez.
*   **Programação Assíncrona:** O design deve suportar nativamente operações assíncronas (`async`/`await`) para I/O não bloqueante ao interagir com MCPs (ex: chamadas de rede, acesso a banco de dados).
*   **Formato de Dados:** JSON será o formato padrão para serialização/deserialização de dados complexos trocados entre componentes, quando aplicável.
*   **Containerização (Para Exemplo/Distribuição):** Incluir um `Dockerfile` básico para demonstrar como empacotar o framework ou uma aplicação de exemplo que o utilize.

**Requisitos Essenciais do Framework:**

1.  **Interface MCP Padronizada (`MCP`):**
    *   Defina um `typing.Protocol` chamado `MCP` que TODA implementação de MCP *deve* seguir.
    *   A interface deve incluir métodos assíncronos essenciais: `async def get_context(self, query_data: Any) -> Any` e, opcionalmente, `async def update_context(self, response_data: Any) -> None`. Use `Any` inicialmente, mas incentive tipos mais específicos nas implementações.

2.  **Orquestrador de MCP (`McpOrchestrator`):**
    *   Crie a classe principal `McpOrchestrator`.
    *   **Inicialização:** Deve aceitar uma lista de instâncias de `MCP` e uma instância de `ContextCombinationStrategy` (veja abaixo).
    *   **Coleta de Contexto:** Implemente um método assíncrono principal (ex: `async def gather_and_combine_context(self, query_data: Any) -> Any`) que:
        *   Execute as chamadas `get_context` para os MCPs registrados **concorrentemente** usando `asyncio` (ex: `asyncio.gather`).
        *   Colete os resultados ou exceções de cada MCP. Implemente uma política de tratamento de erro configurável (ex: falhar se algum MCP falhar, continuar com os resultados parciais, logar erros).
    *   **Combinação de Contexto:** Utilize a instância de `ContextCombinationStrategy` injetada para mesclar os contextos coletados com sucesso.
    *   **Formatação Final (Opcional):** Possibilidade de adicionar um formatador configurável.
    *   **Atualização de Contexto (Opcional):** Implemente um método assíncrono (ex: `async def propagate_update(self, response_data: Any)`) que chame `update_context` nos MCPs aplicáveis, possivelmente também de forma concorrente.

3.  **Estratégias de Combinação de Contexto (`ContextCombinationStrategy`):**
    *   Defina um `typing.Protocol` ou uma classe base abstrata (`ABC`) para as estratégias de combinação, com um método como `combine(contexts: List[Any]) -> Any`.
    *   Implemente pelo menos duas estratégias *básicas* como exemplo:
        *   `SimpleConcatenationStrategy`: Concatena contextos textuais.
        *   `DictionaryMergeStrategy`: Mescla dicionários (com política clara para colisões de chave).
    *   O design deve permitir fácil adição de novas estratégias.

4.  **Configuração e Uso:**
    *   Forneça um exemplo claro em Python demonstrando:
        *   Definição de 2-3 classes `MCP` fictícias (ex: `AsyncMemoryMCP`, `AsyncVectorStoreMCP`) implementando o protocolo.
        *   Instanciação do `McpOrchestrator` com as MCPs e uma estratégia.
        *   Chamada do método `gather_and_combine_context` usando `asyncio.run()`.

**Princípios de Design a Enfatizar:**

*   **Modularidade:** Componentes claros e desacoplados.
*   **Extensibilidade:** Fácil adição de novos MCPs e Estratégias.
*   **Reusabilidade:** Agnosticismo de domínio.
*   **Configurabilidade:** Injeção de dependências (MCPs, Estratégia).
*   **Desempenho:** Uso de `asyncio` para I/O eficiente.
*   **Robustez:** Tipagem estática e tratamento de erros.
*   **Manutenibilidade:** Código limpo, documentado (`docstrings`).

**Entregáveis Esperados:**

*   Código Python definindo os `Protocol`s (`MCP`, `ContextCombinationStrategy`).
*   Implementação da classe `McpOrchestrator` com uso de `asyncio`.
*   Implementação das estratégias de combinação de exemplo.
*   Código de exemplo completo e funcional (usando `asyncio.run`).
*   Um `Dockerfile` simples para demonstrar o empacotamento.
*   Breve documentação (em `docstrings` ou comentários) explicando as escolhas de design, o fluxo assíncrono e como estender o framework.

**Considerações Adicionais (para a IA pensar):**
*   Melhores práticas para gerenciamento de erros em `asyncio.gather`.
*   Como passar configurações específicas para MCPs individuais durante a inicialização do orquestrador?
*   Como o framework poderia ser adaptado para logging e monitoramento padronizados?