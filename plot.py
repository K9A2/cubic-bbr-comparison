# coding=utf-8
# filename: plot.py

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


rtt = [12, 30, 60, 100, 200, 300]
rtt_label = ['12', '30', '60', '100', '200', '300']
loss = [0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 3.0, 5.0]
loss_label = ['0.01', '0.05', '0.1', '0.2', '0.4',
              '0.6', '0.8', '1.0', '3.0', '5.0']

font_size = 30

# color_scheme = ['Accent', 'Accent_r', 'Blues', 'Blues_r', 'BrBG', 'BrBG_r', 
#                 'BuGn', 'BuGn_r', 'BuPu', 'BuPu_r', 'CMRmap', 'CMRmap_r', 
#                 'Dark2', 'Dark2_r', 'GnBu', 'GnBu_r', 'Greens', 'Greens_r', 
#                 'Greys', 'Greys_r', 'OrRd', 'OrRd_r', 'Oranges', 'Oranges_r', 
#                 'PRGn', 'PRGn_r', 'Paired', 'Paired_r', 'Pastel1', 'Pastel1_r', 
#                 'Pastel2', 'Pastel2_r', 'PiYG', 'PiYG_r', 'PuBu', 'PuBuGn', 
#                 'PuBuGn_r', 'PuBu_r', 'PuOr', 'PuOr_r', 'PuRd', 'PuRd_r', 
#                 'Purples', 'Purples_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r', 
#                 'RdPu', 'RdPu_r', 'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r', 
#                 'Reds', 'Reds_r', 'Set1', 'Set1_r', 'Set2', 'Set2_r', 'Set3', 
#                 'Set3_r', 'Spectral', 'Spectral_r', 'Wistia', 'Wistia_r', 
#                 'YlGn', 'YlGnBu', 'YlGnBu_r', 'YlGn_r', 'YlOrBr', 'YlOrBr_r', 
#                 'YlOrRd', 'YlOrRd_r', 'afmhot', 'afmhot_r', 'autumn', 
#                 'autumn_r', 'binary', 'binary_r', 'bone', 'bone_r', 'brg', 
#                 'brg_r', 'bwr', 'bwr_r', 'cividis', 'cividis_r', 'cool', 
#                 'cool_r', 'coolwarm', 'coolwarm_r', 'copper', 'copper_r', 
#                 'cubehelix', 'cubehelix_r', 'flag', 'flag_r', 'gist_earth', 
#                 'gist_earth_r', 'gist_gray', 'gist_gray_r', 'gist_heat', 
#                 'gist_heat_r', 'gist_ncar', 'gist_ncar_r', 'gist_rainbow', 
#                 'gist_rainbow_r', 'gist_stern', 'gist_stern_r', 'gist_yarg', 
#                 'gist_yarg_r', 'gnuplot', 'gnuplot2', 'gnuplot2_r', 'gnuplot_r', 
#                 'gray', 'gray_r', 'hot', 'hot_r', 'hsv', 'hsv_r', 'icefire', 
#                 'icefire_r', 'inferno', 'inferno_r', 'jet', 'jet_r', 'magma', 
#                 'magma_r', 'mako', 'mako_r', 'nipy_spectral', 'nipy_spectral_r',
#                  'ocean', 'ocean_r', 'pink', 'pink_r', 'plasma', 'plasma_r', 
#                  'prism', 'prism_r', 'rainbow', 'rainbow_r', 'rocket', 
#                  'rocket_r', 'seismic', 'seismic_r', 'spring', 'spring_r', 
#                  'summer', 'summer_r', 'tab10', 'tab10_r', 'tab20', 'tab20_r', 
#                  'tab20b', 'tab20b_r', 'tab20c', 'tab20c_r', 'terrain', 
#                  'terrain_r', 'viridis', 'viridis_r', 'vlag', 'vlag_r', 
#                  'winter', 'winter_r']

color_scheme = ['magma_r']

