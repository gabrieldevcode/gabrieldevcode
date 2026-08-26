<div align="center">

<img src="./assets/hero.svg" width="100%" alt="Gabriel — Engenharia Eletrônica e de Computação / UFRJ"/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=17&pause=1200&color=2DD4BF&center=true&vCenter=true&width=760&lines=firmware+em+ESP32-S3+e+sistemas+embarcados;agentes+de+IA+e+servidores+MCP+em+produ%C3%A7%C3%A3o;automa%C3%A7%C3%A3o+de+processos+que+ningu%C3%A9m+queria+fazer+na+m%C3%A3o;pesquisa+aplicada+em+ACV%2C+energia+e+dado+confi%C3%A1vel" alt="stack"/>

<br/>

<a href="https://www.linkedin.com/in/SEU-LINKEDIN"><img src="https://img.shields.io/badge/LinkedIn-0B1119?style=for-the-badge&logo=linkedin&logoColor=2DD4BF&labelColor=070B10"/></a>
<a href="mailto:gabriel.robalo@outlook.com.br"><img src="https://img.shields.io/badge/Email-0B1119?style=for-the-badge&logo=maildotru&logoColor=F5A524&labelColor=070B10"/></a>
<a href="https://lattes.cnpq.br/6770070890433954"><img src="https://img.shields.io/badge/Lattes-0B1119?style=for-the-badge&logo=googlescholar&logoColor=38BDF8&labelColor=070B10"/></a>
<img src="https://komarev.com/ghpvc/?username=gabrieldevcode&style=for-the-badge&color=2DD4BF&label=VISITS&labelColor=070B10"/>

</div>

---

<table>
<tr>
<td width="62%" valign="top">

```console
gabriel@poli-ufrj:~$ whoami --verbose

  NOME .......... Gabriel
  BASE .......... Rio de Janeiro, BR
  CURSO ......... Eng. Eletrônica e de Computação — UFRJ / Poli
  DESDE ......... 2025
  PESQUISA ...... Iniciação Científica — IA, IoT, Engenharia de Software, Hardware e TinyML
  FOCO .......... embarcados · agentes de IA · automação · dado confiável

gabriel@poli-ufrj:~$ cat manifesto.txt

  Não gosto de projeto que fica bonito no slide e morre no protoboard.
  Construo a coisa inteira: firmware, backend, agente, e o processo
  chato que faz aquilo virar rotina de alguém.

gabriel@poli-ufrj:~$ uptime
  building since 2025 · 0 dias sem começar projeto novo ▊
```

</td>
<td width="38%" valign="top" align="center">

<img src="./assets/scan.svg" width="100%" alt="identity scan"/>

</td>
</tr>
</table>

---

## `~/stack`

<div align="center">

<img src="https://skillicons.dev/icons?i=python,c,cpp,js,ts,react,nodejs,arduino,raspberrypi,linux,git,github,docker,firebase,supabase,figma&theme=dark&perline=8"/>

</div>

```text
EMBARCADOS   ESP32-S3 · RP2040 · Arduino · ESP-IDF · SPI/I²C · ST7789 · NFC/RFID
LINGUAGENS   Python · C · C++ · JavaScript/TypeScript
IA           Claude Code · MCP (FastMCP) · subagents · RAG · TinyML (pesquisa)
AUTOMAÇÃO    pywinauto · pyautogui · APIs bancárias · scraping · pipelines Excel
APP/BACKEND  React Native · Expo · Supabase
FERRAMENTAL  Linux · FreeBSD · Make · RCS/Git · openLCA IPC
```

---

## `~/projects --status=active`

<table>
<tr><td width="34%">

### `SENTINELA Offshore`
**Wearable ocupacional + gêmeo digital**

ESP32-S3 acoplado ao EPI com sensores de temperatura, ruído, postura e zona/GPS.
Registro assinado no dispositivo, cadeia de custódia e trilha para o eSocial S-2240.
Hardware, firmware e regulatório (NR-37, PGR, LGPD) desenhados juntos.

`ESP32-S3` `sensores` `blockchain` `3D print`

</td><td width="33%">

### `acv-mcp`
**Servidor MCP para openLCA**

Um MCP que recebe "faça a ACV de uma garrafa PET" e constrói o inventário inteiro
dentro do software: busca materiais, casa com a base de dados, monta o product
system e valida. Arquitetura FastMCP, um mini-servidor por fase da ISO 14044.

`Python` `FastMCP` `openLCA IPC` `ISO 14044`

</td><td width="33%">

### `Blip`
**Gadget de mesa ESP32 + display**

Monolito impresso em 3D com tela de 2.8" mostrando consumo de contexto em tempo
real, mais um modo mascote. Firmware, daemon local e industrial design próprios.

