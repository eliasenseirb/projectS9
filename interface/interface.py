# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 23:49:47 2022

@author: elias
"""

from tkinter import *

main = Tk()

main.title("Code Pol'eirb")
main.geometry("720x480")
main.minsize(width=480, height=360)
main.iconbitmap("img/logo.ico")

## Partie paramètres

param = LabelFrame(main, text="Paramètres", bg='#41484c', fg='white')
param.pack(side=LEFT, fill="both", expand="yes")
 
Label(param, text="Valeur de K", bg='#41484c', fg='white').pack()
spin_K = Spinbox(param, values=(128, 256, 512, 1024, 2048))
spin_K.pack()

Label(param, text="Valeur de N", bg='#41484c', fg='white').pack()
spin_N = Spinbox(param, values=(512, 1024, 2048, 4096, 8192))
spin_N.pack()

Label(param, text="Débit symbole", bg='#41484c', fg='white').pack()
spin_debit = Spinbox(param, values=(1E4, 5E4, 1E5, 5E5, 1E6))
spin_debit.pack()

Label(param, text="Confidentialité", bg='#41484c', fg='white').pack()

def printButton():
   selected = "Confidentialité " + var_conf.get()
   label_conf.config(text = selected)

var_conf = StringVar()
var_conf.set("Faible") # init


but_conf1 = Radiobutton(param, text = "Faible", variable=var_conf, value='Faible',\
                        command=printButton, bg='#41484c', fg='white',\
                        activebackground='#41484c', activeforeground='white')
    
but_conf2 = Radiobutton(param, text = "Forte", variable=var_conf, value='Forte',\
                        command=printButton, bg='#41484c', fg='white',\
                        activebackground='#41484c', activeforeground='white')
but_conf3 = Radiobutton(param, text = "Sans sécurité", variable=var_conf, value='Sans sécurité',\
                        command=printButton, bg='#41484c', fg='white',\
                        activebackground='#41484c', activeforeground='white')
but_conf1.pack()
but_conf2.pack()
but_conf3.pack()


label_conf = Label(param, bg='#41484c', fg='white')
label_conf.pack()



## Partie figures

fig = LabelFrame(main, text="Figures", bg='#41484c', fg='white')
fig.pack(side=RIGHT, fill="both", expand="yes")

fig_bob = LabelFrame(fig, text="Courbes de Bob", bg='#41484c', fg='white')
fig_bob.pack(side=TOP, fill="both", expand="yes")


fig_eve = LabelFrame(fig, text="Courbes d'Eve", bg='#41484c', fg='white')
fig_eve.pack(side=BOTTOM, fill="both", expand="yes")


main.mainloop()