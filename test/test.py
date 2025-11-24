import unittest
import tkinter as tk
from app.app import  MileageTracker

class Test1(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.app = MileageTracker(self.root)

    def tearDown(self):
        self.root.destroy()
    

    def test_window_opens(self):

        print(self.app.root.title())
        self.assertEqual(self.app.root.title(), "Mileage tracker")

if __name__ == "__main__":
    unittest.main()