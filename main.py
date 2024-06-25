from data_retrieval import data_reciever
from visualization import data_visualizer


if __name__ == '__main__':
    data = data_reciever()
    vis = data_visualizer(data.data)

    vis.plot_data()