`ESP32 CYD` `LVGL` `firmware` `produto`

</td></tr>
<tr><td>

### `Rally`
**App da comunidade de futevôlei**

Agendamento de sessões, ranking por comunidade, confirmação cruzada de partidas
e sistema Rei/Pato. Conceito validado com pesquisa n=65, PRD e 9 specs antes da
primeira linha de código.

`React Native` `Expo` `Firebase` `spec-driven`

</td><td>

### `Automação fiscal`
**Robôs para escritório de contabilidade**

Scripts que leem planilha e preenchem declarações da Receita (IR, DIMOB) e
emitem boletos via API bancária em lote. Automação de app Delphi legado com
pywinauto, tratamento de popup e detecção por imagem.

[`automacao_IR`](https://github.com/gabrieldevcode/automacao_IR) · [`verifica_coordenadas`](https://github.com/gabrieldevcode/verifica_coordenadas)

</td><td>

### `Drone / Lab`
**Eletrônica de bancada**

Controlador de voo próprio em ESP32, bancada maker completa, orquestrador de
quarto com CYD + tags NFC, e um display IPS com carinha animada que reage ao que
acontece na tela do PC.

`flight control` `NFC` `ST7789` `3D print`

</td></tr>
</table>

---

## `~/research`

```text
[ ativo   ] Iniciação Científica — orquestração em lote de Avaliação de Ciclo de
            Vida no openLCA via Python. Orientação: Prof. Rodrigo (UFRJ).

[ ativo   ] Frente de P&D em resfriamento de data centers no Brasil — controle
            que escolhe dinamicamente a estratégia (ar externo, circuito fechado,
            evaporativo) minimizando água + energia, com ACV como função de custo.

[ leitura ] Revisão sistemática em TinyML / ML embarcado: quantização, pruning e
            inferência em microcontrolador (Scopus + Web of Science).

[ base    ] Robótica competitiva — FLL (Technozacca) e F1 in Schools (Cariotoca).
```

---

## `~/arcade` — os commits viram jogo

> A navinha abaixo é gerada todo dia a partir do meu gráfico de contribuições real:
> cada célula é arrancada da grade, vira invasor e é abatida em ondas.

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/gabrieldevcode/gabrieldevcode/output/commit-invaders-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/gabrieldevcode/gabrieldevcode/output/commit-invaders.svg">
  <img alt="Commit Invaders" src="https://raw.githubusercontent.com/gabrieldevcode/gabrieldevcode/output/commit-invaders.svg" width="100%">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/gabrieldevcode/gabrieldevcode/output/snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/gabrieldevcode/gabrieldevcode/output/snake-light.svg">
  <img alt="Snake" src="https://raw.githubusercontent.com/gabrieldevcode/gabrieldevcode/output/snake-dark.svg" width="100%">
</picture>

<img src="./profile-3d-contrib/profile-night-view.svg" width="100%" alt="contribuições em 3D"/>

</div>

---

## `~/telemetry`

<div align="center">

<img height="165" src="https://github-readme-stats.vercel.app/api?username=gabrieldevcode&show_icons=true&hide_border=true&bg_color=00000000&title_color=2DD4BF&text_color=D6E2EC&icon_color=F5A524&rank_icon=github&include_all_commits=true"/>
<img height="165" src="https://github-readme-stats.vercel.app/api/top-langs/?username=gabrieldevcode&layout=compact&langs_count=8&hide_border=true&bg_color=00000000&title_color=2DD4BF&text_color=D6E2EC"/>

<img height="165" src="https://streak-stats.demolab.com?user=gabrieldevcode&hide_border=true&background=00000000&stroke=1E2E3A&ring=2DD4BF&fire=F5A524&currStreakLabel=2DD4BF&sideLabels=D6E2EC&currStreakNum=D6E2EC&sideNums=D6E2EC&dates=4C5C6B"/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=gabrieldevcode&bg_color=00000000&color=2DD4BF&line=2DD4BF&point=F5A524&area=true&area_color=0B1119&hide_border=true&custom_title=commit%20rate" width="100%"/>

<img src="https://github-profile-trophy.vercel.app/?username=gabrieldevcode&theme=darkhub&no-frame=true&no-bg=true&column=7&margin-w=6"/>

</div>

---

## `~/now`

```text
[####################----] SENTINELA — definindo MVP de sensores e firmware
[################--------] acv-mcp   — fases 3 e 4 da ISO 14044 + relatório
[############------------] Blip      — firmware e industrial design
[########----------------] C++       — projeto de estudo com spec-driven dev
```

<div align="center">
<br/>

**Aberto a estágio, pesquisa e colaboração** — embarcados, IA aplicada e automação.

<sub><code>if (problema.chato && problema.repetitivo) return automatizar(problema);</code></sub>

</div>
