import unittest
import tkinter as tk
from unittest.mock import patch, MagicMock
from app.app import MileageTracker
import tempfile
import os
import csv

class Test1(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = MileageTracker(self.root)
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()
    

    def test_window_opens(self):

        # verifica se a jenela é inicializada corretamente
        self.assertEqual(self.app.root.title(), "Mileage tracker")

    def test_smoke_write_and_validate_csv(self):
        # smoke-test que escreve diretamente no CSV e valida formato e valores
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = os.path.join(tmp, "data")
            os.makedirs(data_dir, exist_ok=True)
            csv_path = os.path.join(data_dir, "trips.csv")

            header = ["origin", "destination", "start_odometer", "end_odometer", "distance", "tolls", "parking"]
            # exemplo de linha válida
            row = ["Origem A", "Destino B", "100.0", "150.0", "50.0", "2.50", "5.00"]

            # escreve arquivo
            with open(csv_path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerow(row)

            # lê e valida
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)

            # valida header
            self.assertGreaterEqual(len(rows), 2)
            self.assertEqual(rows[0], header)

            # valida a linha de dados
            data_row = rows[1]
            self.assertEqual(len(data_row), 7)
            # verifica campos numéricos podem ser convertidos e distância bate
            start = float(data_row[2].replace(',', '.'))
            end = float(data_row[3].replace(',', '.'))
            distance = float(data_row[4].replace(',', '.'))
            tolls = float(data_row[5].replace(',', '.'))
            parking = float(data_row[6].replace(',', '.'))

            self.assertAlmostEqual(end - start, distance, places=3)
            self.assertGreaterEqual(tolls, 0.0)
            self.assertGreaterEqual(parking, 0.0)


    # Teste unitário para verificar função __init__
    def test_widget_creation_and_type(self):    
    
        # Widgets de Entrada (tk.Entry)
        self.assertIsInstance(self.app.entry_origin, tk.Entry, "Campo Endereço origem não encontrado")
        self.assertIsInstance(self.app.entry_dest, tk.Entry, "Campo Endereço destino não encontrado")
        self.assertIsInstance(self.app.entry_start, tk.Entry, "Campo Hodômetro inicial não encontrado")
        self.assertIsInstance(self.app.entry_end, tk.Entry, "Campo Hodômetro final não encontrado")
        self.assertIsInstance(self.app.entry_tolls, tk.Entry, "Cmpo Pedágio não encontrado")
        self.assertIsInstance(self.app.entry_parking, tk.Entry, "Campo Estacionamento não encontrado")
        
        # Botão
        self.assertIsInstance(self.app.btn_save, tk.Button, "Botão Salvar Viagem não encontrado")
        
        # 3. Rótulo de Status
        self.assertIsInstance(self.app.status, tk.Label, "Campo status não encontrado")
        
        #Listbox de Registros
        self.assertIsInstance(self.app.listbox, tk.Listbox, "Campo ultimos registros não encontrado")
            
class TestGoogleMapsDistance(unittest.TestCase):
    def setUp(self):
        # Cria a janela raiz e a app
        self.root = tk.Tk()
        self.app = MileageTracker(self.root)
        self.root.withdraw()

        # Garante que a app tenha uma "chave" para não cair no erro de chave ausente
        self.app.api_key = "fake-api-key-for-tests"

    def tearDown(self):
        self.root.destroy()

    @patch("app.app.requests.post")
    def test_get_distance_from_gmaps_success(self, mock_post):
        """
        Caso de sucesso: a API retorna uma rota com distanceMeters
        e a função converte corretamente para km.
        """
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "routes": [{"distanceMeters": 12345}]  # 12.345 km
        }
        mock_post.return_value = mock_response

        distance = self.app.get_distance_from_gmaps("Origem X", "Destino Y")

        # 12345 m = 12.345 km
        self.assertAlmostEqual(distance, 12.345, places=3)
        mock_post.assert_called_once()  # garante que fez a chamada HTTP simulada

    def test_get_distance_from_gmaps_missing_api_key(self):
        """
        Se não houver API key configurada, deve lançar RuntimeError
        antes de tentar chamar a API.
        """
        self.app.api_key = ""  # força estado "sem chave"

        with self.assertRaises(RuntimeError) as ctx:
            self.app.get_distance_from_gmaps("Origem X", "Destino Y")

        self.assertIn("Chave da API do Google Maps não configurada", str(ctx.exception))

    @patch("app.app.requests.post")
    def test_get_distance_from_gmaps_http_error(self, mock_post):
        """
        Se a API responder com erro HTTP (ex.: 400, 500),
        a função deve lançar RuntimeError com a mensagem adequada.
        """
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Invalid request"}}
        mock_post.return_value = mock_response

        with self.assertRaises(RuntimeError) as ctx:
            self.app.get_distance_from_gmaps("Origem X", "Destino Y")

        self.assertIn("Erro HTTP 400", str(ctx.exception))
        self.assertIn("Invalid request", str(ctx.exception))

    @patch("app.app.requests.post")
    def test_get_distance_from_gmaps_no_routes(self, mock_post):
        """
        Se a API não retornar nenhuma rota, deve lançar RuntimeError
        com mensagem clara.
        """
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "routes": []  # sem rotas
        }
        mock_post.return_value = mock_response

        with self.assertRaises(RuntimeError) as ctx:
            self.app.get_distance_from_gmaps("Origem X", "Destino Y")

        self.assertIn("não retornou nenhuma rota", str(ctx.exception))



if __name__ == "__main__":
    unittest.main()