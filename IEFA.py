# High-level script for running the IEFA tool
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

# Define default parameter values
def_installCost = 1000
def_marketPrice = 2.50
def_hydroPrice = 0.0981
def_seasonality = 1

# Query the user for certain inputs
def calculate():
    try:
        parkingLotSize = int(parking_lot_size_entry.get())
        rebatePercent = float(rebate_percent_entry.get())
        markup = float(markup_entry.get())
        weeks = int(weeks_entry.get())
        installCost = float(installation_cost_entry.get() or def_installCost)
        marketPrice = float(market_price_entry.get() or def_marketPrice)
        hydroPrice = float(hydro_price_entry.get() or def_hydroPrice)
        seasonality = float(seasonality_entry.get() or def_seasonality)

        # Run IEFA based on newly set inputs
        subprocess.run(["python", "CapstoneCode.py", str(parkingLotSize), str(rebatePercent), str(markup), str(weeks), str(installCost), str(marketPrice), str(hydroPrice), str(seasonality)], check=False)
        messagebox.showinfo("IEFA run complete", "Model has finished running. Go ahead and check the data file.")
        return True
    # If there was an error with specifying the inputs, generate a message box to show the error.
    except:
        messagebox.showerror("Error", "There was an error initializing the inputs. Please ensure that all specified inputs have numerical values and that all required input fields have been filled in.")

# Create the main window
root = tk.Tk()
root.title("IEFA Input Form")

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
installation_cost_entry.insert(0, def_installCost)

ttk.Label(root, text="Market price ($/hr):").grid(row=7, column=0, sticky=tk.W)
market_price_entry = ttk.Entry(root)
market_price_entry.grid(row=7, column=1)
market_price_entry.insert(0, def_marketPrice)

ttk.Label(root, text="Hydro price ($/kWh):").grid(row=8, column=0, sticky=tk.W)
hydro_price_entry = ttk.Entry(root)
hydro_price_entry.grid(row=8, column=1)
hydro_price_entry.insert(0, def_hydroPrice)

ttk.Label(root, text="Seasonality (Winter demand scaling factor):").grid(row=9, column=0, sticky=tk.W)
seasonality_entry = ttk.Entry(root)
seasonality_entry.grid(row=9, column=1)
seasonality_entry.insert(0, def_seasonality)

# Create a button to trigger the calculation
calculate_button = ttk.Button(root, text="Calculate", command=calculate)
calculate_button.grid(row=10, column=0, columnspan=2)

root.mainloop()
