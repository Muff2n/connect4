from connect4.neural.config import AlphaZeroConfig, StorageConfig

# config = AlphaZeroConfig(simulations=100,
#                          n_training_games=10,
#                          n_training_epochs=2,
#                          use_pytorch=True)

config = AlphaZeroConfig(storage_config=StorageConfig(save_dir='/home/richard/Downloads/nn/new_dir2'),
                         game_processes=11,
                         game_threads=10,
                         n_training_epochs=1,
                         n_training_games=110,
                         use_pytorch=True)
