"""Model definition and training code."""
import numpy as np
import keras as kr
from keras import layers
import logic as lgc
from logic import timer
from history import History


INDEX_TO_ACTION = {
    0: 'L',
    1: 'U',
    2: 'R',
    3: 'D',
}

INDEX_TO_ACTION_FUNCTION = {
    0: lgc.left,
    1: lgc.up,
    2: lgc.right,
    3: lgc.down,
}

REWARDS = {
    'WIN': 5,
    'LOSE': -5,
    'NO_RESULT': -1,
    'CONTINUE': 0,
}

@timer
def choose_action(state, exploration_rate):
    """Returns encoded action"""
    if np.random.uniform(0, 1) > exploration_rate:
        batch_state = state.reshape(1, 4, 4)
        action = np.argmax(model.predict(batch_state)[0, 0, :])
    else:
        action = np.random.randint(0, 4)
    return action

@timer
def do_action(state, action):
    """Returns new state and evaluates reward and game state"""
    new_state, done = INDEX_TO_ACTION_FUNCTION[action](state)
    lgc.add_two(new_state)
    if np.array_equal(state, new_state):
        return new_state, REWARDS['NO_RESULT'], False
    game_state = lgc.game_state(new_state)
    if game_state == 1:
        return new_state, REWARDS['WIN'], True
    if game_state == -1:
        return new_state, REWARDS['LOSE'], True
    return new_state, REWARDS['CONTINUE'], False

@timer
def update_qtable(state, action, reward, new_state):
    """Updates Q-table"""
    batch_state = state.reshape(1, 4, 4)
    batch_new_state = new_state.reshape(1, 4, 4)
    if game_ended:
        target_action_qvalue = reward
    else:
        target_action_qvalue = np.max(model.predict(batch_state, verbose=False)[0, 0, :]) * (1 - learning_rate) + \
                learning_rate * (reward + discount_rate * np.max(model.predict(batch_new_state, verbose=False)[0, 0, :]))
    target_qvalues = model.predict(batch_state, verbose=False)
    target_qvalues[0, 0, action] = target_action_qvalue
    timed_fit = timer(model.fit)
    timed_fit(batch_state, target_qvalues, epochs=1, verbose=0)


MODEL_NICKNAME = "ProtoOrganism"
model = kr.models.Sequential([
    layers.Input(shape=(4, 4)),
    layers.Conv1D(16, (3, ), activation='relu'),
    layers.Conv1D(4, (2, ), activation='relu'),
    layers.Dense(4, activation='softmax'),
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# Hyperparameters
number_of_games = 1
max_moves = 100

learning_rate = 0.001
discount_rate = 0.99

exploration_rate = 1
max_exploration_rate = 1
min_exploration_rate = 0.01
exploration_decay_rate = 0.01

rewards_all_games = []
for game in range(number_of_games):
    print(f"---------------GAME {game}---------------")
    state = lgc.new_game(n=4)
    done = False
    rewards_current_game = 0

    history = History(mode="w", dir="history", filename=f"{MODEL_NICKNAME}_game_{game}")
    history.saveMatrix(state)

    for move in range(max_moves):
        print(f"-----Move {move}-----")
        # Choose action
        action = choose_action(state, exploration_rate)
        new_state, reward, game_ended = do_action(state, action)

        print(f"Action: {INDEX_TO_ACTION[action]}")

        # Save history
        history.saveMatrix(new_state)
        history.saveMove(INDEX_TO_ACTION[action])

        # Update Q-table
        update_qtable(state, action, reward, new_state)

        state = new_state
        rewards_current_game += reward

        if game_ended:
            history.close()
            break

    exploration_rate = min_exploration_rate + \
        (max_exploration_rate - min_exploration_rate) * np.exp(-exploration_decay_rate * game)
    
    rewards_all_games.append(rewards_current_game)

for game, rewards in enumerate(rewards_all_games):
    print(f"Game {game} avg. reward: {rewards} ")

# Updated model weights
model.save(f"models/{MODEL_NICKNAME}.keras")
# Print them
print(model.get_weights())