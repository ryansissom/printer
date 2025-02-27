import tkinter as tk
from tkinter import ttk, messagebox
import requests
from label_generator import (create_1x2_product_label, create_2x4_shelf_label, create_1x3_product_label, generate_codes)
import pandas as pd
import os
import sys
import zebra
import subprocess
from test import align_test_1x2, align_test_1x3, align_test_2x4


# Handle paths dynamically based on how the script is run
if hasattr(sys, '_MEIPASS'):  # When running as .exe
    base_path = sys._MEIPASS  # Temporary folder
else:  # When running as a normal Python script
    base_path = os.path.abspath(".")

# Full path to the data file
data_file = os.path.join(base_path, "data.csv")

# Load the CSV file
df = pd.read_csv(data_file)
products_ids = sorted(df['Part ID'].dropna().astype(int).unique().tolist())
branches = df['Store Name'].dropna().unique().tolist()


def get_printers():
    """Get a list of all printers available on the system using lpstat."""
    try:
        result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, check=True)
        printers = []
        for line in result.stdout.splitlines():
            if line.startswith('printer'):
                printer_name = line.split()[1]
                printers.append(printer_name)
        return printers
    except subprocess.CalledProcessError as e:
        print(f"Failed to get printers: {e}")
        return []


 
def align_test(printer_name):
    zpl_content = """
    ^XA
    ^PW406
    ^LL203
    ^FO0,0^GFA,10353,10353,51,,::::gU0180C60307C01F81806I03FE0C06,gU0180C6030FF07FC180E0E03FF0E0607,gU0180C6031830E0E1C0C0E03038E0607,gU0180C6031818C070C0C0B03018F06058,gU0180C60330198030C181B03018B860D8,gU0180C60318018018E1819830189860CC,gU01FFC6031F01801861811830388C608C,gU01FFC6030FF180186303183FF08C618C,gU0180C6030079801873030C3FF0866186,gU0180C603001980303307FC30388763FE,gU0180C603301980303607FC30188363FE,gU0180C6073018C1F01E0606301881E303,gU0180C70E1838E1E01E0C06301881E603,gU0180C3FC1FF07FE01C0C07301880E6038,gU0180C0F807E01F300C1803301C80EC018,hN01,,::::::::::::::::M0MF0FF00787LF8,:::M0FK0F0F0F87878J078,M0FK0F0F0F87878J078gS01E20FE1E0C061E04600F0400CF01F84F8,M0FK0F0F0F87878J078gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:M0F0IF0F00FF878787FF878gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::M0F0IF0F0FF0780787FF878gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::::::M0FK0F0FF007878J078gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::M0MF0F0F8787LF8gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::V0JF8hG01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::P0F00F00FK07FF87F8gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::Q0F00LF80787IF8gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::O0FF00F0FI07F87FF8gV01E30FE1E0C0E1F0C601F0600CF01FCCF8,::::N0FF0F00LF807F87878gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::M0FFI0FFN07878078gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::U0FI07FF8787878gS01E30FE1E0C0E1F0C601F0600CF01FCCF8,:::M0MFI0FF8I0787F8gT01E30FE1E0C0E1F0C601F0600CF01FCCF8,M0MFI0FF8I0787F8gT01E20FE1E0C061E04600F0400CF01F84F8,M0MFI0FF8I0787F8,:M0FK0FI0FF8078I07F8,:::M0F0IF0FI0F8M07F8,:::M0F0IF0F0KF87F8787F8hL0C0E1FC3C,M0F0IF0F0KF87F8787F8hL0C1100C46,M0F0IF0F0KF87F8787F8hK03C21808C2,M0F0IF0F0KF87F8787F8hL0C208188,M0F0IF0F00F07FF87878078hL0C20830BC,M0F0IF0F00F07FF87878078hL0C20830C6,M0F0IF0F00F07FF87878078hL0C2082082,M0F0IF0F00F07FF87878078hL0C2086082,M0FK0F00IF878787878hM0C2184082,M0FK0F00IF878787878hM0C31040C6,M0FK0F00IF878787878hM0C0E0C038,M0FK0F00IF878787878,M0MFI0F8007F87F8,:::,::::i02CQ0FE0FES0FE0101,hV018062C0183E1F8030C30C1007C1CM0C3018307,hV0180E2C018631I030C18C180C6223F71FB8C1018307,hV0780E2C078413I0F0C08C180824I3I9IC1008605,hV0181624018412I030C0CC180824131898C4C300C6098,hV01836I018033E0030C0CC1I06413109884FE00C6088,hV01866I01806318030C0CFEI0C412109084C1004C188,hV01846I01808018030C0CC01E10412109084C1806C1FC,hV018FFI0183I08030C08CI060412109084C18068104,hV01806I01860218030C18CI0C0432109084C18038306,hV01806I01840310030C30CI080622109084C10038206,hV01806I0187F1E0030FE0CI0FE1C2109084FE0030602,,:::::hV0FFJ0F0604FFC078L01FC2J0C,hV0C184030C6040C0086L01862J0C,hV0C08402046040C01821F318818221F0FC38,hV0C08406066040C018331318818223119C44,hV0C18404006040C00C021939818622190C86,hV0FF0404006040C00780192901FC20190C82,hV0C18404006040CI0E1F9A9018221F904FE,hV0C084F4006040CI03319AD0183231B048,hV0C08406062040C0103218A7018322190C8,hV0C084020420C0C0183218E6018322190CC6,hV0C0C4030C3080C0086338C6018223399C44,hV0C0C400F00F00C007C1IC601FC21CCF438,,::::::::::::::::::::::::::::::::::::::::::::^FS^XZ
    """
    try:
        z = zebra.Zebra()
        printers = z.getqueues()
        if not printers:
            print("No Zebra printers found.")
            return
        
        if printer_name not in printers:
            print(f"Printer {printer_name} not found.")
            return
        
        # Set the specified printer
        z.setqueue(printer_name)
        
        # Send the ZPL content to the printer
        z.output(zpl_content)
        print(f"ZPL sent to printer: {printer_name}")
    except Exception as e:
        print(f"Failed to send to printer: {e}")
        
