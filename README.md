# 📌 Agenda de Tarefas com Tkinter + SQLite  

Este projeto é uma **aplicação de agenda de tarefas** com interface gráfica feita em **Tkinter** e armazenamento em **SQLite**.  
Permite cadastrar, listar, buscar, filtrar, alterar e excluir tarefas de forma simples.

---

## 🚀 Funcionalidades  

✅ **Cadastro de tarefas** com:
- Nome  
- Tipo  
- Descrição  
- Data e hora de início e fim (`DD/MM/YYYY HH:MM`)  
- Situação (**feito** ou **não feito**)  

✅ **Listagem de tarefas** em tabela com ordenação por colunas  

✅ **Filtros disponíveis**:
- Filtrar por **situação** (feito / não feito / todas)  
- Buscar por **texto no nome da tarefa** (case-insensitive)  

✅ **Alterar situação** de uma tarefa selecionada  

✅ **Excluir tarefa** (somente se estiver com situação **“não feito”**)  

✅ Banco de dados local **SQLite** (`agenda_tarefas.db`) criado automaticamente  

---

## 🛠️ Tecnologias utilizadas  

- [Python 3.x](https://www.python.org/)  
- [Tkinter](https://docs.python.org/3/library/tkinter.html) (interface gráfica)  
- [SQLite3](https://docs.python.org/3/library/sqlite3.html) (banco de dados local)  

---

## 📂 Estrutura do projeto  

```
📁 agenda-tarefas
 ┣ 📄 main.py          # Código principal da aplicação
 ┣ 📄 agenda_tarefas.db # Banco SQLite (criado após rodar o programa)
 ┗ 📄 README.md        # Documentação
```

---

## ▶️ Como rodar o projeto  

1. **Clone o repositório** ou copie os arquivos para sua máquina.  

```bash
git clone https://github.com/seuusuario/agenda-tarefas.git
cd agenda-tarefas
```

2. **Certifique-se de ter o Python instalado**:  

```bash
python --version
```

3. **Rode o programa**:  

```bash
python main.py
```

4. A janela do programa abrirá.  

---

## 💻 Uso da interface  

- **Cadastrar**: Preencha os campos e clique em **Cadastrar**  
- **Listar**: Ao abrir, todas as tarefas são listadas  
- **Filtrar por situação**: Selecione no combobox e clique em **Aplicar filtro**  
- **Buscar por nome**: Digite parte do nome e pressione **Enter** ou clique em **Buscar**  
- **Alterar situação**: Selecione uma tarefa → clique em **Alterar situação**  
- **Excluir**: Selecione uma tarefa com situação “não feito” → clique em **Excluir**  

---

## 📝 Observações  

- Datas devem ser digitadas no formato brasileiro:  
  ```
  DD/MM/YYYY HH:MM
  Ex.: 29/08/2025 14:30
  ```
- Apenas tarefas com situação **“não feito”** podem ser excluídas.  

---

⚡ Projeto simples, ideal para aprender **Tkinter + SQLite** com CRUD e interface amigável!  
