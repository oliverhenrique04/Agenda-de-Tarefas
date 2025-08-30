import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# =========================
# Banco de Dados (CRUD)
# =========================
def criar_banco():
    conn = sqlite3.connect('agenda_tarefas.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        data_inicio TEXT NOT NULL,
        data_fim TEXT NOT NULL,
        tipo_tarefa TEXT NOT NULL,
        situacao TEXT NOT NULL CHECK(situacao IN ('feito', 'não feito'))
    )
    ''')
    conn.commit()
    conn.close()

def conectar():
    return sqlite3.connect('agenda_tarefas.db')

def cadastrar_tarefa(nome, descricao, data_inicio_iso, data_fim_iso, tipo_tarefa, situacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tarefas (nome, descricao, data_inicio, data_fim, tipo_tarefa, situacao)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, descricao, data_inicio_iso, data_fim_iso, tipo_tarefa, situacao))
    conn.commit()
    conn.close()

def listar_tarefas_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tarefas')
    tarefas = cursor.fetchall()
    conn.close()
    return tarefas

def listar_por_situacao_db(situacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tarefas WHERE situacao = ?', (situacao,))
    tarefas = cursor.fetchall()
    conn.close()
    return tarefas

def buscar_por_nome_db(termo):
    """Busca por nome contendo o termo (case-insensitive)."""
    conn = conectar()
    cursor = conn.cursor()
    padrao = f"%{termo}%"
    cursor.execute('SELECT * FROM tarefas WHERE nome LIKE ? COLLATE NOCASE', (padrao,))
    tarefas = cursor.fetchall()
    conn.close()
    return tarefas

def alterar_situacao_db(id_tarefa, nova_situacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE tarefas SET situacao = ? WHERE id = ?', (nova_situacao, id_tarefa))
    conn.commit()
    conn.close()

def excluir_tarefa_db(id_tarefa):
    """Exclui somente se a tarefa estiver com situacao = 'não feito'."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ? AND situacao = 'não feito'", (id_tarefa,))
    conn.commit()
    apagadas = cursor.rowcount
    conn.close()
    return apagadas > 0

# =========================
# Datas: BR <-> ISO
# =========================
def to_iso(br_date: str) -> str:
    """'DD/MM/YYYY HH:MM' -> 'YYYY-MM-DD HH:MM'"""
    return datetime.strptime(br_date.strip(), "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M")

def to_br(iso_date: str) -> str:
    """'YYYY-MM-DD HH:MM' -> 'DD/MM/YYYY HH:MM'"""
    return datetime.strptime(iso_date.strip(), "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")

def valida_data_br(texto: str) -> bool:
    try:
        datetime.strptime(texto.strip(), "%d/%m/%Y %H:%M")
        return True
    except ValueError:
        return False

SITUACOES = ['não feito', 'feito']

# =========================
# Interface Tkinter
# =========================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda de Tarefas")
        self.geometry("1100x620")
        self.minsize(980, 580)

        self._build_form()
        self._build_toolbar()
        self._build_table()
        self.carregar_todas()

    # ----- UI -----
    def _build_form(self):
        frm = ttk.LabelFrame(self, text="Nova tarefa")
        frm.pack(fill="x", padx=10, pady=10)

        # Linha 1
        ttk.Label(frm, text="Nome*").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.ent_nome = ttk.Entry(frm, width=40)
        self.ent_nome.grid(row=0, column=1, sticky="we", padx=6, pady=6)

        ttk.Label(frm, text="Tipo*").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        self.ent_tipo = ttk.Entry(frm, width=22)
        self.ent_tipo.grid(row=0, column=3, sticky="we", padx=6, pady=6)

        ttk.Label(frm, text="Situação*").grid(row=0, column=4, sticky="w", padx=6, pady=6)
        self.combo_situacao = ttk.Combobox(frm, values=SITUACOES, state="readonly", width=14)
        self.combo_situacao.set("não feito")
        self.combo_situacao.grid(row=0, column=5, sticky="we", padx=6, pady=6)

        # Linha 2
        ttk.Label(frm, text="Início* (DD/MM/YYYY HH:MM)").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.ent_inicio = ttk.Entry(frm, width=22)
        self.ent_inicio.grid(row=1, column=1, sticky="we", padx=6, pady=6)

        ttk.Label(frm, text="Fim* (DD/MM/YYYY HH:MM)").grid(row=1, column=2, sticky="w", padx=6, pady=6)
        self.ent_fim = ttk.Entry(frm, width=22)
        self.ent_fim.grid(row=1, column=3, sticky="we", padx=6, pady=6)

        # Linha 3
        ttk.Label(frm, text="Descrição").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.ent_desc = ttk.Entry(frm)
        self.ent_desc.grid(row=2, column=1, columnspan=5, sticky="we", padx=6, pady=6)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)
        frm.columnconfigure(5, weight=1)

    def _build_toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=10, pady=(0,10))

        ttk.Button(bar, text="Cadastrar", command=self.ui_cadastrar).pack(side="left", padx=4)
        ttk.Button(bar, text="Alterar situação (seleção)", command=self.ui_alterar_situacao).pack(side="left", padx=4)
        ttk.Button(bar, text="Excluir (apenas 'não feito')", command=self.ui_excluir).pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)

        ttk.Button(bar, text="Carregar todas", command=self.carregar_todas).pack(side="left", padx=4)

        ttk.Label(bar, text="Filtrar por situação: ").pack(side="left", padx=(16,4))
        self.combo_filtro = ttk.Combobox(bar, values=["todas"] + SITUACOES, state="readonly", width=12)
        self.combo_filtro.set("todas")
        self.combo_filtro.pack(side="left")
        ttk.Button(bar, text="Aplicar filtro", command=self.ui_filtrar).pack(side="left", padx=4)

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=8)

        # --- Busca por nome ---
        ttk.Label(bar, text="Buscar por nome: ").pack(side="left", padx=(8,4))
        self.ent_busca = ttk.Entry(bar, width=24)
        self.ent_busca.pack(side="left")
        self.ent_busca.bind("<Return>", lambda e: self.ui_buscar())
        ttk.Button(bar, text="Buscar", command=self.ui_buscar).pack(side="left", padx=4)
        ttk.Button(bar, text="Limpar busca", command=self.ui_limpar_busca).pack(side="left", padx=4)

        ttk.Button(bar, text="Limpar campos", command=self.ui_limpar_campos).pack(side="right", padx=4)

    def _build_table(self):
        cols = ("id", "nome", "descricao", "inicio", "fim", "tipo", "situacao")
        self.tv = ttk.Treeview(self, columns=cols, show="headings", height=14)
        self.tv.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.tv.heading("id", text="ID")
        self.tv.heading("nome", text="Nome")
        self.tv.heading("descricao", text="Descrição")
        self.tv.heading("inicio", text="Início")
        self.tv.heading("fim", text="Fim")
        self.tv.heading("tipo", text="Tipo")
        self.tv.heading("situacao", text="Situação")

        self.tv.column("id", width=60, anchor="center")
        self.tv.column("nome", width=220)
        self.tv.column("descricao", width=280)
        self.tv.column("inicio", width=150, anchor="center")
        self.tv.column("fim", width=150, anchor="center")
        self.tv.column("tipo", width=120, anchor="center")
        self.tv.column("situacao", width=100, anchor="center")

        self.tv.bind("<Double-1>", self.ui_carregar_selecao_no_form)

    # ----- Ações UI -----
    def ui_cadastrar(self):
        nome = self.ent_nome.get().strip()
        tipo = self.ent_tipo.get().strip()
        inicio_br = self.ent_inicio.get().strip()
        fim_br = self.ent_fim.get().strip()
        desc = self.ent_desc.get().strip()
        situacao = self.combo_situacao.get().strip().lower()

        if not nome or not tipo or not inicio_br or not fim_br:
            messagebox.showwarning("Campos obrigatórios", "Preencha Nome, Tipo, Início e Fim.")
            return
        if situacao not in SITUACOES:
            messagebox.showwarning("Situação inválida", "Use 'feito' ou 'não feito'.")
            return
        if not (valida_data_br(inicio_br) and valida_data_br(fim_br)):
            messagebox.showwarning("Data inválida",
                                   "Use o formato DD/MM/YYYY HH:MM (ex.: 29/08/2025 09:30).")
            return

        try:
            inicio_iso = to_iso(inicio_br)
            fim_iso = to_iso(fim_br)
        except ValueError:
            messagebox.showwarning("Data inválida",
                                   "Use o formato DD/MM/YYYY HH:MM (ex.: 29/08/2025 09:30).")
            return

        if datetime.strptime(fim_iso, "%Y-%m-%d %H:%M") < datetime.strptime(inicio_iso, "%Y-%m-%d %H:%M"):
            messagebox.showwarning("Datas inconsistentes", "Fim não pode ser anterior ao início.")
            return

        try:
            cadastrar_tarefa(nome, desc, inicio_iso, fim_iso, tipo, situacao)
            messagebox.showinfo("Sucesso", "Tarefa cadastrada!")
            self.ui_limpar_campos()
            self.carregar_todas()
        except Exception as e:
            messagebox.showerror("Erro ao cadastrar", str(e))

    def ui_alterar_situacao(self):
        item = self._item_selecionado()
        if not item:
            return
        id_tarefa = int(item["values"][0])

        nova = simpledialog.askstring(
            "Alterar situação",
            "Digite a nova situação ('feito' ou 'não feito'):",
            parent=self
        )
        if not nova:
            return
        nova = nova.strip().lower()
        if nova not in SITUACOES:
            messagebox.showwarning("Situação inválida", "Use 'feito' ou 'não feito'.")
            return

        try:
            alterar_situacao_db(id_tarefa, nova)
            messagebox.showinfo("Sucesso", "Situação atualizada!")
            self.carregar_todas()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def ui_excluir(self):
        item = self._item_selecionado()
        if not item:
            return
        id_tarefa = int(item["values"][0])
        situacao = str(item["values"][6]).lower()

        if situacao != "não feito":
            messagebox.showwarning(
                "Não permitido",
                "Só é possível excluir tarefas com situação 'não feito'."
            )
            return

        if not messagebox.askyesno("Confirmar exclusão", f"Deseja excluir a tarefa ID {id_tarefa}?"):
            return

        try:
            if excluir_tarefa_db(id_tarefa):
                messagebox.showinfo("Sucesso", "Tarefa excluída!")
                self.carregar_todas()
            else:
                messagebox.showwarning(
                    "Aviso",
                    "Não foi possível excluir. Talvez o ID não exista ou a situação não seja 'não feito'."
                )
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def ui_filtrar(self):
        valor = self.combo_filtro.get()
        if valor == "todas":
            self.carregar_todas()
        else:
            self._preencher_tabela(listar_por_situacao_db(valor))

    def ui_buscar(self):
        termo = self.ent_busca.get().strip()
        if not termo:
            # vazio -> recarrega tudo (comunica claramente)
            self.carregar_todas()
            return
        resultados = buscar_por_nome_db(termo)
        if not resultados:
            messagebox.showinfo("Sem resultados", f"Nenhuma tarefa com nome contendo: {termo}")
        self._preencher_tabela(resultados)

    def ui_limpar_busca(self):
        self.ent_busca.delete(0, tk.END)
        self.carregar_todas()

    def ui_limpar_campos(self):
        self.ent_nome.delete(0, tk.END)
        self.ent_tipo.delete(0, tk.END)
        self.ent_inicio.delete(0, tk.END)
        self.ent_fim.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.combo_situacao.set("não feito")

    def ui_carregar_selecao_no_form(self, _event=None):
        item = self._item_selecionado()
        if not item:
            return
        _, nome, desc, inicio_br, fim_br, tipo, situacao = item["values"]
        self.ent_nome.delete(0, tk.END); self.ent_nome.insert(0, nome)
        self.ent_tipo.delete(0, tk.END); self.ent_tipo.insert(0, tipo)
        self.ent_inicio.delete(0, tk.END); self.ent_inicio.insert(0, inicio_br)
        self.ent_fim.delete(0, tk.END); self.ent_fim.insert(0, fim_br)
        self.ent_desc.delete(0, tk.END); self.ent_desc.insert(0, desc)
        self.combo_situacao.set(situacao)

    # ----- Helpers -----
    def carregar_todas(self):
        self._preencher_tabela(listar_tarefas_db())

    def _preencher_tabela(self, linhas):
        # linhas: [(id, nome, desc, inicio_iso, fim_iso, tipo, situacao), ...]
        for i in self.tv.get_children():
            self.tv.delete(i)
        for row in linhas:
            r = list(row)
            r[3] = to_br(r[3])  # inicio
            r[4] = to_br(r[4])  # fim
            self.tv.insert("", "end", values=r)

    def _item_selecionado(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Seleção necessária", "Selecione uma tarefa na tabela.")
            return None
        return self.tv.item(sel[0])

# =========================
# Execução
# =========================
if __name__ == "__main__":
    criar_banco()
    app = App()
    app.mainloop()
