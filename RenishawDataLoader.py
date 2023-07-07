import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from renishawWiRE import WDFReader


def subtract_baseline(data: np.ndarray):
    baseline = np.linspace(data[0], data[-1], data.shape[0])
    return data - baseline


# Calibratorは自作ライブラリ。Rayleigh, Raman用のデータとフィッティングの関数等が含まれている。
class RenishawDataLoader:
    def __init__(self):
        self.wavenumber_list = []
        self.spectra_list = []
        self.maporigin_list = np.empty((0, 2))
        self.pixelsize_list = np.empty((0, 2))
        self.mapsize_list = np.empty((0, 2))
        self.img_list = []
        self.imgorigin_list = np.empty((0, 2))
        self.imgsize_list = np.empty((0, 2))
        self.current_selected_index = 0

    def load(self, filename: str) -> bool:
        # 二次元マッピングファイルを読み込む
        reader = WDFReader(filename)
        # 二次元じゃない場合False (x座標) x (y座標) x (スペクトル) の3次元のはず
        if len(reader.spectra.shape) != 3:
            return False
        self.wavenumber_list.append(reader.xdata)
        self.spectra_list.append(reader.spectra)
        # self.shape = self.map_data.shape[:2]
        # マッピングの一番右下の座標
        self.maporigin_list = np.append(self.maporigin_list, np.array([[
            reader.map_info['x_start'],
            reader.map_info['y_start'],
        ]]), axis=0)
        # マッピングの1ピクセルあたりのサイズ
        self.pixelsize_list = np.append(self.pixelsize_list, np.array([[
            reader.map_info['x_pad'],
            reader.map_info['y_pad'],
        ]]), axis=0)
        # マッピングの全体のサイズ
        self.mapsize_list = np.append(self.mapsize_list, np.array([[
            reader.map_info['x_span'],
            reader.map_info['y_span'],
        ]]), axis=0)
        # 光学像
        self.img_list.append(reader.img)
        # 光学像の原点
        self.imgorigin_list = np.append(self.imgorigin_list, np.array([reader.img_origins]), axis=0)
        # 光学像のサイズ
        self.imgsize_list = np.append(self.imgsize_list, np.array([reader.img_dimensions]), axis=0)
        return True

    def load_files(self, filenames: list[str]) -> bool:
        ok_list = [self.load(filename) for filename in filenames]
        return all(ok_list)

    def show_img(self, ax: plt.Axes, map_range: list[float], cmap, cmap_range: list[float], alpha: float) -> None:
        # 光学像の表示
        for img, (img_x0, img_y0), (img_w, img_h) in zip(self.img_list, self.imgorigin_list, self.imgsize_list):
            img = Image.open(img)
            extent_optical = (img_x0, img_x0 + img_w, img_y0 + img_h, img_y0)
            ax.imshow(img, extent=extent_optical)
        ax.set_xlim(self.imgorigin_list[:, 0].min(), (self.imgorigin_list + self.imgsize_list)[:, 0].max())
        ax.set_ylim(self.imgorigin_list[:, 1].min(), (self.imgorigin_list + self.imgsize_list)[:, 1].max())
        # マッピングの表示
        for wavenumber, spectra, (map_x0, map_y0), (map_w, map_h), (px, py) in zip(self.wavenumber_list, self.spectra_list, self.maporigin_list, self.mapsize_list, self.pixelsize_list):
            extent_mapping = (map_x0, map_x0 + map_w, map_y0, map_y0 + map_h)
            map_range_idx = (map_range[0] < wavenumber) & (wavenumber < map_range[1])
            data = spectra[:, :, map_range_idx]
            if data.shape[2] == 0:  # out of range
                return
            data = np.array([[subtract_baseline(d).sum() for d in dat] for dat in data])
            data = data.reshape(data.shape[::-1]).T
            ax.imshow(data, alpha=alpha, extent=extent_mapping, origin='lower', cmap=cmap, norm=Normalize(vmin=cmap_range[0], vmax=cmap_range[1]))
        ax.invert_yaxis()

    def get_current_shape(self):
        return self.spectra_list[self.current_selected_index].shape[:2]

    def col2row(self, row: int, col: int) -> [int, int]:
        shape = self.spectra_list[self.current_selected_index].shape[:2]
        idx = col * shape[0] + row
        # column major to row major
        row = idx // shape[1]
        col = idx % shape[1]

        return row, col

    def row2col(self, row: int, col: int) -> [int, int]:
        shape = self.spectra_list[self.current_selected_index].shape[:2]
        idx = row * shape[1] + col
        # row major to column major
        col = idx // shape[0]
        row = idx % shape[0]

        return row, col

    def coord2idx(self, x_pos: float, y_pos: float) -> [int, int]:
        # get index of column major
        x0, y0 = self.maporigin_list[self.current_selected_index]
        w, h = self.pixelsize_list[self.current_selected_index]
        col = round((x_pos - x0) // w)
        row = round((y_pos - y0) // h)
        # change to row major and return it
        return self.col2row(row, col)

    def idx2coord(self, row: int, col: int) -> [float, float]:
        # get column major index
        row, col = self.row2col(row, col)
        x0, y0 = self.maporigin_list[self.current_selected_index]
        px, py = self.pixelsize_list[self.current_selected_index]
        return x0 + px * (col + 0.5), y0 + py * (row + 0.5)

    def is_inside(self, x: float, y: float) -> bool:
        # check if the selected position is inside the mapping
        x0, y0 = self.maporigin_list[self.current_selected_index]
        w, h = self.mapsize_list[self.current_selected_index]
        if (x0 <= x <= x0 + w) and (y0 + h <= y <= y0):
            return True
        else:
            return False

    def set_index_from_coord(self, x: float, y: float):
        for i in range(len(self.mapsize_list)):
            self.current_selected_index = i
            if self.is_inside(x, y):
                return True
        return False
