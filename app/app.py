import tkinter as tk
from tkinter import messagebox
import csv
import os
import requests
from dotenv import load_dotenv


class MileageTracker:
    def __init__(self, root):
        # Criacao da janela
        self.root = root
        root.title("Mileage tracker")
        root.geometry("500x380")

        # Configuração da API do Google Maps
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
        if not self.api_key:
            # Não é erro fatal: o sistema continua usando apenas o hodômetro
            print(
                "Aviso: GOOGLE_MAPS_API_KEY não definida. "
                "Distâncias serão calculadas apenas pelo hodômetro."
            )

        # Campos do formulário
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Endereço Origem:").grid(row=0, column=0, sticky='w')
        self.entry_origin = tk.Entry(frame, width=50)
        self.entry_origin.grid(row=0, column=1, pady=2)

        tk.Label(frame, text="Endereço Destino:").grid(row=1, column=0, sticky='w')
        self.entry_dest = tk.Entry(frame, width=50)
        self.entry_dest.grid(row=1, column=1, pady=2)

        tk.Label(frame, text="Hodômetro Inicial:").grid(row=2, column=0, sticky='w')
        self.entry_start = tk.Entry(frame, width=20)
        self.entry_start.grid(row=2, column=1, sticky='w', pady=2)

        tk.Label(frame, text="Hodômetro Final:").grid(row=3, column=0, sticky='w')
        self.entry_end = tk.Entry(frame, width=20)
        self.entry_end.grid(row=3, column=1, sticky='w', pady=2)

        tk.Label(frame, text="Pedágios (R$):").grid(row=4, column=0, sticky='w')
        self.entry_tolls = tk.Entry(frame, width=20)
        self.entry_tolls.grid(row=4, column=1, sticky='w', pady=2)

        tk.Label(frame, text="Estacionamento (R$):").grid(row=5, column=0, sticky='w')
        self.entry_parking = tk.Entry(frame, width=20)
        self.entry_parking.grid(row=5, column=1, sticky='w', pady=2)

        self.btn_save = tk.Button(frame, text="Salvar Viagem", command=self.save_trip)
        self.btn_save.grid(row=6, column=0, columnspan=2, pady=10)

        self.status = tk.Label(frame, text="", fg="green")
        self.status.grid(row=7, column=0, columnspan=2)

        # área para visualizar últimos registros
        tk.Label(frame, text="Últimos registros:").grid(
            row=8, column=0, sticky='w', pady=(10, 0)
        )
        self.listbox = tk.Listbox(frame, width=80, height=6)
        self.listbox.grid(row=9, column=0, columnspan=2, pady=2)

        # garante pasta de dados e carrega existentes
        self.data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.csv_path = os.path.join(self.data_dir, "trips.csv")
        self.load_existing()

    def load_existing(self):
        self.listbox.delete(0, tk.END)
        if os.path.exists(self.csv_path):
            with open(self.csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.listbox.insert(tk.END, " | ".join(row))

    def get_distance_from_gmaps(self, origin: str, dest: str) -> float:
        """
        Obtém a distância em km usando a Google Maps Routes API
        (directions/v2:computeRoutes).

        Lança RuntimeError com mensagem clara em caso de problema.
        """
        if not self.api_key:
            raise RuntimeError(
                "Chave da API do Google Maps não configurada. "
                "Defina a variável de ambiente GOOGLE_MAPS_API_KEY."
            )

        url = "https://routes.googleapis.com/directions/v2:computeRoutes"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            # Campo obrigatório: pelo menos um campo em routes.*
            "X-Goog-FieldMask": "routes.distanceMeters",
        }

        body = {
            "origin": {
                "address": origin
            },
            "destination": {
                "address": dest
            },
            "travelMode": "DRIVE",
            # Mantemos o exemplo simples, compatível com a documentação.
        }

        try:
            resp = requests.post(url, headers=headers, json=body, timeout=10)
        except requests.RequestException as e:
            # Erros de rede (sem internet, DNS, timeout, etc.)
            raise RuntimeError(f"Falha de comunicação com a API do Google Maps: {e}")

        # Se vier 4xx/5xx, queremos ver a mensagem do Google, não só "400 Bad Request"
        if not resp.ok:
            try:
                err_json = resp.json()
            except ValueError:
                err_json = resp.text
            raise RuntimeError(
                f"Erro HTTP {resp.status_code} da API do Google Maps.\n"
                f"Resposta: {err_json}"
            )

        data = resp.json()
        routes = data.get("routes")
        if not routes:
            raise RuntimeError(
                "A API do Google Maps não retornou nenhuma rota para os endereços informados."
            )

        distance_meters = routes[0].get("distanceMeters")
        if distance_meters is None:
            raise RuntimeError(
                "A API do Google Maps não retornou o campo distanceMeters."
            )

        distance_km = float(distance_meters) / 1000.0
        if distance_km <= 0:
            raise RuntimeError(
                "Distância retornada pela API do Google Maps é inválida (<= 0)."
            )

        return distance_km

    def save_trip(self):
        origin = self.entry_origin.get().strip()
        dest = self.entry_dest.get().strip()
        start = self.entry_start.get().strip()
        end = self.entry_end.get().strip()
        tolls = self.entry_tolls.get().strip() or "0"
        parking = self.entry_parking.get().strip() or "0"

        # validações simples
        if not origin or not dest or not start or not end:
            messagebox.showerror("Erro", "Preencha origem, destino e hodômetros.")
            return
        try:
            start_f = float(start.replace(',', '.'))
            end_f = float(end.replace(',', '.'))
            tolls_f = float(tolls.replace(',', '.'))
            parking_f = float(parking.replace(',', '.'))
        except ValueError:
            messagebox.showerror("Erro", "Hodômetros e valores devem ser numéricos.")
            return

        # distância padrão calculada pelo hodômetro
        distance = end_f - start_f
        if distance < 0:
            messagebox.showerror("Erro", "Hodômetro final menor que inicial.")
            return

        distance_source = "hodometro"

        # tenta calcular distância via Google Maps (Compute Routes)
        try:
            distance_gmaps = self.get_distance_from_gmaps(origin, dest)
            if distance_gmaps > 0:
                distance = distance_gmaps
                distance_source = "gmaps"
        except RuntimeError as e:
            # Feedback claro, mas continua usando a distância do hodômetro
            messagebox.showwarning(
                "Aviso",
                "Não foi possível calcular a distância via Google Maps. "
                "A distância desta viagem será calculada pelo hodômetro.\n\n"
                f"Detalhes: {e}"
            )

        # escreve no CSV (adiciona header se não existir)
        new_row = [
            origin,
            dest,
            f"{start_f:.1f}",
            f"{end_f:.1f}",
            f"{distance:.1f}",
            f"{tolls_f:.2f}",
            f"{parking_f:.2f}",
        ]
        write_header = not os.path.exists(self.csv_path)
        with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow([
                    "origin",
                    "destination",
                    "start_odometer",
                    "end_odometer",
                    "distance",
                    "tolls",
                    "parking",
                ])
            writer.writerow(new_row)

        # mensagem de status mostrando a origem da distância (só na UI)
        if distance_source == "gmaps":
            self.status.config(
                text="Viagem salva com sucesso (distância via Google Maps)."
            )
        else:
            self.status.config(
                text="Viagem salva com sucesso (distância via hodômetro)."
            )

        self.load_existing()
        # limpa campos
        self.entry_origin.delete(0, tk.END)
        self.entry_dest.delete(0, tk.END)
        self.entry_start.delete(0, tk.END)
        self.entry_end.delete(0, tk.END)
        self.entry_tolls.delete(0, tk.END)
        self.entry_parking.delete(0, tk.END)


if __name__ == '__main__':
    root = tk.Tk()
    app = MileageTracker(root)
    root.mainloop()
