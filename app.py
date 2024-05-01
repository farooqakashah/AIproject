from flask import Flask, render_template, request, jsonify
from nim import Nim, NimAI, GamePlay
from threading import Thread

app = Flask(__name__)

# Initialize the AI player
ai = NimAI()

# Initialize the game
game = Nim()

# Background thread for training the AI
def train_ai():
    global ai
    ai = GamePlay.train(10000)  # Train the AI for 10000 iterations
    # After training, return to the '/' route
    with app.app_context():
        render_template('index.html')

# Start the training process in the background
training_thread = Thread(target=train_ai)
training_thread.start()

@app.route('/')
def index():
    # Pass the piles information to the template
    piles = game.piles
    return render_template('index.html', piles=piles)

@app.route('/make_move', methods=['POST'])
def make_move():
    try:
        pile = int(request.json.get('pile', ''))
        count = int(request.json.get('count', ''))

        # Check if pile and count are valid
        if pile not in range(1, 5) or count < 1:
            raise ValueError("Invalid input.")

        # Make move in the game
        game.move((pile - 1, count))

        # Check game status
        if game.winner is not None:
            message = f"Player {game.winner + 1} wins!"
        else:
            message = "Move made successfully."

        # Let AI make a move
        ai_pile, ai_count = ai.choose_action(game.piles, epsilon=False)
        game.move((ai_pile, ai_count))

        return jsonify({'message': message, 'ai_move': {'pile': ai_pile, 'count': ai_count}})

    except (ValueError, KeyError) as e:
        return jsonify({'message': f"Error: {e}"}), 400

@app.route('/reset_game', methods=['POST'])
def reset_game():
    global game
    game = Nim()
    return jsonify({'message': 'Game reset.'})

if __name__ == '__main__':
    app.run(debug=True,port=8000)
