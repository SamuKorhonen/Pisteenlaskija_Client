from tkinter import *
from tkinter.font import Font
from PIL import ImageTk, Image
from globals import *

window = Tk()

window.title("Sanghai Pisteenlaskija")
#window.geometry("1280x720")
#window.minsize(width=640, height=360)



SijaintiX = SijaintiXOletus
SijaintiY = SijaintiYOletus



#e = Tausta(window)

#e.pack(fill=BOTH, expand=YES)
#e.pack_propagate(False)

background_image = Image.open(".venv/media/tausta.png")

resized_background = background_image.resize((1280,720), Image.ADAPTIVE)
background_width, background_height = resized_background.size
background_image2 = ImageTk.PhotoImage(resized_background)

ikkunaCanvas = Canvas(window, width=background_width, height=background_height)
ikkunaCanvas.pack()

ikkunaCanvas.create_image(0,0, anchor="nw", image=background_image2)

#kierrosCanvas = Canvas(e, width=100, height=600)
#kierrosCanvas.pack()

ikkunaCanvasHeight = ikkunaCanvas.winfo_height()
ekaKierrosYLocation = int(0.1 *ikkunaCanvasHeight)
print(ekaKierrosYLocation)

ikkunaCanvas.create_text(10, 80, anchor="w", text="2xK")
ikkunaCanvas.create_text(10, 120, anchor="w",text=background_height)

#kierrosFrame = Frame(window, relief = 'raised', borderwidth=0)
#kierrosFrame.place(y= 85, anchor='w')
#text1=kierrosFrame.winfo_geometry()

#Label(kierrosFrame, text=text1, font= ('Helvetica 15')).pack()
#Label(kierrosFrame, text="K+S", font= ('Helvetica 15')).pack()

window.mainloop()