def plot_bar_chart():

    bbr = {
        12:  [1.066, 1.070, 1.072, 1.076, 1.083,
              1.089, 1.094, 1.096, 1.120, 1.190],
        30:  [1.068, 1.070, 1.073, 1.079, 1.085,
              1.092, 1.093, 1.098, 1.117, 1.140],
        60:  [1.064, 1.072, 1.075, 1.081, 1.088,
              1.092, 1.092, 1.094, 1.119, 1.138],
        100: [1.067, 1.078, 1.083, 1.083, 1.093,
              1.092, 1.095, 1.097, 1.119, 1.139],
        200: [1.093, 1.094, 1.096, 1.106, 1.101,
              1.103, 1.098, 1.101, 1.121, 1.143],
        300: [1.099, 1.100, 1.096, 1.097, 1.108,
              1.105, 1.105, 1.105, 1.124, 1.148]
    }

    cubic = {
        12:  [1.066, 1.067, 1.068, 1.071, 1.073,
              1.077, 1.081, 1.083, 1.111, 1.137],
        30:  [1.066, 1.066, 1.070, 1.072, 1.074,
              1.077, 1.080, 1.084, 1.110, 1.137],
        60:  [1.062, 1.068, 1.070, 1.072, 1.075,
              1.077, 1.081, 1.084, 1.111, 1.137],
        100: [1.061, 1.067, 1.069, 1.072, 1.075,
              1.077, 1.080, 1.083, 1.110, 1.138],
        200: [1.059, 1.068, 1.069, 1.072, 1.074,
              1.076, 1.081, 1.084, 1.112, 1.138],
        300: [1.062, 1.065, 1.069, 1.068, 1.074,
              1.077, 1.081, 1.084, 1.112, 1.138]
    }

    diff = {}

    loss_labels = ['0.01', '0.05', '0.1', '0.2', '0.4',
                    '0.6', '0.8', '1.0', '3.0', '5.0']

    fig, ax1 = plt.subplots(figsize=(16, 9))
    plt.xlabel('Loss Rate (%)', fontsize=font_size)
    plt.ylabel('P', fontsize=font_size)
    plt.yticks(fontsize=font_size)

    lines = []

    size = len(loss)

    x = np.arange(size)
    total_width, n = 0.8, 2

    width = total_width / n

    # 求百分比
    for i in range(0, len(rtt)):
        diff[rtt[i]] = np.array(bbr[rtt[i]]) - np.array(cubic[rtt[i]])

    data_1 = np.array(diff[30]) / cubic[30] * 100
    data_2 = np.array(diff[200]) / cubic[200] * 100

    pos_1 = x - 0.2
    pos_2 = x + 0.2

    plt.bar(pos_1, data_1, width=0.4, label='30ms', color='royalblue')
    plt.bar(pos_2, data_2, width=0.4, label='200ms', color='coral')

    plt.ylim(0, 4)
    plt.legend(fontsize=font_size)

    plt.subplots_adjust(left=0.12, right=0.95, top=0.96, bottom=0.15)
    plt.xticks(np.arange(len(loss_label)), loss_label, fontsize=font_size, y=-0.03)

    plt.show()


def plot_heatmap(data, size, cbar_label, margin, range, fmt, file_name):

    fig, ax1 = plt.subplots(figsize=size)

    sns.set()
    sns.heatmap(data, yticklabels=rtt_label, xticklabels=loss_label,
                vmin=range['min'], vmax=range['max'],
                annot=True, annot_kws={'size': font_size},
                cmap=color_scheme[0],
                cbar_kws={'label': cbar_label},
                fmt=fmt)

    plt.xticks(rotation=45, fontsize=font_size)
    plt.yticks(rotation=45, fontsize=font_size)

    plt.xlabel('Loss Rate (%)', fontsize=font_size)
    plt.ylabel('RTT (ms)', fontsize=font_size)

    cax = plt.gcf().axes[-1]
    cax.tick_params(labelsize=font_size)

    ax1.figure.axes[-1].yaxis.label.set_size(font_size)

    # plt.subplots_adjust(left=0.11, right=1.00, top=0.93, bottom=0.20)
    plt.subplots_adjust(left=margin['left'], right=margin['right'], top=margin['top'], bottom=margin['bottom'])
    plt.tight_layout()
    # plt.savefig('C:\\Users\\stormlin\\sample\\' + c + '.png')
    plt.savefig(file_name)
    # plt.show()


def plot_heatmap_retr_per_packet():

    bbr = [
        [0.000, 0.001, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.052],
        [0.000, 0.001, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.000, 0.001, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.002, 0.002, 0.003, 0.004, 0.006, 0.006, 0.009, 0.010, 0.032, 0.053],
        [0.020, 0.009, 0.010, 0.016, 0.013, 0.013, 0.013, 0.014, 0.034, 0.052],
        [0.022, 0.013, 0.007, 0.008, 0.017, 0.014, 0.015, 0.016, 0.032, 0.054]
    ]

    cubic = [
        [0.000, 0.001, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.000, 0.000, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.000, 0.001, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.000, 0.000, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.000, 0.000, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053],
        [0.000, 0.000, 0.001, 0.002, 0.004, 0.006, 0.008, 0.010, 0.031, 0.053]
    ]

    plot_heatmap(np.array(cubic) * 100, (20, 9), '% of retransmission\nin all packets',
        { 'left': 0.11, 'right': 1.00, 'top': 0.93, 'bottom': 0.20 },
        { 'min': 0.0, 'max': 6.0 },
        '.1f', 'C:\\Users\\stormlin\\sample\\cubic-heatmap-retr-in-all.pdf')

    plot_heatmap(np.array(bbr) * 100, (20, 9), '% of retransmission\nin all packets',
        { 'left': 0.11, 'right': 1.00, 'top': 0.93, 'bottom': 0.20 },
        { 'min': 0.0, 'max': 6.0 },
        '.1f', 'C:\\Users\\stormlin\\sample\\bbr-heatmap-retr-in-all.pdf')


