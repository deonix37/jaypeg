import io
import os
import platform
import random
import subprocess
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import urllib.request

from PIL import Image


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('JayPeg™')
        self.geometry('256x256')
        JayPeg(self)


class JayPeg(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)
        self.jaypeg_button = JayPegButton(self)
        self.jaypeg_url_button = JayPegUrlButton(self)
        self.quality_from = tk.Scale(
            self, from_=1, to=100,
            orient=tk.HORIZONTAL,
            label='Min quality',
        )
        self.quality_to = tk.Scale(
            self, from_=1, to=100,
            orient=tk.HORIZONTAL,
            label='Max quality',
        )
        self.repeats = tk.Scale(
            self, from_=1, to=1000,
            orient=tk.HORIZONTAL,
            label='Repeats',
        )
        self.jaypeg_button.grid(row=1, pady=10)
        self.jaypeg_url_button.grid(row=1, column=2, pady=10)
        self.quality_from.grid(row=2)
        self.quality_to.grid(row=3)
        self.repeats.grid(row=4)


class JayPegButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(text='Select an image', command=self.process)

    def process(self):
        filename = tk.filedialog.askopenfilename()

        if filename:
            self.process_image(filename)

    def process_image(self, input_image):
        try:
            image = Image.open(input_image).convert('RGB')
        except OSError as e:
            return tk.messagebox.showerror('Error', str(e))

        output_filename = tk.filedialog.asksaveasfilename(
            filetypes=(('JayPeg™', '*.jpg'),),
            defaultextension='.jpg',
        )

        if not output_filename:
            return

        if not output_filename.endswith(('.jpg', '.jpeg')):
            return tk.messagebox.showerror(
                'Error', 'Output must be saved as .jpg',
            )

        try:
            self.jaypeg(image, output_filename)
        except Exception as e:
            tk.messagebox.showerror('Error', str(e))
        else:
            if tk.messagebox.askyesno('Confirm', 'Open result folder?'):
                path = os.path.dirname(output_filename)

                if platform.system() == 'Windows':
                    os.startfile(path)
                elif platform.system() == 'Darwin':
                    subprocess.Popen(('open', path))
                else:
                    subprocess.Popen(('xdg-open', path))

    def jaypeg(self, image, output_filename):
        image.save(output_filename)
        quality_from = self.master.quality_from.get()
        quality_to = self.master.quality_to.get()
        repeats = self.master.repeats.get()

        if quality_from > quality_to:
            raise Exception('Invalid quality range')

        for i in range(repeats):
            quality = random.randint(quality_from, quality_to)

            try:
                Image.open(output_filename).save(
                    output_filename, quality=quality,
                )
            except OSError:
                continue


class JayPegUrlButton(JayPegButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(text='From URL')

    def process(self):
        url = tk.simpledialog.askstring('From URL', 'Enter image URL')

        if not url:
            return

        try:
            response = urllib.request.urlopen(url)
        except Exception as e:
            return tk.messagebox.showerror('Error', str(e))

        if not response.headers.get('Content-Type', '').startswith('image'):
            return tk.messagebox.showerror('Error', 'Not an image')

        self.process_image(io.BytesIO(response.read()))


if __name__ == '__main__':
    App().mainloop()
