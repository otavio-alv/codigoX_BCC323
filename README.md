# CódigoX

Plataforma gamificada para o ensino de programação e uso do computador para estudantes do ensino fundamental!

Projeto prático da disciplina **BCC323 – Programação Web**

## Sobre o projeto

O CódigoX é uma aplicação web em que os alunos aprendem os primeiros passos no mundo digital por meio de uma trilha de desafios, com pontuação e medalhas. O conteúdo é baseado na cartilha *Jornada Código X: Primeiros Passos no Digital*, do Código X, e cobre desde ligar o computador até o uso de e-mail, ferramentas do Google, atalhos de teclado e componentes do computador.

As mentoras gerenciam turmas, acompanham o progresso das alunas e avaliam candidaturas.

## Funcionalidades

- Cadastro e login com perfis de aluno, mentor e administrador
- Trilha com 13 desafios e barra de progresso
- Simuladores interativos: atalhos de teclado e componentes do computador
- Pontuação e medalhas
- Formulário de candidatura
- Painel da mentora: turmas, progresso dos alunos, avaliação de candidaturas e ajuste de pontos

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Django | Back-end, rotas, autenticação e templates |
| Tailwind CSS | Estilização e design system |
| SQLite | Banco de dados |

## Páginas e rotas

### Públicas

| Rota | Página |
|---|---|
| `/` | Início |
| `/sobre/` | Sobre o projeto |
| `/como-funciona/` | Como funciona a trilha |
| `/contato/` | Contato |
| `/candidatura/` | Formulário de candidatura |
| `/login/` | Login |
| `/cadastro/` | Cadastro |

### Aluna

| Rota | Página |
|---|---|
| `/trilha/` | Trilha com progresso |
| `/desafios/<id>/` | Desafio |
| `/simuladores/atalhos/` | Simulador de atalhos de teclado |
| `/simuladores/componentes/` | Simulador de componentes do computador |
| `/perfil/` | Perfil, pontos e medalhas |

### Mentora

| Rota | Página |
|---|---|
| `/painel/` | Visão geral |
| `/painel/turmas/` | Lista de turmas |
| `/painel/turmas/nova/` | Criar turma |
| `/painel/turmas/<id>/` | Detalhes da turma e progresso das alunas |
| `/painel/alunas/<id>/` | Perfil da aluna e ajuste de pontos |
| `/painel/candidaturas/` | Lista de candidaturas |
| `/painel/candidaturas/<id>/` | Avaliar candidatura |

### Administração

| Rota | Página |
|---|---|
| `/admin/` | Painel administrativo do Django |


## Equipe

* Ana Paula Tadim
* Ana Clara Pereira
* Beatriz Coelho
* Heitor Augusto
* Michelle de Oliveira
* Otávio Alves
