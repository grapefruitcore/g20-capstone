# High-level script for running the IEFA tool
import tkinter as tk
from tkinter import ttk
import subprocess

# Query the user for certain inputs
def calculate():
    parkingLotSize = int(parking_lot_size_entry.get())
    rebatePercent = float(rebate_percent_entry.get())
    markup = float(markup_entry.get())
    weeks = int(weeks_entry.get())
    installCost = float(installation_cost_entry.get() or 1000)
    marketPrice = float(market_price_entry.get() or 2.50)
    hydroPrice = float(hydro_price_entry.get() or 0.0981)
    seasonality = float(seasonality_entry.get() or 1)
    
    # Run IEFA based on newly set inputs
    subprocess.run(["python", "g20-capstone/CapstoneCode.py", str(parkingLotSize), str(rebatePercent), str(markup), str(weeks), str(installCost), str(marketPrice), str(hydroPrice), str(seasonality)], check=False)

# Create the main window
root = tk.Tk()
root.title("Input Form")

# Create labels and entry widgets for each input
ttk.Label(root, text="REQUIRED INPUTS:").grid(row=0, column=0, columnspan=2, sticky=tk.W)

ttk.Label(root, text="Parking lot size (total # of spots):").grid(row=1, column=0, sticky=tk.W)
parking_lot_size_entry = ttk.Entry(root)
parking_lot_size_entry.grid(row=1, column=1)

ttk.Label(root, text="Rebate percent (between 0 and 1):").grid(row=2, column=0, sticky=tk.W)
rebate_percent_entry = ttk.Entry(root)
rebate_percent_entry.grid(row=2, column=1)

ttk.Label(root, text="Markup ($/kWhr):").grid(row=3, column=0, sticky=tk.W)
markup_entry = ttk.Entry(root)
markup_entry.grid(row=3, column=1)

ttk.Label(root, text="Weeks (timespan considered):").grid(row=4, column=0, sticky=tk.W)
weeks_entry = ttk.Entry(root)
weeks_entry.grid(row=4, column=1)

ttk.Label(root, text="OPTIONAL INPUTS:").grid(row=5, column=0, columnspan=2, sticky=tk.W)

ttk.Label(root, text="Installation cost ($):").grid(row=6, column=0, sticky=tk.W)
installation_cost_entry = ttk.Entry(root)
installation_cost_entry.grid(row=6, column=1)

ttk.Label(root, text="Market price ($/kWh):").grid(row=7, column=0, sticky=tk.W)
market_price_entry = ttk.Entry(root)
market_price_entry.grid(row=7, column=1)

ttk.Label(root, text="Hydro price ($/kWh):").grid(row=8, column=0, sticky=tk.W)
hydro_price_entry = ttk.Entry(root)
hydro_price_entry.grid(row=8, column=1)

ttk.Label(root, text="Seasonality (Winter demand scaling factor):").grid(row=9, column=0, sticky=tk.W)
seasonality_entry = ttk.Entry(root)
seasonality_entry.grid(row=9, column=1)

# Create a button to trigger the calculation
calculate_button = ttk.Button(root, text="Calculate", command=calculate)
calculate_button.grid(row=10, column=0, columnspan=2)

root.mainloop()