# Send ZPL Content via CUPS to Print
def send_zpl_to_printer(zpl_content, printer_name):
    """Send ZPL content to the specified Zebra printer."""
    try:
        z = zebra.Zebra()
        printers = z.getqueues()
        if not printers:
            print("No Zebra printers found.")
            return
        
        if printer_name not in printers:
            print(f"Printer {printer_name} not found.")
            return
        
        # Set the specified printer
        z.setqueue(printer_name)
        
        # Send the ZPL content to the printer
        z.output(zpl_content)
        print(f"ZPL sent to printer: {printer_name}")
    except Exception as e:
        print(f"Failed to send to printer: {e}")
        
# Send ZPL Content via CUPS to Print
def send_zpl_to_printer(zpl_content, printer_name):
    """Send ZPL content to the specified Zebra printer."""
    try:
        z = zebra.Zebra()
        printers = z.getqueues()
        if printer_name not in printers:
            print(f"Printer {printer_name} not found.")
            return
        # Set the specified printer
        z.setqueue(printer_name)
        # Send the ZPL content to the printer
        z.output(zpl_content)
        print(f"ZPL sent to printer: {printer_name}")
    except Exception as e:
        print(f"Failed to send to printer: {e}")

def convert_to_zpl(png_file):
    """Send the PNG to the Labelary API and save the ZPL output."""
    url = "http://api.labelary.com/v1/graphics"
    try:
        with open(png_file, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            zpl_content = response.text
            print(f"ZPL Content:\n{zpl_content}")  # Print the ZPL content for debugging
            return zpl_content
        else:
            print("Error:", response.status_code, response.text)
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def align():
    """Align the printer based on the selected label type."""
    selected_label = label_var.get()
    if selected_label == "1x2":
        align_test_1x2()
    elif selected_label == "1x3":
        align_test_1x3()
    elif selected_label == "2x4":
        align_test_2x4()
    else:
        print("No label type selected.")

def generate_labels():
    """Generate labels dynamically with a button click."""
    # Get user input
    po_number = po_entry.get()  # Unused for now
    product_number = product_combo.get()
    manufacturer_number = manufacturer_entry.get()
    bin_location = bin_combo.get()
    description = description_entry.get()
    manufacturer = provider_entry.get()
    num_copies = int(copies_combo.get())  # Get the number of copies

    label_file = None  # Initialize to handle cleanup properly
    zpl_content = None

    try:
        # Determine selected label type
        selected_label = label_var.get()
        if selected_label == "1x2":
            label_file = create_1x2_product_label(
                qr_data=manufacturer_number,
                barcode_data=product_number,
                description=description,
                bin_location=manufacturer_number,
                product_code=product_number,
                title=manufacturer
            )
        elif selected_label == "1x3":
            label_file = create_1x3_product_label(
                qr_data=manufacturer_number,
                barcode_data=product_number,
                description=description,
                bin_location=manufacturer_number,
                product_code=product_number,
                title=manufacturer
            )
        elif selected_label == "2x4":
            label_file = create_2x4_shelf_label(
                bin_location=bin_location,
                title="EquipmentShare"
            )
        else:
            print("No label type selected.")
            return

        print(f"Label saved to temporary file: {label_file}")

        # Convert the generated file to ZPL
        zpl_content = convert_to_zpl(label_file)

        # Send the ZPL to the selected printer
        selected_printer = printer_combo.get()
        if selected_printer and zpl_content:
            for _ in range(num_copies):
                send_zpl_to_printer(zpl_content, selected_printer)
            print(zpl_content)
            print(selected_printer)
        else:
            print("No printer selected or ZPL content is empty.")
    finally:
        # Cleanup temporary files
        try:
            if label_file and os.path.exists(label_file):
                os.remove(label_file)
            print("Temporary files cleaned up.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def filter_autocomplete(event):
    """Filter the dropdown options and keep the dropdown open."""
    typed_text = product_combo.get()  # Get the current input
    if typed_text == "":
        # Show all options if the input is empty
        product_combo['values'] = products_ids
    else:
        # Filter options that start with the typed text
        filtered = [item for item in products_ids if str(item).startswith(typed_text)]
        product_combo['values'] = filtered

def populate_fields():
    """Populate Manufacturer part number, Description, and Provider based on Product Number."""
    selected_product = product_combo.get()
    if selected_product:
        try:
            # Filter the dataframe for the selected product
            product_data = df[df['Part ID'] == int(selected_product)]

            if not product_data.empty:
                # Extract Manufacturer Number, Description, and Provider
                manufacturer_number = product_data['Part Number'].values[0] if 'Part Number' in product_data else ""
                description = product_data['Description'].values[0] if 'Description' in product_data else ""
                provider = product_data['Provider'].values[0] if 'Provider' in product_data else ""

                # Populate the Manufacturer field
                manufacturer_entry.delete(0, tk.END)
                manufacturer_entry.insert(0, manufacturer_number if pd.notna(manufacturer_number) else "")

                # Populate the Description field
                description_entry.delete(0, tk.END)
                description_entry.insert(0, description if pd.notna(description) else "")

                # Populate the Provider field
                provider_entry.delete(0, tk.END)
                provider_entry.insert(0, provider if pd.notna(provider) else "")
            else:
                # Clear fields if no matching product is found
                manufacturer_entry.delete(0, tk.END)
                description_entry.delete(0, tk.END)
                provider_entry.delete(0, tk.END)
        except ValueError:
            print("Invalid product ID format.")
    else:
        # Clear fields if the product combo is empty
        manufacturer_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        provider_entry.delete(0, tk.END)

def filter_bin_locations(event):
    """Filter bin locations based on user input."""
    typed_text = bin_combo.get()  # Get the current input
    selected_branch = branch_combo.get()

    if selected_branch:
        # Filter bins for the selected branch
        branch_bins = df[df['Store Name'] == selected_branch]['Bin Location'].dropna().unique().tolist()
    else:
        branch_bins = []  # Default to an empty list if no branch is selected

    if typed_text == "":
        # Show all bins if input is empty
        bin_combo['values'] = branch_bins
    else:
        # Filter options based on typed text
        filtered_bins = [bin for bin in branch_bins if bin.lower().startswith(typed_text.lower())]
        bin_combo['values'] = filtered_bins

def update_bin_locations(event):
    """Update Bin Location dropdown based on selected Branch Location."""
    selected_branch = branch_combo.get()
    if selected_branch:
        # Filter the dataframe for the selected branch
        branch_data = df[df['Store Name'] == selected_branch]

        if not branch_data.empty:
            # Get unique bin locations for the branch
            bin_locations = branch_data['Bin Location'].dropna().unique().tolist()
            bin_combo['values'] = sorted(bin_locations)  # Update dropdown
            if bin_locations:
                bin_combo.set(bin_locations[0])  # Set the first value as default
        else:
            bin_combo['values'] = []  # Clear dropdown if no bins found
            bin_combo.set("")  # Clear the current selection

LARGE_FONT = ("Helvetica", 12)  # Adjust size as needed
# Initialize Tkinter
root = tk.Tk()
root.title("Label Generator")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.5)  # 50% of screen width
window_height = int(screen_height * 0.5)  # 50% of screen height
root.geometry(f"{window_width}x{window_height}")
# Create a Canvas and a Scrollbar
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

# Configure Canvas and Scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create a window within the Canvas to hold the scrollable frame
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def on_frame_configure(event):
    """Adjust the scroll region to include the entire scrollable frame."""
    canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the frame resize event to adjust the canvas scroll region
scrollable_frame.bind("<Configure>", on_frame_configure)

# Create Left and Right Frames
left_frame = tk.Frame(scrollable_frame, width=400)
left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

right_frame = tk.Frame(scrollable_frame, width=400)
right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

third_frame = tk.Frame(scrollable_frame, width=400)
third_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Left Frame Content
branch_label = tk.Label(left_frame, text="Select Branch:", font=LARGE_FONT)
branch_label.pack(pady=10, anchor="w")
branch_combo = ttk.Combobox(left_frame, values=branches, state="readonly", width=30, font=LARGE_FONT)
branch_combo.pack(pady=10, ipady=5)
branch_combo.current(0)
branch_combo.bind("<<ComboboxSelected>>", update_bin_locations)

product_label = tk.Label(left_frame, text="Product Number:", font=LARGE_FONT)
product_label.pack(pady=10, anchor="w")
product_combo = ttk.Combobox(left_frame, values=products_ids, state="normal", width=28, font=LARGE_FONT)
product_combo.pack(pady=10, ipady=5)
product_combo.focus()
product_combo.bind("<KeyRelease>", filter_autocomplete)

bin_label = tk.Label(left_frame, text="Bin Location:", font=LARGE_FONT)
bin_label.pack(pady=10, anchor="w")
bin_combo = ttk.Combobox(left_frame, state="normal", width=30, font=LARGE_FONT)
bin_combo.pack(pady=10, ipady=5)
bin_combo.set("")
bin_combo.bind("<KeyRelease>", filter_bin_locations)

po_label = tk.Label(left_frame, text="PO Number:", font=LARGE_FONT)
po_label.pack(pady=10, anchor="w")
po_entry = tk.Entry(left_frame, width=30, font=LARGE_FONT)
po_entry.pack(pady=10, ipady=5)

populate_button = tk.Button(left_frame, text="Auto-Fill Fields", command=populate_fields, font=LARGE_FONT)
populate_button.pack(pady=10)

align_button = tk.Button(left_frame, text="Align Printer", command=lambda: align_test(printer_combo.get()), font=LARGE_FONT)
align_button.pack(pady=10)

# Right Frame Content
provider_label = tk.Label(right_frame, text="Provider:", font=LARGE_FONT)
provider_label.pack(pady=10, anchor="w")
provider_entry = tk.Entry(right_frame, width=30, font=LARGE_FONT)
provider_entry.pack(pady=10, ipady=5)

manufacturer_label = tk.Label(right_frame, text="Manufacturer Number:", font=LARGE_FONT)
manufacturer_label.pack(pady=10, anchor="w")
manufacturer_entry = tk.Entry(right_frame, width=30, font=LARGE_FONT)
manufacturer_entry.pack(pady=10, ipady=5)

description_label = tk.Label(right_frame, text="Description:", font=LARGE_FONT)
description_label.pack(pady=10, anchor="w")
description_entry = tk.Entry(right_frame, width=50, font=LARGE_FONT)
description_entry.pack(pady=10, ipady=5)

tk.Label(third_frame, text="Select Printer:", font=LARGE_FONT).pack(pady=10, anchor="w")
printers = get_printers()
printer_combo = ttk.Combobox(third_frame, values=printers, state="readonly", width=40, font=LARGE_FONT)  # Increased width
printer_combo.pack(pady=10, ipady=5)
if printers:
    printer_combo.current(0)

label_var = tk.StringVar(value="None")
tk.Label(third_frame, text="Select Label Type:", font=LARGE_FONT).pack(anchor="w")
tk.Radiobutton(third_frame, text="Product Label 1x2", variable=label_var, value="1x2", font=LARGE_FONT).pack(anchor="w", padx=20)
tk.Radiobutton(third_frame, text="Product Label 1x3", variable=label_var, value="1x3", font=LARGE_FONT).pack(anchor="w", padx=20)
tk.Radiobutton(third_frame, text="Shelf Label 2x4", variable=label_var, value="2x4", font=LARGE_FONT).pack(anchor="w", padx=20)

# Add a label for the number of copies
copies_label = tk.Label(third_frame, text="Number of Copies:", font=LARGE_FONT)
copies_label.pack(anchor="w", padx=10, pady=10)
copies_combo = ttk.Combobox(third_frame, values=list(range(1, 11)), state="readonly", width=5, font=LARGE_FONT)
copies_combo.pack(anchor="w", padx=10, pady=10)
copies_combo.current(0)

generate_button = tk.Button(third_frame, text="Generate and Print Label", command=generate_labels, font=LARGE_FONT)
generate_button.pack(pady=20)

root.mainloop()

