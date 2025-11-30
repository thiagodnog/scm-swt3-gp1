import tkinter as tk
from tkinter import messagebox
import csv
from decimal import Decimal, ROUND_HALF_UP
import os
from datetime import datetime

class ExpenseCalculator:
    """
    Classe responsável por calcular as despesas consolidadas de uma viagem.
    Consolida o custo total baseado na quilometragem, pedágios e taxas de estacionamento.
    """
    
    # Taxa padrão por quilômetro (em R$)
    DEFAULT_KM_RATE = 0.50
    
    def __init__(self, km_rate=None):
        """
        Inicializa o calculador de despesas.
        
        Args:
            km_rate (float): Taxa de reembolso por km (padrão: R$ 0.50/km)
        """
        self.km_rate = km_rate if km_rate is not None else self.DEFAULT_KM_RATE
    
    def calculate_km_expense(self, distance):
        """
        Calcula a despesa baseada na quilometragem.
        
        Args:
            distance (float): Distância em km
            
        Returns:
            float: Despesa de quilometragem em R$
        """
        if distance < 0:
            raise ValueError("Distância não pode ser negativa")
        # Use Decimal for deterministic monetary rounding (ROUND_HALF_UP)
        d_distance = Decimal(str(distance))
        d_rate = Decimal(str(self.km_rate))
        km_cost = (d_distance * d_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return float(km_cost)
    
    def calculate_total_expense(self, distance, tolls=0, parking=0):
        """
        Calcula a despesa total consolidada.
        
        Args:
            distance (float): Distância em km
            tolls (float): Valor de pedágios em R$
            parking (float): Valor de estacionamento em R$
            
        Returns:
            dict: Dicionário com detalhamento das despesas
                {
                    'distance_km': float,
                    'km_expense': float,
                    'tolls': float,
                    'parking': float,
                    'total': float
                }
        """
        try:
            tolls = float(tolls) if tolls else 0
            parking = float(parking) if parking else 0
            distance = float(distance)
            
            if distance < 0:
                raise ValueError("Distância não pode ser negativa")
            if tolls < 0:
                raise ValueError("Pedágio não pode ser negativo")
            if parking < 0:
                raise ValueError("Estacionamento não pode ser negativo")
            
            km_expense = self.calculate_km_expense(distance)
            # Use Decimal for rounding monetary values to avoid floating point
            d_distance = Decimal(str(distance))
            d_tolls = Decimal(str(tolls)) if str(tolls) != "" else Decimal('0')
            d_parking = Decimal(str(parking)) if str(parking) != "" else Decimal('0')

            km_expense = Decimal(str(self.calculate_km_expense(float(d_distance))))

            d_tolls = d_tolls.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            d_parking = d_parking.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            total = (km_expense + d_tolls + d_parking).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            return {
                'distance_km': float(d_distance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'km_expense': float(km_expense),
                'tolls': float(d_tolls),
                'parking': float(d_parking),
                'total': float(total)
            }
            
            return {
                'distance_km': round(distance, 2),
                'km_expense': km_expense,
                'tolls': round(tolls, 2),
                'parking': round(parking, 2),
                'total': total
            }
        except ValueError as e:
            raise ValueError(f"Erro no cálculo de despesas: {str(e)}")
    
    def get_expense_summary(self, distance, tolls=0, parking=0):
        """
        Retorna um resumo formatado das despesas.
        
        Args:
            distance (float): Distância em km
            tolls (float): Valor de pedágios em R$
            parking (float): Valor de estacionamento em R$
            
        Returns:
            str: String formatada com resumo das despesas
        """
        expense = self.calculate_total_expense(distance, tolls, parking)
        summary = (
            f"=== RESUMO DE DESPESAS ===\n"
            f"Distância: {expense['distance_km']:.2f} km\n"
            f"Despesa km: R$ {expense['km_expense']:.2f}\n"
            f"Pedágios: R$ {expense['tolls']:.2f}\n"
            f"Estacionamento: R$ {expense['parking']:.2f}\n"
            f"─────────────────────────\n"
            f"TOTAL: R$ {expense['total']:.2f}"
        )
        return summary
try:
    import requests
except ImportError:
    requests = None

try:
    from dotenv import load_dotenv
except ImportError:
    # fallback no-op if python-dotenv is not installed
    def load_dotenv(*args, **kwargs):
        return None


class MileageTracker:
    def __init__(self, root):
        # Criacao da janela
        self.root = root
        root.title("Mileage tracker")
        root.geometry("600x480")
        
        # Inicializa o calculador de despesas com taxa padrão de R$ 0.50/km
        self.expense_calculator = ExpenseCalculator(km_rate=0.50)

        # Configuração da API do Google Maps
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
        if not self.api_key:
            # Não é erro fatal: o sistema continua usando apenas o hodômetro
            print(
                "Aviso: GOOGLE_MAPS_API_KEY não definida. "
                "Distâncias serão calculadas apenas pelo hodômetro."
            )

        # Se requests não estiver disponível, avisamos — o método que usa a API irá
        # lançar um RuntimeError caso alguém tente usar a integração.
        if requests is None:
            print(
                "Aviso: pacote 'requests' não encontrado. "
                "A integração com Google Maps ficará indisponível."
            )

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
        
        # Área para visualizar resumo de despesas
        tk.Label(frame, text="Resumo de Despesas:", font=("Arial", 9, "bold")).grid(row=8, column=0, sticky='w', pady=(10,0))
        self.expense_text = tk.Text(frame, width=80, height=5)
        self.expense_text.grid(row=9, column=0, columnspan=2, pady=2)
        self.expense_text.config(state='disabled')  # Somente leitura

        # área para visualizar últimos registros
        tk.Label(frame, text="Últimos registros:", font=("Arial", 9, "bold")).grid(row=10, column=0, sticky='w', pady=(10,0))
        self.listbox = tk.Listbox(frame, width=80, height=6)
        self.listbox.grid(row=11, column=0, columnspan=2, pady=2)

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
        except TypeError:
            # requests is None or not callable
            raise RuntimeError(
                "A biblioteca 'requests' não está disponível. Instale-a com: pip install requests"
            )
        except Exception as e:
            # requests may raise RequestException, handle below
            raise
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
        # Calcula as despesas usando ExpenseCalculator
        try:
            expense_details = self.expense_calculator.calculate_total_expense(
                distance, tolls_f, parking_f
            )
            expense_summary = self.expense_calculator.get_expense_summary(
                distance, tolls_f, parking_f
            )
            # Exibe o resumo de despesas na UI
            self.expense_text.config(state='normal')
            self.expense_text.delete(1.0, tk.END)
            self.expense_text.insert(1.0, expense_summary)
            self.expense_text.config(state='disabled')
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        new_row = [
            origin,
            dest,
            f"{start_f:.1f}",
            f"{end_f:.1f}",
            f"{distance:.1f}",
            f"{tolls_f:.2f}",
            f"{parking_f:.2f}",
            f"{expense_details['km_expense']:.2f}",
            f"{expense_details['total']:.2f}",
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
                    "km_expense",
                    "total_expense",
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
    
    def display_expense_summary(self, summary: str):
        """
        Exibe o resumo de despesas na área de texto.
        """
        self.expense_text.config(state='normal')
        self.expense_text.delete(1.0, tk.END)
        self.expense_text.insert(1.0, summary)
        self.expense_text.config(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = MileageTracker(root)
    root.mainloop()
