# swim-time-tracker
tool for saving times for swim events


 pyinstaller --onefile --windowed 
 --add-data "C:\Users\Bcbak\AppData\Local\Programs\Python\Python311\Lib\site-packages\pypdfium2_raw\pdfium.dll;pypdfium2_raw" 
 --add-data "C:\Users\Bcbak\AppData\Local\Programs\Python\Python311\Lib\site-packages\pypdfium2_raw\version.json;pypdfium2_raw" 
 --add-data "C:\Users\Bcbak\AppData\Local\Programs\Python\Python311\Lib\site-packages\pypdfium2\version.json;pypdfium2" 
 --add-data "<CustomTkinter Location>/customtkinter;customtkinter/"
 -i"C:\Users\Bcbak\OneDrive\Documents\projects\swim-time-tracker\swimmer.ico" src/app.py