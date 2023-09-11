"""Main entrypoint."""

from gymnasium import make
from gymnasium.wrappers import FlattenObservation
from sb3_contrib import MaskablePPO
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from rl_bin_packing.container.two_d import Container, Shipment
from rl_bin_packing.utils import DataClassGenerator

if __name__ == "__main__":
    container = Container(600, 300)

    shipments = DataClassGenerator(
        Shipment,
        length=100,
        height=100,
        weight=1000,
        stackable=True,
        rotatable=False,
        identifier="abc",
    ).generate_instances(num_instances=10)

    # Environment initialization
    env = make(
        "2DBinPackingEnv-v0",
        container=container,
        shipments=shipments,
    )
    env = FlattenObservation(env)
    env.reset()

    check_env(env, warn=True)

    # model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="logs")
    # print("begin training")
    # model.learn(total_timesteps=10)
    # print("done training")
    # model.save("ppo")
    model = PPO.load("ppo")

    obs = env.reset()
    while True:
        action = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        fig = env.render()
        if terminated:
            break
    fig.show(renderer="browser")

    # gif = GIF(gif_name="random_rollout.gif", gif_path="../gifs")
    # for step_num in range(80):
    #     fig = env.render()
    #     gif.create_image(fig)
    #     action_mask = obs["action_mask"]
    #     action = env.action_space.sample(mask=action_mask)
    #     obs, reward, done, info = env.step(action)
    #     if done:
    #         break

    # gif.create_gif()
    # gif.save_gif("random_rollout.gif")
