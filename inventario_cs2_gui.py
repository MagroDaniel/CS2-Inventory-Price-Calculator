import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
import csv
import time
import os
import sys

# ── Paleta ──────────────────────────────────────────────────────────────────
BG        = "#0f1117"
BG2       = "#1a1d27"
BG3       = "#22263a"
ACCENT    = "#f0a500"
ACCENT2   = "#e06c00"
TEXT      = "#e8e8f0"
TEXT2     = "#8a8aaa"
GREEN     = "#4caf80"
RED       = "#e05050"
BORDER    = "#2e3250"
FONT      = ("Segoe UI", 10)
FONT_B    = ("Segoe UI", 10, "bold")
FONT_H    = ("Segoe UI", 14, "bold")
FONT_BIG  = ("Segoe UI", 22, "bold")

CURRENCY_OPTIONS = {"BRL (R$)": (7, "R$"), "USD ($)": (1, "$"), "EUR (€)": (3, "€")}

# ── App principal ────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CS2 Inventory Exporter")
        self.geometry("900x680")
        self.minsize(820, 600)
        self.configure(bg=BG)
        self.resizable(True, True)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._items: list[dict] = []
        self._running = False

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header
        hdr = tk.Frame(self, bg=BG2, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="CS2  INVENTORY  EXPORTER",
                 font=("Segoe UI", 16, "bold"), bg=BG2, fg=ACCENT).pack()
        tk.Label(hdr, text="extrai seu inventário da Steam com cotações em tempo real",
                 font=("Segoe UI", 9), bg=BG2, fg=TEXT2).pack()

        # ── Inputs
        inp = tk.Frame(self, bg=BG, padx=24, pady=16)
        inp.pack(fill="x")

        tk.Label(inp, text="Steam ID64", font=FONT_B, bg=BG, fg=TEXT2).grid(row=0, column=0, sticky="w")
        tk.Label(inp, text="  (encontre em steamid.io)", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT2).grid(row=0, column=1, sticky="w")

        self.var_id = tk.StringVar()
        entry = tk.Entry(inp, textvariable=self.var_id, font=("Segoe UI", 11),
                         bg=BG3, fg=TEXT, insertbackground=ACCENT,
                         relief="flat", bd=0, highlightthickness=1,
                         highlightbackground=BORDER, highlightcolor=ACCENT, width=36)
        entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0), ipady=7)

        tk.Label(inp, text="  Moeda", font=FONT_B, bg=BG, fg=TEXT2).grid(
            row=1, column=2, sticky="w", padx=(16, 0))
        self.var_currency = tk.StringVar(value="BRL (R$)")
        cb = ttk.Combobox(inp, textvariable=self.var_currency,
                          values=list(CURRENCY_OPTIONS.keys()),
                          state="readonly", width=12, font=FONT)
        cb.grid(row=1, column=3, padx=(4, 16), pady=(4, 0))

        self.btn_fetch = tk.Button(
            inp, text="▶  Buscar inventário", font=FONT_B,
            bg=ACCENT, fg="#000", activebackground=ACCENT2, activeforeground="#000",
            relief="flat", bd=0, padx=18, pady=7, cursor="hand2",
            command=self._start_fetch)
        self.btn_fetch.grid(row=1, column=4, pady=(4, 0))
        inp.columnconfigure(0, weight=1)

        # ── Status bar
        self.var_status = tk.StringVar(value="Pronto. Informe seu Steam ID64 e clique em Buscar.")
        sb = tk.Label(self, textvariable=self.var_status, font=("Segoe UI", 9),
                      bg=BG2, fg=TEXT2, anchor="w", padx=16, pady=6)
        sb.pack(fill="x")

        # ── Progress
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Gold.Horizontal.TProgressbar",
                        troughcolor=BG3, background=ACCENT,
                        bordercolor=BG3, lightcolor=ACCENT, darkcolor=ACCENT)
        self.progress = ttk.Progressbar(self, style="Gold.Horizontal.TProgressbar",
                                        mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=0)

        # ── Metrics
        mf = tk.Frame(self, bg=BG, padx=24, pady=10)
        mf.pack(fill="x")
        self.metric_total   = self._metric_card(mf, "ITENS ÚNICOS",     "—", 0)
        self.metric_priced  = self._metric_card(mf, "COM COTAÇÃO",      "—", 1)
        self.metric_value   = self._metric_card(mf, "VALOR ESTIMADO",   "—", 2)
        for i in range(3):
            mf.columnconfigure(i, weight=1)

        # ── Table
        tf = tk.Frame(self, bg=BG, padx=24)
        tf.pack(fill="both", expand=True)

        cols = ("#", "Nome", "market_hash_name", "Qtd", "Preço unit.", "Total", "Negociável")
        widths = (36, 240, 240, 44, 90, 90, 80)

        style.configure("Dark.Treeview",
                        background=BG2, foreground=TEXT, fieldbackground=BG2,
                        rowheight=26, bordercolor=BORDER, font=FONT)
        style.configure("Dark.Treeview.Heading",
                        background=BG3, foreground=ACCENT, font=FONT_B, relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", BG3)],
                  foreground=[("selected", ACCENT)])

        scroll_y = tk.Scrollbar(tf, orient="vertical")
        scroll_x = tk.Scrollbar(tf, orient="horizontal")

        self.tree = ttk.Treeview(tf, columns=cols, show="headings",
                                 style="Dark.Treeview",
                                 yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set)

        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            anchor = "e" if col in ("Qtd", "Preço unit.", "Total") else "w"
            self.tree.column(col, width=w, anchor=anchor, stretch=(col == "Nome"))

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # ── Bottom buttons
        bf = tk.Frame(self, bg=BG, padx=24, pady=12)
        bf.pack(fill="x")
        self.btn_csv = tk.Button(
            bf, text="💾  Salvar CSV", font=FONT_B,
            bg=BG3, fg=TEXT, activebackground=BORDER, relief="flat",
            bd=0, padx=16, pady=6, cursor="hand2",
            state="disabled", command=self._save_csv)
        self.btn_csv.pack(side="left", padx=(0, 8))

        self.btn_cancel = tk.Button(
            bf, text="✕  Cancelar", font=FONT_B,
            bg=BG3, fg=RED, activebackground=BORDER, relief="flat",
            bd=0, padx=16, pady=6, cursor="hand2",
            state="disabled", command=self._cancel)
        self.btn_cancel.pack(side="left")

        tk.Label(bf, text="dica: inventário deve estar público na Steam",
                 font=("Segoe UI", 8), bg=BG, fg=TEXT2).pack(side="right")

    def _metric_card(self, parent, label, value, col):
        card = tk.Frame(parent, bg=BG2, padx=16, pady=10)
        card.grid(row=0, column=col, sticky="ew", padx=(0, 8) if col < 2 else 0)
        tk.Label(card, text=label, font=("Segoe UI", 8, "bold"),
                 bg=BG2, fg=TEXT2).pack(anchor="w")
        var = tk.StringVar(value=value)
        tk.Label(card, textvariable=var, font=("Segoe UI", 20, "bold"),
                 bg=BG2, fg=ACCENT).pack(anchor="w")
        return var

    # ── Fetch logic ───────────────────────────────────────────────────────────
    def _start_fetch(self):
        steam_id = self.var_id.get().strip()
        if not steam_id or len(steam_id) < 15:
            messagebox.showerror("Erro", "Informe um Steam ID64 válido (17 dígitos).\nEncontre em steamid.io")
            return
        self._running = True
        self._items = []
        self.btn_fetch.config(state="disabled")
        self.btn_cancel.config(state="normal")
        self.btn_csv.config(state="disabled")
        self.progress["value"] = 0
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.metric_total.set("…")
        self.metric_priced.set("…")
        self.metric_value.set("…")
        threading.Thread(target=self._fetch_thread, args=(steam_id,), daemon=True).start()

    def _cancel(self):
        self._running = False
        self._set_status("Cancelado pelo usuário.")
        self.btn_fetch.config(state="normal")
        self.btn_cancel.config(state="disabled")

    def _fetch_thread(self, steam_id: str):
        currency_name = self.var_currency.get()
        currency_id, symbol = CURRENCY_OPTIONS[currency_name]

        try:
            self._set_status("Buscando inventário na Steam…")
            items = self._get_inventory(steam_id)
            if not self._running:
                return
            total = len(items)
            self.metric_total.set(str(total))
            self._set_status(f"{total} itens encontrados. Buscando cotações…")

            for i, item in enumerate(items):
                if not self._running:
                    return
                price = self._get_price(item["market_name"], currency_id)
                item["price"] = price
                item["total"] = round(price * item["qty"], 2) if price is not None else None
                self._add_row(i + 1, item, symbol)
                pct = int((i + 1) / total * 100)
                self.progress["value"] = pct
                self._set_status(
                    f"[{i+1}/{total}]  {item['name'][:60]}  —  "
                    f"{symbol} {price:.2f}" if price else f"[{i+1}/{total}]  {item['name'][:60]}  —  sem cotação"
                )
                if i < total - 1:
                    time.sleep(1.5)

            self._items = items
            self._update_metrics(symbol)
            self._set_status(f"Concluído! {total} itens carregados.")
            self.btn_csv.config(state="normal")

        except Exception as e:
            self._set_status(f"Erro: {e}")
            messagebox.showerror("Erro", str(e))
        finally:
            self.btn_fetch.config(state="normal")
            self.btn_cancel.config(state="disabled")

    def _get_inventory(self, steam_id: str) -> list[dict]:
        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=portuguese&count=2000"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            raise Exception(f"Erro HTTP {r.status_code}. Inventário pode estar privado.")
        data = r.json()
        if not data.get("success"):
            raise Exception("Inventário privado ou Steam ID inválido.")

        descriptions = {
            f"{d['classid']}_{d['instanceid']}": d
            for d in data.get("descriptions", [])
        }
        count_map: dict[str, int] = {}
        for asset in data.get("assets", []):
            key = f"{asset['classid']}_{asset['instanceid']}"
            count_map[key] = count_map.get(key, 0) + int(asset.get("amount", 1))

        items, seen = [], set()
        for key, desc in descriptions.items():
            if key in seen:
                continue
            seen.add(key)
            items.append({
                "name":        desc.get("name", ""),
                "market_name": desc.get("market_hash_name", ""),
                "qty":         count_map.get(key, 1),
                "tradable":    desc.get("tradable", 0) == 1,
            })
        return items

    def _get_price(self, market_hash_name: str, currency: int):
        url = (
            "https://steamcommunity.com/market/priceoverview/"
            f"?appid=730&currency={currency}"
            f"&market_hash_name={requests.utils.quote(market_hash_name)}"
        )
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 429:
                time.sleep(60)
                r = requests.get(url, timeout=15)
            if r.status_code != 200:
                return None
            data = r.json()
            raw = data.get("lowest_price") or data.get("median_price")
            if not raw:
                return None
            cleaned = "".join(c for c in raw if c.isdigit() or c in ".,")
            cleaned = cleaned.replace(",", ".")
            parts = cleaned.split(".")
            if len(parts) > 2:
                cleaned = "".join(parts[:-1]) + "." + parts[-1]
            return float(cleaned)
        except Exception:
            return None

    def _add_row(self, idx: int, item: dict, symbol: str):
        price_str = f"{symbol} {item['price']:.2f}" if item["price"] is not None else "—"
        total_str = f"{symbol} {item['total']:.2f}" if item["total"] is not None else "—"
        tag = "even" if idx % 2 == 0 else "odd"
        self.tree.insert("", "end", values=(
            idx,
            item["name"],
            item["market_name"],
            item["qty"],
            price_str,
            total_str,
            "Sim" if item["tradable"] else "Não"
        ), tags=(tag,))
        self.tree.tag_configure("even", background=BG2)
        self.tree.tag_configure("odd",  background=BG)
        self.tree.yview_moveto(1)

    def _update_metrics(self, symbol: str):
        with_price = [x for x in self._items if x["price"] is not None]
        total_val  = sum(x["total"] for x in with_price)
        self.metric_priced.set(str(len(with_price)))
        self.metric_value.set(f"{symbol} {total_val:,.2f}")

    def _set_status(self, msg: str):
        self.var_status.set(msg)

    # ── Save CSV ──────────────────────────────────────────────────────────────
    def _save_csv(self):
        if not self._items:
            return
        _, symbol = CURRENCY_OPTIONS[self.var_currency.get()]
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="inventario_cs2.csv"
        )
        if not path:
            return
        items_sorted = sorted(self._items, key=lambda x: x["total"] or 0, reverse=True)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["#", "Nome", "market_hash_name", "Quantidade",
                        f"Preço unitário ({symbol})", f"Total ({symbol})", "Negociável"])
            for i, item in enumerate(items_sorted, 1):
                w.writerow([
                    i,
                    item["name"],
                    item["market_name"],
                    item["qty"],
                    f"{item['price']:.2f}".replace(".", ",") if item["price"] is not None else "",
                    f"{item['total']:.2f}".replace(".", ",") if item["total"] is not None else "",
                    "Sim" if item["tradable"] else "Não",
                ])
        messagebox.showinfo("Salvo!", f"CSV salvo em:\n{path}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
