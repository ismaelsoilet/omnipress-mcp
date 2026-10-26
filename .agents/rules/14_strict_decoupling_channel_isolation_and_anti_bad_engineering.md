# Regra 14 — Padrão de Desacoplamento Estrito, Isolamento de Canais e Erradicação de Engenharia Incorreta

> **Status**: Mandatória / Normativa Canônica  
> **Escopo**: Todos os componentes de `src/` (`src/core/`, `src/engine/`, `src/adapters/`, `src/video/`), testes e agentes autônomos.  
> **Objetivo**: Garantir que o motor central permaneça 100% agnóstico, reutilizável e imutável frente à alta volatilidade e constante evolução dos canais (`channels/<slug>/`).

---

## 1. O Problema Fundamental: A "Engenharia Errada" e o Acoplamento Frágil

Canais de mídia social e documentários mudam frequentemente:
- Alteram paletas de cores, margens, avatares e tipografias.
- Criam novos formatos de slides, tabelas, mockups e narrativas.
- Atualizam tokens, credenciais e contas em redes sociais.

Quando um agente de IA ou desenvolvedor insere atalhos (*gambiarras*) no motor central para resolver uma urgência de um canal específico (ex.: verificações `if channel_slug == "x"`, caminhos hardcoded, nomes de criadores em comentários, mutação de atributos de instância para passar dados ou leitura direta de arquivos de canal no `src/`), o sistema sofre **colapso de arquitetura**: a alteração em um canal quebra outro canal ou polui o código-fonte universal.

---

## 2. Princípios Mandatórios da Regra 14

### Princípio 1: Invariância e Agnosticismo Absoluto de `src/` (Zero Hardcoded Slugs)
1. **Nenhum arquivo em `src/` pode conter slugs de canal, nomes de marcas, títulos de criadores ou caminhos absolutos para um canal específico.**
2. O código de `src/` deve funcionar de maneira idêntica se houver 1 canal ou 1.000 canais cadastrados.
3. Toda comunicação entre o motor e o canal ocorre por passagem de parâmetros estruturados (`channel_slug: str`, `channel_data: dict`, `recipe: dict`, `slide_data: dict`).

### Princípio 2: Cascata Top-Down de Parâmetros Declarativos (DRY & Cascading)
Qualquer parâmetro de layout, tipografia, contraste ou comportamento visual deve ser resolvido seguindo rigorosamente a cascata universal:
```
1. slide_data (específico do item no recipe)
   ↓
2. recipe.layout_parameters / recipe.<param> (específico do lote/postagem)
   ↓
3. channel.json -> visual_identity.presets[preset] (preset configurado no canal)
   ↓
4. channel.json -> visual_identity.layout_parameters (geometria padrão do canal)
   ↓
5. channel.json -> branding (compatibilidade legada)
   ↓
6. Engine Universals (fallbacks seguros em src/)
```
- O motor nunca deve chumbar valores mágicos em código que impeçam o canal ou a receita de controlar seu próprio resultado visual.

### Princípio 3: Imutabilidade e Execução Sem Estado (Statelessness)
1. Motores e adaptadores de publicação **NUNCA** devem armazenar dados de requisição em atributos mutáveis de instância (`self._channel_services`, `self.current_post`, `self._cached_slide`).
2. Requisições concorrentes ou consecutivas devem ser puramente funcionais e reentrantes:
   - Entrada: `platforms`, `channel_slug`, `text`, `media_urls`.
   - Saída: dicionário ou lista de resultados independentes por destino.
3. Proibido reaproveitar payloads ou heurísticas globais em despachos multi-rede (ex.: aplicar metadados do Twitter no LinkedIn).

### Princípio 4: Resolução Universal de Credenciais via `ChannelManager`
1. Proibido usar `os.getenv(...)` diretamente dentro de adaptadores para credenciais de canal.
2. Toda credencial deve ser obtida via [`ChannelManager.get_credential(key, channel_slug)`](file:///home/ismaelsoilet/omnipress-mcp/src/core/channel_manager.py), que aplica a cascata canônica da Regra 04:
   - **Nível 1**: `channels/<slug>/.env` (privacidade máxima, isolado da raiz)
   - **Nível 2**: `<SLUG>_<KEY>` (variável de processo prefixada)
   - **Nível 3**: `.env` global na raiz (fallback padrão)

### Princípio 5: Cache de Alta Performance com Validação por Assinatura de Disco
1. O acesso a configurações de canal e arquivos `.env` deve utilizar cache em memória indexado por assinatura em nanossegundos: `(st_mtime_ns, st_size)`.
2. Isso garante tempo de resposta de **0ms** em loops intensivos de publicação ou renderização, sem o risco de leituras obsoletas (*stale reads*), pois qualquer edição no disco invalida a assinatura instantaneamente.

### Princípio 6: Generalização Obrigatória de Novas Features (Anti-Bespoke)
Se um canal necessitar de um novo elemento visual (ex.: mockup de janela de terminal, caixa de citação judicial, card de estatística, carimbo pericial ou badge animado):
- **Ação Permitida**: Adicionar o novo componente visual de forma parametrizada em `src/engine/` como um novo preset ou flag genérica (`ui_mockup`, `bullet_style`, `badge_type`), documentando os parâmetros no schema e adicionando testes unitários agnósticos.
- **Ação Terminantemente Proibida**: Criar scripts paralelos que sobrescrevem bibliotecas do core ou condicionais verificando `channel_slug`.

---

## 3. Checklist de Auditoria para Agentes de IA (Portão AG11)

Antes de concluir qualquer tarefa ou realizar commit:
- [ ] O código em `src/` contém referências a nomes ou slugs de canais reais? **(Deve ser NÃO)**
- [ ] Parâmetros visuais ou de publicação estão sendo forçados com valores fixos no Python sem possibilidade de override via recipe/channel.json? **(Deve ser NÃO)**
- [ ] Adaptadores utilizam dicionários mutáveis de instância que vazam estado entre chamadas? **(Deve ser NÃO)**
- [ ] Chaves de API foram lidas via `ChannelManager.get_credential`? **(Deve ser SIM)**
- [ ] A suíte completa de testes (`uv run pytest`) foi executada e passou com 100% de sucesso? **(Deve ser SIM)**
