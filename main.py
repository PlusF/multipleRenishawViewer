import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import matplotlib.pyplot as plt
import matplotlib.backend_bases
from matplotlib import rcParams, patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler, MouseButton, _Mode
from RenishawDataLoader import RenishawDataLoader

rcParams['keymap.back'].remove('left')
rcParams['keymap.forward'].remove('right')


class MainWindow(tk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self.master = master
        self.width_master = 1600
        self.height_master = 650
        self.master.geometry(f'{self.width_master}x{self.height_master}')
        self.master.title('multiple Viewer')

        self.dataloader = RenishawDataLoader()
        self.index, self.row, self.col = 0, 0, 0
        self.line = None

        self.create_widgets()

    def create_widgets(self):
        # canvas
        self.width_canvas = 1200
        self.height_canvas = 600
        dpi = 50
        if os.name == 'posix':
            self.width_canvas /= 2
            self.height_canvas /= 2
        fig, self.ax = plt.subplots(1, 2, figsize=(self.width_canvas / dpi, self.height_canvas / dpi), dpi=dpi)
        self.canvas = FigureCanvasTkAgg(fig, self.master)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=3)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=3, column=0)
        plt.subplots_adjust(left=0.03, right=0.99, bottom=0.05, top=0.99)
        fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('key_press_event', self.key_pressed)
        self.canvas.mpl_connect('key_press_event', key_press_handler)

        # frames
        frame_data = tk.LabelFrame(self.master, text='Data')
        frame_plot = tk.LabelFrame(self.master, text='Plot')
        frame_data.grid(row=0, column=1)
        frame_plot.grid(row=1, column=1)

        # frame data
        label_folder = tk.Label(frame_data, text='Folder:')
        label_filename = tk.Label(frame_data, text='Filename:')
        self.folder = tk.StringVar(value='None')
        self.filename = tk.StringVar(value='None')
        label_folder_value = tk.Label(frame_data, textvariable=self.folder)
        label_filename_value = tk.Label(frame_data, textvariable=self.filename)
        label_folder.grid(row=0, column=0)
        label_folder_value.grid(row=0, column=1)
        label_filename.grid(row=1, column=0)
        label_filename_value.grid(row=1, column=1)

        # frame plot
        label_map_range = tk.Label(frame_plot, text='Map Range')
        self.map_range = tk.StringVar(value='G(1570~1610)')
        self.optionmenu_map_range = tk.OptionMenu(frame_plot, self.map_range, 'G(1570~1610)', '2D(2550~2750)',
                                                  command=self.change_map_range)
        self.optionmenu_map_range.config(state=tk.DISABLED)
        self.map_range_1 = tk.DoubleVar(value=1570)
        self.map_range_2 = tk.DoubleVar(value=1610)
        entry_map_range_1 = tk.Entry(frame_plot, textvariable=self.map_range_1, width=7, justify=tk.CENTER)
        entry_map_range_2 = tk.Entry(frame_plot, textvariable=self.map_range_2, width=7, justify=tk.CENTER)
        label_cmap_range = tk.Label(frame_plot, text='Color Range')
        self.cmap_range_1 = tk.DoubleVar(value=0)
        self.cmap_range_2 = tk.DoubleVar(value=10000)
        entry_cmap_range_1 = tk.Entry(frame_plot, textvariable=self.cmap_range_1, width=7, justify=tk.CENTER)
        entry_cmap_range_2 = tk.Entry(frame_plot, textvariable=self.cmap_range_2, width=7, justify=tk.CENTER)
        self.button_apply = tk.Button(frame_plot, text='APPLY', command=self.show_img, width=7, state=tk.DISABLED)
        label_map_color = tk.Label(frame_plot, text='Color Map')
        self.map_color = tk.StringVar(value='hot')
        self.optionmenu_map_color = tk.OptionMenu(frame_plot, self.map_color,
                                                  *sorted(['viridis', 'plasma', 'inferno', 'magma', 'cividis',
                                                           'Wistia', 'hot', 'binary', 'bone', 'cool', 'copper',
                                                           'gray', 'pink', 'spring', 'summer', 'autumn', 'winter',
                                                           'RdBu', 'Spectral', 'bwr', 'coolwarm', 'hsv', 'twilight',
                                                           'CMRmap', 'cubehelix', 'brg', 'gist_rainbow', 'rainbow',
                                                           'jet', 'nipy_spectral', 'gist_ncar']),
                                                  command=self.show_img)
        self.optionmenu_map_color.config(state=tk.DISABLED)
        label_alpha = tk.Label(frame_plot, text='Alpha')
        self.alpha = tk.DoubleVar(value=1)
        entry_alpha = tk.Entry(frame_plot, textvariable=self.alpha, width=7, justify=tk.CENTER)
        self.autoscale = tk.BooleanVar(value=True)
        checkbox_autoscale = tk.Checkbutton(frame_plot, text='Auto Scale', variable=self.autoscale)

        label_map_range.grid(row=0, column=0, rowspan=2)
        self.optionmenu_map_range.grid(row=0, column=1, columnspan=2)
        self.button_apply.grid(row=0, column=3, rowspan=5, sticky=tk.NSEW)
        entry_map_range_1.grid(row=1, column=1)
        entry_map_range_2.grid(row=1, column=2)
        label_cmap_range.grid(row=2, column=0)
        entry_cmap_range_1.grid(row=2, column=1)
        entry_cmap_range_2.grid(row=2, column=2)
        label_map_color.grid(row=3, column=0)
        self.optionmenu_map_color.grid(row=3, column=1, columnspan=2)
        label_alpha.grid(row=4, column=0)
        entry_alpha.grid(row=4, column=1)
        checkbox_autoscale.grid(row=5, column=0, columnspan=3)

    def on_click(self, event: matplotlib.backend_bases.MouseEvent) -> None:
        # クリックした点のスペクトルを表示する
        # 移動モード（不具合あり）
        if event.button == MouseButton.MIDDLE:
            self.toolbar.pan()
            return
        if event.xdata is None or event.ydata is None:
            return
        # どのファイルか探す
        found = self.dataloader.set_index_from_coord(event.xdata, event.ydata)
        if not found:
            return
        # ファイルが特定されたらファイル名を表示
        filename = self.dataloader.get_current_filename()
        folder, basename = os.path.split(filename)
        self.folder.set(folder)
        self.filename.set(basename)
        # インデックスを計算
        self.row, self.col = self.dataloader.coord2idx(event.xdata, event.ydata)
        self.update_plot()

    def key_pressed(self, event: matplotlib.backend_bases.KeyEvent) -> None:
        # 矢印キーで表示するスペクトルを変えられる
        if event.key == 'enter':
            self.show_img()
            return
        # column majorに変換
        row, col = self.dataloader.row2col(self.row, self.col)
        if event.key == 'up' and row < self.dataloader.get_current_shape()[0] - 1:
            row += 1
        elif event.key == 'down' and 0 < row:
            row -= 1
        elif event.key == 'right' and col < self.dataloader.get_current_shape()[1] - 1:
            col += 1
        elif event.key == 'left' and 0 < col:
            col -= 1
        else:
            return
        self.row, self.col = self.dataloader.col2row(row, col)
        self.update_plot()

    def drop(self, event: TkinterDnD.DnDEvent=None) -> None:
        # ドラッグ&ドロップされたファイルを処理
        if event.data[0] == '{':
            filenames = map(lambda f: f.strip('{').strip('}'), event.data.split('} {'))
        else:
            filenames = event.data.split()

        # wdfファイルのみ受け付ける
        filenames = [fn for fn in filenames if fn.split('.')[-1] == 'wdf']

        ok = self.dataloader.load_files(filenames)
        if not ok:
            messagebox.showwarning('Warning', 'Some of them are not map data.')

        self.optionmenu_map_range.config(state=tk.ACTIVE)
        self.button_apply.config(state=tk.ACTIVE)
        self.optionmenu_map_color.config(state=tk.ACTIVE)
        self.show_img()

    def change_map_range(self, event=None) -> None:
        if self.map_range.get() == 'G(1570~1610)':
            self.map_range_1.set(1570)
            self.map_range_2.set(1610)
        elif self.map_range.get() == '2D(2550~2750)':
            self.map_range_1.set(2550)
            self.map_range_2.set(2750)
        self.show_img()

    def show_img(self, event=None) -> None:
        self.ax[0].cla()
        self.horizontal_line = self.ax[0].axhline(color='k', lw=1, ls='--')
        self.vertical_line = self.ax[0].axvline(color='k', lw=1, ls='--')
        self.dataloader.show_img(
            self.ax[0],
            [self.map_range_1.get(), self.map_range_2.get()],
            self.map_color.get(),
            [self.cmap_range_1.get(), self.cmap_range_2.get()],
            self.alpha.get())
        self.canvas.draw()

    def update_plot(self) -> None:
        # マッピング上のクロスヘアを移動
        x, y = self.dataloader.idx2coord(self.row, self.col)
        self.horizontal_line.set_ydata(y)
        self.vertical_line.set_xdata(x)

        shape = self.dataloader.get_current_shape()
        if not (0 <= self.row < shape[0] and 0 <= self.col < shape[1]):
            return

        if self.autoscale.get():
            plt.autoscale(True)
            self.ax[1].cla()
        else:
            if self.line is not None:
                plt.autoscale(False)  # The very first time requires autoscale
                self.line[0].remove()
            else:  # for after calibration
                self.ax[1].cla()
        idx = self.dataloader.row2col(self.row, self.col)
        xdata = self.dataloader.wavenumber_list[self.dataloader.current_selected_index]
        ydata = self.dataloader.spectra_list[self.dataloader.current_selected_index][self.row][self.col]
        self.line = self.ax[1].plot(xdata, ydata, label=str(idx), color='r', linewidth=0.8)
        self.ax[1].legend()
        self.canvas.draw()

    def quit(self) -> None:
        self.master.quit()
        self.master.destroy()


def main():
    root = TkinterDnD.Tk()
    app = MainWindow(master=root)
    root.protocol('WM_DELETE_WINDOW', app.quit)
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', app.drop)
    app.mainloop()


if __name__ == '__main__':
    main()