def plot_heatmap_retr_per_loss():

    bbr = [
        [1.011, 1.014, 1.001, 1.004, 1.004, 1.005, 1.008, 1.009, 1.033, 1.052],
        [1.000, 1.008, 1.000, 1.002, 1.007, 1.008, 1.009, 1.011, 1.034, 1.052],
        [1.000, 1.011, 1.001, 1.009, 1.005, 1.007, 1.014, 1.012, 1.031, 1.053],
        [1.001, 1.004, 1.063, 1.001, 1.089, 1.007, 1.010, 1.008, 1.032, 1.054],
        [1.002, 1.013, 1.010, 1.002, 1.007, 1.010, 1.008, 1.011, 1.030, 1.052],
        [1.012, 1.011, 1.031, 1.017, 1.036, 1.047, 1.008, 1.010, 1.030, 1.054]
    ]

    cubic = [
        [1.001, 1.002, 1.001, 1.003, 1.004, 1.007, 1.008, 1.008, 1.032, 1.059],
        [1.000, 1.003, 1.000, 1.003, 1.003, 1.005, 1.007, 1.016, 1.032, 1.057],
        [1.000, 1.000, 1.001, 1.001, 1.003, 1.007, 1.007, 1.010, 1.031, 1.058],
        [1.000, 1.000, 1.000, 1.001, 1.004, 1.006, 1.007, 1.010, 1.032, 1.054],
        [1.000, 1.000, 1.003, 1.001, 1.004, 1.006, 1.008, 1.011, 1.031, 1.054],
        [1.000, 1.000, 1.003, 1.003, 1.004, 1.008, 1.009, 1.010, 1.030, 1.057]
    ]

    plot_heatmap(np.array(cubic), (20, 9), 'Retransmission per loss',
        { 'left': 0.11, 'right': 1.00, 'top': 0.93, 'bottom': 0.20 },
        { 'min': 1.00, 'max': 1.10 },
        '.3f', 'C:\\Users\\stormlin\\sample\\cubic-heatmap-retr-per-loss.pdf')

    plot_heatmap(np.array(bbr), (20, 9), 'Retransmission per loss',
        { 'left': 0.11, 'right': 1.00, 'top': 0.93, 'bottom': 0.20 },
        { 'min': 1.00, 'max': 1.10 },
        '.3f', 'C:\\Users\\stormlin\\sample\\bbr-heatmap-retr-per-loss.pdf')


def plot_throughput_heatmap():

    bbr = [
        [89.9, 89.5, 89.8, 89.6, 89.4, 89.5, 89.2, 89.8, 89.8, 91.2],
        [89.8, 89.5, 89.7, 89.5, 89.5, 89.3, 89.5, 89.6, 90.7, 90.3],
        [89.3, 89.0, 89.3, 88.8, 88.8, 88.0, 88.8, 89.1, 90.4, 89.3],
        [88.4, 88.0, 88.3, 87.8, 87.5, 87.5, 87.6, 88.2, 90.4, 88.6],
        [85.8, 85.5, 86.1, 87.5, 85.9, 84.5, 82.9, 85.0, 70.8, 62.7],
        [83.1, 82.5, 82.1, 80.3, 84.9, 68.1, 64.3, 80.7, 50.3, 44.1]
    ]

    cubic = [
        [89.6, 46.9, 33.2, 22.9, 15.5, 12.5, 10.5, 9.40, 4.30, 2.90],
        [43.8, 20.5, 14.0, 9.70, 6.50, 5.10, 4.30, 3.70, 1.70, 1.20],
        [26.9, 10.1, 7.00, 4.90, 3.20, 2.60, 2.20, 7.90, 0.90, 0.60],
        [21.8, 8.10, 4.80, 3.20, 2.20, 1.70, 1.40, 1.10, 0.60, 0.50],
        [26.1, 6.20, 3.60, 2.20, 1.30, 0.90, 0.70, 0.70, 0.30, 0.20],
        [17.9, 6.00, 3.30, 1.90, 1.20, 0.80, 0.70, 0.60, 0.30, 0.20]
    ]

    plot_heatmap(cubic, (20, 9), 'Throughput (Mbps)',
        { 'left': 0.11, 'right': 1.00, 'top': 0.93, 'bottom': 0.20 },
        { 'min': 0, 'max': 100 },
        '.1f', 'C:\\Users\\stormlin\\sample\\cubic-heatmap-throughput.pdf')

    plot_heatmap(bbr, (20, 9), 'Throughput (Mbps)',
        { 'left': 0.11, 'right': 1.00, 'top': 0.93, 'bottom': 0.20 },
        { 'min': 0, 'max': 100 },
        '.1f', 'C:\\Users\\stormlin\\sample\\bbr-heatmap-throughput.pdf')


def main():

    # plot_bar_chart()
    plot_heatmap_retr_per_packet()
    plot_heatmap_retr_per_loss()
    plot_throughput_heatmap()


if __name__ == "__main__":
    main()
