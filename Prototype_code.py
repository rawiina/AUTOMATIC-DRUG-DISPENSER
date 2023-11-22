import tkinter as tk
from tkinter import messagebox
import time
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import RPi.GPIO as GPIO
import time
import qrcode

# Define medicine costs
medicine_costs = {
    "Balamritam": 10.00,
    "Asava and Arishta": 20.00,
    "Medicine3": 30.00,
    "Medicine4": 40.00,
    # Add more medicines and their costs here
}

# GPIO setup
M1_PIN = 11
M2_PIN = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(M1_PIN, GPIO.OUT)
GPIO.setup(M2_PIN, GPIO.OUT)
mot_p1 = GPIO.PWM(M1_PIN, 50)
mot_p2 = GPIO.PWM(M2_PIN, 50)


num = 1
num1 = 1

medication_dict = {}

cap = cv2.VideoCapture(0)

while True:
    ret, img = cap.read()
    decoded_objects = decode(img)

    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        obj_type = obj.type
        a = data

        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            cv2.polylines(img, [hull], True, (0, 255, 0), 2)

        cv2.putText(img, data, (obj.rect.left, obj.rect.top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imwrite('/home/pi/images/' + str(num) + '.jpg', img)
        print('Capture ' + str(num) + ' Successful')
        num = num + 1

    cv2.imshow("QR Code Detection", img)

    if num == 2:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print(str(a))
decode_data = str(a)

medication_entries = decode_data.split('\n')
cap.release()
cv2.destroyAllWindows()

for entry in medication_entries:
    parts = entry.split('-')
    if len(parts) == 2:
        medication_name = parts[0].strip()
        dosage_part = parts[1].strip()

        if dosage_part.startswith("Dosage:"):
            dosage = dosage_part.replace("Dosage:", "").strip()

           
            medication_dict[medication_name] = {"dosage": dosage, "quantity": 0, "cost": medicine_costs.get(medication_name, 0)}


unavailable_medicines = [medicine_name for medicine_name in medication_dict if medicine_name not in medicine_costs]

def delete_medication():
    selected_medication = medication_listbox.get(tk.ACTIVE)
   
    if selected_medication:
        if selected_medication in medication_dict:
            del medication_dict[selected_medication]
            # Remove the medication from the Listbox as well
            medication_listbox.delete(tk.ACTIVE)
            calculate_total_cost()
            messagebox.showinfo("Info", f"{selected_medication} deleted from the dictionary.")
        else:
            messagebox.showerror("Error", f"{selected_medication} not found in the dictionary.")


def increment_quantity(medication_name):
    if medication_name in medication_dict:
        medication_dict[medication_name]["quantity"] += 1
        update_quantity_label(medication_name)


def decrement_quantity(medication_name):
    if medication_name in medication_dict and medication_dict[medication_name]["quantity"] > 0:
        medication_dict[medication_name]["quantity"] -= 1
        update_quantity_label(medication_name)


def update_quantity_label(medication_name):
    quantity_label = medication_dict[medication_name]["quantity_label"]
    quantity = medication_dict[medication_name]["quantity"]
    cost = medication_dict[medication_name]["cost"]
    quantity_label.config(text=f"Quantity: {quantity} - Cost: {quantity * cost}")
    calculate_total_cost()


def calculate_total_cost():
    total_cost = sum(medication_dict[medication_name]["quantity"] * medication_dict[medication_name]["cost"]
                     for medication_name in medication_dict)
    total_cost_label.config(text=f"Total Cost: {total_cost:.2f}")
    return total_cost

# Tkinter GUI window
root = tk.Tk()
root.title("Automatic Ayush Drug Dispenser")
root.geometry("800x600")

bill_frame = tk.Frame(root)
bill_frame.pack(pady=20)


medication_listbox = tk.Listbox(bill_frame, width=30, height=10)
medication_listbox.pack(side="left", padx=20)

button_frame = tk.Frame(bill_frame)
button_frame.pack(side="left", padx=20)

medication_label = tk.Label(bill_frame, text="Medication List")
medication_label.pack(side="top")


for medication_name in medication_dict:
    frame = tk.Frame(button_frame)
    frame.pack()

    label = tk.Label(frame, text=medication_name, width=15)
    label.pack(side="left")

    increment_button = tk.Button(frame, text="+", command=lambda name=medication_name: increment_quantity(name))
    increment_button.pack(side="left")

    decrement_button = tk.Button(frame, text="-", command=lambda name=medication_name: decrement_quantity(name))
    decrement_button.pack(side="left")

    quantity_label = tk.Label(frame, text=f"Quantity: {medication_dict[medication_name]['quantity']} - Cost: {0.00}")
    quantity_label.pack(side="left")


    medication_dict[medication_name]["quantity_label"] = quantity_label

  
    if medication_name in unavailable_medicines:
        medication_listbox.insert(tk.END, medication_name)
        medication_listbox.itemconfig(tk.END, {'fg': 'red'})
    else:
        medication_listbox.insert(tk.END, medication_name)
        medication_listbox.itemconfig(tk.END, {'fg': 'green'})

delete_button = tk.Button(root, text="Delete Medication", command=delete_medication)
delete_button.pack(pady=10)


total_cost_label = tk.Label(root, text="Total Cost: 0.00")
total_cost_label.pack()

def close_gui():
    upi_payment_link = f"UPI_LINK"

    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_payment_link)
    qr.make(fit=True)

   
    img = qr.make_image(fill_color="black", back_color="white")
    qr_photo = ImageTk.PhotoImage(img)

    qr_label.config(image=qr_photo)
    qr_label.photo = qr_photo

proceed_button=tk.Button(root,text='Proceed',command=close_gui)
proceed_button.pack()
qr_label=tk.Label(root)
qr_label.pack()


root.mainloop()



medicine_names = list(medication_dict.keys())

print(medicine_names)

time.sleep(15)
for name in medicine_names:
    if name.lower() == 'balamritam':
        while num1 < 4:
            mot_p1.start(2.5)
            mot_p1.ChangeDutyCycle(7.5)
            print('360 degree')
            time.sleep(1)
            num1 = num1 + 1
        num1 = 1
    elif name.lower() == 'asava and arishta':
        while num1 < 5:
            mot_p2.start(2.5)
            mot_p2.ChangeDutyCycle(7.5)
            print('360 degree')
            time.sleep(1)
            num1 = num1 + 1
    else:
        print('not available')

GPIO.cleanup()
